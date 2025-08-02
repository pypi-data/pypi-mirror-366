import os
import time
import uuid
import json
import logging
import threading
import asyncio
import multiprocessing
from typing import Dict, Any, List, Set
from enum import Enum
from collections import defaultdict

import redis

logger = logging.getLogger('app')


class ConsumerStrategy(Enum):
    """消费者名称策略
    
    策略选择指南：
    
    ⚠️  POD (仅推荐单进程使用):
       - 基于K8s Pod名称的固定consumer
       - 适用场景: 单进程应用 (asyncio/thread执行器)
       - 优点: 语义清晰，便于监控
       - 缺点: 多进程下会产生冲突
       
    🔧 FIXED (高级用户):
       - 完全自定义的consumer名称
       - 适用场景: 有特殊命名需求的场景 
       - 优点: 完全可控
       - 缺点: 需要用户确保唯一性
    
    🔥 HEARTBEAT (推荐用于生产环境):
       - 基于心跳的简化策略
       - 适用场景: 无状态服务平台（Cloud Run、Serverless、K8s）
       - 优点: 逻辑简单，稳定可靠，自动故障恢复
       - 特点: 使用随机consumer name，通过有序集合维护心跳
    """
    FIXED = "fixed"      # 固定名称
    POD = "pod"          # K8s Pod名称 (⚠️ 多进程下不推荐)
    HEARTBEAT = "heartbeat"  # 心跳策略 (推荐用于生产环境)


class ConsumerManager:
    """消费者名称管理器"""
    
    def __init__(
        self, 
        redis_client: redis.StrictRedis,
        strategy: ConsumerStrategy = ConsumerStrategy.HEARTBEAT,
        config: Dict[str, Any] = None
    ):
        self.redis_client = redis_client
        self.strategy = strategy
        self.config = config or {}
        self._consumer_name = None
        
        # Redis prefix configuration
        self.redis_prefix = config.get('redis_prefix', 'jettask')
        
        # 验证策略配置的合理性
        self._validate_strategy_configuration()
        
        # 心跳策略实例 - 如果是HEARTBEAT策略，立即初始化
        if self.strategy == ConsumerStrategy.HEARTBEAT:
            # 传递队列信息到心跳策略
            heartbeat_config = self.config.copy()
            heartbeat_config['queues'] = self.config.get('queues', [])
            self._heartbeat_strategy = HeartbeatConsumerStrategy(
                self.redis_client,
                heartbeat_config
            )
        else:
            self._heartbeat_strategy = None
    
    def get_prefixed_queue_name(self, queue: str) -> str:
        """为队列名称添加前缀"""
        return f"{self.redis_prefix}:{queue}"
    
    def _validate_strategy_configuration(self):
        """验证消费者策略配置的合理性"""
        # 检查是否在多进程环境中
        current_process = multiprocessing.current_process()
        is_multiprocess = current_process.name != 'MainProcess'
        
        if self.strategy == ConsumerStrategy.POD and is_multiprocess:
            # POD策略在多进程环境下是不允许的，直接退出
            error_msg = (
                "\n"
                "❌ 错误: POD策略不能在多进程环境中使用！\n"
                "\n"
                "原因: POD策略使用固定的consumer名称，多进程会导致消息重复消费。\n"
                "\n"
                "解决方案:\n"
                "  1. 使用 ConsumerStrategy.HEARTBEAT - 心跳策略 (推荐)\n"
                "  2. 使用 ConsumerStrategy.FIXED - 自定义固定名称\n"
                "  3. 使用单进程执行器 (asyncio/thread)\n"
                "\n"
                f"当前环境: {current_process.name} (PID: {os.getpid()})\n"
            )
            logger.error(error_msg)
            # 立即退出程序
            import sys
            sys.exit(1)
        
        # 记录策略选择用于调试
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Consumer strategy: {self.strategy.value}, Process: {current_process.name}")
        
    def get_consumer_name(self, queue: str) -> str:
        """获取消费者名称"""
        if self.strategy == ConsumerStrategy.FIXED:
            return self._get_fixed_name(queue)
        elif self.strategy == ConsumerStrategy.POD:
            return self._get_pod_name(queue)
        elif self.strategy == ConsumerStrategy.HEARTBEAT:
            return self._get_heartbeat_name(queue)
        else:
            raise ValueError(f"Unknown consumer strategy: {self.strategy}")
    
    def _get_fixed_name(self, queue: str) -> str:
        """获取固定的消费者名称"""
        if not self._consumer_name:
            # 可以从配置、环境变量或文件中读取
            self._consumer_name = self.config.get('consumer_name') or \
                                  os.environ.get('EASYTASK_CONSUMER_NAME') or \
                                  f"worker-{os.getpid()}"
        return f"{self._consumer_name}-{queue}"
    
    def _get_pod_name(self, queue: str) -> str:
        """获取基于K8s Pod的消费者名称
        
        注意：POD策略只能在单进程环境下使用
        """
        if not self._consumer_name:
            # 在K8s中，通常通过环境变量获取Pod名称
            pod_name = os.environ.get('HOSTNAME') or \
                       os.environ.get('POD_NAME') or \
                       os.environ.get('K8S_POD_NAME')
            
            if not pod_name:
                logger.warning("Pod name not found, falling back to hostname")
                import socket
                pod_name = socket.gethostname()
            
            # 由于已经在_validate_strategy_configuration中验证过，
            # 这里应该只会在MainProcess中执行
            self._consumer_name = pod_name
            logger.info(f"使用Pod策略的consumer名称: {self._consumer_name}")
                
        return f"{self._consumer_name}-{queue}"
    
    
    def _get_heartbeat_name(self, queue: str) -> str:
        """基于心跳策略获取消费者名称"""
        if not self._heartbeat_strategy:
            raise RuntimeError("Heartbeat strategy not initialized properly")
        
        return self._heartbeat_strategy.get_consumer_name(queue)
    
    def cleanup(self):
        """清理资源（优雅关闭时调用）"""
        # 处理心跳策略的清理
        if self.strategy == ConsumerStrategy.HEARTBEAT and self._heartbeat_strategy:
            self._heartbeat_strategy.cleanup()
    
    def update_stats(self, queue: str, success: bool = True, processing_time: float = 0.0):
        """更新消费者的统计信息（仅对HEARTBEAT策略有效）"""
        if self.strategy == ConsumerStrategy.HEARTBEAT and self._heartbeat_strategy:
            self._heartbeat_strategy.update_stats(queue, success, processing_time)
    
    def task_started(self, queue: str):
        """任务开始执行时调用（仅对HEARTBEAT策略有效）"""
        if self.strategy == ConsumerStrategy.HEARTBEAT and self._heartbeat_strategy:
            self._heartbeat_strategy.task_started(queue)
    
    def task_finished(self, queue: str):
        """任务完成时调用（仅对HEARTBEAT策略有效）"""
        if self.strategy == ConsumerStrategy.HEARTBEAT and self._heartbeat_strategy:
            self._heartbeat_strategy.task_finished(queue)
    
    def cleanup_expired_consumers(self, queue: str):
        """清理过期的消费者（可选功能）"""
        try:
            # 获取消费者组的pending消息信息
            prefixed_queue = self.get_prefixed_queue_name(queue)
            pending_info = self.redis_client.xpending(prefixed_queue, prefixed_queue)
            if not pending_info:
                return
                
            # 获取详细的pending消息
            consumers = self.redis_client.xpending_range(
                prefixed_queue, prefixed_queue, min='-', max='+', count=100
            )
            
            for consumer_info in consumers:
                consumer_name = consumer_info['consumer']
                idle_time = consumer_info['time_since_delivered']
                
                # 如果消息空闲时间超过阈值，可能消费者已经死亡
                # 使用120秒作为默认的死亡检测阈值
                if idle_time > 120 * 1000:  # 120秒
                    logger.warning(
                        f"Consumer {consumer_name} has pending messages "
                        f"idle for {idle_time/1000}s, may be dead"
                    )
                    # 这里可以实现消息重新分配逻辑
                    
        except Exception as e:
            logger.error(f"Error cleaning up expired consumers: {e}")

class HeartbeatConsumerStrategy:
    """基于心跳的简化消费者策略
    
    特点：
    1. 使用随机consumer name
    2. 每个队列维护独立的心跳有序集合
    3. 心跳数据包含worker的详细信息
    4. 自动重置死亡worker的pending任务
    """
    
    def __init__(self, redis_client: redis.StrictRedis, config: Dict = None):
        self.redis = redis_client
        self.config = config or {}
        
        # 配置参数
        self.heartbeat_interval = self.config.get('heartbeat_interval', 5)  # 5秒心跳
        self.heartbeat_timeout = self.config.get('heartbeat_timeout', 30)  # 30秒超时
        self.scan_interval = self.config.get('scan_interval', 10)  # 10秒扫描一次
        
        # 生成consumer ID，使用hostname或IP作为前缀
        import socket
        try:
            # 首先尝试获取hostname
            hostname = socket.gethostname()
            # 尝试获取IP地址
            ip = socket.gethostbyname(hostname)
            # 优先使用hostname，如果hostname是localhost则使用IP
            prefix = hostname if hostname != 'localhost' else ip
        except:
            # 如果获取失败，使用环境变量或默认值
            prefix = os.environ.get('HOSTNAME', 'unknown')
        
        self.consumer_id = f"{prefix}-{uuid.uuid4().hex[:8]}-{os.getpid()}"
        
        # 新的数据结构设计
        # 获取Redis前缀（从配置中）
        self.redis_prefix = config.get('redis_prefix', 'jettask').lower()
        self.worker_key = f'{self.redis_prefix}:worker:{self.consumer_id}'  # worker的hash键
        self.global_queue_workers_key = f'{self.redis_prefix}:global:queue_workers'  # 全局队列worker管理
        
        self.consumer_names = {}  # queue -> consumer_name mapping
        self.active_queues = set()  # 记录当前活跃的队列
        
        # 后台线程控制
        self._heartbeat_threads = {}  # queue -> thread mapping
        self._heartbeat_stops = {}   # queue -> stop_event mapping
        self._scanner_thread = None
        self._scanner_stop = threading.Event()
        
        # 统计缓冲区
        self.stats_buffer = {
            'running_tasks': defaultdict(int),
            'success_count': defaultdict(int),
            'failed_count': defaultdict(int),
            'total_time': defaultdict(float),
            'total_count': defaultdict(int)
        }
        self.stats_buffer_lock = threading.Lock()  # 因为有后台线程，需要锁
        self.stats_flush_interval = self.config.get('stats_flush_interval', 1.0)
        self.last_stats_flush = time.time()
        
        # 启动扫描线程
        self._start_scanner_thread()
        
        # 注册退出处理
        import atexit
        atexit.register(self.cleanup)
    
    def get_prefixed_queue_name(self, queue: str) -> str:
        """为队列名称添加前缀"""
        return f"{self.redis_prefix}:{queue}"
    
    def update_stats(self, queue: str, success: bool = True, processing_time: float = 0.0):
        """更新worker的统计信息 - 缓冲到内存中
        
        Args:
            queue: 队列名称
            success: 是否执行成功
            processing_time: 处理时间（秒）
        """
        with self.stats_buffer_lock:
            if success:
                self.stats_buffer['success_count'][queue] += 1
            else:
                self.stats_buffer['failed_count'][queue] += 1
            
            self.stats_buffer['total_count'][queue] += 1
            self.stats_buffer['total_time'][queue] += processing_time
    
    def task_started(self, queue: str):
        """任务开始执行时调用 - 缓冲到内存中"""
        with self.stats_buffer_lock:
            self.stats_buffer['running_tasks'][queue] += 1
    
    def task_finished(self, queue: str):
        """任务完成时调用 - 缓冲到内存中"""
        with self.stats_buffer_lock:
            if self.stats_buffer['running_tasks'][queue] > 0:
                self.stats_buffer['running_tasks'][queue] -= 1
    
    def flush_stats_buffer(self):
        """刷新统计缓冲到 Redis"""
        with self.stats_buffer_lock:
            # 检查是否有数据需要刷新
            has_data = False
            for buffer in self.stats_buffer.values():
                if buffer:
                    has_data = True
                    break
            
            if not has_data:
                return
            
            try:
                pipeline = self.redis.pipeline()
                
                # 更新运行中任务数
                for queue, delta in self.stats_buffer['running_tasks'].items():
                    if delta != 0:
                        pipeline.hincrby(self.worker_key, f'{queue}:running_tasks', delta)
                
                # 更新统计数据
                processed_queues = set()
                for queue in set().union(
                    self.stats_buffer['success_count'].keys(),
                    self.stats_buffer['failed_count'].keys(),
                    self.stats_buffer['total_count'].keys()
                ):
                    processed_queues.add(queue)
                    
                    if queue in self.stats_buffer['success_count']:
                        pipeline.hincrby(self.worker_key, f'{queue}:success_count', 
                                       self.stats_buffer['success_count'][queue])
                    
                    if queue in self.stats_buffer['failed_count']:
                        pipeline.hincrby(self.worker_key, f'{queue}:failed_count', 
                                       self.stats_buffer['failed_count'][queue])
                    
                    if queue in self.stats_buffer['total_count']:
                        pipeline.hincrby(self.worker_key, f'{queue}:total_count', 
                                       self.stats_buffer['total_count'][queue])
                        pipeline.hincrbyfloat(self.worker_key, f'{queue}:total_processing_time', 
                                            self.stats_buffer['total_time'][queue])
                
                # 执行批量更新
                pipeline.execute()
                
                # 更新平均处理时间
                for queue in processed_queues:
                    if queue in self.stats_buffer['total_count'] and self.stats_buffer['total_count'][queue] > 0:
                        # 获取当前总数
                        current_total = self.redis.hget(self.worker_key, f'{queue}:total_count')
                        current_time = self.redis.hget(self.worker_key, f'{queue}:total_processing_time')
                        
                        if current_total and current_time:
                            total_count = int(current_total)
                            total_time = float(current_time)
                            avg_time = total_time / total_count
                            self.redis.hset(self.worker_key, f'{queue}:avg_processing_time', f'{avg_time:.3f}')
                
                # 清空缓冲区
                for buffer in self.stats_buffer.values():
                    buffer.clear()
                    
            except Exception as e:
                logger.error(f"Failed to flush stats buffer: {e}")
    
    def get_stats(self, queue: str) -> dict:
        """获取队列的统计信息 - 从Redis Hash读取"""
        try:
            # 批量获取该队列的所有统计字段
            fields = [
                f'{queue}:success_count',
                f'{queue}:failed_count', 
                f'{queue}:total_count',
                f'{queue}:running_tasks',
                f'{queue}:avg_processing_time'
            ]
            
            values = self.redis.hmget(self.worker_key, fields)
            
            return {
                'success_count': int(values[0] or 0),
                'failed_count': int(values[1] or 0),
                'total_count': int(values[2] or 0),
                'running_tasks': int(values[3] or 0),
                'avg_processing_time': float(values[4] or 0.0)
            }
        except Exception as e:
            logger.error(f"Failed to get stats for queue {queue}: {e}")
            return {
                'success_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'running_tasks': 0,
                'avg_processing_time': 0.0
            }
    
    def get_consumer_name(self, queue: str) -> str:
        """获取消费者名称"""
        if queue not in self.consumer_names:
            # 为每个队列生成唯一的consumer name
            self.consumer_names[queue] = f"{self.consumer_id}-{queue}"
            self.active_queues.add(queue)
            
            # 为这个队列启动心跳线程
            if queue not in self._heartbeat_threads:
                self._start_heartbeat_thread_for_queue(queue)
            
            logger.info(f"Created consumer name for queue {queue}: {self.consumer_names[queue]}")
        return self.consumer_names[queue]
    
    def _start_heartbeat_thread_for_queue(self, queue: str):
        """为特定队列启动心跳线程"""
        if queue in self._heartbeat_threads:
            return
        
        stop_event = threading.Event()
        self._heartbeat_stops[queue] = stop_event
        
        thread = threading.Thread(
            target=self._heartbeat_loop_for_queue,
            args=(queue, stop_event),
            daemon=True,
            name=f"heartbeat-{queue}"
        )
        thread.start()
        self._heartbeat_threads[queue] = thread
        
        logger.info(f"Started heartbeat thread for queue {queue}")
    
    def _start_scanner_thread(self):
        """启动扫描线程"""
        self._scanner_thread = threading.Thread(
            target=self._scanner_loop,
            daemon=True,
            name="heartbeat-scanner"
        )
        self._scanner_thread.start()
        
        # 立即执行一次扫描，清理可能存在的死亡worker
        threading.Thread(
            target=self._immediate_scan,
            daemon=True,
            name="immediate-scanner"
        ).start()
        
        logger.info(f"Started heartbeat scanner for consumer {self.consumer_id}")
    
    def _immediate_scan(self):
        """启动时立即执行一次扫描"""
        try:
            logger.info("Performing immediate scan for dead workers...")
            self._perform_scan()
            logger.info("Immediate scan completed")
        except Exception as e:
            logger.error(f"Error in immediate scan: {e}")
    
    def _heartbeat_loop_for_queue(self, queue: str, stop_event: threading.Event):
        """特定队列的心跳循环 - 简化版本，只维护worker hash"""
        consumer_name = self.consumer_names[queue]
        
        # 获取主机名或IP（一次性获取）
        import socket
        try:
            hostname = socket.gethostname()
            if not hostname or hostname == 'localhost':
                hostname = socket.gethostbyname(socket.gethostname())
        except:
            hostname = os.environ.get('HOSTNAME', 'unknown')
        
        heartbeat_update_count = 0
        
        while not stop_event.is_set():
            try:
                current_time = time.time()
                
                # 使用pipeline批量更新worker信息
                pipeline = self.redis.pipeline()
                
                # 检查是否需要设置created_at
                if not self.redis.hexists(self.worker_key, 'created_at'):
                    pipeline.hset(self.worker_key, 'created_at', str(current_time))
                
                # 更新worker的基本信息
                pipeline.hset(self.worker_key, mapping={
                    'consumer_id': self.consumer_id,
                    'host': hostname,
                    'pid': str(os.getpid()),
                    'last_heartbeat': str(current_time),
                    'is_alive': 'true'
                })
                
                # 更新队列列表
                current_queues = self.redis.hget(self.worker_key, 'queues') or ''
                queue_list = set(current_queues.split(',')) if current_queues else set()
                queue_list.add(queue)
                pipeline.hset(self.worker_key, 'queues', ','.join(sorted(queue_list)))
                
                # 在全局hash中维护队列的worker列表
                current_workers = self.redis.hget(self.global_queue_workers_key, queue) or ''
                worker_set = set(current_workers.split(',')) if current_workers else set()
                worker_set.add(self.consumer_id)
                pipeline.hset(self.global_queue_workers_key, queue, ','.join(sorted(worker_set)))
                
                # 执行批量更新
                pipeline.execute()
                
                heartbeat_update_count += 1
                
                # 检查是否需要刷新统计缓冲
                if current_time - self.last_stats_flush >= self.stats_flush_interval:
                    self.flush_stats_buffer()
                    self.last_stats_flush = current_time
                
                # 定期日志（每100次更新记录一次）
                if heartbeat_update_count % 100 == 0:
                    logger.debug(f"Heartbeat updated {heartbeat_update_count} times for {consumer_name}")
                
                stop_event.wait(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat loop for queue {queue}: {e}")
                stop_event.wait(1)
    
    def _perform_scan(self):
        """执行一次扫描操作 - 新的Hash结构版本"""
        current_time = time.time()
        timeout_threshold = current_time - self.heartbeat_timeout
        
        try:
            # 扫描所有worker hash键
            pattern = f"{self.redis_prefix}:worker:*"
            worker_keys = []
            cursor = 0
            
            # 使用SCAN迭代获取所有worker键
            while True:
                cursor, keys = self.redis.scan(cursor, match=pattern, count=100)
                worker_keys.extend(keys)
                if cursor == 0:
                    break
            
            if not worker_keys:
                logger.debug("No worker keys found")
                return
            
            timeout_workers = []
            
            # 检查每个worker的心跳时间
            for worker_key in worker_keys:
                try:
                    # 跳过history相关的键
                    if ':history:' in worker_key:
                        continue
                    
                    # 先检查key的类型
                    key_type = self.redis.type(worker_key)
                    if key_type != 'hash':
                        logger.warning(f"Worker key {worker_key} is not a hash, type: {key_type}, skipping")
                        continue
                    
                    worker_data = self.redis.hgetall(worker_key)
                    if not worker_data:
                        continue
                        
                    last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                    consumer_id = worker_data.get('consumer_id')
                    is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                    
                    # 跳过自己
                    if consumer_id == self.consumer_id:
                        continue
                    
                    # 检查是否超时且当前标记为在线
                    if is_alive and last_heartbeat < timeout_threshold:
                        timeout_workers.append((worker_key, worker_data))
                        
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing worker data from {worker_key}: {e}")
                    continue
            
            if timeout_workers:
                logger.info(f"Found {len(timeout_workers)} timeout workers")
                
                for worker_key, worker_data in timeout_workers:
                    consumer_id = worker_data.get('consumer_id')
                    queues = worker_data.get('queues', '').split(',') if worker_data.get('queues') else []
                    
                    # 使用分布式锁来避免多个scanner同时处理同一个worker
                    lock_key = f"{self.redis_prefix}:scanner:lock:{consumer_id}"
                    lock_ttl = self.scan_interval * 2
                    
                    if not self.redis.set(lock_key, self.consumer_id, nx=True, ex=lock_ttl):
                        logger.debug(f"Another scanner is processing worker {consumer_id}, skipping")
                        continue
                    
                    try:
                        # 再次检查worker是否真的超时（避免竞态条件）
                        current_heartbeat = self.redis.hget(worker_key, 'last_heartbeat')
                        if current_heartbeat and float(current_heartbeat) >= timeout_threshold:
                            logger.info(f"Worker {consumer_id} is now alive, skipping")
                            continue
                        
                        logger.info(f"Processing timeout worker: {consumer_id}")
                        # 标记worker为离线并清理消费者
                        self._mark_worker_offline_and_cleanup_v2(worker_key, worker_data, queues)
                        
                    except Exception as e:
                        logger.error(f"Error processing timeout worker {consumer_id}: {e}")
                    finally:
                        # 释放锁
                        self.redis.delete(lock_key)
                        
        except Exception as e:
            logger.error(f"Error in scanner: {e}")
    
    def _mark_worker_offline_and_cleanup_v2(self, worker_key: str, worker_data: dict, queues: list):
        """标记worker为离线状态并清理消费者 - 简化版本"""
        consumer_id = worker_data.get('consumer_id')
        
        try:
            current_time = time.time()
            
            # 保存worker下线历史记录
            self._save_worker_offline_history(consumer_id, worker_data, current_time)
            
            # 标记worker为离线状态
            pipeline = self.redis.pipeline()
            pipeline.hset(worker_key, mapping={
                'is_alive': 'false',
                'offline_time': str(current_time)
            })
            
            # 将执行中任务归零，并从全局队列worker列表中移除
            for queue in queues:
                if queue.strip():  # 确保队列名不为空
                    pipeline.hset(worker_key, f'{queue}:running_tasks', '0')
                    
                    # 从全局队列worker列表中移除当前worker
                    current_workers = self.redis.hget(self.global_queue_workers_key, queue.strip()) or ''
                    if current_workers:
                        worker_set = set(current_workers.split(','))
                        worker_set.discard(consumer_id)
                        if worker_set:
                            pipeline.hset(self.global_queue_workers_key, queue.strip(), ','.join(sorted(worker_set)))
                        else:
                            pipeline.hdel(self.global_queue_workers_key, queue.strip())
            
            # 执行批量更新
            pipeline.execute()
            
            logger.info(f"Marked worker {consumer_id} as offline")
            
            # 清理Redis Stream消费者组中的consumer
            for queue in queues:
                if queue.strip():
                    # 获取consumer name（需要重构这部分逻辑）
                    consumer_name = f"{consumer_id}-{queue}"
                    self._cleanup_stream_consumer(queue, consumer_name)
                    self._reset_consumer_pending_messages(queue, consumer_name)
                    
        except Exception as e:
            logger.error(f"Error marking worker {consumer_id} offline: {e}")
    
    def _scanner_loop(self):
        """扫描超时worker的循环"""
        while not self._scanner_stop.is_set():
            try:
                self._perform_scan()
                self._scanner_stop.wait(self.scan_interval)
            except Exception as e:
                logger.error(f"Error in scanner loop: {e}")
                self._scanner_stop.wait(5)  # 错误时等待5秒后重试
    
    
    def _cleanup_stream_consumer(self, queue: str, consumer_name: str):
        """从Redis Stream消费者组中删除consumer"""
        try:
            # 删除消费者（这会阻止它重新加入后继续消费消息）
            prefixed_queue = self.get_prefixed_queue_name(queue)
            result = self.redis.execute_command('XGROUP', 'DELCONSUMER', prefixed_queue, prefixed_queue, consumer_name)
            if result > 0:
                logger.info(f"Deleted stream consumer {consumer_name} from group {queue}")
            else:
                logger.debug(f"Stream consumer {consumer_name} was not found in group {queue}")
        except Exception as e:
            logger.error(f"Error deleting stream consumer {consumer_name}: {e}")

    def _handle_dead_worker(self, queue: str, worker_info: dict, worker_data: bytes):
        """处理死亡的worker"""
        consumer_name = worker_info.get('consumer_name', 'unknown')
        
        # 使用分布式锁来避免多个scanner同时处理同一个consumer
        consumer_lock_key = f"{self.redis_prefix}:consumer:lock:{consumer_name}"
        consumer_lock_ttl = 30  # 30秒锁超时
        
        # 尝试获取consumer级别的锁
        if not self.redis.set(consumer_lock_key, self.consumer_id, nx=True, ex=consumer_lock_ttl):
            logger.debug(f"Another scanner is handling consumer {consumer_name}, skipping")
            return
        
        try:
            heartbeat_key = f"{self.heartbeat_key_prefix}{queue}"
            
            # 再次检查worker是否真的超时（避免竞态条件）
            current_score = self.redis.zscore(heartbeat_key, worker_data)
            if current_score and time.time() - current_score < self.heartbeat_timeout:
                logger.info(f"Worker {consumer_name} is now alive, skipping")
                return
            
            # 从有序集合中删除死亡的worker（使用原始的worker_data）
            removed = self.redis.zrem(heartbeat_key, worker_data)
            if removed:
                logger.info(f"Removed dead worker {consumer_name} from heartbeat set for queue {queue}")
                
                # 重置该consumer的pending消息
                self._reset_consumer_pending_messages(queue, consumer_name)
            else:
                logger.debug(f"Worker {consumer_name} already removed by another scanner")
            
        except Exception as e:
            logger.error(f"Error handling dead worker {consumer_name}: {e}")
        finally:
            # 释放consumer锁
            self.redis.delete(consumer_lock_key)
    
    def _reset_consumer_pending_messages(self, queue: str, consumer_name: str):
        """重置指定consumer的pending消息"""
        try:
            # 首先获取该consumer的所有pending消息
            consumer_messages = []
            try:
                # 分批获取该consumer的所有pending消息
                batch_size = 1000
                last_id = '-'
                
                while True:
                    # 获取一批pending消息
                    prefixed_queue = self.get_prefixed_queue_name(queue)
                    pending_batch = self.redis.xpending_range(
                        prefixed_queue, prefixed_queue,
                        min=last_id, max='+',
                        count=batch_size
                    )
                    
                    if not pending_batch:
                        break
                    
                    # 过滤出属于该consumer的消息
                    for msg in pending_batch:
                        msg_consumer = msg['consumer']
                        # 处理bytes类型
                        if isinstance(msg_consumer, bytes):
                            msg_consumer = msg_consumer.decode('utf-8')
                        if msg_consumer == consumer_name:
                            consumer_messages.append(msg)
                    
                    # 如果获取的消息数小于batch_size，说明已经获取完所有消息
                    if len(pending_batch) < batch_size:
                        break
                    
                    # 更新last_id为最后一条消息的ID，用于下一批查询
                    last_id = pending_batch[-1]['message_id']
                
                if not consumer_messages:
                    logger.debug(f"No pending messages for consumer {consumer_name}")
                    # 仍然尝试删除consumer
                    try:
                        prefixed_queue = self.get_prefixed_queue_name(queue)
                        self.redis.execute_command('XGROUP', 'DELCONSUMER', prefixed_queue, prefixed_queue, consumer_name)
                    except:
                        pass
                    return
                
                logger.info(f"Found {len(consumer_messages)} pending messages for dead consumer {consumer_name}")
                
                # 获取消息ID列表
                message_ids = [msg['message_id'] for msg in consumer_messages]
                
                # 使用一个特殊的consumer来claim这些消息，然后立即ACK并重新添加
                temp_consumer = f"recovery-{uuid.uuid4().hex[:8]}"
                
                # 分批处理消息
                recovered_count = 0
                for i in range(0, len(message_ids), 100):
                    batch = message_ids[i:i+100]
                    try:
                        # 1. Claim消息到临时consumer
                        claimed = self.redis.xclaim(
                            queue, queue,
                            temp_consumer,
                            min_idle_time=0,
                            message_ids=batch,
                            force=True
                        )
                        
                        if claimed:
                            # 2. 将消息内容重新添加到stream
                            for msg_id, msg_data in claimed:
                                try:
                                    # 重新添加消息到stream末尾
                                    self.redis.xadd(queue, msg_data)
                                    recovered_count += 1
                                except Exception as e:
                                    logger.error(f"Failed to re-add message {msg_id}: {e}")
                            
                            # 3. ACK原始消息
                            self.redis.xack(queue, queue, *[msg[0] for msg in claimed])
                            
                    except Exception as e:
                        logger.error(f"Error recovering batch of messages: {e}")
                
                logger.info(f"Successfully recovered {recovered_count} pending messages from {consumer_name}")
                
            except Exception as e:
                logger.error(f"Error getting pending messages: {e}")
            
            # 最后删除死亡的consumer
            try:
                prefixed_queue = self.get_prefixed_queue_name(queue)
                self.redis.execute_command('XGROUP', 'DELCONSUMER', prefixed_queue, prefixed_queue, consumer_name)
                logger.debug(f"Deleted consumer {consumer_name}")
            except:
                pass
                        
        except Exception as e:
            logger.error(f"Error resetting pending messages for {consumer_name}: {e}")
    
    def _save_worker_offline_history(self, consumer_id: str, worker_data: dict, offline_time: float):
        """保存worker下线历史记录"""
        try:
            # 历史记录key
            history_key = f"{self.redis_prefix}:worker:history:{consumer_id}"
            
            # 获取worker的运行统计
            online_time = float(worker_data.get('created_at', offline_time))
            duration = offline_time - online_time
            
            # 获取所有队列的统计信息
            queues = worker_data.get('queues', '').split(',') if worker_data.get('queues') else []
            total_success = 0
            total_failed = 0
            total_tasks = 0
            total_running = 0
            total_processing_time = 0.0
            
            # 聚合所有队列的统计
            for queue in queues:
                if queue.strip():
                    queue = queue.strip()
                    success_count = int(worker_data.get(f'{queue}:success_count', 0))
                    failed_count = int(worker_data.get(f'{queue}:failed_count', 0))
                    task_count = int(worker_data.get(f'{queue}:total_count', 0))
                    running_tasks = int(worker_data.get(f'{queue}:running_tasks', 0))
                    processing_time = float(worker_data.get(f'{queue}:total_processing_time', 0))
                    
                    total_success += success_count
                    total_failed += failed_count
                    total_tasks += task_count
                    total_running += running_tasks
                    total_processing_time += processing_time
            
            # 计算平均处理时间
            avg_processing_time = total_processing_time / total_tasks if total_tasks > 0 else 0.0
            
            # 构建历史记录
            history_data = {
                'consumer_id': consumer_id,
                'host': worker_data.get('host', 'unknown'),
                'pid': worker_data.get('pid', '0'),
                'queues': worker_data.get('queues', ''),
                'online_time': str(online_time),
                'offline_time': str(offline_time),
                'duration_seconds': str(int(duration)),
                'last_heartbeat': worker_data.get('last_heartbeat', '0'),
                'shutdown_reason': 'heartbeat_timeout',
                'final_status': 'offline',
                # 添加统计信息
                'total_success_count': str(total_success),
                'total_failed_count': str(total_failed),
                'total_count': str(total_tasks),
                'total_running_tasks': str(total_running),
                'total_processing_time': str(total_processing_time),
                'avg_processing_time': str(avg_processing_time)
            }
            
            # 保存历史记录（使用hash存储）
            self.redis.hset(history_key, mapping=history_data)
            
            # 设置过期时间（保留7天的历史记录）
            self.redis.expire(history_key, 7 * 24 * 3600)
            
            # 将历史记录ID添加到有序集合中（按下线时间排序）
            history_index_key = f"{self.redis_prefix}:worker:history:index"
            self.redis.zadd(history_index_key, {consumer_id: offline_time})
            
            # 清理过期的历史记录索引（保留最近7天的）
            expire_threshold = offline_time - (7 * 24 * 3600)
            self.redis.zremrangebyscore(history_index_key, '-inf', expire_threshold)
            
            logger.info(f"Saved offline history for worker {consumer_id}, duration: {int(duration)}s")
            
        except Exception as e:
            logger.error(f"Error saving worker offline history: {e}")
    
    def get_worker_offline_history(self, limit: int = 100, start_time: float = None, end_time: float = None):
        """获取worker下线历史记录"""
        try:
            history_index_key = f"{self.redis_prefix}:worker:history:index"
            
            # 设置时间范围
            if start_time is None:
                start_time = '-inf'
            if end_time is None:
                end_time = '+inf'
                
            # 从索引中获取consumer_id列表
            consumer_ids = self.redis.zrevrangebyscore(
                history_index_key, 
                end_time, 
                start_time,
                start=0,
                num=limit
            )
            
            # 获取详细历史记录
            history_records = []
            for consumer_id in consumer_ids:
                history_key = f"{self.redis_prefix}:worker:history:{consumer_id}"
                record = self.redis.hgetall(history_key)
                if record:
                    # 转换数值类型
                    record['online_time'] = float(record.get('online_time', 0))
                    record['offline_time'] = float(record.get('offline_time', 0))
                    record['duration_seconds'] = int(record.get('duration_seconds', 0))
                    
                    # 转换统计信息
                    record['total_success_count'] = int(record.get('total_success_count', 0))
                    record['total_failed_count'] = int(record.get('total_failed_count', 0))
                    record['total_count'] = int(record.get('total_count', 0))
                    record['total_running_tasks'] = int(record.get('total_running_tasks', 0))
                    record['total_processing_time'] = float(record.get('total_processing_time', 0))
                    record['avg_processing_time'] = float(record.get('avg_processing_time', 0))
                    
                    history_records.append(record)
            
            return history_records
            
        except Exception as e:
            logger.error(f"Error getting worker offline history: {e}")
            return []
    
    def cleanup(self):
        """清理资源"""
        logger.info(f"Cleaning up heartbeat consumer {self.consumer_id}")
        
        # 最后刷新一次统计缓冲
        try:
            self.flush_stats_buffer()
        except Exception as e:
            logger.error(f"Failed to flush stats buffer during cleanup: {e}")
        
        # 停止所有心跳线程
        for queue, stop_event in self._heartbeat_stops.items():
            stop_event.set()
        
        # 停止扫描线程
        self._scanner_stop.set()
        
        # 等待所有心跳线程结束
        for queue, thread in self._heartbeat_threads.items():
            if thread and thread.is_alive():
                thread.join(timeout=2)
        
        # 等待扫描线程结束
        if self._scanner_thread and self._scanner_thread.is_alive():
            self._scanner_thread.join(timeout=2)
        
        # 重要：不删除心跳记录！
        # 心跳记录必须保留，让scanner能够检测到worker离线并恢复pending消息
        # 心跳会因为超时自动被scanner清理
        logger.info(f"Heartbeat consumer {self.consumer_id} stopped (heartbeat will timeout naturally)")
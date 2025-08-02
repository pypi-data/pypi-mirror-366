import asyncio
import time
import logging
import traceback
import ujson
from typing import Optional, Union
from collections import defaultdict, deque

from .base import BaseExecutor

logger = logging.getLogger('app')

# Try to use uvloop for better performance
try:
    import uvloop
    uvloop.install()
    logger.info("Using uvloop for better performance")
except ImportError:
    pass


class AsyncioExecutor(BaseExecutor):
    """High-performance asyncio executor"""
    
    def __init__(self, event_queue, app, concurrency=100):
        super().__init__(event_queue, app, concurrency)
        
        # Caching for pending count
        self.pending_cache = {}
        self.pending_cache_expire = 0
        
        # Enhanced batch ACK with larger buffer
        self.pending_acks = []
        self.ack_buffer_size = 100  # 优化：增大批量大小
        self.last_flush_time = time.time()
        
        # 批量状态更新缓冲
        self.status_updates = []  # [(event_id, status_dict)]
        self.data_updates = []    # [(event_id, data)]
        
        # 性能优化：预编译常量
        self._status_prefix = self.app._status_prefix
        self._result_prefix = self.app._result_prefix
        
    async def get_pending_count_cached(self, queue: str) -> int:
        """Get cached pending count"""
        current_time = time.time()
        
        if (current_time - self.pending_cache_expire > 30 or  # 优化：延长缓存时间
            queue not in self.pending_cache):
            try:
                pending_info = await self.app.ep.async_redis_client.xpending(queue, queue)
                self.pending_cache[queue] = pending_info.get("pending", 0)
                self.pending_cache_expire = current_time
            except Exception:
                self.pending_cache[queue] = 0
                
        return self.pending_cache.get(queue, 0)
    
    async def _quick_ack(self, queue: str, event_id: str):
        """Quick ACK - add to buffer"""
        self.pending_acks.append((queue, event_id))
        
        # Flush immediately when threshold reached
        if len(self.pending_acks) >= self.ack_buffer_size:
            await self._flush_acks()
    
    async def _flush_acks(self):
        """Batch execute ACKs - optimized"""
        if not self.pending_acks:
            return
            
        # 按队列分组以优化批量操作
        from collections import defaultdict
        acks_by_queue = defaultdict(list)
        for queue, event_id in self.pending_acks:
            acks_by_queue[queue].append(event_id)
        
        self.pending_acks.clear()
        
        # 并发执行每个队列的批量ACK
        tasks = []
        
        for queue, event_ids in acks_by_queue.items():
            # 分批处理大量ACK（优化：每批1000个）
            for i in range(0, len(event_ids), 1000):
                batch = event_ids[i:i+1000]
                tasks.append(self.app.ep.async_redis_client.xack(queue, queue, *batch))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.last_flush_time = time.time()
    
    async def _flush_status_updates(self):
        """批量更新状态 - 优化使用MSET"""
        if not self.status_updates:
            return
            
        # 使用批量状态更新API
        updates = self.status_updates[:200]  # 优化：增大批量大小
        self.status_updates = self.status_updates[200:]
        
        # 优化：使用MSET进行超高效批量更新
        mapping = {}
        expire_keys = []
        
        for event_id, status_dict in updates:
            key = f"{self._status_prefix}{event_id}"
            mapping[key] = ujson.dumps(status_dict)
            expire_keys.append(key)
        
        if mapping:
            # 使用pipeline批量设置值和过期时间
            pipeline = self.app.ep.async_redis_client.pipeline()
            pipeline.mset(mapping)
            
            # 批量设置过期时间
            for key in expire_keys:
                pipeline.expire(key, 3600)
            
            await pipeline.execute()
    
    async def _flush_data_updates(self):
        """批量更新数据 - 优化使用MSET"""
        if not self.data_updates:
            return
            
        # 使用pipeline批量更新
        updates = self.data_updates[:200]  # 优化：增大批量大小
        self.data_updates = self.data_updates[200:]
        
        # 优化：使用MSET
        mapping = {}
        expire_keys = []
        
        for event_id, data in updates:
            key = f"{self._result_prefix}{event_id}"
            mapping[key] = data
            expire_keys.append(key)
        
        if mapping:
            pipeline = self.app.ep.async_redis_client.pipeline()
            pipeline.mset(mapping)
            
            # 批量设置过期时间
            for key in expire_keys:
                pipeline.expire(key, 3600)
                
            await pipeline.execute()
    
    async def _flush_all_buffers(self):
        """并发刷新所有缓冲区"""
        await asyncio.gather(
            self._flush_acks(),
            self._flush_status_updates(),
            self._flush_data_updates(),
            return_exceptions=True
        )
    
        
    async def logic(self, semaphore: asyncio.Semaphore, event_id: str, event_data: dict, queue: str, routing: dict = None, consumer: str = None):
        """Process a single task"""
        try:
            async with semaphore:
                task_name = event_data.get("name", "")
                task = self.app.get_task_by_name(task_name)
                if not task:
                    exception = f"{task_name} {queue} {routing}未绑定任何task"
                    logger.error(exception)
                    await self._quick_ack(queue, event_id)
                    
                    completed_at = time.time()
                    trigger_time_float = float(event_data['trigger_time'])
                    duration = completed_at - trigger_time_float
                    # 缓冲状态更新，添加完成时间和耗时
                    self.status_updates.append((event_id, {
                        "status": "error", 
                        "exception": exception, 
                        "completed_at": completed_at,  # 完成时间戳
                        "duration": duration,  # 耗时（秒）
                        "consumer": consumer  # 消费者信息
                    }))
                    return
                
                self.pedding_count = await self.get_pending_count_cached(queue)
                
                status = "success"
                exception = None
                error_msg = None
                ret = None
                
                args = ujson.loads(event_data["args"])
                kwargs = ujson.loads(event_data["kwargs"])
                
                # Execute lifecycle methods
                result = task.on_before(
                    event_id=event_id,
                    pedding_count=self.pedding_count,
                    args=args,
                    kwargs=kwargs,
                )
                if asyncio.iscoroutine(result):
                    result = await result
                    
                if result and result.reject:
                    return
                    
                # 标记任务开始执行
                if hasattr(self.app, 'consumer_manager') and self.app.consumer_manager:
                    self.app.consumer_manager.task_started(queue)
                
                # 缓冲状态更新，添加完成时间和耗时
                self.status_updates.append((event_id, {
                    "status": "running", 
                    "consumer": consumer  # 消费者信息
                }))
                
                try:
                    task_result = task(event_id, event_data['trigger_time'], *args, **kwargs)
                    if asyncio.iscoroutine(task_result):
                        ret = await task_result
                    else:
                        ret = task_result
                    result = task.on_success(
                        event_id=event_id,
                        args=args,
                        kwargs=kwargs,
                        result=ret,
                    )
                    if asyncio.iscoroutine(result):
                        await result
                        
                except Exception as e:
                    logger.error('任务执行出错')
                    status = "error"
                    exception = traceback.format_exc()
                    error_msg = str(e)
                    traceback.print_exc()
                    
                finally:
                    # 添加到批量缓冲区而不是立即执行
                    await self._quick_ack(queue, event_id)
                    
                    # 计算完成时间和消耗时间
                    completed_at = time.time()
                    trigger_time_float = float(event_data['trigger_time'])
                    duration = completed_at - trigger_time_float
                    
                    # # 标记任务完成并更新统计信息
                    if hasattr(self.app, 'consumer_manager') and self.app.consumer_manager:
                        self.app.consumer_manager.task_finished(queue)
                        self.app.consumer_manager.update_stats(
                            queue=queue,
                            success=(status == "success"),
                            processing_time=duration
                        )
                    
                    # 缓冲状态更新，添加完成时间和耗时
                    self.status_updates.append((event_id, {
                        "status": status, 
                        "exception": exception, 
                        "error_msg": error_msg,
                        # "completed_at": completed_at,  # 完成时间戳
                        # "duration": duration,  # 耗时（秒）
                        "consumer": consumer  # 消费者信息
                    }))
                    
                    if ret is not None:  # 优化：修正条件判断
                        self.data_updates.append((event_id, 
                            ret if isinstance(ret, str) else ujson.dumps(ret)
                        ))
                    
                    result = task.on_end(
                        event_id=event_id,
                        args=args,
                        kwargs=kwargs,
                        result=ret,
                        pedding_count=self.pedding_count,
                    )
                    if asyncio.iscoroutine(result):
                        await result
                        
                    # Handle routing
                    if routing:
                        agg_key = routing.get("agg_key")
                        routing_key = routing.get("routing_key")
                        if routing_key and agg_key:
                            # 避免在多进程环境下使用跨进程的锁
                            # 直接操作，依赖 Python GIL 和原子操作
                            if queue in self.app.ep.solo_running_state and routing_key in self.app.ep.solo_running_state[queue]:
                                self.app.ep.solo_running_state[queue][routing_key] -= 1
                        try:
                            if result and result.urgent_retry:
                                self.app.ep.solo_urgent_retry[routing_key] = True
                        except:
                            pass
                        if result and result.delay:
                            self.app.ep.task_scheduler[queue][routing_key] = time.time() + result.delay
                            
        finally:
            self.batch_counter -= 1
    
    async def loop(self):
        """Optimized main loop with dynamic batching"""
        semaphore = asyncio.Semaphore(self.concurrency)
        
        
        # Dynamic batch processing
        min_batch_size = 10   # 优化：降低最小批次
        max_batch_size = 500  # 优化：提高最大批次
        batch_size = 100
        tasks_batch = []
        
        # Performance tracking
        last_periodic_flush = time.time()
        last_batch_adjust = time.time()
        
        while True:
            # # 动态调整批处理大小
            current_time = time.time()
            if current_time - last_batch_adjust > 1.0:
                # 根据队列类型获取长度
                if isinstance(self.event_queue, deque):
                    queue_len = len(self.event_queue)
                elif isinstance(self.event_queue, asyncio.Queue):
                    queue_len = self.event_queue.qsize()
                else:
                    queue_len = 0
                    
                # 优化：更智能的动态调整
                if queue_len > 5000:
                    batch_size = min(max_batch_size, batch_size + 50)
                elif queue_len > 1000:
                    batch_size = min(max_batch_size, batch_size + 20)
                elif queue_len < 100:
                    batch_size = max(min_batch_size, batch_size - 20)
                elif queue_len < 500:
                    batch_size = max(min_batch_size, batch_size - 10)
                last_batch_adjust = current_time
                
            # 从队列获取事件
            event = None
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                event = None
                    
            if event:
                event.pop("execute_time", None)
                tasks_batch.append(event)
            # 批量创建协程任务
            if tasks_batch:
                for event in tasks_batch:
                    self.batch_counter += 1
                    asyncio.create_task(self.logic(semaphore, **event))
                
                tasks_batch.clear()
            
            # 定期刷新所有缓冲区
            if current_time - last_periodic_flush > 0.05:
                # 优化：只在需要时刷新
                if self.pending_acks or self.status_updates or self.data_updates:
                    asyncio.create_task(self._flush_all_buffers())
                last_periodic_flush = current_time
            
            
            # 智能休眠策略
            has_events = False
            if isinstance(self.event_queue, deque):
                has_events = bool(self.event_queue)
            elif isinstance(self.event_queue, asyncio.Queue):
                has_events = not self.event_queue.empty()
                
            if has_events:
                await asyncio.sleep(0)  # 有任务时立即切换
            else:
                # 检查是否需要立即刷新缓冲区
                if (self.pending_acks or self.status_updates or self.data_updates):
                    await self._flush_all_buffers()
                await asyncio.sleep(0.001)  # 无任务时短暂休眠
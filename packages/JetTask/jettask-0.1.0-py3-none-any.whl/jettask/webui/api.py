import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from redis import asyncio as aioredis
import uvicorn
from pathlib import Path

class RedisMonitor:
    def __init__(self, redis_url: str = "redis://localhost:6379", redis_prefix: str = "jettask"):
        self.redis_url = redis_url
        self.redis_prefix = redis_prefix
        self.redis: Optional[aioredis.Redis] = None
        
    async def connect(self):
        # 使用项目中的连接池模式
        pool = aioredis.ConnectionPool.from_url(
            self.redis_url,
            decode_responses=True,
            max_connections=50,
            retry_on_timeout=True,
            health_check_interval=30
        )
        self.redis = aioredis.Redis(connection_pool=pool)
        
    async def close(self):
        if self.redis:
            await self.redis.close()
    
    def get_prefixed_queue_name(self, queue_name: str) -> str:
        """为队列名称添加前缀"""
        return f"{self.redis_prefix}:{queue_name}"
            
    async def get_task_info(self, event_id: str) -> Dict[str, Any]:
        """获取任务详细信息"""
        status_key = f"{self.redis_prefix}:STATUS:{event_id}"
        result_key = f"{self.redis_prefix}:RESULT:{event_id}"
        
        status = await self.redis.get(status_key)
        result = await self.redis.get(result_key)
        
        task_info = {
            "event_id": event_id,
            "status": status,
            "result": result
        }
        
        # 如果有状态信息，尝试从对应的队列stream中获取详细信息
        if status:
            try:
                status_data = json.loads(status)
                queue_name = status_data.get("queue")
                
                if queue_name:
                    # 从stream中查找该任务
                    # 使用 xrange 扫描最近的消息
                    prefixed_queue_name = self.get_prefixed_queue_name(queue_name)
                    messages = await self.redis.xrange(prefixed_queue_name, count=1000)
                    
                    for msg_id, data in messages:
                        # 检查消息数据中的event_id是否匹配
                        if (data.get("event_id") == event_id or 
                            data.get("id") == event_id or
                            data.get("task_id") == event_id):
                            task_info["stream_data"] = {
                                "message_id": msg_id,
                                "data": data,
                                "queue": queue_name
                            }
                            break
                    
                    # 如果消息ID就是event_id，直接尝试获取
                    if not task_info.get("stream_data"):
                        try:
                            direct_messages = await self.redis.xrange(
                                prefixed_queue_name, 
                                min=event_id, 
                                max=event_id, 
                                count=1
                            )
                            if direct_messages:
                                msg_id, data = direct_messages[0]
                                task_info["stream_data"] = {
                                    "message_id": msg_id,
                                    "data": data,
                                    "queue": queue_name
                                }
                        except:
                            pass
                            
            except Exception as e:
                print(f"Error parsing status for task {event_id}: {e}")
                
        return task_info
        
    async def get_stream_info(self, queue_name: str, event_id: str) -> Optional[Dict[str, Any]]:
        """从Stream中获取任务详细信息"""
        try:
            prefixed_queue_name = self.get_prefixed_queue_name(queue_name)
            # 先尝试按event_id直接查找
            messages = await self.redis.xrange(prefixed_queue_name, min=event_id, max=event_id, count=1)
            if messages:
                msg_id, data = messages[0]
                return {
                    "message_id": msg_id,
                    "data": data,
                    "queue": queue_name
                }
            
            # 如果没找到，可能event_id是消息内容的一部分，扫描最近的消息
            messages = await self.redis.xrange(prefixed_queue_name, count=100)
            for msg_id, data in messages:
                if data.get("event_id") == event_id or data.get("id") == event_id:
                    return {
                        "message_id": msg_id,
                        "data": data,
                        "queue": queue_name
                    }
        except Exception as e:
            print(f"Error reading from stream {prefixed_queue_name}: {e}")
        return None
        
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务状态"""
        tasks = []
        
        # 扫描所有状态键
        cursor = 0
        pattern = f"{self.redis_prefix}_STATUS:*"
        
        while True:
            cursor, keys = await self.redis.scan(
                cursor, match=pattern, count=100
            )
            
            for status_key in keys:
                event_id = status_key.split(":")[-1]
                task_info = await self.get_task_info(event_id)
                
                # 尝试获取Stream信息
                # 这里需要知道任务所在的队列，可能需要从状态信息中解析
                if task_info.get("status"):
                    try:
                        status_data = json.loads(task_info["status"])
                        queue_name = status_data.get("queue")
                        if queue_name:
                            stream_info = await self.get_stream_info(queue_name, event_id)
                            if stream_info:
                                task_info["stream_info"] = stream_info
                    except:
                        pass
                        
                tasks.append(task_info)
                
            if cursor == 0:
                break
                
        return tasks
    
    async def get_queue_tasks(self, queue_name: str, start_time: Optional[str] = None, 
                             end_time: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """获取指定队列的任务（基于时间范围）
        
        Args:
            queue_name: 队列名称
            start_time: 开始时间（Redis Stream ID格式或时间戳）
            end_time: 结束时间（Redis Stream ID格式或时间戳）
            limit: 返回的最大任务数
        """
        all_tasks = []
        
        try:
            # 处理时间参数
            # 如果没有指定结束时间，使用 '+' 表示到最新
            if not end_time:
                end_time = '+'
            
            # 如果没有指定开始时间，使用 '-' 表示从最早开始
            if not start_time:
                start_time = '-'
                
            # 从队列的stream中读取消息
            # 使用 xrevrange 按时间倒序获取（最新的在前）
            prefixed_queue_name = self.get_prefixed_queue_name(queue_name)
            messages = await self.redis.xrevrange(
                prefixed_queue_name, 
                max=end_time,
                min=start_time,
                count=limit
            )
            
            for msg_id, data in messages:
                # 在easy_task中，event_id就是Redis生成的stream消息ID
                event_id = msg_id
                
                # 构建任务信息
                task_info = {
                    "event_id": event_id,
                    "message_id": msg_id,
                    "stream_data": data,
                    "task_name": data.get("name", "unknown"),
                    "queue": data.get("queue", queue_name),
                    "trigger_time": data.get("trigger_time")
                }
                
                # 尝试解析args和kwargs，并组合成参数字符串
                params_str = ""
                try:
                    args_list = []
                    kwargs_dict = {}
                    
                    if data.get("args"):
                        args_list = json.loads(data["args"])
                        task_info["args"] = args_list
                    
                    if data.get("kwargs"):
                        kwargs_dict = json.loads(data["kwargs"])
                        task_info["kwargs"] = kwargs_dict
                    
                    # 构建参数字符串
                    params_parts = []
                    if args_list:
                        params_parts.extend([str(arg) for arg in args_list])
                    if kwargs_dict:
                        params_parts.extend([f"{k}={v}" for k, v in kwargs_dict.items()])
                    
                    params_str = ", ".join(params_parts) if params_parts else "无参数"
                    
                except Exception as e:
                    params_str = "解析失败"
                    
                task_info["params_str"] = params_str
                
                # 从状态键获取信息（不默认获取结果）
                status_key = f"{self.redis_prefix}_STATUS:{event_id}"
                
                # 获取状态
                status = await self.redis.get(status_key)
                
                if status:
                    task_info["status"] = status
                    try:
                        parsed_status = json.loads(status)
                        task_info["parsed_status"] = parsed_status
                        # 从状态中获取消费者信息
                        task_info["consumer"] = parsed_status.get("consumer", "-")
                    except:
                        task_info["parsed_status"] = {"status": "unknown"}
                        task_info["consumer"] = "-"
                else:
                    # 如果没有状态，显示未知
                    task_info["status"] = json.dumps({
                        "status": "未知", 
                        "queue": queue_name,
                        "created_at": datetime.fromtimestamp(float(data.get("trigger_time", 0))).isoformat() if data.get("trigger_time") else None
                    })
                    task_info["parsed_status"] = {
                        "status": "未知", 
                        "queue": queue_name,
                        "created_at": datetime.fromtimestamp(float(data.get("trigger_time", 0))).isoformat() if data.get("trigger_time") else None
                    }
                    task_info["consumer"] = "-"
                
                all_tasks.append(task_info)
                
        except Exception as e:
            print(f"Error reading queue {queue_name}: {e}")
            # 如果stream不存在或出错，返回空结果
            return {
                "tasks": [],
                "count": 0,
                "oldest_id": None,
                "newest_id": None,
                "has_more": False,
                "limit": limit
            }
        
        # 获取最早和最晚的消息ID用于分页导航
        oldest_id = all_tasks[-1]["message_id"] if all_tasks else None
        newest_id = all_tasks[0]["message_id"] if all_tasks else None
        
        # 检查是否还有更多数据
        has_more = len(messages) >= limit
        
        # 获取队列总长度
        total_count = 0
        try:
            queue_info = await self.redis.xinfo_stream(prefixed_queue_name)
            total_count = queue_info.get("length", 0)
        except Exception as e:
            print(f"Error getting queue info for {queue_name}: {e}")
            total_count = len(all_tasks)
        
        return {
            "tasks": all_tasks,
            "count": len(all_tasks),
            "total_count": total_count,
            "oldest_id": oldest_id,
            "newest_id": newest_id,
            "has_more": has_more,
            "limit": limit
        }
        
    async def get_worker_heartbeats(self, queue_name: str) -> List[Dict[str, Any]]:
        """获取指定队列的Worker心跳信息 - 从全局hash读取队列worker信息"""
        worker_list = []
        current_time = datetime.now().timestamp()
        
        # 从全局hash中获取该队列的worker列表
        global_queue_workers_key = f'{self.redis_prefix}:global:queue_workers'
        queue_workers = await self.redis.hget(global_queue_workers_key, queue_name)
        
        if not queue_workers:
            return worker_list
        
        # 获取worker ID列表
        worker_ids = [wid.strip() for wid in queue_workers.split(',') if wid.strip()]
        
        for worker_id in worker_ids:
            try:
                worker_key = f"{self.redis_prefix}:worker:{worker_id}"
                # 获取worker的所有信息
                worker_data = await self.redis.hgetall(worker_key)
                
                if not worker_data:
                    continue
                
                last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                consumer_id = worker_data.get('consumer_id', worker_id)
                
                # 构建显示数据
                display_data = {
                    'consumer_id': consumer_id,
                    'consumer_name': f"{consumer_id}-{queue_name}",  # 保持兼容性
                    'host': worker_data.get('host', 'unknown'),
                    'pid': int(worker_data.get('pid', 0)),
                    'queue': queue_name,
                    'last_heartbeat': last_heartbeat,
                    'last_heartbeat_time': datetime.fromtimestamp(last_heartbeat).isoformat(),
                    'seconds_ago': int(current_time - last_heartbeat),
                    'is_alive': is_alive,
                    # 队列特定的统计信息
                    'success_count': int(worker_data.get(f'{queue_name}:success_count', 0)),
                    'failed_count': int(worker_data.get(f'{queue_name}:failed_count', 0)),
                    'total_count': int(worker_data.get(f'{queue_name}:total_count', 0)),
                    'running_tasks': int(worker_data.get(f'{queue_name}:running_tasks', 0)),
                    'avg_processing_time': float(worker_data.get(f'{queue_name}:avg_processing_time', 0.0))
                }
                
                # 如果离线时间存在，添加离线时间信息
                if 'offline_time' in worker_data:
                    display_data['offline_time'] = float(worker_data['offline_time'])
                    display_data['offline_time_formatted'] = datetime.fromtimestamp(float(worker_data['offline_time'])).isoformat()
                
                worker_list.append(display_data)
                
            except Exception as e:
                print(f"Error processing worker {worker_id}: {e}")
                continue
                
        return worker_list
    
    async def get_queue_worker_summary(self, queue_name: str) -> Dict[str, Any]:
        """获取队列的worker汇总统计信息"""
        try:
            # 从全局hash中获取该队列的worker列表
            global_queue_workers_key = f'{self.redis_prefix}:global:queue_workers'
            queue_workers = await self.redis.hget(global_queue_workers_key, queue_name)
            
            if not queue_workers:
                return {
                    'total_workers': 0,
                    'online_workers': 0,
                    'offline_workers': 0,
                    'total_success_count': 0,
                    'total_failed_count': 0,
                    'total_count': 0,
                    'total_running_tasks': 0,
                    'avg_processing_time': 0.0
                }
            
            # 获取worker ID列表
            worker_ids = [wid.strip() for wid in queue_workers.split(',') if wid.strip()]
            
            # 汇总统计
            total_workers = len(worker_ids)
            online_workers = 0
            offline_workers = 0
            total_success_count = 0
            total_failed_count = 0
            total_count = 0
            total_running_tasks = 0
            total_processing_time = 0.0
            processing_time_count = 0
            
            current_time = datetime.now().timestamp()
            
            for worker_id in worker_ids:
                try:
                    worker_key = f"{self.redis_prefix}:worker:{worker_id}"
                    worker_data = await self.redis.hgetall(worker_key)
                    
                    if not worker_data:
                        continue
                    
                    # 检查worker状态
                    last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                    is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                    
                    if is_alive and (current_time - last_heartbeat) < 30:
                        online_workers += 1
                    else:
                        offline_workers += 1
                    
                    # 汇总队列特定的统计信息
                    success_count = int(worker_data.get(f'{queue_name}:success_count', 0))
                    failed_count = int(worker_data.get(f'{queue_name}:failed_count', 0))
                    running_tasks = int(worker_data.get(f'{queue_name}:running_tasks', 0))
                    avg_processing_time = float(worker_data.get(f'{queue_name}:avg_processing_time', 0.0))
                    
                    total_success_count += success_count
                    total_failed_count += failed_count
                    total_count += success_count + failed_count
                    total_running_tasks += running_tasks
                    
                    if avg_processing_time > 0:
                        total_processing_time += avg_processing_time
                        processing_time_count += 1
                        
                except Exception as e:
                    print(f"Error processing worker {worker_id} summary: {e}")
                    continue
            
            # 获取历史记录中的统计信息（最近7天）
            history_success_count = 0
            history_failed_count = 0
            history_total_count = 0
            history_processing_time = 0.0
            history_processing_count = 0
            offline_workers_with_history = 0
            
            try:
                # 获取该队列的worker下线历史
                all_history = await self.get_worker_offline_history(limit=1000)
                for record in all_history:
                    # 只统计包含该队列的历史worker
                    if queue_name in record.get('queues', '').split(','):
                        offline_workers_with_history += 1
                        history_success_count += int(record.get('total_success_count', 0))
                        history_failed_count += int(record.get('total_failed_count', 0))
                        history_total_count += int(record.get('total_count', 0))
                        
                        # 累加历史的处理时间
                        hist_avg_time = float(record.get('avg_processing_time', 0))
                        hist_task_count = int(record.get('total_count', 0))
                        if hist_avg_time > 0 and hist_task_count > 0:
                            history_processing_time += hist_avg_time * hist_task_count
                            history_processing_count += hist_task_count
            except Exception as e:
                print(f"Error getting history stats: {e}")
            
            # 合并统计数据
            total_success_count += history_success_count
            total_failed_count += history_failed_count
            total_count += history_total_count
            
            # 合并处理时间统计
            total_processing_time += history_processing_time
            processing_time_count += history_processing_count
            
            # 计算平均处理时间（包含历史）
            overall_avg_processing_time = 0.0
            if processing_time_count > 0:
                overall_avg_processing_time = total_processing_time / processing_time_count
            
            return {
                'total_workers': total_workers,
                'online_workers': online_workers,
                'offline_workers': offline_workers,
                'offline_workers_with_history': offline_workers_with_history,
                'total_success_count': total_success_count,
                'total_failed_count': total_failed_count,
                'total_count': total_count,
                'total_running_tasks': total_running_tasks,
                'avg_processing_time': round(overall_avg_processing_time, 3),
                'history_included': True
            }
            
        except Exception as e:
            print(f"Error getting queue worker summary for {queue_name}: {e}")
            return {
                'total_workers': 0,
                'online_workers': 0,
                'offline_workers': 0,
                'total_success_count': 0,
                'total_failed_count': 0,
                'total_count': 0,
                'total_running_tasks': 0,
                'avg_processing_time': 0.0
            }
    
    async def get_worker_offline_history(self, limit: int = 100, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取worker下线历史记录"""
        try:
            history_index_key = f"{self.redis_prefix}:worker:history:index"
            
            # 设置时间范围
            if start_time is None:
                start_time = '-inf'
            if end_time is None:
                end_time = '+inf'
                
            # 从索引中获取consumer_id列表
            consumer_ids = await self.redis.zrevrangebyscore(
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
                record = await self.redis.hgetall(history_key)
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
                    record['avg_processing_time'] = float(record.get('avg_processing_time', 0))
                    
                    # 添加可读的时间格式
                    record['online_time_str'] = datetime.fromtimestamp(record['online_time']).isoformat()
                    record['offline_time_str'] = datetime.fromtimestamp(record['offline_time']).isoformat()
                    
                    # 格式化运行时长
                    duration = record['duration_seconds']
                    hours = duration // 3600
                    minutes = (duration % 3600) // 60
                    seconds = duration % 60
                    record['duration_str'] = f"{hours}h {minutes}m {seconds}s"
                    
                    history_records.append(record)
            
            return history_records
            
        except Exception as e:
            print(f"Error getting worker offline history: {e}")
            return []
    
    async def get_global_stats_with_history(self) -> Dict[str, Any]:
        """获取全局统计信息，包含历史记录"""
        try:
            # 获取所有队列
            queues = await self.get_all_queues()
            
            # 初始化统计
            total_success = 0
            total_failed = 0
            total_tasks = 0
            total_running = 0
            total_workers = 0
            online_workers = 0
            offline_workers = 0
            total_processing_time = 0.0
            total_processing_count = 0
            
            current_time = datetime.now().timestamp()
            
            # 统计每个队列的在线worker
            for queue in queues:
                try:
                    summary = await self.get_queue_worker_summary(queue)
                    total_workers += summary.get('total_workers', 0)
                    online_workers += summary.get('online_workers', 0)
                    offline_workers += summary.get('offline_workers', 0)
                    total_success += summary.get('total_success_count', 0)
                    total_failed += summary.get('total_failed_count', 0)
                    total_tasks += summary.get('total_count', 0)
                    total_running += summary.get('total_running_tasks', 0)
                    
                    # 累加平均处理时间（需要根据任务数加权）
                    avg_time = summary.get('avg_processing_time', 0)
                    task_count = summary.get('total_count', 0)
                    if avg_time > 0 and task_count > 0:
                        total_processing_time += avg_time * task_count
                        total_processing_count += task_count
                        
                except Exception as e:
                    print(f"Error getting stats for queue {queue}: {e}")
            
            # 计算全局平均处理时间
            global_avg_processing_time = 0.0
            if total_processing_count > 0:
                global_avg_processing_time = total_processing_time / total_processing_count
            
            return {
                'total_queues': len(queues),
                'total_workers': total_workers,
                'online_workers': online_workers,
                'offline_workers': offline_workers,
                'total_success_count': total_success,
                'total_failed_count': total_failed,
                'total_count': total_tasks,
                'total_running_tasks': total_running,
                'avg_processing_time': round(global_avg_processing_time, 3),
                'history_included': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting global stats: {e}")
            return {
                'total_queues': 0,
                'total_workers': 0,
                'online_workers': 0,
                'offline_workers': 0,
                'total_success_count': 0,
                'total_failed_count': 0,
                'total_count': 0,
                'total_running_tasks': 0,
                'avg_processing_time': 0.0,
                'history_included': False,
                'error': str(e)
            }
        
    async def get_all_queues(self) -> List[str]:
        """获取所有队列名称 - 从全局hash中读取"""
        try:
            # 从全局hash中获取所有队列名
            global_queue_workers_key = f'{self.redis_prefix}:global:queue_workers'
            queue_data = await self.redis.hgetall(global_queue_workers_key)
            
            # 返回所有队列名（hash的键）
            return list(queue_data.keys()) if queue_data else []
            
        except Exception as e:
            print(f"Error reading queues from global hash: {e}")
            return []
        
    async def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """获取队列统计信息"""
        prefixed_queue_name = self.get_prefixed_queue_name(queue_name)
        info = await self.redis.xinfo_stream(prefixed_queue_name)
        groups = await self.redis.xinfo_groups(prefixed_queue_name)
        
        stats = {
            "queue": queue_name,
            "length": info["length"],
            "first_entry": info.get("first-entry"),
            "last_entry": info.get("last-entry"),
            "consumer_groups": []
        }
        
        for group in groups:
            group_info = {
                "name": group["name"],
                "consumers": group["consumers"],
                "pending": group["pending"],
                "last_delivered_id": group["last-delivered-id"]
            }
            
            # 获取消费者详情
            consumers = await self.redis.xinfo_consumers(prefixed_queue_name, group["name"])
            group_info["consumer_details"] = consumers
            
            stats["consumer_groups"].append(group_info)
            
        return stats

# 创建全局监控器实例
monitor = RedisMonitor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await monitor.connect()
    yield
    # Shutdown
    await monitor.close()

app = FastAPI(title="Jettask Monitor", lifespan=lifespan)

@app.get("/api/tasks")
async def get_tasks():
    """获取所有任务"""
    tasks = await monitor.get_all_tasks()
    return {"tasks": tasks}

@app.get("/api/queue/{queue_name}/tasks")
async def get_queue_tasks(
    queue_name: str, 
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 50
):
    """获取指定队列的任务（基于时间范围）"""
    print(f'{queue_name=} {start_time=} {end_time=} {limit=}')
    result = await monitor.get_queue_tasks(queue_name, start_time, end_time, limit)
    return result

@app.get("/api/queue/{queue_name}/timeline")
async def get_queue_timeline(
    queue_name: str, 
    interval: str = "1m", 
    duration: str = "1h",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """获取队列任务的时间分布（用于时间轴）"""
    try:
        # 解析时间间隔和持续时间
        interval_seconds = parse_time_duration(interval)
        
        # 如果提供了具体的时间范围，使用它；否则使用duration参数
        if start_time and end_time:
            # 使用提供的时间范围
            min_id = start_time
            max_id = end_time if end_time != '+' else '+'
        else:
            # 使用duration参数计算时间范围
            duration_seconds = parse_time_duration(duration)
            now = int(datetime.now().timestamp() * 1000)
            start = now - duration_seconds * 1000
            min_id = f"{start}-0"
            max_id = "+"
        
        # 获取指定时间范围内的所有消息，使用更大的count来确保统计准确性
        messages = await monitor.redis.xrange(
            queue_name,
            min=min_id,
            max=max_id,
            count=50000  # 增加count以获取更完整的数据进行统计
        )
        
        # 按时间间隔统计任务数量
        buckets = {}
        bucket_size = interval_seconds * 1000  # 转换为毫秒
        
        # 计算实际的时间范围用于生成时间轴
        if start_time and end_time:
            # 从参数中解析时间范围
            if start_time != '-':
                actual_start = int(start_time.split('-')[0])
            else:
                actual_start = int(datetime.now().timestamp() * 1000) - 86400000  # 默认24小时前
            
            if end_time != '+':
                actual_end = int(end_time.split('-')[0])
            else:
                actual_end = int(datetime.now().timestamp() * 1000)
        else:
            # 使用duration参数计算的时间范围
            actual_start = start
            actual_end = now
        
        for msg_id, _ in messages:
            # 从消息ID提取时间戳
            timestamp = int(msg_id.split('-')[0])
            bucket_key = (timestamp // bucket_size) * bucket_size
            buckets[bucket_key] = buckets.get(bucket_key, 0) + 1
        
        # 转换为时间序列数据
        timeline_data = []
        current_bucket = (actual_start // bucket_size) * bucket_size
        
        while current_bucket <= actual_end:
            timeline_data.append({
                "timestamp": current_bucket,
                "count": buckets.get(current_bucket, 0)
            })
            current_bucket += bucket_size
        
        # 计算实际任务总数
        total_tasks = len(messages)
        
        return {
            "timeline": timeline_data,
            "interval": interval,
            "duration": duration,
            "start": actual_start,
            "end": actual_end,
            "total_tasks": total_tasks,  # 添加实际任务总数
            "message_count": len(messages)  # 实际获取到的消息数量
        }
        
    except Exception as e:
        print(f"Error getting timeline for queue {queue_name}: {e}")
        return {
            "timeline": [],
            "error": str(e)
        }

def parse_time_duration(duration_str: str) -> int:
    """解析时间字符串为秒数 (如 '1h', '10m', '30s')"""
    units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    if duration_str[-1] in units:
        value = int(duration_str[:-1])
        unit = duration_str[-1]
        return value * units[unit]
    
    # 默认为秒
    return int(duration_str)

@app.get("/api/task/{event_id}/result")
async def get_task_result(event_id: str):
    """获取单个任务的结果"""
    result_key = f"{monitor.redis_prefix}_RESULT:{event_id}"
    result = await monitor.redis.get(result_key)
    return {"event_id": event_id, "result": result}

@app.get("/api/queues")
async def get_queues():
    """获取所有队列"""
    queues = await monitor.get_all_queues()
    return {"queues": queues}

@app.get("/api/queue/{queue_name}/stats")
async def get_queue_stats(queue_name: str):
    """获取队列统计信息"""
    try:
        stats = await monitor.get_queue_stats(queue_name)
        return stats
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/queue/{queue_name}/workers")
async def get_queue_workers(queue_name: str):
    """获取队列的Worker信息"""
    workers = await monitor.get_worker_heartbeats(queue_name)
    return {"queue": queue_name, "workers": workers}

@app.get("/api/queue/{queue_name}/worker-summary")
async def get_queue_worker_summary(queue_name: str):
    """获取队列的Worker汇总统计信息"""
    summary = await monitor.get_queue_worker_summary(queue_name)
    return {"queue": queue_name, "summary": summary}

@app.get("/api/workers/offline-history")
async def get_workers_offline_history(
    limit: int = 100,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None
):
    """获取所有worker的下线历史记录"""
    history = await monitor.get_worker_offline_history(limit, start_time, end_time)
    return {"history": history, "total": len(history)}

@app.get("/api/global-stats")
async def get_global_stats():
    """获取全局统计信息（包含历史记录）"""
    stats = await monitor.get_global_stats_with_history()
    return stats

@app.get("/api/queue/{queue_name}/workers/offline-history")
async def get_queue_workers_offline_history(
    queue_name: str,
    limit: int = 100,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None
):
    """获取指定队列的worker下线历史记录"""
    # 获取所有历史记录，然后过滤出该队列的
    all_history = await monitor.get_worker_offline_history(limit * 10, start_time, end_time)
    queue_history = [
        record for record in all_history 
        if queue_name in record.get('queues', '').split(',')
    ][:limit]
    return {"queue": queue_name, "history": queue_history, "total": len(queue_history)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，用于实时更新"""
    await websocket.accept()
    
    try:
        while True:
            # 定期发送更新数据
            data = {
                "tasks": await monitor.get_all_tasks(),
                "queues": await monitor.get_all_queues(),
                "timestamp": datetime.now().isoformat()
            }
            
            # 为每个队列获取Worker信息
            queue_workers = {}
            for queue in data["queues"]:
                queue_workers[queue] = await monitor.get_worker_heartbeats(queue)
            data["workers"] = queue_workers
            
            await websocket.send_json(data)
            await asyncio.sleep(2)  # 每2秒更新一次
            
    except WebSocketDisconnect:
        pass

# 挂载静态文件
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def read_index():
    """返回主页HTML"""
    html_path = static_dir / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Jettask Monitor</h1><p>Static files not found</p>")

@app.get("/queue.html")
async def read_queue():
    """返回队列详情页HTML"""
    html_path = static_dir / "queue.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Queue Details</h1><p>Page not found</p>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
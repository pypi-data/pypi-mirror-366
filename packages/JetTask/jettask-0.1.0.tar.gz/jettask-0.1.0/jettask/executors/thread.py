import ujson
import time
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

from .base import BaseExecutor

logger = logging.getLogger('app')


class ThreadExecutor(BaseExecutor):
    """Thread-based executor for sync tasks"""
    
    def __init__(self, event_queue, app, concurrency=1):
        super().__init__(event_queue, app, concurrency)
        self.executor = ThreadPoolExecutor(max_workers=concurrency)
        
        # 批量操作缓冲区
        self.batch_status_updates = {}  # {event_id: status_dict}
        self.batch_data_updates = {}    # {event_id: data}
        self.last_batch_flush = time.time()
        
    def logic(self, event_id: str, event_data: dict, queue: str, routing: dict = None, consumer: str = None):
        try:
            if not (task := self.app.get_task_by_name(event_data.get("name", ""))):
                logging.error(f"{event_data} {queue} {routing}未绑定任何task")
                self.app.ep.ack(queue, event_id, asyncio=False)
                return

            # 优化：增加缓存时间到10秒
            if self.last_refresh_pending_time < time.time() - 10:
                pending_info = self.app.ep.redis_client.xpending(queue, queue)
                self.pedding_count = pending_info.get("pending", 0)
                self.last_refresh_pending_time = time.time()

            status = "success"
            exception = None
            error_msg = None
            ret = None
            args = ujson.loads(event_data["args"])
            kwargs = ujson.loads(event_data["kwargs"])
            
            result = task.on_before(
                event_id=event_id,
                pedding_count=self.pedding_count,
                args=args,
                kwargs=kwargs,
            )
            
            if result and result.reject:
                return
                
            # 标记任务开始执行
            if hasattr(self.app, 'consumer_manager') and self.app.consumer_manager:
                self.app.consumer_manager.task_started(queue)
            
            self.app.set_task_status(
                event_id,
                {"status": "running", "exception": exception, "error_msg": error_msg},
                asyncio=False,
            )
            
            try:
                ret = task(event_id, event_data['trigger_time'], *args, **kwargs)
                task.on_success(
                    event_id=event_id,
                    args=args,
                    kwargs=kwargs,
                    result=ret,
                )
            except Exception as e:
                status = "error"
                exception = traceback.format_exc()
                error_msg = str(e)
                traceback.print_exc()
            finally:
                # 计算完成时间和消耗时间
                completed_at = time.time()
                trigger_time_float = float(event_data['trigger_time'])
                duration = completed_at - trigger_time_float
                
                # 标记任务完成并更新统计信息
                if hasattr(self.app, 'consumer_manager') and self.app.consumer_manager:
                    self.app.consumer_manager.task_finished(queue)
                    self.app.consumer_manager.update_stats(
                        queue=queue,
                        success=(status == "success"),
                        processing_time=duration
                    )
                
                # 添加到批量缓冲区，包含完成时间和耗时
                self.batch_status_updates[event_id] = {
                    "status": status, 
                    "exception": exception, 
                    "error_msg": error_msg,
                    "completed_at": completed_at,  # 完成时间戳
                    "duration": duration,  # 耗时（秒）
                    "consumer": consumer  # 消费者信息
                }
                if ret:
                    self.batch_data_updates[event_id] = ret if type(ret) == str else ujson.dumps(ret)
                
                # ACK立即执行
                self.app.ep.ack(queue, event_id, asyncio=False)
                
                task.on_end(
                    event_id=event_id,
                    args=args,
                    kwargs=kwargs,
                    result=ret,
                    pedding_count=self.pedding_count,
                )
                
                # 检查是否需要批量刷新
                self._check_batch_flush()
                
                if routing:
                    agg_key = routing.get("agg_key")
                    routing_key = routing.get("routing_key")
                    if routing_key and agg_key:
                        with self.app.ep.rlock:
                            if routing_key in self.app.ep.solo_running_state[queue]:
                                self.app.ep.solo_running_state[queue][routing_key] -= 1
                    try:
                        if result and result.urgent_retry:
                            self.app.ep.solo_urgent_retry[routing_key] = True
                    except:
                        logger.error(f'出现未知异常 {routing}: {traceback.format_exc()}')
                    if result and result.delay:
                        self.app.ep.task_scheduler[queue][routing_key] = time.time() + result.delay
        finally:
            self.batch_counter -= 1
    
    def batch_logic(self, event_ids: list, event_data_list: list, queue: str, name: str):
        try:
            if not (task := self.app.get_task_by_name(name)):
                logging.error(f"{name}未绑定任何task")
                return

            # 优化：增加缓存时间到10秒
            if self.last_refresh_pending_time < time.time() - 10:
                pending_info = self.app.ep.redis_client.xpending(queue, queue)
                self.pedding_count = pending_info.get("pending", 0)
                self.last_refresh_pending_time = time.time()

            status = "success"
            exception = None
            ret = None
            params = [{'args': ujson.loads(item["args"]), 'kwargs':ujson.loads(item["kwargs"])} for item in event_data_list]
            
            task.on_before(
                event_id=event_ids,
                pedding_count=self.pedding_count,
                kwargs={'params': params},
                args=[]
            )
            
            try:
                ret = task(event_ids, params=params)
                task.on_success(
                    event_id=event_ids,
                    kwargs={'params': params},
                    args=[],
                    result=ret,
                )
            except Exception:
                status = "error"
                exception = traceback.format_exc()
                traceback.print_exc()
            finally:
                # 优化：序列化一次，复用结果
                if ret:
                    serialized_ret = ret if type(ret) == str else ujson.dumps(ret)
                else:
                    serialized_ret = None
                
                # 批量添加到缓冲区
                for event_id in event_ids:
                    self.batch_status_updates[event_id] = {
                        "status": status, 
                        "exception": exception
                    }
                    if serialized_ret:
                        self.batch_data_updates[event_id] = serialized_ret
                    
                    # ACK立即执行
                    self.app.ep.ack(queue, event_id, asyncio=False)
                
                task.on_end(
                    event_id=event_ids,
                    kwargs={'params': params},
                    args=[],
                    result=ret,
                    pedding_count=self.pedding_count,
                )
                
                # 强制批量刷新
                self._force_batch_flush()
        finally:
            self.batch_counter -= 1
    
    def _check_batch_flush(self):
        """检查是否需要批量刷新"""
        # 当缓冲区达到一定大小或时间间隔达到阈值时刷新
        if (len(self.batch_status_updates) >= 50 or 
            len(self.batch_data_updates) >= 50 or
            time.time() - self.last_batch_flush > 0.1):
            self._force_batch_flush()
    
    def _force_batch_flush(self):
        """强制批量刷新所有缓冲区"""
        # 批量更新状态
        if self.batch_status_updates:
            try:
                if hasattr(self.app, 'set_task_status_by_batch'):
                    self.app.set_task_status_by_batch(self.batch_status_updates, asyncio=False)
                else:
                    # 使用pipeline批量更新
                    pipeline = self.app.redis.pipeline()
                    for event_id, status_dict in self.batch_status_updates.items():
                        key = f"{self.app._status_prefix}{event_id}"
                        pipeline.set(key, ujson.dumps(status_dict), ex=3600)
                    pipeline.execute()
                self.batch_status_updates.clear()
            except Exception as e:
                logger.error(f"批量更新状态失败: {e}")
        
        # 批量更新数据
        if self.batch_data_updates:
            try:
                pipeline = self.app.redis.pipeline()
                for event_id, data in self.batch_data_updates.items():
                    key = f"{self.app._result_prefix}{event_id}"
                    pipeline.set(key, data, ex=3600)
                pipeline.execute()
                self.batch_data_updates.clear()
            except Exception as e:
                logger.error(f"批量更新数据失败: {e}")
        
        self.last_batch_flush = time.time()
    
    def loop(self):
        while True:
            if self.event_queue and self.batch_counter <= self.concurrency:
                event = self.event_queue.popleft()
                event.pop("execute_time", None)
                self.batch_counter += 1
                # 移除调试打印以提升性能
                if event.pop('task_type', "") == "batch":
                    self.executor.submit(self.batch_logic, **event)
                else:
                    self.executor.submit(self.logic, **event)
            else:
                # 检查批量刷新
                current_time = time.time()
                if current_time - self.last_batch_flush > 0.1:
                    self._force_batch_flush()
                time.sleep(0.001)
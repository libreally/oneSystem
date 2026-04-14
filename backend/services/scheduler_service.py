"""定时调度中心服务
支持定时任务、周期执行、自动报告、主动提醒等功能
"""
import os
import logging
import threading
import schedule
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from backend.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class RepeatType(Enum):
    """重复类型"""
    ONCE = 'once'  # 仅执行一次
    DAILY = 'daily'  # 每天
    WEEKLY = 'weekly'  # 每周
    MONTHLY = 'monthly'  # 每月
    HOURLY = 'hourly'  # 每小时
    CUSTOM = 'custom'  # 自定义间隔


@dataclass
class ScheduledTask:
    """定时任务定义"""
    task_id: str
    name: str
    description: str = ''
    action: str = ''  # 要执行的动作/Skill
    params: Dict[str, Any] = field(default_factory=dict)
    repeat_type: RepeatType = RepeatType.ONCE
    interval_minutes: int = 0  # 自定义间隔（分钟）
    execute_at: datetime = None  # 执行时间
    day_of_week: int = 0  # 星期几 (0-6, 0=周一)
    day_of_month: int = 1  # 每月几号
    hour: int = 9  # 执行小时
    minute: int = 0  # 执行分钟
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_executed: datetime = None
    next_execution: datetime = None
    execution_count: int = 0
    status: TaskStatus = TaskStatus.PENDING
    callback: Callable = None  # 执行回调函数
    user_id: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'action': self.action,
            'params': self.params,
            'repeat_type': self.repeat_type.value,
            'interval_minutes': self.interval_minutes,
            'execute_at': self.execute_at.isoformat() if self.execute_at else None,
            'day_of_week': self.day_of_week,
            'day_of_month': self.day_of_month,
            'hour': self.hour,
            'minute': self.minute,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'next_execution': self.next_execution.isoformat() if self.next_execution else None,
            'execution_count': self.execution_count,
            'status': self.status.value,
            'user_id': self.user_id
        }


class SchedulerService:
    """定时调度服务"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self._scheduler_thread: threading.Thread = None
        self._running = False
        self._lock = threading.Lock()
        
    def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("调度器已在运行中")
            return
        
        self._running = True
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        logger.info("定时调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        logger.info("定时调度器已停止")
    
    def _run_scheduler(self):
        """运行调度器主循环"""
        while self._running:
            try:
                with self._lock:
                    schedule.run_pending()
                
                # 检查并更新即将执行的任务
                self._update_next_executions()
                
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                logger.error(f"调度器运行异常：{str(e)}")
                time.sleep(5)
    
    def _update_next_executions(self):
        """更新任务的下次执行时间"""
        now = datetime.now()
        for task in self.tasks.values():
            if task.enabled and task.status != TaskStatus.CANCELLED:
                if task.next_execution and task.next_execution <= now:
                    # 任务应该执行了，schedule 会处理
                    pass
                elif not task.next_execution:
                    # 计算下次执行时间
                    task.next_execution = self._calculate_next_execution(task)
    
    def _calculate_next_execution(self, task: ScheduledTask) -> datetime:
        """计算任务的下次执行时间"""
        now = datetime.now()
        
        if task.repeat_type == RepeatType.ONCE:
            if task.execute_at:
                return task.execute_at
            return now + timedelta(minutes=1)  # 默认 1 分钟后执行
        
        elif task.repeat_type == RepeatType.HOURLY:
            next_time = now.replace(minute=task.minute, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(hours=1)
            return next_time
        
        elif task.repeat_type == RepeatType.DAILY:
            next_time = now.replace(hour=task.hour, minute=task.minute, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time
        
        elif task.repeat_type == RepeatType.WEEKLY:
            days_ahead = task.day_of_week - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_time = now.replace(hour=task.hour, minute=task.minute, second=0, microsecond=0)
            next_time += timedelta(days=days_ahead)
            if next_time <= now:
                next_time += timedelta(weeks=1)
            return next_time
        
        elif task.repeat_type == RepeatType.MONTHLY:
            # 简化处理：如果本月已过，则下月
            next_time = now.replace(day=task.day_of_month, hour=task.hour, 
                                   minute=task.minute, second=0, microsecond=0)
            if next_time <= now:
                # 加一个月
                if now.month == 12:
                    next_time = next_time.replace(year=now.year + 1, month=1)
                else:
                    next_time = next_time.replace(month=now.month + 1)
            return next_time
        
        elif task.repeat_type == RepeatType.CUSTOM:
            return now + timedelta(minutes=task.interval_minutes)
        
        return now
    
    def _schedule_task(self, task: ScheduledTask):
        """将任务添加到调度器"""
        def job():
            self._execute_task(task)
        
        if task.repeat_type == RepeatType.HOURLY:
            schedule.every(task.interval_minutes or 60).minutes.do(job)
        elif task.repeat_type == RepeatType.DAILY:
            schedule.every().day.at(f"{task.hour:02d}:{task.minute:02d}").do(job)
        elif task.repeat_type == RepeatType.WEEKLY:
            weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            schedule.every(getattr(schedule, weekdays[task.day_of_week])).at(
                f"{task.hour:02d}:{task.minute:02d}"
            ).do(job)
        elif task.repeat_type == RepeatType.MONTHLY:
            # 简化：每 30 天执行一次
            schedule.every(30).days.at(f"{task.hour:02d}:{task.minute:02d}").do(job)
        elif task.repeat_type == RepeatType.CUSTOM:
            interval = task.interval_minutes or 60
            schedule.every(interval).minutes.do(job)
        else:  # ONCE
            if task.execute_at:
                delay = (task.execute_at - datetime.now()).total_seconds()
                if delay > 0:
                    schedule.every(int(delay)).seconds.do(job).tag(f"once_{task.task_id}")
            else:
                schedule.every(1).minutes.do(job).tag(f"once_{task.task_id}")
    
    def add_task(self, task: ScheduledTask) -> bool:
        """
        添加定时任务
        
        Args:
            task: 任务定义
            
        Returns:
            是否成功
        """
        with self._lock:
            if task.task_id in self.tasks:
                logger.warning(f"任务已存在：{task.task_id}")
                return False
            
            # 计算下次执行时间
            task.next_execution = self._calculate_next_execution(task)
            
            self.tasks[task.task_id] = task
            self._schedule_task(task)
            
            logger.info(f"已添加定时任务：{task.name} ({task.task_id}), 下次执行：{task.next_execution}")
            return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        移除定时任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功
        """
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.enabled = False
            task.status = TaskStatus.CANCELLED
            
            # 从 schedule 中移除所有相关任务
            schedule.clear(f"once_{task_id}")
            # 清除所有任务（schedule 库没有更好的方法按任务ID清除）
            # 注意：这会清除所有任务，然后重新添加剩余的任务
            temp_tasks = list(self.tasks.values())
            schedule.clear()
            
            del self.tasks[task_id]
            
            # 重新添加剩余的任务
            for t in temp_tasks:
                if t.task_id != task_id and t.enabled:
                    self._schedule_task(t)
            
            logger.info(f"已移除定时任务：{task_id}")
            return True
    
    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.enabled = True
            task.next_execution = self._calculate_next_execution(task)
            self._schedule_task(task)
            
            logger.info(f"已启用任务：{task_id}")
            return True
    
    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.enabled = False
            
            # 从调度器中移除任务
            temp_tasks = list(self.tasks.values())
            schedule.clear()
            
            # 重新添加剩余的启用任务
            for t in temp_tasks:
                if t.task_id != task_id and t.enabled:
                    self._schedule_task(t)
            
            logger.info(f"已禁用任务：{task_id}")
            return True
    
    def _execute_task(self, task: ScheduledTask):
        """执行任务"""
        if not task.enabled:
            return
        
        logger.info(f"开始执行定时任务：{task.name} ({task.task_id})")
        
        execution_record = {
            'execution_id': f"exec_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            'task_id': task.task_id,
            'task_name': task.name,
            'start_time': datetime.now(),
            'status': 'running'
        }
        
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.last_executed = datetime.now()
            task.execution_count += 1
            
            # 执行回调或动作
            if task.callback:
                result = task.callback(task.params)
            else:
                # 调用 LLM 模型执行任务
                llm_service = get_llm_service()
                if llm_service:
                    # 构建消息列表
                    messages = [
                        {"role": "system", "content": f"你是一个定时任务执行助手，需要按照任务需求执行操作。"},
                        {"role": "user", "content": f"任务名称：{task.name}\n任务描述：{task.description}\n执行动作：{task.action}\n任务参数：{task.params}"}
                    ]
                    
                    # 调用模型
                    llm_result = llm_service.chat_completion(messages, temperature=0.7, max_tokens=1000)
                    
                    if llm_result.get('success'):
                        result = {
                            'success': True,
                            'message': f'任务 {task.name} 执行完成',
                            'llm_response': llm_result.get('response')
                        }
                    else:
                        result = {
                            'success': False,
                            'message': f'任务 {task.name} 执行失败：{llm_result.get("error", "模型调用失败")}'
                        }
                else:
                    # 当 LLM 服务不可用时，执行默认动作
                    result = {'success': True, 'message': f'任务 {task.name} 执行完成（LLM 服务未启用）'}
            
            execution_record['status'] = 'success'
            execution_record['result'] = result
            
            logger.info(f"定时任务执行成功：{task.task_id}")
            
        except Exception as e:
            logger.error(f"定时任务执行失败：{task.task_id}, 错误：{str(e)}")
            execution_record['status'] = 'failed'
            execution_record['error'] = str(e)
            task.status = TaskStatus.FAILED
        
        finally:
            execution_record['end_time'] = datetime.now()
            self.execution_history.append(execution_record)
            
            # 保留最近 1000 条记录
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-1000:]
            
            # 更新下次执行时间（非一次性任务）
            if task.repeat_type != RepeatType.ONCE and task.enabled:
                task.next_execution = self._calculate_next_execution(task)
            elif task.repeat_type == RepeatType.ONCE:
                task.status = TaskStatus.COMPLETED
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, user_id: str = None, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        列出所有任务
        
        Args:
            user_id: 用户 ID 过滤
            enabled_only: 是否只返回启用的任务
            
        Returns:
            任务列表
        """
        tasks = []
        for task in self.tasks.values():
            if user_id and task.user_id != user_id:
                continue
            if enabled_only and not task.enabled:
                continue
            tasks.append(task.to_dict())
        
        # 按下次执行时间排序
        tasks.sort(key=lambda x: x.get('next_execution') or '9999')
        return tasks
    
    def get_execution_history(self, task_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """获取执行历史"""
        history = self.execution_history.copy()
        
        if task_id:
            history = [h for h in history if h['task_id'] == task_id]
        
        # 格式化时间为统一格式
        for record in history:
            if isinstance(record.get('start_time'), datetime):
                record['start_time'] = record['start_time'].strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(record.get('end_time'), datetime):
                record['end_time'] = record['end_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        history.sort(key=lambda x: x['start_time'], reverse=True)
        return history[:limit]
    
    def create_daily_report_task(self, 
                                  name: str = '每日工作报告',
                                  hour: int = 17,
                                  minute: int = 0,
                                  user_id: str = None,
                                  callback: Callable = None) -> ScheduledTask:
        """
        创建每日报告任务
        
        Args:
            name: 任务名称
            hour: 执行小时
            minute: 执行分钟
            user_id: 用户 ID
            callback: 回调函数
            
        Returns:
            创建的任务
        """
        task = ScheduledTask(
            task_id=f"daily_report_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=name,
            description='自动生成每日工作报告',
            action='generate_daily_report',
            repeat_type=RepeatType.DAILY,
            hour=hour,
            minute=minute,
            user_id=user_id,
            callback=callback
        )
        
        self.add_task(task)
        return task
    
    def create_reminder_task(self,
                             name: str,
                             hour: int,
                             minute: int,
                             params: Dict[str, Any] = None,
                             repeat_type: RepeatType = RepeatType.DAILY,
                             user_id: str = None,
                             callback: Callable = None) -> ScheduledTask:
        """
        创建提醒任务
        
        Args:
            name: 任务名称
            hour: 执行小时
            minute: 执行分钟
            params: 参数
            repeat_type: 重复类型
            user_id: 用户 ID
            callback: 回调函数
            
        Returns:
            创建的任务
        """
        task = ScheduledTask(
            task_id=f"reminder_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=name,
            description='定时提醒',
            action='send_reminder',
            params=params or {},
            repeat_type=repeat_type,
            hour=hour,
            minute=minute,
            user_id=user_id,
            callback=callback
        )
        
        self.add_task(task)
        return task


# 全局调度服务实例
scheduler_service = SchedulerService()


def init_scheduler_service() -> SchedulerService:
    """初始化调度服务"""
    global scheduler_service
    scheduler_service.start()
    return scheduler_service

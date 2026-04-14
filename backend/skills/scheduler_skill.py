"""
定时任务管理 Skill
支持创建、查看、修改和删除定时任务
"""
from .base_skill import BaseSkill
from typing import Dict, Any, List
import logging
from backend.services.scheduler_service import scheduler_service, ScheduledTask, RepeatType, TaskStatus
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class SchedulerSkill(BaseSkill):
    """定时任务管理 Skill"""
    
    def __init__(self):
        super().__init__(
            skill_id='scheduler',
            name='定时任务管理',
            description='支持创建、查看、修改和删除定时任务，设置执行时间和重复规则'
        )
    
    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证参数"""
        errors = []
        
        if 'action' not in params:
            errors.append('缺少 action 参数')
        
        action = params.get('action')
        
        if action == 'create_task':
            if 'name' not in params:
                errors.append('缺少 name 参数')
            if 'action' not in params:
                errors.append('缺少 task_action 参数')
        
        elif action in ['update_task', 'delete_task', 'enable_task', 'disable_task']:
            if 'task_id' not in params:
                errors.append('缺少 task_id 参数')
        
        return len(errors) == 0, errors
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行定时任务管理操作"""
        try:
            action = params.get('action')
            
            if action == 'create_task':
                return self._create_task(params)
            elif action == 'list_tasks':
                return self._list_tasks(params)
            elif action == 'get_task':
                return self._get_task(params)
            elif action == 'update_task':
                return self._update_task(params)
            elif action == 'delete_task':
                return self._delete_task(params)
            elif action == 'enable_task':
                return self._enable_task(params)
            elif action == 'disable_task':
                return self._disable_task(params)
            elif action == 'get_execution_history':
                return self._get_execution_history(params)
            else:
                return {
                    'success': False,
                    'message': f'未知的操作类型：{action}'
                }
                
        except Exception as e:
            logger.error(f"定时任务管理失败：{str(e)}")
            return {
                'success': False,
                'message': f'操作失败：{str(e)}'
            }
    
    def _create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建定时任务"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        name = params.get('name')
        description = params.get('description', '')
        task_action = params.get('task_action')
        task_params = params.get('params', {})
        
        # 解析重复类型
        repeat_type_str = params.get('repeat_type', 'once')
        repeat_type = getattr(RepeatType, repeat_type_str.upper(), RepeatType.ONCE)
        
        # 解析执行时间参数
        execute_at_str = params.get('execute_at')
        execute_at = None
        if execute_at_str:
            try:
                execute_at = datetime.fromisoformat(execute_at_str)
            except Exception:
                pass
        
        # 创建任务
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            description=description,
            action=task_action,
            params=task_params,
            repeat_type=repeat_type,
            interval_minutes=params.get('interval_minutes', 0),
            execute_at=execute_at,
            day_of_week=params.get('day_of_week', 0),
            day_of_month=params.get('day_of_month', 1),
            hour=params.get('hour', 9),
            minute=params.get('minute', 0),
            enabled=params.get('enabled', True),
            user_id=params.get('user_id')
        )
        
        success = scheduler_service.add_task(task)
        
        if success:
            self.log_execution('create_task', f'已创建定时任务：{name} ({task_id})')
            return {
                'success': True,
                'message': '定时任务创建成功',
                'data': task.to_dict()
            }
        else:
            return {
                'success': False,
                'message': '定时任务创建失败'
            }
    
    def _list_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """列出定时任务"""
        user_id = params.get('user_id')
        enabled_only = params.get('enabled_only', False)
        
        tasks = scheduler_service.list_tasks(user_id=user_id, enabled_only=enabled_only)
        
        self.log_execution('list_tasks', f'获取任务列表，共 {len(tasks)} 个任务')
        return {
            'success': True,
            'message': '获取任务列表成功',
            'data': tasks
        }
    
    def _get_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取单个任务详情"""
        task_id = params.get('task_id')
        
        task = scheduler_service.get_task(task_id)
        if task:
            return {
                'success': True,
                'message': '获取任务详情成功',
                'data': task.to_dict()
            }
        else:
            return {
                'success': False,
                'message': '任务不存在'
            }
    
    def _update_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """更新任务"""
        task_id = params.get('task_id')
        task = scheduler_service.get_task(task_id)
        
        if not task:
            return {
                'success': False,
                'message': '任务不存在'
            }
        
        # 更新任务属性
        if 'name' in params:
            task.name = params['name']
        if 'description' in params:
            task.description = params['description']
        if 'task_action' in params:
            task.action = params['task_action']
        if 'params' in params:
            task.params = params['params']
        if 'enabled' in params:
            task.enabled = params['enabled']
        
        # 更新重复类型和时间参数
        if 'repeat_type' in params:
            repeat_type_str = params['repeat_type']
            task.repeat_type = getattr(RepeatType, repeat_type_str.upper(), task.repeat_type)
        if 'interval_minutes' in params:
            task.interval_minutes = params['interval_minutes']
        if 'execute_at' in params:
            try:
                task.execute_at = datetime.fromisoformat(params['execute_at'])
            except Exception:
                pass
        if 'day_of_week' in params:
            task.day_of_week = params['day_of_week']
        if 'day_of_month' in params:
            task.day_of_month = params['day_of_month']
        if 'hour' in params:
            task.hour = params['hour']
        if 'minute' in params:
            task.minute = params['minute']
        
        # 重新计算下次执行时间
        task.next_execution = scheduler_service._calculate_next_execution(task)
        
        # 重新调度任务
        # 先移除再添加
        scheduler_service.remove_task(task_id)
        task.task_id = task_id  # 保持相同的任务ID
        success = scheduler_service.add_task(task)
        
        if success:
            self.log_execution('update_task', f'已更新定时任务：{task_id}')
            return {
                'success': True,
                'message': '任务更新成功',
                'data': task.to_dict()
            }
        else:
            return {
                'success': False,
                'message': '任务更新失败'
            }
    
    def _delete_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """删除任务"""
        task_id = params.get('task_id')
        success = scheduler_service.remove_task(task_id)
        
        if success:
            self.log_execution('delete_task', f'已删除定时任务：{task_id}')
            return {
                'success': True,
                'message': '任务删除成功'
            }
        else:
            return {
                'success': False,
                'message': '任务删除失败或任务不存在'
            }
    
    def _enable_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """启用任务"""
        task_id = params.get('task_id')
        success = scheduler_service.enable_task(task_id)
        
        if success:
            self.log_execution('enable_task', f'已启用定时任务：{task_id}')
            return {
                'success': True,
                'message': '任务启用成功'
            }
        else:
            return {
                'success': False,
                'message': '任务启用失败或任务不存在'
            }
    
    def _disable_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """禁用任务"""
        task_id = params.get('task_id')
        success = scheduler_service.disable_task(task_id)
        
        if success:
            self.log_execution('disable_task', f'已禁用定时任务：{task_id}')
            return {
                'success': True,
                'message': '任务禁用成功'
            }
        else:
            return {
                'success': False,
                'message': '任务禁用失败或任务不存在'
            }
    
    def _get_execution_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取执行历史"""
        task_id = params.get('task_id')
        limit = params.get('limit', 50)
        
        history = scheduler_service.get_execution_history(task_id=task_id, limit=limit)
        
        self.log_execution('get_execution_history', f'获取执行历史，共 {len(history)} 条记录')
        return {
            'success': True,
            'message': '获取执行历史成功',
            'data': history
        }

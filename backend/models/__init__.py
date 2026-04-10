"""
数据模型模块
"""
from datetime import datetime
import json

class Skill:
    """Skill能力模型"""
    
    def __init__(self, skill_id, name, description, category, 
                 input_params=None, output_params=None, 
                 status='active', version='1.0.0'):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.category = category  # 文档处理、数据处理、流程管理等
        self.input_params = input_params or []
        self.output_params = output_params or []
        self.status = status  # active, inactive, draft
        self.version = version
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'input_params': self.input_params,
            'output_params': self.output_params,
            'status': self.status,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        skill = cls(
            skill_id=data.get('skill_id'),
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            input_params=data.get('input_params'),
            output_params=data.get('output_params'),
            status=data.get('status', 'active'),
            version=data.get('version', '1.0.0')
        )
        if 'created_at' in data:
            skill.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            skill.updated_at = datetime.fromisoformat(data['updated_at'])
        return skill


class Task:
    """任务模型"""
    
    def __init__(self, task_id, title, source_system, priority,
                 status='pending', due_date=None, assignee=None,
                 description='', tags=None):
        self.task_id = task_id
        self.title = title
        self.source_system = source_system  # 来源系统
        self.priority = priority  # high, medium, low
        self.status = status  # pending, in_progress, completed, overdue
        self.due_date = due_date
        self.assignee = assignee
        self.description = description
        self.tags = tags or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'title': self.title,
            'source_system': self.source_system,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'assignee': self.assignee,
            'description': self.description,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ScheduledTask:
    """定时任务模型"""
    
    def __init__(self, task_id, name, skill_id, schedule_type,
                 schedule_config, params=None, status='active'):
        self.task_id = task_id
        self.name = name
        self.skill_id = skill_id
        self.schedule_type = schedule_type  # cron, interval, date
        self.schedule_config = schedule_config  # cron表达式或间隔配置
        self.params = params or {}
        self.status = status  # active, paused, disabled
        self.last_run = None
        self.next_run = None
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'name': self.name,
            'skill_id': self.skill_id,
            'schedule_type': self.schedule_type,
            'schedule_config': self.schedule_config,
            'params': self.params,
            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'created_at': self.created_at.isoformat()
        }


class ConfigItem:
    """配置项模型"""
    
    def __init__(self, config_id, config_type, key, value,
                 scope='public', user_id=None, description=''):
        self.config_id = config_id
        self.config_type = config_type  # template, sensitive_word, rule, etc.
        self.key = key
        self.value = value
        self.scope = scope  # public, personal
        self.user_id = user_id
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            'config_id': self.config_id,
            'config_type': self.config_type,
            'key': self.key,
            'value': self.value,
            'scope': self.scope,
            'user_id': self.user_id,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class UserPreference:
    """用户偏好模型"""
    
    def __init__(self, user_id, preferences=None):
        self.user_id = user_id
        self.preferences = preferences or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

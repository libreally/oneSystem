"""
智能办公平台 - 一系统
数据库模型定义
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    preferences = db.relationship('UserPreference', backref='user', lazy='joined', uselist=False)
    # tasks relationship removed due to multiple foreign keys
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'last_login': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class UserPreference(db.Model):
    """用户偏好设置"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='zh-CN')
    notifications_enabled = db.Column(db.Boolean, default=True)
    auto_save = db.Column(db.Boolean, default=True)
    custom_settings = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'language': self.language,
            'notifications_enabled': self.notifications_enabled,
            'auto_save': self.auto_save,
            'custom_settings': self.custom_settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Skill(db.Model):
    """技能表"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    parameters = db.Column(db.JSON, default=list)
    code = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_dynamic = db.Column(db.Boolean, default=False)
    llm_model = db.Column(db.String(50))
    version = db.Column(db.String(20), default='1.0.0')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'parameters': self.parameters,
            'is_active': self.is_active,
            'is_dynamic': self.is_dynamic,
            'llm_model': self.llm_model,
            'version': self.version,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ScheduledTask(db.Model):
    """定时任务表"""
    __tablename__ = 'scheduled_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'))
    cron_expression = db.Column(db.String(50))
    repeat_type = db.Column(db.String(20), default='once')
    repeat_interval = db.Column(db.Integer)
    next_run_time = db.Column(db.DateTime)
    last_run_time = db.Column(db.DateTime)
    last_run_status = db.Column(db.String(20))
    last_run_result = db.Column(db.JSON)
    is_enabled = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    skill = db.relationship('Skill', backref='scheduled_tasks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'skill_id': self.skill_id,
            'cron_expression': self.cron_expression,
            'repeat_type': self.repeat_type,
            'repeat_interval': self.repeat_interval,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'last_run_status': self.last_run_status,
            'last_run_result': self.last_run_result,
            'is_enabled': self.is_enabled,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Task(db.Model):
    """任务表（待办事项）"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    source_system = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending')
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    task_metadata = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source_system': self.source_system,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'metadata': self.task_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ConfigItem(db.Model):
    """配置项表"""
    __tablename__ = 'config_items'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.JSON, nullable=False)
    config_type = db.Column(db.String(50), default='general')
    scope = db.Column(db.String(20), default='public')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    description = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)
    is_encrypted = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'config_type': self.config_type,
            'scope': self.scope,
            'user_id': self.user_id,
            'description': self.description,
            'version': self.version,
            'is_encrypted': self.is_encrypted,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ChatSession(db.Model):
    """聊天会话表"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200))
    messages = db.Column(db.JSON, default=list)
    context = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'messages': self.messages,
            'context': self.context,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SkillExecutionLog(db.Model):
    """技能执行日志表"""
    __tablename__ = 'skill_execution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    input_params = db.Column(db.JSON)
    output_result = db.Column(db.JSON)
    status = db.Column(db.String(20), default='success')
    error_message = db.Column(db.Text)
    execution_time = db.Column(db.Float)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # 关联
    skill = db.relationship('Skill', backref='execution_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'user_id': self.user_id,
            'input_params': self.input_params,
            'output_result': self.output_result,
            'status': self.status,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class IntentModel(db.Model):
    """意图识别模型表"""
    __tablename__ = 'intent_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50), default='rule')
    model_path = db.Column(db.String(256))
    accuracy = db.Column(db.Float)
    training_data_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=False)
    version = db.Column(db.String(20), default='1.0.0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'model_path': self.model_path,
            'accuracy': self.accuracy,
            'training_data_count': self.training_data_count,
            'is_active': self.is_active,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

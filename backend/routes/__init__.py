"""
API 路由模块初始化
"""
from .api_routes import api_bp
from .skill_routes import skill_bp
from .task_routes import task_bp
from .config_routes import config_bp
from .scheduler_routes import scheduler_bp
from .file_retrieval_routes import file_retrieval_bp

__all__ = ['api_bp', 'skill_bp', 'task_bp', 'config_bp', 'scheduler_bp', 'file_retrieval_bp']

"""
服务模块初始化
"""
from .skill_engine import SkillEngine, skill_engine
from .ai_service import AIAssistantService, init_ai_service, ai_assistant_service

__all__ = [
    'SkillEngine',
    'skill_engine',
    'AIAssistantService',
    'init_ai_service',
    'ai_assistant_service'
]

"""
Skill 基类
定义所有 Skill 的通用接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseSkill(ABC):
    """Skill 基类"""
    
    def __init__(self, skill_id: str, name: str, description: str):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.version = "1.0.0"
        self.created_at = datetime.now()
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行 Skill
        
        Args:
            params: 输入参数字典
            
        Returns:
            执行结果字典，包含：
            - success: bool, 是否成功
            - data: Any, 返回数据
            - message: str, 消息
            - file_path: str, 生成的文件路径（如果有）
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证输入参数
        
        Args:
            params: 输入参数字典
            
        Returns:
            (is_valid, error_messages)
        """
        # 默认实现，子类可重写
        return True, []
    
    def get_info(self) -> Dict[str, Any]:
        """获取 Skill 信息"""
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'created_at': self.created_at.isoformat()
        }
    
    def log_execution(self, action: str, details: str):
        """记录执行日志"""
        logger.info(f"[{self.name}] {action}: {details}")
    
    def update_info(self, info: Dict[str, Any]):
        """
        更新技能信息
        
        Args:
            info: 包含要更新的信息的字典
        """
        if 'name' in info:
            self.name = info['name']
        if 'description' in info:
            self.description = info['description']
        if 'version' in info:
            self.version = info['version']

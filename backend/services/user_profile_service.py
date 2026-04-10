"""
用户画像与个性化服务
负责管理用户偏好、历史记录和个性化推荐
"""
import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class UserProfile:
    """用户画像类"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.preferences = {
            'default_doc_type': '通知',
            'sensitive_word_level': 'medium',  # low, medium, high
            'auto_save': True,
            'notification_enabled': True,
            'theme': 'light'
        }
        self.usage_stats = {
            'total_requests': 0,
            'skills_used': defaultdict(int),
            'favorite_skills': [],
            'last_active': None
        }
        self.history = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_preference(self, key: str, value: Any):
        """更新用户偏好"""
        if key in self.preferences:
            self.preferences[key] = value
            self.updated_at = datetime.now()
            logger.info(f"用户 {self.user_id} 更新偏好：{key} = {value}")
            return True
        return False
    
    def record_usage(self, skill_id: str, action: str, details: Dict[str, Any] = None):
        """记录使用行为"""
        self.usage_stats['total_requests'] += 1
        self.usage_stats['skills_used'][skill_id] += 1
        self.usage_stats['last_active'] = datetime.now()
        
        # 记录历史
        record = {
            'timestamp': datetime.now(),
            'skill_id': skill_id,
            'action': action,
            'details': details or {}
        }
        self.history.append(record)
        
        # 保留最近 500 条记录
        if len(self.history) > 500:
            self.history = self.history[-500:]
        
        # 更新常用技能
        self._update_favorite_skills()
        
        self.updated_at = datetime.now()
    
    def _update_favorite_skills(self):
        """更新常用技能列表"""
        sorted_skills = sorted(
            self.usage_stats['skills_used'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        self.usage_stats['favorite_skills'] = [skill_id for skill_id, _ in sorted_skills[:5]]
    
    def get_recommendations(self) -> List[str]:
        """获取个性化推荐技能"""
        # 基于使用频率推荐
        recommendations = self.usage_stats['favorite_skills'].copy()
        
        # 如果常用技能少于 3 个，添加默认推荐
        if len(recommendations) < 3:
            default_recommendations = ['doc_processor', 'sensitive_word_checker']
            for skill_id in default_recommendations:
                if skill_id not in recommendations:
                    recommendations.append(skill_id)
        
        return recommendations[:5]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'preferences': self.preferences,
            'usage_stats': {
                'total_requests': self.usage_stats['total_requests'],
                'skills_used': dict(self.usage_stats['skills_used']),
                'favorite_skills': self.usage_stats['favorite_skills'],
                'last_active': self.usage_stats['last_active'].isoformat() if self.usage_stats['last_active'] else None
            },
            'history': [
                {
                    'timestamp': h['timestamp'].isoformat(),
                    'skill_id': h['skill_id'],
                    'action': h['action'],
                    'details': h['details']
                }
                for h in self.history[-50:]  # 只返回最近 50 条
            ],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """从字典创建"""
        profile = cls(data['user_id'])
        profile.preferences.update(data.get('preferences', {}))
        profile.usage_stats['total_requests'] = data.get('usage_stats', {}).get('total_requests', 0)
        profile.usage_stats['favorite_skills'] = data.get('usage_stats', {}).get('favorite_skills', [])
        
        if data.get('usage_stats', {}).get('last_active'):
            profile.usage_stats['last_active'] = datetime.fromisoformat(
                data['usage_stats']['last_active']
            )
        
        profile.created_at = datetime.fromisoformat(data['created_at'])
        profile.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return profile


class UserProfileService:
    """用户画像服务"""
    
    def __init__(self, storage_path: str = 'backend/data/user_profiles'):
        self.storage_path = storage_path
        self.profiles: Dict[str, UserProfile] = {}
        self._ensure_storage_dir()
        self._load_profiles()
    
    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _load_profiles(self):
        """加载已保存的用户画像"""
        if not os.path.exists(self.storage_path):
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                user_id = filename[:-5]
                try:
                    with open(os.path.join(self.storage_path, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.profiles[user_id] = UserProfile.from_dict(data)
                except Exception as e:
                    logger.error(f"加载用户画像失败 {user_id}: {str(e)}")
        
        logger.info(f"已加载 {len(self.profiles)} 个用户画像")
    
    def get_profile(self, user_id: str) -> UserProfile:
        """获取用户画像"""
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(user_id)
        return self.profiles[user_id]
    
    def save_profile(self, user_id: str):
        """保存用户画像"""
        if user_id not in self.profiles:
            return False
        
        profile = self.profiles[user_id]
        filepath = os.path.join(self.storage_path, f"{user_id}.json")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"已保存用户画像：{user_id}")
            return True
        except Exception as e:
            logger.error(f"保存用户画像失败 {user_id}: {str(e)}")
            return False
    
    def update_preference(self, user_id: str, key: str, value: Any) -> bool:
        """更新用户偏好"""
        profile = self.get_profile(user_id)
        success = profile.update_preference(key, value)
        if success:
            self.save_profile(user_id)
        return success
    
    def record_usage(self, user_id: str, skill_id: str, action: str, 
                     details: Dict[str, Any] = None):
        """记录使用行为"""
        profile = self.get_profile(user_id)
        profile.record_usage(skill_id, action, details)
        
        # 每 10 次操作自动保存一次
        if profile.usage_stats['total_requests'] % 10 == 0:
            self.save_profile(user_id)
    
    def get_recommendations(self, user_id: str) -> List[str]:
        """获取个性化推荐"""
        profile = self.get_profile(user_id)
        return profile.get_recommendations()
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        profile = self.get_profile(user_id)
        return {
            'user_id': user_id,
            'total_requests': profile.usage_stats['total_requests'],
            'favorite_skills': profile.usage_stats['favorite_skills'],
            'last_active': profile.usage_stats['last_active'],
            'member_since': profile.created_at
        }
    
    def delete_profile(self, user_id: str) -> bool:
        """删除用户画像"""
        if user_id in self.profiles:
            del self.profiles[user_id]
        
        filepath = os.path.join(self.storage_path, f"{user_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"已删除用户画像：{user_id}")
            return True
        return False


# 全局用户画像服务实例
user_profile_service = UserProfileService()

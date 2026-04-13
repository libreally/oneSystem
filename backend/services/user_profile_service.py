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
            'theme': 'light',
            'preferred_output_format': 'docx',
            'preferred_analysis_style': 'summary',
            'preferred_reminder_time': '09:00',
            'work_hours_start': '09:00',
            'work_hours_end': '18:00'
        }
        self.usage_stats = {
            'total_requests': 0,
            'skills_used': defaultdict(int),
            'favorite_skills': [],
            'last_active': None,
            'request_times': defaultdict(int),  # 按时间段统计请求次数
            'document_types': defaultdict(int),  # 文档类型偏好
            'analysis_types': defaultdict(int)  # 分析类型偏好
        }
        self.history = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.personality_traits = {
            'communication_style': 'formal',  # formal, casual, technical
            'preferred_detail_level': 'medium',  # low, medium, high
            'task_urgency': 'balanced'  # urgent, balanced, relaxed
        }
    
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
        now = datetime.now()
        self.usage_stats['total_requests'] += 1
        self.usage_stats['skills_used'][skill_id] += 1
        self.usage_stats['last_active'] = now
        
        # 记录时间分布
        hour = now.hour
        time_slot = f'{hour:02d}:00'
        self.usage_stats['request_times'][time_slot] += 1
        
        # 记录文档类型偏好
        if details and 'doc_type' in details:
            self.usage_stats['document_types'][details['doc_type']] += 1
        
        # 记录分析类型偏好
        if details and 'analysis_type' in details:
            self.usage_stats['analysis_types'][details['analysis_type']] += 1
        
        # 记录历史
        record = {
            'timestamp': now,
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
        
        # 分析用户行为模式
        self._analyze_behavior_patterns()
        
        self.updated_at = now
    
    def _update_favorite_skills(self):
        """更新常用技能列表"""
        sorted_skills = sorted(
            self.usage_stats['skills_used'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        self.usage_stats['favorite_skills'] = [skill_id for skill_id, _ in sorted_skills[:5]]
    
    def _analyze_behavior_patterns(self):
        """分析用户行为模式"""
        # 分析沟通风格
        if self.usage_stats['total_requests'] > 10:
            # 基于技能使用情况分析沟通风格
            technical_skills = ['data_merger', 'analyzer']
            casual_skills = ['chat', 'assistant']
            
            technical_count = sum(self.usage_stats['skills_used'].get(skill, 0) for skill in technical_skills)
            casual_count = sum(self.usage_stats['skills_used'].get(skill, 0) for skill in casual_skills)
            
            if technical_count > casual_count * 2:
                self.personality_traits['communication_style'] = 'technical'
            elif casual_count > technical_count * 2:
                self.personality_traits['communication_style'] = 'casual'
            else:
                self.personality_traits['communication_style'] = 'formal'
        
        # 分析任务紧急性
        if self.usage_stats['total_requests'] > 5:
            # 基于时间分布分析任务紧急性
            evening_requests = sum(self.usage_stats['request_times'].get(f'{h:02d}:00', 0) for h in range(18, 24))
            morning_requests = sum(self.usage_stats['request_times'].get(f'{h:02d}:00', 0) for h in range(9, 12))
            
            if evening_requests > morning_requests * 1.5:
                self.personality_traits['task_urgency'] = 'urgent'
            elif morning_requests > evening_requests * 1.5:
                self.personality_traits['task_urgency'] = 'relaxed'
            else:
                self.personality_traits['task_urgency'] = 'balanced'
        
        # 分析偏好的详细程度
        if self.usage_stats['total_requests'] > 5:
            # 基于分析类型偏好分析详细程度
            detailed_analyses = ['detailed', 'comprehensive']
            summary_analyses = ['summary', 'overview']
            
            detailed_count = sum(self.usage_stats['analysis_types'].get(atype, 0) for atype in detailed_analyses)
            summary_count = sum(self.usage_stats['analysis_types'].get(atype, 0) for atype in summary_analyses)
            
            if detailed_count > summary_count * 1.5:
                self.personality_traits['preferred_detail_level'] = 'high'
            elif summary_count > detailed_count * 1.5:
                self.personality_traits['preferred_detail_level'] = 'low'
            else:
                self.personality_traits['preferred_detail_level'] = 'medium'
    
    def get_recommendations(self) -> List[str]:
        """获取个性化推荐技能"""
        # 基于使用频率推荐
        recommendations = self.usage_stats['favorite_skills'].copy()
        
        # 根据用户个性特征添加推荐
        if self.personality_traits['communication_style'] == 'technical':
            technical_skills = ['data_merger', 'analyzer']
            for skill in technical_skills:
                if skill not in recommendations:
                    recommendations.append(skill)
        elif self.personality_traits['communication_style'] == 'casual':
            casual_skills = ['chat', 'assistant']
            for skill in casual_skills:
                if skill not in recommendations:
                    recommendations.append(skill)
        
        # 根据任务紧急性添加推荐
        if self.personality_traits['task_urgency'] == 'urgent':
            urgent_skills = ['task_manager', 'reminder']
            for skill in urgent_skills:
                if skill not in recommendations:
                    recommendations.append(skill)
        
        # 根据详细程度偏好添加推荐
        if self.personality_traits['preferred_detail_level'] == 'high':
            detailed_skills = ['detailed_analyzer']
            for skill in detailed_skills:
                if skill not in recommendations:
                    recommendations.append(skill)
        elif self.personality_traits['preferred_detail_level'] == 'low':
            summary_skills = ['summary_generator']
            for skill in summary_skills:
                if skill not in recommendations:
                    recommendations.append(skill)
        
        # 如果常用技能少于 3 个，添加默认推荐
        if len(recommendations) < 3:
            default_recommendations = ['doc_processor', 'sensitive_word_checker', 'task_manager']
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
                'last_active': self.usage_stats['last_active'].isoformat() if self.usage_stats['last_active'] else None,
                'request_times': dict(self.usage_stats['request_times']),
                'document_types': dict(self.usage_stats['document_types']),
                'analysis_types': dict(self.usage_stats['analysis_types'])
            },
            'personality_traits': self.personality_traits,
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
        
        # 加载使用统计
        usage_stats = data.get('usage_stats', {})
        profile.usage_stats['total_requests'] = usage_stats.get('total_requests', 0)
        profile.usage_stats['favorite_skills'] = usage_stats.get('favorite_skills', [])
        profile.usage_stats['request_times'] = defaultdict(int, usage_stats.get('request_times', {}))
        profile.usage_stats['document_types'] = defaultdict(int, usage_stats.get('document_types', {}))
        profile.usage_stats['analysis_types'] = defaultdict(int, usage_stats.get('analysis_types', {}))
        
        if usage_stats.get('last_active'):
            profile.usage_stats['last_active'] = datetime.fromisoformat(
                usage_stats['last_active']
            )
        
        # 加载个性特征
        profile.personality_traits.update(data.get('personality_traits', {}))
        
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
    
    def get_personality_traits(self, user_id: str) -> Dict[str, Any]:
        """获取用户个性特征"""
        profile = self.get_profile(user_id)
        return profile.personality_traits
    
    def update_personality_traits(self, user_id: str, traits: Dict[str, Any]) -> bool:
        """更新用户个性特征"""
        profile = self.get_profile(user_id)
        profile.personality_traits.update(traits)
        profile.updated_at = datetime.now()
        return self.save_profile(user_id)
    
    def get_behavior_analysis(self, user_id: str) -> Dict[str, Any]:
        """获取用户行为分析报告"""
        profile = self.get_profile(user_id)
        
        # 分析使用模式
        usage_patterns = {
            'most_active_hour': None,
            'preferred_document_type': None,
            'preferred_analysis_type': None
        }
        
        # 找出最活跃的时间段
        if profile.usage_stats['request_times']:
            most_active = max(profile.usage_stats['request_times'].items(), key=lambda x: x[1])
            usage_patterns['most_active_hour'] = most_active[0]
        
        # 找出偏好的文档类型
        if profile.usage_stats['document_types']:
            preferred_doc = max(profile.usage_stats['document_types'].items(), key=lambda x: x[1])
            usage_patterns['preferred_document_type'] = preferred_doc[0]
        
        # 找出偏好的分析类型
        if profile.usage_stats['analysis_types']:
            preferred_analysis = max(profile.usage_stats['analysis_types'].items(), key=lambda x: x[1])
            usage_patterns['preferred_analysis_type'] = preferred_analysis[0]
        
        return {
            'user_id': user_id,
            'personality_traits': profile.personality_traits,
            'usage_patterns': usage_patterns,
            'statistics': self.get_user_statistics(user_id),
            'recommendations': profile.get_recommendations()
        }
    
    def get_time_based_recommendations(self, user_id: str) -> List[str]:
        """根据当前时间提供推荐"""
        profile = self.get_profile(user_id)
        current_hour = datetime.now().hour
        time_slot = f'{current_hour:02d}:00'
        
        # 基于时间的推荐
        time_based_recommendations = []
        
        # 早上（9-12点）
        if 9 <= current_hour < 12:
            time_based_recommendations = ['task_manager', 'email_processor']
        # 下午（14-17点）
        elif 14 <= current_hour < 17:
            time_based_recommendations = ['document_processor', 'data_analyzer']
        # 晚上（18-22点）
        elif 18 <= current_hour < 22:
            time_based_recommendations = ['report_generator', 'scheduler']
        
        # 合并基础推荐
        base_recommendations = profile.get_recommendations()
        for skill in time_based_recommendations:
            if skill not in base_recommendations:
                base_recommendations.append(skill)
        
        return base_recommendations[:5]


# 全局用户画像服务实例
user_profile_service = UserProfileService()

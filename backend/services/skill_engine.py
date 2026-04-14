"""
Skills 执行引擎
负责调度、执行和管理所有 Skills
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.skills.base_skill import BaseSkill
from backend.skills.document_skill import DocumentSkill
from backend.skills.sensitive_word_skill import SensitiveWordSkill
from backend.skills.data_merge_skill import DataMergeSkill
from backend.skills.scheduler_skill import SchedulerSkill

logger = logging.getLogger(__name__)


class SkillEngine:
    """Skills 执行引擎"""
    
    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self._register_builtin_skills()
    
    def _register_builtin_skills(self):
        """注册内置 Skills"""
        self.register_skill(DocumentSkill())
        self.register_skill(SensitiveWordSkill())
        self.register_skill(DataMergeSkill())
        self.register_skill(SchedulerSkill())
        logger.info(f"已注册 {len(self.skills)} 个内置 Skills")
    
    def register_skill(self, skill: BaseSkill):
        """注册一个 Skill"""
        self.skills[skill.skill_id] = skill
        logger.info(f"注册 Skill: {skill.name} ({skill.skill_id})")
    
    def unregister_skill(self, skill_id: str) -> bool:
        """注销一个 Skill"""
        if skill_id in self.skills:
            del self.skills[skill_id]
            logger.info(f"注销 Skill: {skill_id}")
            return True
        return False
    
    def get_skill(self, skill_id: str) -> Optional[BaseSkill]:
        """获取指定 Skill"""
        return self.skills.get(skill_id)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有可用 Skills"""
        return [skill.get_info() for skill in self.skills.values()]
    
    def execute_skill(self, skill_id: str, params: Dict[str, Any], 
                      user_id: str = None) -> Dict[str, Any]:
        """
        执行 Skill
        
        Args:
            skill_id: Skill ID
            params: 输入参数
            user_id: 用户 ID（可选）
            
        Returns:
            执行结果
        """
        if skill_id not in self.skills:
            return {
                'success': False,
                'message': f'Skill 不存在：{skill_id}'
            }
        
        skill = self.skills[skill_id]
        
        # 验证参数
        is_valid, errors = skill.validate_params(params)
        if not is_valid:
            return {
                'success': False,
                'message': '参数验证失败',
                'errors': errors
            }
        
        # 记录执行开始
        execution_record = {
            'execution_id': f"exec_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            'skill_id': skill_id,
            'skill_name': skill.name,
            'user_id': user_id,
            'params': params,
            'start_time': datetime.now(),
            'status': 'running'
        }
        
        try:
            # 执行 Skill
            logger.info(f"开始执行 Skill: {skill_id}, 参数：{params}")
            result = skill.execute(params)
            
            # 记录执行完成
            execution_record['end_time'] = datetime.now()
            execution_record['status'] = 'success' if result.get('success') else 'failed'
            execution_record['result'] = result
            
            self.execution_history.append(execution_record)
            
            # 保留最近 1000 条记录
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-1000:]
            
            logger.info(f"Skill 执行完成：{skill_id}, 状态：{execution_record['status']}")
            return result
            
        except Exception as e:
            logger.error(f"Skill 执行异常：{skill_id}, 错误：{str(e)}")
            execution_record['end_time'] = datetime.now()
            execution_record['status'] = 'error'
            execution_record['error'] = str(e)
            self.execution_history.append(execution_record)
            
            return {
                'success': False,
                'message': f'执行异常：{str(e)}'
            }
    
    def get_execution_history(self, skill_id: str = None, 
                              user_id: str = None,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """获取执行历史"""
        history = self.execution_history.copy()
        
        if skill_id:
            history = [h for h in history if h['skill_id'] == skill_id]
        if user_id:
            history = [h for h in history if h.get('user_id') == user_id]
        
        # 按时间倒序
        history.sort(key=lambda x: x['start_time'], reverse=True)
        
        return history[:limit]
    
    def get_skill_statistics(self) -> Dict[str, Any]:
        """获取 Skill 统计信息"""
        stats = {
            'total_skills': len(self.skills),
            'total_executions': len(self.execution_history),
            'skills': {}
        }
        
        for skill_id, skill in self.skills.items():
            executions = [h for h in self.execution_history if h['skill_id'] == skill_id]
            success_count = len([h for h in executions if h['status'] == 'success'])
            failed_count = len([h for h in executions if h['status'] in ['failed', 'error']])
            
            stats['skills'][skill_id] = {
                'name': skill.name,
                'total_executions': len(executions),
                'success_count': success_count,
                'failed_count': failed_count,
                'success_rate': success_count / len(executions) * 100 if executions else 0
            }
        
        return stats


# 全局 Skill 引擎实例
skill_engine = SkillEngine()

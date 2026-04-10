"""
AI 助手服务
负责理解用户意图、调度 Skills、生成执行逻辑
"""
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AIAssistantService:
    """AI 助手服务"""
    
    def __init__(self, skill_engine=None):
        self.skill_engine = skill_engine
        self.intent_patterns = self._build_intent_patterns()
        
    def _build_intent_patterns(self) -> Dict[str, List[re.Pattern]]:
        """构建意图识别模式"""
        patterns = {
            'document_convert': [
                re.compile(r'转\s*(成 | 为 | 换|到)'),
                re.compile(r'(把 | 将).*转换'),
                re.compile(r'生成.*公文'),
                re.compile(r'.*公文.*格式'),
                re.compile(r'.*转成.*公文'),
            ],
            'sensitive_word_check': [
                re.compile(r'检查.*敏感'),
                re.compile(r'检测.*敏感'),
                re.compile(r'查找.*违禁'),
                re.compile(r'敏感词'),
            ],
            'data_merge': [
                re.compile(r'合并.*(表格 | 文件 |excel| 数据)'),
                re.compile(r'比对.*(表格 | 文件 | 数据)'),
                re.compile(r'对比.*(表格 | 文件 | 数据)'),
                re.compile(r'合并.*excel', re.IGNORECASE),
                re.compile(r'合并.*表'),
            ],
            'report_generate': [
                re.compile(r'生成.*报告'),
                re.compile(r'生成.*总结'),
                re.compile(r'写.*周报'),
                re.compile(r'写.*月报'),
                re.compile(r'生成周报'),
                re.compile(r'生成月报'),
            ],
        }
        return patterns
    
    def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        分析用户意图
        
        Args:
            message: 用户输入消息
            
        Returns:
            意图分析结果
        """
        result = {
            'intent': 'unknown',
            'confidence': 0.0,
            'skill_id': None,
            'params': {},
            'missing_params': [],
            'suggestions': []
        }
        
        # 匹配意图
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    result['intent'] = intent
                    result['confidence'] = 0.8
                    break
            if result['intent'] != 'unknown':
                break
        
        # 根据意图映射到 Skill
        intent_to_skill = {
            'document_convert': 'doc_processor',
            'sensitive_word_check': 'sensitive_word_checker',
            'data_merge': 'data_merger',
            'report_generate': 'doc_processor'
        }
        
        if result['intent'] in intent_to_skill:
            result['skill_id'] = intent_to_skill[result['intent']]
        
        # 提取参数
        result['params'] = self._extract_params(message, result['intent'])
        
        # 检查缺失参数
        result['missing_params'] = self._check_missing_params(result['intent'], result['params'])
        
        # 生成建议
        if result['missing_params']:
            result['suggestions'] = self._generate_suggestions(result['intent'], result['missing_params'])
        
        return result
    
    def _extract_params(self, message: str, intent: str) -> Dict[str, Any]:
        """从消息中提取参数"""
        params = {}
        
        # 提取文件路径
        file_patterns = [
            r'(?:文件 | 文档)[:：]?\s*([^\s,，]+)',
            r'([^\s,，]+\.(?:docx?|xlsx?|csv|pdf|txt))',
        ]
        for pattern in file_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['file_path'] = match.group(1)
                break
        
        # 提取文档类型
        doc_type_patterns = [
            r'(通知 | 报告 | 请示 | 函 | 决定 | 公告)',
        ]
        for pattern in doc_type_patterns:
            match = re.search(pattern, message)
            if match:
                params['doc_type'] = match.group(1)
                break
        
        # 提取操作类型
        if '替换' in message or '替代' in message:
            params['action'] = 'replace'
        elif '标记' in message:
            params['action'] = 'mark'
        elif '合并' in message:
            params['action'] = 'merge_files'
        elif '比对' in message or '对比' in message:
            params['action'] = 'compare_files'
        elif '转换' in message or '转成' in message:
            params['action'] = 'convert_to_official'
        
        return params
    
    def _check_missing_params(self, intent: str, params: Dict[str, Any]) -> List[str]:
        """检查缺失的关键参数"""
        missing = []
        
        if intent == 'document_convert':
            if 'file_path' not in params and 'content' not in params:
                missing.append('file_path')
            if 'doc_type' not in params:
                missing.append('doc_type')
        
        elif intent == 'sensitive_word_check':
            if 'file_path' not in params and 'content' not in params:
                missing.append('file_path')
        
        elif intent == 'data_merge':
            if 'file_paths' not in params and 'file_path' not in params:
                missing.append('file_paths')
        
        return missing
    
    def _generate_suggestions(self, intent: str, missing_params: List[str]) -> List[str]:
        """生成参数补充建议"""
        suggestions = []
        
        param_prompts = {
            'file_path': '请提供需要处理的文件路径或上传文件',
            'file_paths': '请提供需要合并/比对的多个文件路径',
            'doc_type': '请指定公文类型（如：通知、报告、请示等）',
            'content': '请提供需要处理的文本内容',
            'output_path': '请指定输出文件路径（可选）',
        }
        
        for param in missing_params:
            if param in param_prompts:
                suggestions.append(param_prompts[param])
        
        return suggestions
    
    def process_message(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            message: 用户输入消息
            user_id: 用户 ID
            
        Returns:
            处理结果
        """
        logger.info(f"收到用户消息：{message}, 用户：{user_id}")
        
        # 分析意图
        intent_result = self.analyze_intent(message)
        
        # 如果有缺失参数，返回询问
        if intent_result['missing_params']:
            return {
                'success': True,
                'need_more_info': True,
                'intent': intent_result['intent'],
                'message': f"我需要更多信息才能完成任务。{'; '.join(intent_result['suggestions'])}",
                'suggestions': intent_result['suggestions']
            }
        
        # 如果没有匹配的 Skill，返回通用回复
        if not intent_result['skill_id']:
            return {
                'success': True,
                'need_more_info': False,
                'message': '抱歉，我暂时无法理解您的需求。您可以尝试：\n- 帮我转换公文\n- 检查敏感词\n- 合并 Excel 表格',
                'suggestions': [
                    '把这个文件转成标准公文',
                    '检查这篇材料的敏感词',
                    '合并这两个表'
                ]
            }
        
        # 执行 Skill
        if self.skill_engine:
            result = self.skill_engine.execute_skill(
                intent_result['skill_id'],
                intent_result['params'],
                user_id
            )
            
            return {
                'success': result.get('success', False),
                'need_more_info': False,
                'intent': intent_result['intent'],
                'skill_id': intent_result['skill_id'],
                'message': result.get('message', ''),
                'data': result.get('data'),
                'file_path': result.get('file_path')
            }
        else:
            return {
                'success': False,
                'need_more_info': False,
                'message': 'Skill 引擎未初始化'
            }
    
    def get_help_text(self) -> str:
        """获取帮助文本"""
        return """
我可以帮您完成以下任务：

📄 文档处理
  - 把文件转换成标准公文格式
  - 生成通知、报告、请示等公文
  - 调整文档格式

🔍 敏感词检查
  - 检查文档中的敏感词
  - 替换敏感词
  - 标记敏感词

📊 数据合并
  - 合并多个 Excel/CSV 文件
  - 比对两个数据表
  - 数据统计分析

💡 使用示例：
  - "把这个文件转成通知公文"
  - "检查这篇材料的敏感词"
  - "合并这两个 Excel 表格"
  - "找出两个表中不一样的数据"

请告诉我您需要什么帮助？
"""


# 全局 AI 助手服务实例
ai_assistant_service = None


def init_ai_service(skill_engine=None):
    """初始化 AI 助手服务"""
    global ai_assistant_service
    ai_assistant_service = AIAssistantService(skill_engine)
    return ai_assistant_service

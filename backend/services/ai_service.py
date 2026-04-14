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
        logger.info("开始构建意图识别模式")
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
        logger.info(f"意图识别模式构建完成，包含 {len(patterns)} 种意图类型")
        return patterns
    
    def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        分析用户意图
        
        Args:
            message: 用户输入消息
            
        Returns:
            意图分析结果
        """
        logger.info(f"开始分析用户意图: {message}")
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
                    logger.info(f"匹配到意图: {intent}, 置信度: 0.8")
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
            logger.info(f"意图映射到 Skill: {result['skill_id']}")
        
        # 提取参数
        result['params'] = self._extract_params(message, result['intent'])
        logger.info(f"提取到参数: {result['params']}")
        
        # 检查缺失参数
        result['missing_params'] = self._check_missing_params(result['intent'], result['params'])
        if result['missing_params']:
            logger.info(f"检测到缺失参数: {result['missing_params']}")
        
        # 生成建议
        if result['missing_params']:
            result['suggestions'] = self._generate_suggestions(result['intent'], result['missing_params'])
            logger.info(f"生成补充建议: {result['suggestions']}")
        
        logger.info(f"意图分析完成: {result}")
        return result
    
    def _extract_params(self, message: str, intent: str) -> Dict[str, Any]:
        """从消息中提取参数"""
        logger.info(f"开始提取参数，消息: {message}, 意图: {intent}")
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
                logger.info(f"提取到文件路径: {params['file_path']}")
                break
        
        # 提取文档类型
        doc_type_patterns = [
            r'(通知 | 报告 | 请示 | 函 | 决定 | 公告)',
        ]
        for pattern in doc_type_patterns:
            match = re.search(pattern, message)
            if match:
                params['doc_type'] = match.group(1)
                logger.info(f"提取到文档类型: {params['doc_type']}")
                break
        
        # 提取操作类型
        if '替换' in message or '替代' in message:
            params['action'] = 'replace'
            logger.info("提取到操作类型: replace")
        elif '标记' in message:
            params['action'] = 'mark'
            logger.info("提取到操作类型: mark")
        elif '合并' in message:
            params['action'] = 'merge_files'
            logger.info("提取到操作类型: merge_files")
        elif '比对' in message or '对比' in message:
            params['action'] = 'compare_files'
            logger.info("提取到操作类型: compare_files")
        elif '转换' in message or '转成' in message:
            params['action'] = 'convert_to_official'
            logger.info("提取到操作类型: convert_to_official")
        
        logger.info(f"参数提取完成: {params}")
        return params
    
    def _check_missing_params(self, intent: str, params: Dict[str, Any]) -> List[str]:
        """检查缺失的关键参数"""
        logger.info(f"开始检查缺失参数，意图: {intent}, 当前参数: {params}")
        missing = []
        
        if intent == 'document_convert':
            if 'file_path' not in params and 'content' not in params:
                missing.append('file_path')
                logger.info("缺少参数: file_path")
            if 'doc_type' not in params:
                missing.append('doc_type')
                logger.info("缺少参数: doc_type")
        
        elif intent == 'sensitive_word_check':
            if 'file_path' not in params and 'content' not in params:
                missing.append('file_path')
                logger.info("缺少参数: file_path")
        
        elif intent == 'data_merge':
            if 'file_paths' not in params and 'file_path' not in params:
                missing.append('file_paths')
                logger.info("缺少参数: file_paths")
        
        logger.info(f"缺失参数检查完成: {missing}")
        return missing
    
    def _generate_suggestions(self, intent: str, missing_params: List[str]) -> List[str]:
        """生成参数补充建议"""
        logger.info(f"开始生成补充建议，意图: {intent}, 缺失参数: {missing_params}")
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
                suggestion = param_prompts[param]
                suggestions.append(suggestion)
                logger.info(f"为参数 {param} 生成建议: {suggestion}")
        
        logger.info(f"补充建议生成完成: {suggestions}")
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
        logger.info(f"开始处理用户消息：{message}, 用户：{user_id}")
        
        # 从配置中心加载用户偏好配置
        from backend.services.config_service import config_service
        logger.info("加载用户偏好配置")
        user_preference = config_service.get_config('user_preference', 'default', user_id)
        logger.info(f"用户偏好配置加载完成：{user_preference}")
        
        # 分析意图
        logger.info("开始分析用户意图")
        intent_result = self.analyze_intent(message)
        logger.info(f"意图分析完成：{intent_result}")
        
        # 如果有缺失参数，返回询问
        if intent_result['missing_params']:
            logger.info(f"存在缺失参数：{intent_result['missing_params']}，返回补充信息请求")
            response = {
                'success': True,
                'need_more_info': True,
                'intent': intent_result['intent'],
                'message': f"我需要更多信息才能完成任务。{'; '.join(intent_result['suggestions'])}",
                'suggestions': intent_result['suggestions']
            }
            logger.info(f"返回补充信息请求：{response}")
            return response
        
        # 尝试使用 LLM 服务生成真实响应
        logger.info("尝试使用 LLM 服务生成响应")
        try:
            from backend.services.llm_service import get_llm_service
            llm_service = get_llm_service()
            
            if llm_service and llm_service.enabled:
                logger.info("LLM 服务已启用，准备调用模型")
                # 构建消息列表
                system_prompt = "你是一系统 AI 助手，一个专业的办公自动化助手，擅长处理文档、数据和任务管理。请根据用户的需求，提供专业、准确的回答。"
                
                # 应用用户偏好配置
                if user_preference and 'preferences' in user_preference:
                    preferences = user_preference['preferences']
                    if 'response_language' in preferences:
                        system_prompt += f"\n请使用{preferences['response_language']}回答。"
                        logger.info(f"应用语言偏好：{preferences['response_language']}")
                    if 'response_style' in preferences:
                        system_prompt += f"\n回答风格：{preferences['response_style']}。"
                        logger.info(f"应用风格偏好：{preferences['response_style']}")
                
                messages = [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
                
                # 调用 LLM 服务
                logger.info("调用 LLM 服务生成回复")
                llm_result = llm_service.chat_completion(messages, temperature=0.7, max_tokens=1000)
                logger.info(f"LLM 服务返回结果：{llm_result}")
                
                if llm_result.get('success'):
                    logger.info("LLM 服务生成回复成功")
                    response = {
                        'success': True,
                        'need_more_info': False,
                        'intent': intent_result['intent'],
                        'message': llm_result['response'],
                        'suggestions': []
                    }
                    logger.info(f"返回 LLM 生成的回复：{response}")
                    return response
        except Exception as e:
            logger.error(f"使用 LLM 服务失败：{str(e)}")
        
        # 如果没有匹配的 Skill，返回通用回复
        if not intent_result['skill_id']:
            logger.info("没有匹配的 Skill，返回通用回复")
            # 应用用户偏好配置
            default_message = '抱歉，我暂时无法理解您的需求。您可以尝试：\n- 帮我转换公文\n- 检查敏感词\n- 合并 Excel 表格'
            default_suggestions = [
                '把这个文件转成标准公文',
                '检查这篇材料的敏感词',
                '合并这两个表'
            ]
            
            if user_preference and 'preferences' in user_preference:
                preferences = user_preference['preferences']
                if 'default_suggestions' in preferences:
                    default_suggestions = preferences['default_suggestions']
                    logger.info(f"应用自定义建议：{default_suggestions}")
            
            response = {
                'success': True,
                'need_more_info': False,
                'message': default_message,
                'suggestions': default_suggestions
            }
            logger.info(f"返回通用回复：{response}")
            return response
        
        # 执行 Skill
        logger.info("准备执行 Skill")
        if self.skill_engine:
            logger.info(f"执行 Skill：{intent_result['skill_id']}，参数：{intent_result['params']}")
            result = self.skill_engine.execute_skill(
                intent_result['skill_id'],
                intent_result['params'],
                user_id
            )
            logger.info(f"Skill 执行结果：{result}")
            
            response = {
                'success': result.get('success', False),
                'need_more_info': False,
                'intent': intent_result['intent'],
                'skill_id': intent_result['skill_id'],
                'message': result.get('message', ''),
                'data': result.get('data'),
                'file_path': result.get('file_path')
            }
            logger.info(f"返回 Skill 执行结果：{response}")
            return response
        else:
            logger.error("Skill 引擎未初始化")
            response = {
                'success': False,
                'need_more_info': False,
                'message': 'Skill 引擎未初始化'
            }
            logger.info(f"返回错误响应：{response}")
            return response
    
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

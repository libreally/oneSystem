"""
LLM 服务层
支持基于大语言模型的智能技能生成、意图识别增强等功能
"""
import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI 库未安装，LLM 功能将受限")


class LLMService:
    """LLM 服务类"""
    
    def __init__(self, api_key: str = None, api_base: str = None, model: str = None):
        """
        初始化 LLM 服务
        
        Args:
            api_key: API Key
            api_base: API Base URL
            model: 模型名称
        """
        self.api_key = api_key or os.getenv('LLM_API_KEY', '')
        self.api_base = api_base or os.getenv('LLM_API_BASE', 'https://api.openai.com/v1')
        self.model = model or os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        self.enabled = bool(self.api_key) and OPENAI_AVAILABLE
        
        if self.enabled:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            logger.info(f"LLM 服务已初始化，模型：{self.model}")
        else:
            self.client = None
            logger.warning("LLM 服务未启用，请配置 LLM_API_KEY")
    
    def generate_skill_code(self, description: str, params: List[Dict] = None) -> Dict[str, Any]:
        """
        根据自然语言描述生成 Skill 代码
        
        Args:
            description: 技能描述（自然语言）
            params: 预期参数列表
            
        Returns:
            生成的技能代码和元数据
        """
        logger.info(f"开始生成技能代码，描述：{description[:100]}...")
        
        if not self.enabled:
            logger.info("LLM 服务未启用，使用模拟技能生成")
            result = self._generate_mock_skill(description, params)
            logger.info(f"模拟技能生成完成：{result.get('name', 'unknown')}")
            return result
        
        system_prompt = """你是一个专业的 Python 开发者，专门为一系统 AI 助手创建 Skills。
Skills 需要继承 BaseSkill 类，并实现以下方法：
- get_metadata(): 返回技能元数据（name, description, version, author, parameters）
- execute(params): 执行技能逻辑，返回结果字典

请确保：
1. 代码安全，不包含危险操作（如 os.system, eval 等）
2. 有完善的错误处理
3. 返回清晰的执行结果
4. 参数验证完整"""

        user_prompt = f"""请创建一个 Skill，需求描述如下：
{description}

预期参数：
{json.dumps(params, ensure_ascii=False) if params else '自动推断'}

请返回 JSON 格式的技能定义：
{{
    "name": "技能英文名称",
    "description": "技能描述",
    "version": "1.0.0",
    "author": "AI Assistant",
    "parameters": [
        {{"name": "param1", "type": "string", "required": true, "description": "参数描述"}}
    ],
    "code": "完整的 Python 代码字符串"
}}"""

        try:
            logger.info("调用 LLM 生成技能代码")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            logger.info("LLM 响应获取成功")
            
            # 尝试解析 JSON
            if content.startswith('```json'):
                content = content[7:-3].strip()
                logger.info("解析 JSON 格式响应")
            elif content.startswith('```'):
                content = content[3:-3].strip()
                logger.info("解析代码块格式响应")
            
            skill_definition = json.loads(content)
            logger.info(f"成功生成技能：{skill_definition.get('name', 'unknown')}")
            
            result = {
                'success': True,
                'skill_definition': skill_definition,
                'raw_response': content
            }
            logger.info("技能代码生成完成")
            return result
            
        except Exception as e:
            logger.error(f"生成技能代码失败：{str(e)}")
            fallback_result = self._generate_mock_skill(description, params)
            logger.info(f"使用模拟技能作为 fallback：{fallback_result.get('name', 'unknown')}")
            return {
                'success': False,
                'error': str(e),
                'fallback': fallback_result
            }
    
    def enhance_intent_recognition(self, message: str, context: List[Dict] = None) -> Dict[str, Any]:
        """
        使用 LLM 增强意图识别
        
        Args:
            message: 用户消息
            context: 对话上下文
            
        Returns:
            增强的意图识别结果
        """
        logger.info(f"开始增强意图识别，消息：{message[:100]}...")
        
        if not self.enabled:
            logger.info("LLM 服务未启用，使用模拟意图识别")
            result = self._mock_intent_recognition(message)
            logger.info(f"模拟意图识别结果：{result.get('intent', 'unknown')}")
            return result
        
        system_prompt = """你是一个智能意图识别助手。请分析用户消息，识别其意图。
支持的意图类型：
- document_convert: 文档转换（转成公文、格式调整等）
- sensitive_word_check: 敏感词检查
- data_merge: 数据合并/比对
- report_generate: 报告生成
- schedule_task: 定时任务设置
- file_search: 文件检索
- general_chat: 普通聊天

请返回 JSON 格式：
{
    "intent": "意图类型",
    "confidence": 0.9,
    "entities": {"entity_name": "value"},
    "missing_info": ["需要补充的信息"],
    "suggested_action": "建议的操作"
}"""

        context_str = ""
        if context:
            context_str = "对话上下文:\n" + "\n".join([
                f"{msg['role']}: {msg['content']}" for msg in context[-5:]
            ]) + "\n\n"
            logger.info(f"使用对话上下文，共 {len(context)} 条消息")
        
        user_prompt = f"{context_str}用户消息：{message}"
        
        try:
            logger.info("调用 LLM 增强意图识别")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            logger.info("LLM 响应获取成功")
            
            # 解析 JSON
            if content.startswith('```json'):
                content = content[7:-3].strip()
                logger.info("解析 JSON 格式响应")
            elif content.startswith('```'):
                content = content[3:-3].strip()
                logger.info("解析代码块格式响应")
            
            intent_result = json.loads(content)
            logger.info(f"增强意图识别结果：{intent_result.get('intent', 'unknown')}")
            
            result = {
                'success': True,
                'intent_result': intent_result,
                'enhanced': True
            }
            logger.info("意图识别增强完成")
            return result
            
        except Exception as e:
            logger.error(f"意图识别增强失败：{str(e)}")
            fallback_result = self._mock_intent_recognition(message)
            logger.info(f"使用模拟意图识别作为 fallback：{fallback_result.get('intent', 'unknown')}")
            return {
                'success': False,
                'error': str(e),
                'fallback': fallback_result
            }
    
    def generate_code_explanation(self, code: str) -> str:
        """
        生成代码解释
        
        Args:
            code: 代码字符串
            
        Returns:
            代码解释
        """
        if not self.enabled:
            return "代码解释功能需要配置 LLM API Key"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "请用简洁的中文解释这段代码的功能。"},
                    {"role": "user", "content": code}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"代码解释生成失败：{str(e)}")
            return f"生成解释失败：{str(e)}"
    
    def _generate_mock_skill(self, description: str, params: List[Dict] = None) -> Dict[str, Any]:
        """生成模拟技能（当 LLM 不可用时）"""
        skill_name = f"custom_skill_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        mock_code = f'''
from backend.skills.base_skill import BaseSkill
from typing import Dict, Any

class {skill_name.title().replace('_', '')}(BaseSkill):
    """自动生成的技能 - {description[:50]}"""
    
    def get_metadata(self) -> Dict[str, Any]:
        return {{
            'name': '{skill_name}',
            'description': '{description}',
            'version': '1.0.0',
            'author': 'AI Assistant (Mock)',
            'parameters': [
                {{'name': 'input_data', 'type': 'string', 'required': True, 'description': '输入数据'}}
            ]
        }}
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能"""
        try:
            input_data = params.get('input_data', '')
            
            # TODO: 根据实际需求实现具体逻辑
            result = {{
                'success': True,
                'message': f'技能{{self.get_metadata()["name"]}}执行完成',
                'data': {{'processed': input_data}}
            }}
            
            return result
            
        except Exception as e:
            return {{
                'success': False,
                'error': str(e),
                'message': '技能执行失败'
            }}
'''
        
        return {
            'name': skill_name,
            'description': description,
            'version': '1.0.0',
            'author': 'AI Assistant (Mock)',
            'parameters': [{'name': 'input_data', 'type': 'string', 'required': True, 'description': '输入数据'}],
            'code': mock_code
        }
    
    def _mock_intent_recognition(self, message: str) -> Dict[str, Any]:
        """模拟意图识别（当 LLM 不可用时）"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['转换', '转成', 'format', 'convert']):
            intent = 'document_convert'
            confidence = 0.6
        elif any(word in message_lower for word in ['敏感词', '检查', 'detect']):
            intent = 'sensitive_word_check'
            confidence = 0.6
        elif any(word in message_lower for word in ['合并', 'merge', 'combine']):
            intent = 'data_merge'
            confidence = 0.6
        elif any(word in message_lower for word in ['报告', '总结', 'report']):
            intent = 'report_generate'
            confidence = 0.6
        else:
            intent = 'general_chat'
            confidence = 0.5
        
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': {},
            'missing_info': [],
            'suggested_action': 'process_with_rules'
        }
    
    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        通用聊天补全接口
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数（temperature, max_tokens 等）
            
        Returns:
            响应结果
        """
        logger.info(f"开始聊天补全，消息数量：{len(messages)}")
        
        if not self.enabled:
            logger.info("LLM 服务未启用，返回默认响应")
            return {
                'success': False,
                'error': 'LLM 服务未启用',
                'response': '抱歉，智能服务暂未启用。我正在学习更多技能来帮助您。'
            }
        
        try:
            # 设置默认超时时间为300秒
            timeout = kwargs.pop('timeout', 300)
            logger.info(f"调用 LLM 模型：{self.model}，超时设置：{timeout}秒")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=timeout,
                **kwargs
            )
            
            result = {
                'success': True,
                'response': response.choices[0].message.content,
                'usage': response.usage.model_dump() if hasattr(response.usage, 'model_dump') else vars(response.usage)
            }
            logger.info(f"聊天补全成功，响应长度：{len(result['response'])} 字符")
            return result
            
        except Exception as e:
            logger.error(f"聊天补全失败：{str(e)}")
            error_response = {
                'success': False,
                'error': str(e),
                'response': '抱歉，处理您的请求时遇到错误。'
            }
            logger.info(f"返回错误响应：{error_response}")
            return error_response


# 全局 LLM 服务实例
llm_service = None


def init_llm_service(api_key: str = None, api_base: str = None, model: str = None) -> LLMService:
    """初始化 LLM 服务"""
    global llm_service
    llm_service = LLMService(api_key, api_base, model)
    return llm_service


def get_llm_service() -> Optional[LLMService]:
    """获取 LLM 服务实例"""
    return llm_service

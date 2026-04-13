"""
Skill 动态生成服务
支持根据需求描述生成 skill 模板、执行逻辑等
"""
import os
import json
import logging
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.services.llm_service import llm_service
from backend.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class SkillGeneratorService:
    """Skill 动态生成服务"""
    
    def __init__(self):
        """初始化 Skill 生成服务"""
        self.skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'skills')
        self.skill_templates_dir = os.path.join(self.skills_dir, 'templates')
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保目录存在"""
        os.makedirs(self.skill_templates_dir, exist_ok=True)
    
    def generate_skill_from_description(self, description: str, user_id: str = None) -> Dict[str, Any]:
        """
        根据需求描述生成 skill
        
        Args:
            description: 需求描述
            user_id: 用户 ID
            
        Returns:
            生成的 skill 信息
        """
        try:
            # 1. 分析需求，生成 skill 定义
            skill_definition = self._generate_skill_definition(description)
            
            # 2. 生成执行逻辑
            execution_logic = self._generate_execution_logic(description, skill_definition)
            
            # 3. 生成 skill 代码
            skill_code = self._generate_skill_code(skill_definition, execution_logic)
            
            # 4. 保存 skill 模板
            skill_info = self._save_skill_template(skill_definition, skill_code, user_id)
            
            return {
                'success': True,
                'skill_info': skill_info,
                'message': 'Skill 生成成功'
            }
            
        except Exception as e:
            logger.error(f"生成 Skill 失败: {str(e)}")
            return {
                'success': False,
                'message': f'生成 Skill 失败: {str(e)}'
            }
    
    def _generate_skill_definition(self, description: str) -> Dict[str, Any]:
        """
        生成 skill 定义
        
        Args:
            description: 需求描述
            
        Returns:
            skill 定义
        """
        prompt = f"""
请根据以下需求描述，生成一个完整的 skill 定义：

需求描述：{description}

技能定义应包含以下字段：
- skill_name: 技能名称（简洁明了）
- description: 技能描述
- input_parameters: 输入参数列表（包含参数名、类型、描述、是否必填）
- output_parameters: 输出参数列表（包含参数名、类型、描述）
- category: 技能分类
- version: 版本号
- author: 作者
- dependencies: 依赖项
- example_usage: 使用示例

请以 JSON 格式返回，确保格式正确。
        """
        
        response = llm_service.generate_content(prompt)
        skill_definition = json.loads(response)
        
        # 确保必要字段存在
        skill_definition.setdefault('skill_name', f'skill_{datetime.now().strftime("%Y%m%d%H%M%S")}')
        skill_definition.setdefault('description', description)
        skill_definition.setdefault('input_parameters', [])
        skill_definition.setdefault('output_parameters', [])
        skill_definition.setdefault('category', 'general')
        skill_definition.setdefault('version', '1.0.0')
        skill_definition.setdefault('author', 'AI Generated')
        skill_definition.setdefault('dependencies', [])
        skill_definition.setdefault('example_usage', '')
        
        return skill_definition
    
    def _generate_execution_logic(self, description: str, skill_definition: Dict[str, Any]) -> str:
        """
        生成执行逻辑
        
        Args:
            description: 需求描述
            skill_definition: skill 定义
            
        Returns:
            执行逻辑代码
        """
        prompt = f"""
请根据以下需求描述和技能定义，生成执行逻辑代码：

需求描述：{description}

技能定义：
{json.dumps(skill_definition, ensure_ascii=False, indent=2)}

执行逻辑要求：
1. 代码应是 Python 函数形式，函数名为 `execute`
2. 函数接收 input_data 参数，返回 dict 格式的结果
3. 包含必要的错误处理
4. 代码应符合 Python 最佳实践
5. 不要包含类定义，只提供执行逻辑函数

请只返回代码部分，不要包含其他解释性内容。
        """
        
        response = llm_service.generate_content(prompt)
        return response
    
    def _generate_skill_code(self, skill_definition: Dict[str, Any], execution_logic: str) -> str:
        """
        生成完整的 skill 代码
        
        Args:
            skill_definition: skill 定义
            execution_logic: 执行逻辑
            
        Returns:
            完整的 skill 代码
        """
        template = '''
from typing import Dict, Any, List
from backend.skills.base_skill import BaseSkill


class ''' + skill_definition['skill_name'].title().replace('_', '') + '''Skill(BaseSkill):
    ''' + skill_definition['skill_name'] + ''' 技能
    
    def __init__(self):
        初始化技能
        super().__init__()
        self.skill_name = "''' + skill_definition['skill_name'] + '''"
        self.description = "''' + skill_definition['description'] + '''"
        self.category = "''' + skill_definition['category'] + '''"
        self.version = "''' + skill_definition['version'] + '''"
        self.author = "''' + skill_definition['author'] + '''"
        self.dependencies = ''' + str(skill_definition['dependencies']) + '''
    
    def get_input_parameters(self) -> List[Dict[str, Any]]:
        获取输入参数
        return ''' + str(skill_definition['input_parameters']) + '''
    
    def get_output_parameters(self) -> List[Dict[str, Any]]:
        获取输出参数
        return ''' + str(skill_definition['output_parameters']) + '''
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        执行技能
        try:
            # 验证输入参数
            self.validate_input(input_data)
            
            ''' + execution_logic + '''
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'message': f'执行失败: {str(e)}'
            }
'''


    
        return template
    
    def _save_skill_template(self, skill_definition: Dict[str, Any], skill_code: str, user_id: str = None) -> Dict[str, Any]:
        """
        保存 skill 模板
        
        Args:
            skill_definition: skill 定义
            skill_code: skill 代码
            user_id: 用户 ID
            
        Returns:
            skill 信息
        """
        skill_name = skill_definition['skill_name']
        file_name = f"{skill_name}.py"
        
        # 保存到模板目录
        template_path = os.path.join(self.skill_templates_dir, file_name)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(skill_code)
        
        # 保存 skill 元数据
        metadata = {
            'skill_name': skill_name,
            'description': skill_definition['description'],
            'category': skill_definition['category'],
            'version': skill_definition['version'],
            'author': skill_definition['author'],
            'created_at': datetime.now().isoformat(),
            'created_by': user_id or 'system',
            'template_path': template_path,
            'status': 'draft'  # draft, testing, approved, published, disabled
        }
        
        metadata_path = os.path.join(self.skill_templates_dir, f"{skill_name}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return metadata
    
    def list_skill_templates(self) -> List[Dict[str, Any]]:
        """
        列出所有 skill 模板
        
        Returns:
            skill 模板列表
        """
        templates = []
        
        for file in os.listdir(self.skill_templates_dir):
            if file.endswith('_metadata.json'):
                metadata_path = os.path.join(self.skill_templates_dir, file)
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        templates.append(metadata)
                except Exception as e:
                    logger.error(f"读取 skill 模板元数据失败: {str(e)}")
        
        return templates
    
    def get_skill_template(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定 skill 模板
        
        Args:
            skill_name: skill 名称
            
        Returns:
            skill 模板信息
        """
        metadata_path = os.path.join(self.skill_templates_dir, f"{skill_name}_metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                return metadata
            except Exception as e:
                logger.error(f"读取 skill 模板失败: {str(e)}")
        return None
    
    def update_skill_status(self, skill_name: str, status: str) -> bool:
        """
        更新 skill 状态
        
        Args:
            skill_name: skill 名称
            status: 状态 (draft, testing, approved, published, disabled)
            
        Returns:
            是否成功
        """
        metadata_path = os.path.join(self.skill_templates_dir, f"{skill_name}_metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata['status'] = status
                metadata['updated_at'] = datetime.now().isoformat()
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                return True
            except Exception as e:
                logger.error(f"更新 skill 状态失败: {str(e)}")
        return False
    
    def test_skill(self, skill_name: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试 skill
        
        Args:
            skill_name: skill 名称
            test_data: 测试数据
            
        Returns:
            测试结果
        """
        try:
            # 动态导入 skill
            import importlib.util
            
            template_path = os.path.join(self.skill_templates_dir, f"{skill_name}.py")
            if not os.path.exists(template_path):
                return {'success': False, 'message': 'Skill 模板不存在'}
            
            # 加载模块
            spec = importlib.util.spec_from_file_location(skill_name, template_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 实例化 skill
            skill_class = getattr(module, f"{skill_name.title().replace('_', '')}Skill")
            skill = skill_class()
            
            # 执行测试
            result = skill.execute(test_data)
            
            # 更新状态为测试中
            self.update_skill_status(skill_name, 'testing')
            
            return {
                'success': True,
                'result': result,
                'message': 'Skill 测试成功'
            }
            
        except Exception as e:
            logger.error(f"测试 Skill 失败: {str(e)}")
            return {
                'success': False,
                'message': f'测试 Skill 失败: {str(e)}'
            }
    
    def publish_skill(self, skill_name: str) -> bool:
        """
        发布 skill
        
        Args:
            skill_name: skill 名称
            
        Returns:
            是否成功
        """
        try:
            # 复制到正式 skills 目录
            template_path = os.path.join(self.skill_templates_dir, f"{skill_name}.py")
            target_path = os.path.join(self.skills_dir, f"{skill_name}.py")
            
            if not os.path.exists(template_path):
                return False
            
            # 读取模板内容
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 写入正式目录
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新状态为已发布
            self.update_skill_status(skill_name, 'published')
            
            logger.info(f"Skill 已发布: {skill_name}")
            return True
            
        except Exception as e:
            logger.error(f"发布 Skill 失败: {str(e)}")
            return False


# 全局 Skill 生成服务实例
skill_generator_service = SkillGeneratorService()


def init_skill_generator_service() -> SkillGeneratorService:
    """初始化 Skill 生成服务"""
    global skill_generator_service
    return skill_generator_service

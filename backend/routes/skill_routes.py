"""
Skills 管理路由
支持动态技能生成和注册
"""
from flask import Blueprint, jsonify, request
from backend.skills import DocumentSkill, SensitiveWordSkill, DataMergeSkill
from backend.services.llm_service import get_llm_service, init_llm_service
import logging
import importlib.util
import sys
import os

logger = logging.getLogger(__name__)

skill_bp = Blueprint('skills', __name__, url_prefix='/api/skills')

# 初始化可用 Skills
available_skills = {
    'doc_processor': DocumentSkill(),
    'sensitive_word_checker': SensitiveWordSkill(),
    'data_merger': DataMergeSkill()
}

# 动态生成的技能存储
dynamic_skills = {}


@skill_bp.route('', methods=['GET'])
def list_skills():
    """获取所有可用 Skills"""
    skills_info = []
    
    # 内置技能
    for skill_id, skill in available_skills.items():
        info = skill.get_info()
        info['category'] = get_skill_category(skill_id)
        info['is_dynamic'] = False
        skills_info.append(info)
    
    # 动态技能
    for skill_id, skill_info in dynamic_skills.items():
        info = skill_info.copy()
        info['is_dynamic'] = True
        skills_info.append(info)
    
    return jsonify({
        'success': True,
        'data': skills_info
    })


@skill_bp.route('/<skill_id>', methods=['GET'])
def get_skill_info(skill_id):
    """获取指定 Skill 信息"""
    if skill_id in available_skills:
        skill = available_skills[skill_id]
        info = skill.get_info()
        info['category'] = get_skill_category(skill_id)
        info['is_dynamic'] = False
        
        return jsonify({
            'success': True,
            'data': info
        })
    elif skill_id in dynamic_skills:
        info = dynamic_skills[skill_id].copy()
        info['is_dynamic'] = True
        
        return jsonify({
            'success': True,
            'data': info
        })
    else:
        return jsonify({
            'success': False,
            'message': f'Skill 不存在：{skill_id}'
        }), 404


@skill_bp.route('/<skill_id>/execute', methods=['POST'])
def execute_skill(skill_id):
    """执行 Skill"""
    skill = None
    
    if skill_id in available_skills:
        skill = available_skills[skill_id]
    elif skill_id in dynamic_skills:
        # 动态技能需要加载执行
        skill_data = dynamic_skills[skill_id]
        if 'class_instance' in skill_data:
            skill = skill_data['class_instance']
        else:
            # 尝试从代码创建实例
            try:
                skill_class = load_dynamic_skill_class(skill_id, skill_data.get('code', ''))
                skill = skill_class()
                skill_data['class_instance'] = skill
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'动态技能加载失败：{str(e)}'
                }), 500
    else:
        return jsonify({
            'success': False,
            'message': f'Skill 不存在：{skill_id}'
        }), 404
    
    data = request.get_json()
    params = data.get('params', {})
    
    # 验证参数
    is_valid, errors = skill.validate_params(params)
    if not is_valid:
        return jsonify({
            'success': False,
            'message': '参数验证失败',
            'errors': errors
        }), 400
    
    # 执行 Skill
    result = skill.execute(params)
    
    return jsonify(result)


@skill_bp.route('/generate', methods=['POST'])
def generate_skill():
    """使用 LLM 生成新技能"""
    data = request.get_json()
    description = data.get('description', '')
    params = data.get('parameters', [])
    
    if not description:
        return jsonify({
            'success': False,
            'message': '请提供技能描述'
        }), 400
    
    # 确保 LLM 服务已初始化
    llm_service = get_llm_service()
    if not llm_service:
        from backend.config.settings import LLM_API_KEY, LLM_API_BASE, LLM_MODEL
        init_llm_service(
            api_key=LLM_API_KEY,
            api_base=LLM_API_BASE,
            model=LLM_MODEL
        )
        llm_service = get_llm_service()
    
    # 调用 LLM 生成技能代码
    result = llm_service.generate_skill_code(description, params)
    
    if result.get('success'):
        skill_def = result.get('skill_definition', result.get('fallback', {}))
        
        # 生成唯一 skill_id
        skill_id = skill_def.get('name', f"custom_{len(dynamic_skills) + 1}")
        
        # 保存动态技能
        dynamic_skills[skill_id] = {
            'name': skill_def.get('name', skill_id),
            'description': skill_def.get('description', ''),
            'version': skill_def.get('version', '1.0.0'),
            'author': skill_def.get('author', 'AI Assistant'),
            'parameters': skill_def.get('parameters', []),
            'code': skill_def.get('code', ''),
            'created_at': __import__('datetime').datetime.now().isoformat()
        }
        
        logger.info(f"成功生成动态技能：{skill_id}")
        
        return jsonify({
            'success': True,
            'message': f'技能 {skill_id} 生成成功',
            'data': {
                'skill_id': skill_id,
                'name': skill_def.get('name'),
                'description': skill_def.get('description'),
                'parameters': skill_def.get('parameters', [])
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': f'技能生成失败：{result.get("error", "未知错误")}'
        }), 500


@skill_bp.route('/register', methods=['POST'])
def register_skill():
    """注册新 Skill（手动或动态）"""
    data = request.get_json()
    skill_id = data.get('skill_id')
    skill_name = data.get('name', skill_id)
    description = data.get('description', '')
    parameters = data.get('parameters', [])
    code = data.get('code', '')
    
    if not skill_id:
        return jsonify({
            'success': False,
            'message': '缺少 skill_id'
        }), 400
    
    # 保存到动态技能库
    dynamic_skills[skill_id] = {
        'skill_id': skill_id,
        'name': skill_name,
        'description': description,
        'parameters': parameters,
        'code': code,
        'registered_at': __import__('datetime').datetime.now().isoformat()
    }
    
    logger.info(f"成功注册技能：{skill_id}")
    
    return jsonify({
        'success': True,
        'message': f'Skill {skill_id} 注册成功',
        'data': {
            'skill_id': skill_id,
            'name': skill_name
        }
    })


@skill_bp.route('/<skill_id>', methods=['PUT'])
def update_skill(skill_id):
    """更新动态技能"""
    if skill_id in available_skills:
        return jsonify({
            'success': False,
            'message': '不能更新内置技能'
        }), 400
    
    if skill_id not in dynamic_skills:
        return jsonify({
            'success': False,
            'message': f'Skill 不存在：{skill_id}'
        }), 404
    
    data = request.get_json()
    skill_name = data.get('name', dynamic_skills[skill_id].get('name'))
    description = data.get('description', dynamic_skills[skill_id].get('description'))
    category = data.get('category', dynamic_skills[skill_id].get('category'))
    version = data.get('version', dynamic_skills[skill_id].get('version'))
    code = data.get('code', dynamic_skills[skill_id].get('code'))
    parameters = data.get('parameters', dynamic_skills[skill_id].get('parameters', []))
    
    # 更新动态技能
    dynamic_skills[skill_id].update({
        'name': skill_name,
        'description': description,
        'category': category,
        'version': version,
        'code': code,
        'parameters': parameters,
        'updated_at': __import__('datetime').datetime.now().isoformat()
    })
    
    logger.info(f"成功更新技能：{skill_id}")
    
    return jsonify({
        'success': True,
        'message': f'Skill {skill_id} 更新成功',
        'data': dynamic_skills[skill_id]
    })


@skill_bp.route('/<skill_id>', methods=['DELETE'])
def delete_skill(skill_id):
    """删除动态技能"""
    if skill_id in available_skills:
        return jsonify({
            'success': False,
            'message': '不能删除内置技能'
        }), 400
    
    if skill_id in dynamic_skills:
        del dynamic_skills[skill_id]
        logger.info(f"已删除动态技能：{skill_id}")
        
        return jsonify({
            'success': True,
            'message': f'Skill {skill_id} 已删除'
        })
    else:
        return jsonify({
            'success': False,
            'message': f'Skill 不存在：{skill_id}'
        }), 404


def load_dynamic_skill_class(skill_id: str, code: str):
    """从代码字符串加载动态技能类"""
    # 安全检查：过滤危险操作
    dangerous_patterns = ['os.system', 'subprocess', 'eval(', 'exec(', '__import__', 'open(']
    for pattern in dangerous_patterns:
        if pattern in code:
            raise ValueError(f"代码包含危险操作：{pattern}")
    
    # 创建临时模块
    module_name = f"dynamic_skill_{skill_id}"
    spec = importlib.util.spec_from_loader(
        module_name,
        loader=importlib.util.SourcelessFileLoader(module_name, '')
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    
    # 执行代码
    exec(code, module.__dict__)
    
    # 查找技能类（假设类名是 skill_id 的驼峰命名）
    class_name = skill_id.title().replace('_', '')
    if hasattr(module, class_name):
        return getattr(module, class_name)
    else:
        # 尝试查找继承 BaseSkill 的类
        from backend.skills.base_skill import BaseSkill
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, BaseSkill) and obj != BaseSkill:
                return obj
        
        raise ValueError(f"未找到技能类：{class_name}")


def get_skill_category(skill_id: str) -> str:
    """获取 Skill 分类"""
    categories = {
        'doc_processor': '文档处理',
        'sensitive_word_checker': '敏感词检查',
        'data_merger': '数据合并'
    }
    return categories.get(skill_id, '其他')

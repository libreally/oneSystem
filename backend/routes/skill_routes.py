"""
Skills 管理路由
"""
from flask import Blueprint, jsonify, request
from backend.skills import DocumentSkill, SensitiveWordSkill, DataMergeSkill

skill_bp = Blueprint('skills', __name__, url_prefix='/api/skills')

# 初始化可用 Skills
available_skills = {
    'doc_processor': DocumentSkill(),
    'sensitive_word_checker': SensitiveWordSkill(),
    'data_merger': DataMergeSkill()
}


@skill_bp.route('', methods=['GET'])
def list_skills():
    """获取所有可用 Skills"""
    skills_info = []
    for skill_id, skill in available_skills.items():
        info = skill.get_info()
        info['category'] = get_skill_category(skill_id)
        skills_info.append(info)
    
    return jsonify({
        'success': True,
        'data': skills_info
    })


@skill_bp.route('/<skill_id>', methods=['GET'])
def get_skill_info(skill_id):
    """获取指定 Skill 信息"""
    if skill_id not in available_skills:
        return jsonify({
            'success': False,
            'message': f'Skill 不存在：{skill_id}'
        }), 404
    
    skill = available_skills[skill_id]
    info = skill.get_info()
    info['category'] = get_skill_category(skill_id)
    
    return jsonify({
        'success': True,
        'data': info
    })


@skill_bp.route('/<skill_id>/execute', methods=['POST'])
def execute_skill(skill_id):
    """执行 Skill"""
    if skill_id not in available_skills:
        return jsonify({
            'success': False,
            'message': f'Skill 不存在：{skill_id}'
        }), 404
    
    data = request.get_json()
    params = data.get('params', {})
    
    skill = available_skills[skill_id]
    
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


@skill_bp.route('/register', methods=['POST'])
def register_skill():
    """注册新 Skill"""
    data = request.get_json()
    skill_id = data.get('skill_id')
    
    if not skill_id:
        return jsonify({
            'success': False,
            'message': '缺少 skill_id'
        }), 400
    
    # TODO: 实现动态 Skill 注册逻辑
    # 这里可以支持从文件加载或动态生成 Skill
    
    return jsonify({
        'success': True,
        'message': f'Skill {skill_id} 注册成功（功能开发中）'
    })


def get_skill_category(skill_id: str) -> str:
    """获取 Skill 分类"""
    categories = {
        'doc_processor': '文档处理',
        'sensitive_word_checker': '敏感词检查',
        'data_merger': '数据合并'
    }
    return categories.get(skill_id, '其他')

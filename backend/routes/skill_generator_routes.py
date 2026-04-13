"""
Skill 动态生成路由
支持 Skill 生成、测试、发布等 API 端点
"""
from flask import Blueprint, jsonify, request
from backend.services.skill_generator_service import skill_generator_service

skill_generator_bp = Blueprint('skill_generator', __name__, url_prefix='/api/skill-generator')


@skill_generator_bp.route('/generate', methods=['POST'])
def generate_skill():
    """
    根据需求描述生成 Skill
    """
    data = request.get_json()
    description = data.get('description')
    user_id = data.get('user_id')
    
    if not description:
        return jsonify({
            'success': False,
            'message': '缺少需求描述'
        }), 400
    
    result = skill_generator_service.generate_skill_from_description(description, user_id)
    return jsonify(result)


@skill_generator_bp.route('/templates', methods=['GET'])
def list_skill_templates():
    """
    列出所有 Skill 模板
    """
    templates = skill_generator_service.list_skill_templates()
    return jsonify({
        'success': True,
        'data': templates
    })


@skill_generator_bp.route('/templates/<skill_name>', methods=['GET'])
def get_skill_template(skill_name):
    """
    获取指定 Skill 模板
    """
    template = skill_generator_service.get_skill_template(skill_name)
    if template:
        return jsonify({
            'success': True,
            'data': template
        })
    else:
        return jsonify({
            'success': False,
            'message': f'Skill 模板不存在: {skill_name}'
        }), 404


@skill_generator_bp.route('/templates/<skill_name>/status', methods=['PUT'])
def update_skill_status(skill_name):
    """
    更新 Skill 状态
    """
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({
            'success': False,
            'message': '缺少状态参数'
        }), 400
    
    success = skill_generator_service.update_skill_status(skill_name, status)
    if success:
        return jsonify({
            'success': True,
            'message': 'Skill 状态已更新'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Skill 状态更新失败'
        }), 500


@skill_generator_bp.route('/templates/<skill_name>/test', methods=['POST'])
def test_skill(skill_name):
    """
    测试 Skill
    """
    data = request.get_json()
    test_data = data.get('test_data', {})
    
    result = skill_generator_service.test_skill(skill_name, test_data)
    return jsonify(result)


@skill_generator_bp.route('/templates/<skill_name>/publish', methods=['POST'])
def publish_skill(skill_name):
    """
    发布 Skill
    """
    success = skill_generator_service.publish_skill(skill_name)
    if success:
        return jsonify({
            'success': True,
            'message': 'Skill 发布成功'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Skill 发布失败'
        }), 500

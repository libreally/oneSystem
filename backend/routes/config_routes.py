"""
配置中心路由
"""
from flask import Blueprint, jsonify, request
from datetime import datetime

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

# 模拟配置数据
mock_configs = {
    'templates': [
        {
            'config_id': 'tpl_001',
            'config_type': 'template',
            'key': 'official_notice',
            'value': {'doc_type': '通知', 'font': '仿宋', 'font_size': 16},
            'scope': 'public',
            'description': '标准通知模板'
        }
    ],
    'sensitive_words': [
        {
            'config_id': 'sw_001',
            'config_type': 'sensitive_word',
            'key': 'high_level',
            'value': ['敏感词 1', '敏感词 2'],
            'scope': 'public',
            'description': '高敏感级别词库'
        }
    ],
    'rules': [
        {
            'config_id': 'rule_001',
            'config_type': 'rule',
            'key': 'deadline_reminder',
            'value': {'days_before': 3, 'enabled': True},
            'scope': 'public',
            'description': '截止日期提醒规则'
        }
    ]
}


@config_bp.route('/<config_type>', methods=['GET'])
def get_config(config_type):
    """获取指定类型配置"""
    scope = request.args.get('scope', 'all')  # all, public, personal
    user_id = request.args.get('user_id')
    
    configs = mock_configs.get(config_type, [])
    
    if scope == 'public':
        configs = [c for c in configs if c['scope'] == 'public']
    elif scope == 'personal' and user_id:
        configs = [c for c in configs if c['scope'] == 'personal' and c.get('user_id') == user_id]
    
    return jsonify({
        'success': True,
        'data': configs
    })


@config_bp.route('/<config_type>', methods=['POST'])
def save_config(config_type):
    """保存配置"""
    data = request.get_json()
    
    config_item = {
        'config_id': f"{config_type}_{len(mock_configs.get(config_type, [])) + 1:03d}",
        'config_type': config_type,
        'key': data.get('key'),
        'value': data.get('value'),
        'scope': data.get('scope', 'public'),
        'user_id': data.get('user_id'),
        'description': data.get('description', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    if config_type not in mock_configs:
        mock_configs[config_type] = []
    
    mock_configs[config_type].append(config_item)
    
    return jsonify({
        'success': True,
        'message': '配置保存成功',
        'data': config_item
    })


@config_bp.route('/<config_type>/<config_id>', methods=['DELETE'])
def delete_config(config_type, config_id):
    """删除配置"""
    configs = mock_configs.get(config_type, [])
    
    config_item = next((c for c in configs if c['config_id'] == config_id), None)
    
    if not config_item:
        return jsonify({
            'success': False,
            'message': f'配置不存在：{config_id}'
        }), 404
    
    configs.remove(config_item)
    
    return jsonify({
        'success': True,
        'message': '配置已删除'
    })


@config_bp.route('/user-preference', methods=['GET'])
def get_user_preference():
    """获取用户偏好"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({
            'success': False,
            'message': '缺少 user_id 参数'
        }), 400
    
    # 返回默认偏好
    preference = {
        'user_id': user_id,
        'preferences': {
            'default_doc_type': '通知',
            'auto_save': True,
            'notification_enabled': True
        }
    }
    
    return jsonify({
        'success': True,
        'data': preference
    })


@config_bp.route('/user-preference', methods=['POST'])
def save_user_preference():
    """保存用户偏好"""
    data = request.get_json()
    user_id = data.get('user_id')
    preferences = data.get('preferences', {})
    
    if not user_id:
        return jsonify({
            'success': False,
            'message': '缺少 user_id 参数'
        }), 400
    
    # TODO: 保存到数据库
    
    return jsonify({
        'success': True,
        'message': '用户偏好已保存'
    })

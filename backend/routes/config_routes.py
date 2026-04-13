"""
配置中心路由
"""
from flask import Blueprint, jsonify, request
from backend.services.config_service import config_service

config_bp = Blueprint('config', __name__, url_prefix='/api/config')


@config_bp.route('/<config_type>/<config_name>', methods=['GET'])
def get_config(config_type, config_name):
    """获取指定配置"""
    user_id = request.args.get('user_id')
    
    config = config_service.get_config(config_type, config_name, user_id)
    if config:
        return jsonify({
            'success': True,
            'data': config
        })
    else:
        return jsonify({
            'success': False,
            'message': f'配置不存在：{config_type}/{config_name}'
        }), 404


@config_bp.route('/<config_type>/<config_name>', methods=['POST'])
def save_config(config_type, config_name):
    """保存配置"""
    data = request.get_json()
    user_id = data.get('user_id')
    config_data = data.get('config_data', {})
    
    success = config_service.save_config(config_type, config_name, config_data, user_id)
    if success:
        return jsonify({
            'success': True,
            'message': '配置保存成功'
        })
    else:
        return jsonify({
            'success': False,
            'message': '配置保存失败'
        }), 500


@config_bp.route('/<config_type>/<config_name>', methods=['DELETE'])
def delete_config(config_type, config_name):
    """删除配置"""
    user_id = request.args.get('user_id')
    
    success = config_service.delete_config(config_type, config_name, user_id)
    if success:
        return jsonify({
            'success': True,
            'message': '配置已删除'
        })
    else:
        return jsonify({
            'success': False,
            'message': '配置删除失败'
        }), 500


@config_bp.route('/list/<config_type>', methods=['GET'])
def list_configs(config_type):
    """列出指定类型的配置"""
    user_id = request.args.get('user_id')
    
    configs = config_service.list_configs(config_type, user_id)
    return jsonify({
        'success': True,
        'data': configs
    })


@config_bp.route('/import', methods=['POST'])
def import_config():
    """导入配置"""
    data = request.get_json()
    config_type = data.get('config_type')
    config_name = data.get('config_name')
    file_path = data.get('file_path')
    user_id = data.get('user_id')
    
    if not config_type or not config_name or not file_path:
        return jsonify({
            'success': False,
            'message': '缺少必要参数'
        }), 400
    
    success = config_service.import_config(config_type, config_name, file_path, user_id)
    if success:
        return jsonify({
            'success': True,
            'message': '配置导入成功'
        })
    else:
        return jsonify({
            'success': False,
            'message': '配置导入失败'
        }), 500


@config_bp.route('/export', methods=['POST'])
def export_config():
    """导出配置"""
    data = request.get_json()
    config_type = data.get('config_type')
    config_name = data.get('config_name')
    output_path = data.get('output_path')
    user_id = data.get('user_id')
    
    if not config_type or not config_name or not output_path:
        return jsonify({
            'success': False,
            'message': '缺少必要参数'
        }), 400
    
    success = config_service.export_config(config_type, config_name, output_path, user_id)
    if success:
        return jsonify({
            'success': True,
            'message': '配置导出成功'
        })
    else:
        return jsonify({
            'success': False,
            'message': '配置导出失败'
        }), 500


@config_bp.route('/user-preference', methods=['GET'])
def get_user_preference():
    """获取用户偏好"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({
            'success': False,
            'message': '缺少 user_id 参数'
        }), 400
    
    # 从配置服务获取用户偏好
    preference = config_service.get_config('user_preference', 'default', user_id)
    if not preference:
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
    
    config_data = {
        'user_id': user_id,
        'preferences': preferences
    }
    
    success = config_service.save_config('user_preference', 'default', config_data, user_id)
    if success:
        return jsonify({
            'success': True,
            'message': '用户偏好已保存'
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户偏好保存失败'
        }), 500

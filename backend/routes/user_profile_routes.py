"""
用户画像与个性化 API 路由
"""
from flask import Blueprint, request, jsonify
from backend.services.user_profile_service import user_profile_service

user_profile_bp = Blueprint('user_profile', __name__, url_prefix='/api/user-profile')


@user_profile_bp.route('/<user_id>', methods=['GET'])
def get_profile(user_id):
    """获取用户画像"""
    try:
        profile = user_profile_service.get_profile(user_id)
        return jsonify({
            'success': True,
            'data': profile.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@user_profile_bp.route('/<user_id>/preferences', methods=['PUT'])
def update_preferences(user_id):
    """更新用户偏好"""
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        
        if not key:
            return jsonify({
                'success': False,
                'message': '缺少 key 参数'
            }), 400
        
        success = user_profile_service.update_preference(user_id, key, value)
        
        if success:
            return jsonify({
                'success': True,
                'message': '偏好更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '无效的偏好键'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@user_profile_bp.route('/<user_id>/recommendations', methods=['GET'])
def get_recommendations(user_id):
    """获取个性化推荐"""
    try:
        recommendations = user_profile_service.get_recommendations(user_id)
        return jsonify({
            'success': True,
            'data': {
                'recommended_skills': recommendations
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@user_profile_bp.route('/<user_id>/statistics', methods=['GET'])
def get_statistics(user_id):
    """获取用户统计信息"""
    try:
        stats = user_profile_service.get_user_statistics(user_id)
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@user_profile_bp.route('/<user_id>', methods=['DELETE'])
def delete_profile(user_id):
    """删除用户画像"""
    try:
        success = user_profile_service.delete_profile(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '用户画像已删除'
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户画像不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@user_profile_bp.route('/<user_id>/usage', methods=['POST'])
def record_usage(user_id):
    """记录使用行为"""
    try:
        data = request.get_json()
        skill_id = data.get('skill_id')
        action = data.get('action')
        details = data.get('details', {})
        
        if not skill_id or not action:
            return jsonify({
                'success': False,
                'message': '缺少 skill_id 或 action 参数'
            }), 400
        
        user_profile_service.record_usage(user_id, skill_id, action, details)
        
        return jsonify({
            'success': True,
            'message': '使用记录已保存'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

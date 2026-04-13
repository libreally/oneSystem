"""
权限管理 API 路由
支持用户认证、权限检查、角色管理等 API 端点
"""
from flask import Blueprint, request, jsonify
from backend.services.permission_service import permission_service, RoleType, PermissionType

permission_bp = Blueprint('permission', __name__, url_prefix='/api/permission')


@permission_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '缺少用户名或密码'
            }), 400
        
        user = permission_service.authenticate(username, password)
        if user:
            return jsonify({
                'success': True,
                'data': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'role': user.role.value,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@permission_bp.route('/check', methods=['POST'])
def check_permission():
    """检查权限"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        permission = data.get('permission')
        
        if not user_id or not permission:
            return jsonify({
                'success': False,
                'message': '缺少用户 ID 或权限'
            }), 400
        
        # 转换权限字符串为枚举
        try:
            permission_enum = PermissionType(permission)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '无效的权限类型'
            }), 400
        
        has_permission = permission_service.check_permission(user_id, permission_enum)
        return jsonify({
            'success': True,
            'data': {
                'has_permission': has_permission
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@permission_bp.route('/users', methods=['GET'])
def list_users():
    """列出所有用户"""
    try:
        users = permission_service.list_users()
        return jsonify({
            'success': True,
            'data': users
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@permission_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '缺少用户名或密码'
            }), 400
        
        try:
            role_enum = RoleType(role)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '无效的角色类型'
            }), 400
        
        user = permission_service.create_user(username, password, role_enum)
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@permission_bp.route('/users/<user_id>/role', methods=['PUT'])
def update_user_role(user_id):
    """更新用户角色"""
    try:
        data = request.get_json()
        role = data.get('role')
        
        if not role:
            return jsonify({
                'success': False,
                'message': '缺少角色参数'
            }), 400
        
        try:
            role_enum = RoleType(role)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '无效的角色类型'
            }), 400
        
        success = permission_service.update_user_role(user_id, role_enum)
        if success:
            return jsonify({
                'success': True,
                'message': '用户角色更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@permission_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    try:
        success = permission_service.delete_user(user_id)
        if success:
            return jsonify({
                'success': True,
                'message': '用户已删除'
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@permission_bp.route('/roles', methods=['GET'])
def list_roles():
    """列出所有角色"""
    try:
        roles = permission_service.list_roles()
        return jsonify({
            'success': True,
            'data': roles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@permission_bp.route('/roles/<role_type>/permissions', methods=['PUT'])
def update_role_permissions(role_type):
    """更新角色权限"""
    try:
        data = request.get_json()
        permissions = data.get('permissions', [])
        
        try:
            role_enum = RoleType(role_type)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '无效的角色类型'
            }), 400
        
        # 转换权限字符串列表为枚举列表
        try:
            permission_enums = [PermissionType(p) for p in permissions]
        except ValueError:
            return jsonify({
                'success': False,
                'message': '无效的权限类型'
            }), 400
        
        success = permission_service.update_role_permissions(role_enum, permission_enums)
        if success:
            return jsonify({
                'success': True,
                'message': '角色权限更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '角色不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

"""
系统集成路由
支持业务系统对接、统一任务管理
"""
from flask import Blueprint, jsonify, request
from backend.services.integration_service import (
    integration_service, 
    init_integration_service,
    SystemConfig,
    SystemType
)
import logging

logger = logging.getLogger(__name__)

integration_bp = Blueprint('integration', __name__, url_prefix='/api/integration')


@integration_bp.route('/systems', methods=['GET'])
def list_systems():
    """获取所有集成的业务系统"""
    summary = integration_service.get_system_summary()
    
    return jsonify({
        'success': True,
        'data': summary
    })


@integration_bp.route('/systems', methods=['POST'])
def add_system():
    """添加业务系统"""
    data = request.get_json()
    
    system_id = data.get('system_id')
    system_name = data.get('system_name')
    system_type = data.get('system_type', 'custom')
    base_url = data.get('base_url', '')
    auth_type = data.get('auth_type', 'api_key')
    api_key = data.get('api_key', '')
    username = data.get('username', '')
    password = data.get('password', '')
    enabled = data.get('enabled', True)
    config = data.get('config', {})
    
    if not system_id or not system_name:
        return jsonify({
            'success': False,
            'message': '缺少 system_id 或 system_name'
        }), 400
    
    try:
        # 转换系统类型
        system_type_enum = SystemType(system_type.lower())
    except ValueError:
        system_type_enum = SystemType.CUSTOM
    
    # 创建系统配置
    system_config = SystemConfig(
        system_id=system_id,
        system_name=system_name,
        system_type=system_type_enum,
        base_url=base_url,
        auth_type=auth_type,
        api_key=api_key,
        username=username,
        password=password,
        enabled=enabled,
        config=config
    )
    
    # 添加系统
    success = integration_service.add_system(system_config)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'系统 {system_name} 添加成功',
            'data': system_config.to_dict()
        })
    else:
        return jsonify({
            'success': False,
            'message': f'系统 {system_id} 已存在'
        }), 400


@integration_bp.route('/systems/<system_id>', methods=['DELETE'])
def remove_system(system_id):
    """移除业务系统"""
    success = integration_service.remove_system(system_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'系统 {system_id} 已移除'
        })
    else:
        return jsonify({
            'success': False,
            'message': f'系统 {system_id} 不存在'
        }), 404


@integration_bp.route('/systems/<system_id>/enable', methods=['POST'])
def enable_system(system_id):
    """启用业务系统"""
    success = integration_service.enable_system(system_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'系统 {system_id} 已启用'
        })
    else:
        return jsonify({
            'success': False,
            'message': f'系统 {system_id} 不存在'
        }), 404


@integration_bp.route('/systems/<system_id>/disable', methods=['POST'])
def disable_system(system_id):
    """禁用业务系统"""
    success = integration_service.disable_system(system_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'系统 {system_id} 已禁用'
        })
    else:
        return jsonify({
            'success': False,
            'message': f'系统 {system_id} 不存在'
        }), 404


@integration_bp.route('/systems/<system_id>/test', methods=['POST'])
def test_system(system_id):
    """测试系统连接"""
    adapter = integration_service.factory.get_adapter(system_id)
    
    if not adapter:
        return jsonify({
            'success': False,
            'message': f'系统 {system_id} 不存在'
        }), 404
    
    try:
        connected = adapter.test_connection()
        
        return jsonify({
            'success': connected,
            'message': '连接成功' if connected else '连接失败',
            'connected': connected
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'连接测试失败：{str(e)}',
            'connected': False
        })


@integration_bp.route('/tasks', methods=['GET'])
def get_all_tasks():
    """获取所有系统的任务"""
    # 获取过滤参数
    filters = {}
    if 'status' in request.args:
        filters['status'] = request.args.get('status')
    if 'priority' in request.args:
        filters['priority'] = request.args.get('priority')
    if 'assignee' in request.args:
        filters['assignee'] = request.args.get('assignee')
    if 'source_system' in request.args:
        filters['source_system'] = request.args.get('source_system')
    
    tasks = integration_service.get_all_tasks(filters)
    
    return jsonify({
        'success': True,
        'data': {
            'tasks': tasks,
            'total': len(tasks),
            'filters': filters
        }
    })


@integration_bp.route('/summary', methods=['GET'])
def get_integration_summary():
    """获取集成摘要"""
    summary = integration_service.get_system_summary()
    
    # 添加额外统计信息
    all_tasks = integration_service.get_all_tasks()
    summary['total_tasks'] = len(all_tasks)
    summary['pending_tasks'] = sum(1 for t in all_tasks if t.get('status') == 'pending')
    summary['high_priority_tasks'] = sum(1 for t in all_tasks if t.get('priority') in ['high', 'urgent'])
    
    return jsonify({
        'success': True,
        'data': summary
    })


@integration_bp.route('/sync', methods=['POST'])
def sync_all_systems():
    """同步所有系统数据"""
    data = request.get_json() or {}
    system_id = data.get('system_id')  # 可选，指定系统 ID
    
    results = []
    
    if system_id:
        # 同步指定系统
        adapter = integration_service.factory.get_adapter(system_id)
        if adapter and adapter.connected:
            try:
                tasks = adapter.sync_tasks()
                results.append({
                    'system_id': system_id,
                    'success': True,
                    'task_count': len(tasks)
                })
            except Exception as e:
                results.append({
                    'system_id': system_id,
                    'success': False,
                    'error': str(e)
                })
        else:
            results.append({
                'system_id': system_id,
                'success': False,
                'error': '系统未连接'
            })
    else:
        # 同步所有系统
        for sys_id in integration_service.systems.keys():
            adapter = integration_service.factory.get_adapter(sys_id)
            if adapter and adapter.connected:
                try:
                    tasks = adapter.sync_tasks()
                    results.append({
                        'system_id': sys_id,
                        'success': True,
                        'task_count': len(tasks)
                    })
                except Exception as e:
                    results.append({
                        'system_id': sys_id,
                        'success': False,
                        'error': str(e)
                    })
    
    return jsonify({
        'success': True,
        'data': {
            'results': results,
            'total_synced': sum(1 for r in results if r['success']),
            'total_failed': sum(1 for r in results if not r['success'])
        }
    })

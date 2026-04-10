"""
定时任务 API 路由
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from backend.services.scheduler_service import scheduler_service, ScheduledTask, RepeatType

scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/api/scheduler')


@scheduler_bp.route('/tasks', methods=['GET'])
def list_tasks():
    """获取所有定时任务"""
    user_id = request.args.get('user_id')
    enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
    
    tasks = scheduler_service.list_tasks(user_id=user_id, enabled_only=enabled_only)
    
    return jsonify({
        'success': True,
        'data': {
            'tasks': tasks,
            'total': len(tasks)
        }
    })


@scheduler_bp.route('/tasks', methods=['POST'])
def create_task():
    """创建定时任务"""
    data = request.get_json()
    
    required_fields = ['name', 'repeat_type']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'缺少必填字段：{field}'
            }), 400
    
    try:
        # 解析重复类型
        repeat_type = RepeatType(data.get('repeat_type', 'once'))
        
        # 创建任务
        task = ScheduledTask(
            task_id=data.get('task_id', f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            name=data['name'],
            description=data.get('description', ''),
            action=data.get('action', ''),
            params=data.get('params', {}),
            repeat_type=repeat_type,
            interval_minutes=data.get('interval_minutes', 0),
            day_of_week=data.get('day_of_week', 0),
            day_of_month=data.get('day_of_month', 1),
            hour=data.get('hour', 9),
            minute=data.get('minute', 0),
            user_id=data.get('user_id')
        )
        
        success = scheduler_service.add_task(task)
        
        if success:
            return jsonify({
                'success': True,
                'message': '任务创建成功',
                'data': task.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': '任务创建失败，可能任务已存在'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建失败：{str(e)}'
        }), 500


@scheduler_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """获取单个任务"""
    task = scheduler_service.get_task(task_id)
    
    if task:
        return jsonify({
            'success': True,
            'data': task.to_dict()
        })
    else:
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404


@scheduler_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除定时任务"""
    success = scheduler_service.remove_task(task_id)
    
    return jsonify({
        'success': success,
        'message': '任务删除成功' if success else '任务不存在'
    })


@scheduler_bp.route('/tasks/<task_id>/enable', methods=['POST'])
def enable_task(task_id):
    """启用任务"""
    success = scheduler_service.enable_task(task_id)
    
    return jsonify({
        'success': success,
        'message': '任务已启用' if success else '任务不存在'
    })


@scheduler_bp.route('/tasks/<task_id>/disable', methods=['POST'])
def disable_task(task_id):
    """禁用任务"""
    success = scheduler_service.disable_task(task_id)
    
    return jsonify({
        'success': success,
        'message': '任务已禁用' if success else '任务不存在'
    })


@scheduler_bp.route('/tasks/<task_id>/history', methods=['GET'])
def get_task_history(task_id):
    """获取任务执行历史"""
    limit = int(request.args.get('limit', 50))
    history = scheduler_service.get_execution_history(task_id=task_id, limit=limit)
    
    return jsonify({
        'success': True,
        'data': {
            'history': history,
            'total': len(history)
        }
    })


@scheduler_bp.route('/history', methods=['GET'])
def get_all_history():
    """获取所有任务执行历史"""
    task_id = request.args.get('task_id')
    limit = int(request.args.get('limit', 50))
    
    history = scheduler_service.get_execution_history(task_id=task_id, limit=limit)
    
    return jsonify({
        'success': True,
        'data': {
            'history': history,
            'total': len(history)
        }
    })


@scheduler_bp.route('/tasks/daily-report', methods=['POST'])
def create_daily_report():
    """创建每日报告任务"""
    data = request.get_json() or {}
    
    task = scheduler_service.create_daily_report_task(
        name=data.get('name', '每日工作报告'),
        hour=data.get('hour', 17),
        minute=data.get('minute', 0),
        user_id=data.get('user_id')
    )
    
    return jsonify({
        'success': True,
        'message': '每日报告任务已创建',
        'data': task.to_dict()
    })


@scheduler_bp.route('/tasks/reminder', methods=['POST'])
def create_reminder():
    """创建提醒任务"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({
            'success': False,
            'message': '缺少任务名称'
        }), 400
    
    try:
        repeat_type = RepeatType(data.get('repeat_type', 'daily'))
        
        task = scheduler_service.create_reminder_task(
            name=data['name'],
            hour=data.get('hour', 9),
            minute=data.get('minute', 0),
            params=data.get('params', {}),
            repeat_type=repeat_type,
            user_id=data.get('user_id')
        )
        
        return jsonify({
            'success': True,
            'message': '提醒任务已创建',
            'data': task.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建失败：{str(e)}'
        }), 500


@scheduler_bp.route('/status', methods=['GET'])
def get_scheduler_status():
    """获取调度器状态"""
    tasks = scheduler_service.list_tasks()
    enabled_count = len([t for t in tasks if t.get('enabled')])
    
    return jsonify({
        'success': True,
        'data': {
            'running': True,  # TODO: 实际状态
            'total_tasks': len(tasks),
            'enabled_tasks': enabled_count,
            'disabled_tasks': len(tasks) - enabled_count
        }
    })

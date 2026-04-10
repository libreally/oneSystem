"""
任务管理路由
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

task_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

# 模拟任务数据
mock_tasks = [
    {
        'task_id': 'task_001',
        'title': '完成项目评审报告',
        'source_system': '项目管理系统的',
        'priority': 'high',
        'status': 'in_progress',
        'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        'assignee': '张三',
        'description': '完成 Q4 项目评审报告',
        'tags': ['项目', '报告']
    },
    {
        'task_id': 'task_002',
        'title': '整理会议纪要',
        'source_system': '会议管理系统',
        'priority': 'medium',
        'status': 'pending',
        'due_date': (datetime.now() + timedelta(days=1)).isoformat(),
        'assignee': '李四',
        'description': '整理周例会会议纪要',
        'tags': ['会议', '纪要']
    },
    {
        'task_id': 'task_003',
        'title': '审核预算方案',
        'source_system': '财务系统',
        'priority': 'high',
        'status': 'pending',
        'due_date': (datetime.now() + timedelta(days=3)).isoformat(),
        'assignee': '王五',
        'description': '审核 2024 年预算方案',
        'tags': ['财务', '预算']
    }
]


@task_bp.route('', methods=['GET'])
def list_tasks():
    """获取任务列表"""
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    
    tasks = mock_tasks.copy()
    
    if status_filter:
        tasks = [t for t in tasks if t['status'] == status_filter]
    
    if priority_filter:
        tasks = [t for t in tasks if t['priority'] == priority_filter]
    
    return jsonify({
        'success': True,
        'data': tasks
    })


@task_bp.route('/summary', methods=['GET'])
def get_tasks_summary():
    """获取任务汇总"""
    total = len(mock_tasks)
    pending = len([t for t in mock_tasks if t['status'] == 'pending'])
    in_progress = len([t for t in mock_tasks if t['status'] == 'in_progress'])
    completed = len([t for t in mock_tasks if t['status'] == 'completed'])
    high_priority = len([t for t in mock_tasks if t['priority'] == 'high'])
    
    summary = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'overdue': 0,  # TODO: 计算超期任务
        'high_priority': high_priority
    }
    
    return jsonify({
        'success': True,
        'data': summary
    })


@task_bp.route('/<task_id>', methods=['GET'])
def get_task(task_id):
    """获取指定任务"""
    task = next((t for t in mock_tasks if t['task_id'] == task_id), None)
    
    if not task:
        return jsonify({
            'success': False,
            'message': f'任务不存在：{task_id}'
        }), 404
    
    return jsonify({
        'success': True,
        'data': task
    })


@task_bp.route('/<task_id>/update', methods=['POST'])
def update_task(task_id):
    """更新任务状态"""
    data = request.get_json()
    new_status = data.get('status')
    
    task = next((t for t in mock_tasks if t['task_id'] == task_id), None)
    
    if not task:
        return jsonify({
            'success': False,
            'message': f'任务不存在：{task_id}'
        }), 404
    
    if new_status:
        task['status'] = new_status
        task['updated_at'] = datetime.now().isoformat()
    
    return jsonify({
        'success': True,
        'message': '任务已更新',
        'data': task
    })


@task_bp.route('/work-summary', methods=['GET'])
def get_work_summary():
    """获取工作总结"""
    period = request.args.get('period', 'week')  # week or month
    
    # 生成工作总结
    summary = {
        'period': period,
        'completed_tasks': [
            {
                'title': '完成系统设计文档',
                'completed_at': datetime.now().isoformat()
            }
        ],
        'in_progress_tasks': [
            {
                'title': '开发 API 接口',
                'progress': 60
            }
        ],
        'risks': [],
        'next_plan': [
            '继续推进 API 开发',
            '准备测试用例'
        ]
    }
    
    return jsonify({
        'success': True,
        'data': summary
    })

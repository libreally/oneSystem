"""
任务管理路由
包含任务管理和工作总结功能
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from typing import Dict, Any, List

task_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

# 模拟任务数据
mock_tasks = [
    {
        'task_id': 'task_001',
        'title': '完成项目评审报告',
        'source_system': '项目管理系统',
        'priority': 'high',
        'status': 'in_progress',
        'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        'assignee': '张三',
        'description': '完成 Q4 项目评审报告',
        'tags': ['项目', '报告'],
        'created_at': (datetime.now() - timedelta(days=5)).isoformat(),
        'updated_at': datetime.now().isoformat(),
        'progress': 60,
        'subtasks': [
            {'title': '收集项目数据', 'completed': True},
            {'title': '编写报告初稿', 'completed': True},
            {'title': '内部评审', 'completed': False},
            {'title': '修改完善', 'completed': False}
        ]
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
        'tags': ['会议', '纪要'],
        'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=1)).isoformat(),
        'progress': 0,
        'subtasks': []
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
        'tags': ['财务', '预算'],
        'created_at': (datetime.now() - timedelta(days=2)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=2)).isoformat(),
        'progress': 0,
        'subtasks': [
            {'title': '审阅预算明细', 'completed': False},
            {'title': '对比历史数据', 'completed': False},
            {'title': '提出修改意见', 'completed': False}
        ]
    },
    {
        'task_id': 'task_004',
        'title': '完成系统设计文档',
        'source_system': '研发管理系统',
        'priority': 'high',
        'status': 'completed',
        'due_date': (datetime.now() - timedelta(days=1)).isoformat(),
        'assignee': '张三',
        'description': '完成新系统的架构设计文档',
        'tags': ['设计', '文档'],
        'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=1)).isoformat(),
        'completed_at': (datetime.now() - timedelta(days=1)).isoformat(),
        'progress': 100,
        'subtasks': [
            {'title': '需求分析', 'completed': True},
            {'title': '架构设计', 'completed': True},
            {'title': '接口定义', 'completed': True},
            {'title': '文档评审', 'completed': True}
        ]
    },
    {
        'task_id': 'task_005',
        'title': '开发 API 接口',
        'source_system': '研发管理系统',
        'priority': 'medium',
        'status': 'in_progress',
        'due_date': (datetime.now() + timedelta(days=5)).isoformat(),
        'assignee': '赵六',
        'description': '开发用户管理和权限控制 API',
        'tags': ['开发', 'API'],
        'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
        'updated_at': datetime.now().isoformat(),
        'progress': 60,
        'subtasks': [
            {'title': '数据库设计', 'completed': True},
            {'title': '基础 CRUD 接口', 'completed': True},
            {'title': '权限验证逻辑', 'completed': False},
            {'title': '单元测试', 'completed': False}
        ]
    },
    {
        'task_id': 'task_006',
        'title': '超期任务示例',
        'source_system': '测试系统',
        'priority': 'high',
        'status': 'pending',
        'due_date': (datetime.now() - timedelta(days=2)).isoformat(),
        'assignee': '测试人员',
        'description': '这是一个超期的任务示例',
        'tags': ['测试', '超期'],
        'created_at': (datetime.now() - timedelta(days=7)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=7)).isoformat(),
        'progress': 0,
        'subtasks': []
    }
]


def _calculate_overdue_tasks(tasks: List[Dict]) -> int:
    """计算超期任务数量"""
    now = datetime.now()
    overdue_count = 0
    for task in tasks:
        if task['status'] != 'completed':
            due_date = datetime.fromisoformat(task['due_date'])
            if due_date < now:
                overdue_count += 1
    return overdue_count


def _get_tasks_by_period(tasks: List[Dict], period: str) -> List[Dict]:
    """根据时间段筛选任务"""
    now = datetime.now()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'quarter':
        start_date = now - timedelta(days=90)
    else:
        start_date = now - timedelta(days=7)
    
    filtered_tasks = []
    for task in tasks:
        created_at = datetime.fromisoformat(task['created_at'])
        if created_at >= start_date:
            filtered_tasks.append(task)
    return filtered_tasks


def _generate_work_summary(period: str = 'week') -> Dict[str, Any]:
    """生成工作总结"""
    now = datetime.now()
    period_tasks = _get_tasks_by_period(mock_tasks, period)
    
    # 已完成任务
    completed_tasks = [
        {
            'task_id': t['task_id'],
            'title': t['title'],
            'completed_at': t.get('completed_at'),
            'source_system': t['source_system'],
            'tags': t['tags']
        }
        for t in period_tasks 
        if t['status'] == 'completed'
    ]
    
    # 进行中的任务
    in_progress_tasks = [
        {
            'task_id': t['task_id'],
            'title': t['title'],
            'progress': t.get('progress', 0),
            'due_date': t['due_date'],
            'source_system': t['source_system'],
            'subtasks': t.get('subtasks', []),
            'next_steps': [st['title'] for st in t.get('subtasks', []) if not st.get('completed', False)][:3]
        }
        for t in period_tasks 
        if t['status'] == 'in_progress'
    ]
    
    # 未开始的任务
    pending_tasks = [
        {
            'task_id': t['task_id'],
            'title': t['title'],
            'due_date': t['due_date'],
            'priority': t['priority'],
            'source_system': t['source_system']
        }
        for t in period_tasks 
        if t['status'] == 'pending'
    ]
    
    # 风险和超期事项
    risks = []
    overdue_tasks = []
    for task in period_tasks:
        if task['status'] != 'completed':
            due_date = datetime.fromisoformat(task['due_date'])
            days_until_due = (due_date - now).days
            
            if days_until_due < 0:
                overdue_tasks.append({
                    'task_id': task['task_id'],
                    'title': task['title'],
                    'due_date': task['due_date'],
                    'overdue_days': abs(days_until_due),
                    'priority': task['priority']
                })
                risks.append({
                    'type': 'overdue',
                    'level': 'high',
                    'task_id': task['task_id'],
                    'title': task['title'],
                    'description': f"已超期 {abs(days_until_due)} 天",
                    'suggestion': '立即处理或申请延期'
                })
            elif days_until_due <= 2 and task['priority'] == 'high':
                risks.append({
                    'type': 'approaching_deadline',
                    'level': 'medium',
                    'task_id': task['task_id'],
                    'title': task['title'],
                    'description': f"距离截止日期还有 {days_until_due} 天",
                    'suggestion': '优先安排时间处理'
                })
            
            # 进度风险
            if task['status'] == 'in_progress':
                progress = task.get('progress', 0)
                total_days = (due_date - datetime.fromisoformat(task['created_at'])).days
                elapsed_days = (now - datetime.fromisoformat(task['created_at'])).days
                expected_progress = min(100, int((elapsed_days / total_days) * 100)) if total_days > 0 else 0
                
                if progress < expected_progress * 0.7:
                    risks.append({
                        'type': 'progress_delay',
                        'level': 'medium',
                        'task_id': task['task_id'],
                        'title': task['title'],
                        'description': f'当前进度{progress}%，预期进度{expected_progress}%',
                        'suggestion': '加快进度或寻求协助'
                    })
    
    # 已生成的成果文件
    deliverables = []
    for task in completed_tasks:
        if '报告' in task['title'] or '文档' in task['title']:
            deliverables.append({
                'task_id': task['task_id'],
                'title': f"{task['title']} - 最终版",
                'type': 'document',
                'generated_at': task['completed_at']
            })
    
    # 下周/下月工作建议
    next_plan = []
    
    # 基于未完成的任务生成建议
    if in_progress_tasks:
        next_plan.append({
            'category': 'continue',
            'title': '继续推进进行中的任务',
            'items': [t['title'] for t in in_progress_tasks[:3]],
            'priority': 'high'
        })
    
    if pending_tasks:
        high_priority_pending = [t for t in pending_tasks if t['priority'] == 'high']
        if high_priority_pending:
            next_plan.append({
                'category': 'start',
                'title': '启动高优先级待办任务',
                'items': [t['title'] for t in high_priority_pending[:3]],
                'priority': 'high'
            })
        
        normal_pending = [t for t in pending_tasks if t['priority'] != 'high']
        if normal_pending:
            next_plan.append({
                'category': 'schedule',
                'title': '安排常规待办任务',
                'items': [t['title'] for t in normal_pending[:3]],
                'priority': 'medium'
            })
    
    if overdue_tasks:
        next_plan.append({
            'category': 'urgent',
            'title': '紧急处理超期任务',
            'items': [t['title'] for t in overdue_tasks],
            'priority': 'urgent'
        })
    
    # 统计信息
    stats = {
        'total_tasks': len(period_tasks),
        'completed_count': len(completed_tasks),
        'in_progress_count': len(in_progress_tasks),
        'pending_count': len(pending_tasks),
        'overdue_count': len(overdue_tasks),
        'risk_count': len(risks),
        'completion_rate': round(len(completed_tasks) / len(period_tasks) * 100, 1) if period_tasks else 0
    }
    
    return {
        'period': period,
        'period_label': '本周' if period == 'week' else ('本月' if period == 'month' else '本季度'),
        'generated_at': now.isoformat(),
        'statistics': stats,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'risks': risks,
        'overdue_tasks': overdue_tasks,
        'deliverables': deliverables,
        'next_plan': next_plan
    }


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
    overdue = _calculate_overdue_tasks(mock_tasks)
    
    summary = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'overdue': overdue,
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
    period = request.args.get('period', 'week')  # week, month, or quarter
    
    # 使用新生成的工作总结函数
    summary = _generate_work_summary(period)
    
    return jsonify({
        'success': True,
        'data': summary
    })

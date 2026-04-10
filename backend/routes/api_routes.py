"""
基础 API 路由
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from backend.services.skill_engine import skill_engine
from backend.services.ai_service import init_ai_service

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 初始化 AI 服务
init_ai_service(skill_engine)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': '一系统 AI 助手'
    })


@api_bp.route('/chat', methods=['POST'])
def chat():
    """AI 聊天接口"""
    from backend.services.ai_service import ai_assistant_service
    
    data = request.get_json()
    message = data.get('message', '')
    user_id = data.get('user_id')
    
    if not message:
        return jsonify({
            'success': False,
            'message': '消息内容不能为空'
        }), 400
    
    # 使用 AI 服务处理消息
    result = ai_assistant_service.process_message(message, user_id)
    
    return jsonify(result)


@api_bp.route('/tasks/summary', methods=['GET'])
def get_tasks_summary():
    """获取任务汇总"""
    # 模拟数据
    summary = {
        'total': 25,
        'pending': 8,
        'in_progress': 10,
        'completed': 5,
        'overdue': 2,
        'high_priority': 3
    }
    
    return jsonify({
        'success': True,
        'data': summary
    })


@api_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """获取智能推荐"""
    # 模拟数据
    recommendations = [
        {
            'id': 'rec_001',
            'title': '生成周报',
            'description': '检测到今天是周五，是否需要生成本周工作总结？',
            'type': 'report',
            'priority': 'high'
        },
        {
            'id': 'rec_002',
            'title': '督办任务提醒',
            'description': '有 2 个督办任务即将到期',
            'type': 'reminder',
            'priority': 'medium'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': recommendations
    })

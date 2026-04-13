"""
基础 API 路由
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from backend.services.skill_engine import skill_engine
from backend.services.ai_service import init_ai_service
from backend.services.user_profile_service import user_profile_service

api_bp = Blueprint('api', __name__, url_prefix='/api')


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
    user_id = data.get('user_id', 'default_user')
    
    if not message:
        return jsonify({
            'success': False,
            'message': '消息内容不能为空'
        }), 400
    
    # 使用 AI 服务处理消息
    result = ai_assistant_service.process_message(message, user_id)
    
    # 记录用户使用行为
    if result.get('success') and result.get('skill_id'):
        user_profile_service.record_usage(
            user_id=user_id,
            skill_id=result['skill_id'],
            action='chat_execution',
            details={'message': message, 'intent': result.get('intent')}
        )
    
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
    user_id = request.args.get('user_id', 'default_user')
    
    # 基于用户画像的个性化推荐
    recommended_skills = user_profile_service.get_recommendations(user_id)
    
    # 构建推荐列表
    recommendations = []
    
    # 根据推荐技能生成具体建议
    skill_descriptions = {
        'doc_processor': {
            'title': '文档处理',
            'description': '帮您转换公文格式、生成标准文档',
            'type': 'document',
            'priority': 'high'
        },
        'sensitive_word_checker': {
            'title': '敏感词检查',
            'description': '检测并处理文档中的敏感词汇',
            'type': 'check',
            'priority': 'high'
        },
        'data_merger': {
            'title': '数据合并',
            'description': '合并多个 Excel/CSV 文件，比对数据差异',
            'type': 'data',
            'priority': 'medium'
        }
    }
    
    for skill_id in recommended_skills:
        if skill_id in skill_descriptions:
            desc = skill_descriptions[skill_id]
            recommendations.append({
                'id': f'rec_{skill_id}',
                'skill_id': skill_id,
                'title': desc['title'],
                'description': desc['description'],
                'type': desc['type'],
                'priority': desc['priority']
            })
    
    # 添加时间相关的智能推荐
    from datetime import datetime
    now = datetime.now()
    
    # 周五推荐生成周报
    if now.weekday() == 4:  # 周五
        recommendations.append({
            'id': 'rec_weekly_report',
            'title': '生成周报',
            'description': '检测到今天是周五，是否需要生成本周工作总结？',
            'type': 'report',
            'priority': 'high'
        })
    
    return jsonify({
        'success': True,
        'data': recommendations
    })

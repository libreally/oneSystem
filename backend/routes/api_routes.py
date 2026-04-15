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
    from flask import request, jsonify
    import logging
    import traceback
    from backend.services.ai_service import ai_assistant_service
    from backend.models.db_models import ChatSession
    from backend.models import get_db
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'default_user')
        session_id = data.get('session_id')
        
        logger.info(f"收到聊天请求：message={message}, user_id={user_id}, session_id={session_id}")
    
        if not message:
            return jsonify({
                'success': False,
                'message': '消息内容不能为空'
            }), 400
    
        # 处理字符串类型的user_id，默认为1（admin用户）
        if isinstance(user_id, str) and user_id != 'default_user':
            # 尝试查找用户
            from backend.models.db_models import User
            user = User.query.filter_by(username=user_id).first()
            if user:
                user_id = user.id
            else:
                user_id = 1
        elif user_id == 'default_user':
            user_id = 1
        
        # 保存消息到会话（先保存用户消息，确保消息不丢失）
        db = get_db()
        ai_response = '抱歉，处理您的请求时遇到错误。'
        
        try:
            # 使用 AI 服务处理消息
            result = ai_assistant_service.process_message(message, user_id)
            ai_response = result.get('message', result.get('response', ai_response))
            
            # 记录用户使用行为
            if result.get('success') and result.get('skill_id'):
                from backend.services.user_profile_service import user_profile_service
                user_profile_service.record_usage(
                    user_id=user_id,
                    skill_id=result['skill_id'],
                    action='chat_execution',
                    details={'message': message, 'intent': result.get('intent')}
                )
        except Exception as e:
            logger.error(f"处理消息失败：{str(e)}")
            # 即使AI服务失败，也要返回一个默认响应
            result = {
                'success': False,
                'message': ai_response,
                'need_more_info': False
            }
    except Exception as e:
        logger.error(f"整个聊天处理失败：{str(e)}")
        return jsonify({
            'success': False,
            'message': '处理请求时遇到错误',
            'need_more_info': False
        })
    
    try:
        # 保存消息到会话
        logger.info(f"准备保存消息到会话：session_id={session_id}, user_id={user_id}")
        if session_id:
            # 先查询所有会话，看看会话是否存在
            all_sessions = db.query(ChatSession).all()
            logger.info(f"所有会话：{[s.id for s in all_sessions]}")
            
            # 查询会话
            session = db.query(ChatSession).filter_by(id=session_id).first()
            logger.info(f"查询会话结果：session={session}")
            if session:
                logger.info(f"会话的user_id：{session.user_id}")
                # 创建新的消息列表，包含原有消息和新消息
                new_messages = session.messages.copy()
                
                # 添加用户消息
                user_message = {
                    'role': 'user',
                    'content': message,
                    'timestamp': datetime.utcnow().isoformat()
                }
                new_messages.append(user_message)
                # 添加AI回复
                assistant_message = {
                    'role': 'assistant',
                    'content': ai_response,
                    'timestamp': datetime.utcnow().isoformat()
                }
                new_messages.append(assistant_message)
                logger.info(f"添加消息到会话：user_message={user_message}, assistant_message={assistant_message}")
                logger.info(f"添加消息后，会话的消息数量：{len(new_messages)}")
                
                # 显式地重新赋值messages字段
                session.messages = new_messages
                
                try:
                    db.commit()
                    logger.info("消息保存成功")
                    # 重新查询会话，确认消息是否被保存
                    updated_session = db.query(ChatSession).filter_by(id=session_id).first()
                    logger.info(f"更新后会话的消息数量：{len(updated_session.messages)}")
                except Exception as e:
                    logger.error(f"消息保存失败：{str(e)}")
                    db.rollback()
        else:
            # 如果没有会话ID，创建一个新会话
            new_session = ChatSession(
                user_id=user_id,
                title='新对话',
                messages=[
                    {
                        'role': 'user',
                        'content': message,
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    {
                        'role': 'assistant',
                        'content': ai_response,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                ],
                context={}
            )
            db.add(new_session)
            try:
                db.commit()
                db.refresh(new_session)
                session_id = new_session.id
                logger.info(f"创建新会话成功：session_id={session_id}")
            except Exception as e:
                logger.error(f"创建新会话失败：{str(e)}")
                db.rollback()
        
        # 返回会话ID
        result['session_id'] = session_id
        logger.info(f"返回聊天结果：session_id={session_id}, result={result}")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"保存会话失败：{str(e)}")
        return jsonify({
            'success': False,
            'message': '保存会话时遇到错误',
            'need_more_info': False
        })


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
        },
         'scheduler_manager': {
            'title': '定时任务管理',
            'description': '支持创建、查看、修改和删除定时任务，设置执行时间和重复规则',
            'type': 'scheduler',
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


@api_bp.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """获取聊天会话列表"""
    from backend.models.db_models import ChatSession
    from backend.models import get_db
    
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    db = get_db()
    
    # 获取用户的所有会话
    sessions = db.query(ChatSession).filter_by(user_id=user_id).order_by(ChatSession.updated_at.desc()).all()
    
    # 转换为字典列表
    session_list = []
    for session in sessions:
        session_list.append({
            'id': session.id,
            'title': session.title,
            'created_at': session.created_at.isoformat() if session.created_at else None,
            'updated_at': session.updated_at.isoformat() if session.updated_at else None,
            'message_count': len(session.messages) if session.messages else 0
        })
    
    return jsonify({
        'success': True,
        'sessions': session_list
    })


@api_bp.route('/chat/sessions', methods=['POST'])
def create_chat_session():
    """创建新的聊天会话"""
    from backend.models.db_models import ChatSession
    from backend.models import get_db
    
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')
    title = data.get('title', '新对话')
    
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    db = get_db()
    
    # 创建新会话
    new_session = ChatSession(
        user_id=user_id,
        title=title,
        messages=[],
        context={}
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return jsonify({
        'success': True,
        'session': {
            'id': new_session.id,
            'title': new_session.title,
            'created_at': new_session.created_at.isoformat() if new_session.created_at else None,
            'updated_at': new_session.updated_at.isoformat() if new_session.updated_at else None,
            'messages': new_session.messages
        }
    })


@api_bp.route('/chat/history/<int:session_id>', methods=['GET'])
def get_chat_history(session_id):
    """获取聊天会话历史"""
    from backend.models.db_models import ChatSession
    from backend.models import get_db
    
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    db = get_db()
    
    # 获取会话
    session = db.query(ChatSession).filter_by(id=session_id, user_id=user_id).first()
    
    if not session:
        return jsonify({
            'success': False,
            'message': '会话不存在或无权限访问'
        }), 404
    
    # 限制返回的消息数量
    limit = int(request.args.get('limit', 100))
    messages = session.messages[-limit:] if session.messages else []
    
    return jsonify({
        'success': True,
        'messages': messages
    })


@api_bp.route('/chat/sessions/<int:session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """删除聊天会话"""
    from backend.models.db_models import ChatSession
    from backend.models import get_db
    
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    db = get_db()
    
    # 获取会话
    session = db.query(ChatSession).filter_by(id=session_id, user_id=user_id).first()
    
    if not session:
        return jsonify({
            'success': False,
            'message': '会话不存在或无权限访问'
        }), 404
    
    # 删除会话
    db.delete(session)
    db.commit()
    
    return jsonify({
        'success': True,
        'message': '会话已删除'
    })


@api_bp.route('/chat/sessions/<int:session_id>/clear', methods=['POST'])
def clear_chat_session(session_id):
    """清空聊天会话历史"""
    from backend.models.db_models import ChatSession
    from backend.models import get_db
    
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    db = get_db()
    
    # 获取会话
    session = db.query(ChatSession).filter_by(id=session_id, user_id=user_id).first()
    
    if not session:
        return jsonify({
            'success': False,
            'message': '会话不存在或无权限访问'
        }), 404
    
    # 清空消息和上下文
    session.messages = []
    session.context = {}
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': '会话已清空'
    })


@api_bp.route('/user/profile', methods=['GET'])
def get_user_profile():
    """获取用户个人资料"""
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    # 从数据库获取用户信息
    from backend.models.db_models import User
    from backend.models import get_db
    db = get_db()
    user = db.query(User).filter_by(id=user_id).first()
    
    if not user:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 404
    
    # 从用户画像服务获取额外信息
    profile = user_profile_service.get_profile(str(user_id))
    
    return jsonify({
        'success': True,
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'last_login': user.updated_at.isoformat() if user.updated_at else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'preferences': profile.preferences,
            'usage_stats': profile.usage_stats
        }
    })


@api_bp.route('/user/profile', methods=['PUT'])
def update_user_profile():
    """更新用户个人资料"""
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    data = request.get_json()
    
    # 从数据库获取用户信息
    from backend.models.db_models import User
    from backend.models import get_db
    db = get_db()
    user = db.query(User).filter_by(id=user_id).first()
    
    if not user:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 404
    
    # 更新用户信息
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data and data['password']:
        from werkzeug.security import generate_password_hash
        user.password = generate_password_hash(data['password'])
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': '个人资料更新成功'
    })


@api_bp.route('/user/usage-stats', methods=['GET'])
def get_user_usage_stats():
    """获取用户使用统计"""
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    # 从用户画像服务获取使用统计
    stats = user_profile_service.get_user_statistics(str(user_id))
    
    # 计算额外的统计信息
    profile = user_profile_service.get_profile(str(user_id))
    
    return jsonify({
        'success': True,
        'data': {
            'total_chats': stats.get('total_requests', 0),
            'total_skills': len(profile.usage_stats.get('skills_used', {})),
            'skill_trend': 5,  # 模拟数据
            'average_response_time': 1.2,  # 模拟数据
            'active_days': 10  # 模拟数据
        }
    })


@api_bp.route('/user/skill-preferences', methods=['GET'])
def get_user_skill_preferences():
    """获取用户技能偏好"""
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    # 从用户画像服务获取技能使用情况
    profile = user_profile_service.get_profile(str(user_id))
    skills_used = profile.usage_stats.get('skills_used', {})
    
    # 计算技能偏好分数
    total_usage = sum(skills_used.values()) if skills_used else 1
    preferences = []
    
    # 技能名称映射
    skill_names = {
        'doc_processor': '文档处理',
        'sensitive_word_checker': '敏感词检查',
        'data_merger': '数据合并',
        'scheduler_manager': '定时任务管理',
        'chat': '聊天助手',
        'assistant': '智能助手'
    }
    
    for skill_id, count in skills_used.items():
        score = count / total_usage
        preferences.append({
            'skill_id': skill_id,
            'skill_name': skill_names.get(skill_id, skill_id),
            'score': score
        })
    
    # 按分数排序
    preferences.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'success': True,
        'data': {
            'preferences': preferences
        }
    })


@api_bp.route('/user/skill-preferences', methods=['POST'])
def update_user_skill_preferences():
    """更新用户技能偏好"""
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    data = request.get_json()
    
    # 这里可以实现更新技能偏好的逻辑
    # 目前我们只是返回成功
    
    return jsonify({
        'success': True,
        'message': '技能偏好更新成功'
    })


@api_bp.route('/user/recommendations', methods=['GET'])
def get_user_recommendations():
    """获取用户推荐技能"""
    user_id = request.args.get('user_id', 'default_user')
    # 处理字符串类型的user_id，默认为1（admin用户）
    if isinstance(user_id, str) and user_id != 'default_user':
        # 尝试查找用户
        from backend.models.db_models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user_id = user.id
        else:
            user_id = 1
    elif user_id == 'default_user':
        user_id = 1
    
    # 从用户画像服务获取推荐
    recommended_skill_ids = user_profile_service.get_recommendations(str(user_id))
    
    # 技能信息映射
    skill_info = {
        'doc_processor': {
            'skill_name': '文档处理',
            'description': '帮您转换公文格式、生成标准文档',
            'match_score': 0.9
        },
        'sensitive_word_checker': {
            'skill_name': '敏感词检查',
            'description': '检测并处理文档中的敏感词汇',
            'match_score': 0.85
        },
        'data_merger': {
            'skill_name': '数据合并',
            'description': '合并多个 Excel/CSV 文件，比对数据差异',
            'match_score': 0.8
        },
        'scheduler_manager': {
            'skill_name': '定时任务管理',
            'description': '支持创建、查看、修改和删除定时任务，设置执行时间和重复规则',
            'match_score': 0.75
        },
        'chat': {
            'skill_name': '聊天助手',
            'description': '智能对话，解答各种问题',
            'match_score': 0.95
        },
        'assistant': {
            'skill_name': '智能助手',
            'description': '提供全方位的办公辅助',
            'match_score': 0.9
        }
    }
    
    # 构建推荐列表
    recommendations = []
    for skill_id in recommended_skill_ids:
        if skill_id in skill_info:
            recommendations.append(skill_info[skill_id])
    
    return jsonify({
        'success': True,
        'data': {
            'recommendations': recommendations
        }
    })

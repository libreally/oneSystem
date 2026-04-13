"""
智能办公平台 - 一系统
数据库初始化模块
"""
from .db_models import db, User, UserPreference, Skill


def init_db(app):
    """初始化数据库"""
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@yixitong.com',
                password_hash='pbkdf2:sha256:260000$default$salt$hash',
                role='admin'
            )
            db.session.add(admin)
            
            # 创建默认偏好设置
            pref = UserPreference(user=admin, theme='light', language='zh-CN')
            db.session.add(pref)
            
            db.session.commit()
            print("默认管理员用户已创建 (用户名：admin)")
        
        # 创建内置 Skills
        builtin_skills = [
            {
                'name': 'document_convert',
                'description': '文档格式转换',
                'category': 'document',
                'parameters': [
                    {'name': 'file_path', 'type': 'string', 'required': True},
                    {'name': 'target_format', 'type': 'string', 'required': True}
                ],
                'is_active': True,
                'is_dynamic': False
            },
            {
                'name': 'sensitive_word_check',
                'description': '敏感词检查',
                'category': 'security',
                'parameters': [
                    {'name': 'text', 'type': 'string', 'required': True},
                    {'name': 'action', 'type': 'string', 'default': 'mark'}
                ],
                'is_active': True,
                'is_dynamic': False
            },
            {
                'name': 'data_merge',
                'description': '数据文件合并',
                'category': 'data',
                'parameters': [
                    {'name': 'file_paths', 'type': 'array', 'required': True},
                    {'name': 'output_path', 'type': 'string', 'required': True}
                ],
                'is_active': True,
                'is_dynamic': False
            }
        ]
        
        for skill_data in builtin_skills:
            skill = Skill.query.filter_by(name=skill_data['name']).first()
            if not skill:
                skill = Skill(**skill_data)
                db.session.add(skill)
        
        db.session.commit()
        print("内置 Skills 已初始化")


def get_db():
    """获取数据库会话"""
    return db.session

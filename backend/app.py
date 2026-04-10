"""
智能办公平台 - 一系统
Flask 应用入口
"""
import os
import sys
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.settings import *
from backend.routes import api_bp, skill_bp, task_bp, config_bp


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__, 
                static_folder='../frontend/static',
                template_folder='../frontend')
    
    # 基础配置
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    
    # 启用 CORS
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(config_bp)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT
    )
    
    # 首页路由
    @app.route('/')
    def index():
        return send_from_directory('../', 'ai-v1.html')
    
    # 健康检查
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': '一系统'}
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("  智能办公平台 - 一系统")
    print("=" * 50)
    print(f"  服务地址：http://{HOST}:{PORT}")
    print(f"  API 文档：http://{HOST}:{PORT}/api/health")
    print("=" * 50)
    app.run(host=HOST, port=PORT, debug=DEBUG)

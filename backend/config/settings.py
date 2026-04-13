"""
智能办公平台 - 一系统
配置文件
"""
import os

# 基础配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Flask配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'yixitong-secret-key-2024')
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# 数据目录
TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')
SENSITIVE_WORDS_DIR = os.path.join(DATA_DIR, 'sensitive_words')
TASKS_DIR = os.path.join(DATA_DIR, 'tasks')
SKILLS_DIR = os.path.join(DATA_DIR, 'skills')

# 确保数据目录存在
for dir_path in [DATA_DIR, TEMPLATES_DIR, SENSITIVE_WORDS_DIR, TASKS_DIR, SKILLS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# 数据库配置（使用SQLite）
DATABASE_URI = os.environ.get('DATABASE_URI', f'sqlite:///{os.path.join(DATA_DIR, "yixitong.db")}')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = DEBUG

# LLM 配置
LLM_API_KEY = os.environ.get('LLM_API_KEY', 'sk-lgpuyorgfzhmicnknlythkfvfocrhqrsnzbvqjkdosomxqgw')
LLM_API_BASE = os.environ.get('LLM_API_BASE', 'https://api.siliconflow.cn/v1')
LLM_MODEL = os.environ.get('LLM_MODEL', 'Qwen/Qwen3-8B')
LLM_ENABLED = bool(LLM_API_KEY)

# 定时任务配置
SCHEDULER_API_ENABLED = True
SCHEDULER_TIMEZONE = 'Asia/Shanghai'

# AI助手配置
AI_ASSISTANT_NAME = 'AI自动化助手'
AI_DEFAULT_RESPONSE_DELAY = 1.0  # 秒

# 文件检索配置
DEFAULT_SEARCH_DIRS = [
    os.path.expanduser('~/Documents'),
    os.path.expanduser('~/Downloads'),
    os.path.expanduser('~/Desktop'),
]
MAX_SEARCH_FILES = 20
SUPPORTED_FILE_TYPES = ['.doc', '.docx', '.txt', '.pdf', '.xls', '.xlsx', '.csv', '.ppt', '.pptx']

# 权限配置
ADMIN_ROLES = ['admin', 'manager']
DEFAULT_USER_ROLE = 'user'

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

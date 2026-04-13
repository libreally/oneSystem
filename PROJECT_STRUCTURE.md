# 智能办公平台 - 一系统

## 项目结构

```
d:\work_document\oneSystem\
├── README.md                    # 项目需求文档
├── ai-v1.html                  # 前端页面（遗留）
├── requirements.txt            # Python 依赖
├── 一系统.txt                  # 需求规格文档
│
├── backend/                    # Flask 后端服务
│   ├── app.py                  # Flask 应用入口
│   ├── config/                 # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py         # 环境配置
│   ├── models/                 # 数据模型
│   │   ├── __init__.py         # 数据库初始化
│   │   └── db_models.py        # SQLAlchemy 模型
│   ├── routes/                 # API 路由
│   │   ├── __init__.py         # 路由模块导出
│   │   ├── api_routes.py       # 基础 API 路由
│   │   ├── skill_routes.py     # Skill 管理路由
│   │   ├── task_routes.py      # 任务管理路由
│   │   ├── config_routes.py     # 配置中心路由
│   │   ├── scheduler_routes.py  # 定时调度路由
│   │   ├── file_retrieval_routes.py  # 文件检索路由
│   │   ├── user_profile_routes.py    # 用户画像路由
│   │   ├── integration_routes.py      # 系统集成路由
│   │   ├── wps_routes.py            # WPS 集成路由
│   │   ├── skill_generator_routes.py  # Skill 生成路由
│   │   └── permission_routes.py       # 权限管理路由
│   ├── services/               # 业务服务层
│   │   ├── __init__.py
│   │   ├── ai_service.py           # AI 助手服务
│   │   ├── skill_engine.py          # Skill 引擎
│   │   ├── llm_service.py           # LLM 服务
│   │   ├── scheduler_service.py     # 定时调度服务
│   │   ├── file_retrieval_service.py  # 文件检索服务
│   │   ├── user_profile_service.py    # 用户画像服务
│   │   ├── integration_service.py      # 系统集成服务（OA/ERP/CRM）
│   │   ├── wps_integration_service.py  # WPS 集成服务
│   │   ├── config_service.py            # 配置中心服务
│   │   ├── skill_generator_service.py  # Skill 动态生成服务
│   │   └── permission_service.py       # 权限管理服务
│   ├── skills/                 # Skills 能力模块
│   │   ├── __init__.py
│   │   ├── base_skill.py           # Skill 基类
│   │   ├── document_skill.py       # 文档处理 Skill
│   │   ├── sensitive_word_skill.py  # 敏感词检查 Skill
│   │   └── data_merge_skill.py      # 数据合并 Skill
│   └── data/                   # 数据目录
│       ├── sensitive_words/    # 敏感词库
│       │   └── words.txt
│       ├── templates/          # 公文模板
│       │   ├── default_template.json
│       │   └── report_template.json
│       └── yixitong.db         # SQLite 数据库
│
├── frontend/                   # Vue.js 前端
│   ├── package.json           # 前端依赖
│   ├── vite.config.js         # Vite 配置
│   ├── index.html              # HTML 入口
│   ├── public/                 # 静态资源
│   │   ├── favicon.svg
│   │   └── icons.svg
│   └── src/                    # 前端源码
│       ├── main.js             # Vue 入口
│       ├── App.vue             # 根组件
│       ├── api/                # API 调用模块
│       │   ├── index.js        # Axios 实例
│       │   └── modules.js      # API 接口定义
│       ├── components/         # 公共组件
│       │   ├── ChatWindow.vue
│       │   └── HelloWorld.vue
│       ├── router/             # 路由配置
│       │   └── index.js
│       ├── stores/              # Pinia 状态管理
│       │   ├── chat.js
│       │   └── skill.js
│       ├── views/               # 页面视图
│       │   ├── Dashboard.vue     # 工作台
│       │   ├── Chat.vue          # AI 助手
│       │   ├── Tasks.vue         # 任务管理
│       │   ├── Skills.vue        # 技能中心
│       │   ├── Schedule.vue      # 定时调度
│       │   ├── Documents.vue     # 文档检索
│       │   ├── Reports.vue       # 报表中心
│       │   ├── Config.vue        # 配置中心
│       │   ├── Profile.vue       # 个人中心
│       │   └── NotFound.vue      # 404 页面
│       └── utils/               # 工具函数
│           └── helpers.js
│
├── docs/                      # 文档目录
│   └── api.md                 # API 文档
│
├── PROJECT_STRUCTURE.md       # 项目结构文档
├── DEVELOPMENT_PROGRESS.md    # 开发进度文档
└── DEVELOPMENT_PROGRESS.md    # 开发进度文档
```

## 技术架构

### 后端技术栈
- **框架**: Flask 3.1 + Flask-CORS + Flask-SQLAlchemy
- **数据库**: SQLite (yixitong.db)
- **定时任务**: schedule
- **AI 服务**: 支持多模型 LLM API
- **WPS 集成**: win32com (Windows COM)

### 前端技术栈
- **框架**: Vue 3.5 + Vue Router 4 + Pinia 3
- **构建工具**: Vite 5
- **HTTP 客户端**: Axios
- **UI**: 原生 CSS (无 UI 框架)

### 已实现的 API 服务
- AI 聊天服务 (/api/chat)
- Skill 管理 (/api/skills)
- 任务管理 (/api/tasks)
- 配置中心 (/api/config)
- 定时调度 (/api/schedule)
- 文件检索 (/api/documents)
- 用户画像 (/api/user)
- 系统集成 (/api/integration)
- WPS 集成 (/api/wps)
- Skill 生成 (/api/skill-generator)
- 权限管理 (/api/permission)

## 功能模块

### 核心能力
- [x] AI 助手服务 - 意图识别、参数提取、Skill 调度
- [x] Skills 能力体系 - 文档处理、敏感词检查、数据合并
- [x] 定时调度中心 - 多种重复类型、自动报告生成
- [x] 本地文件检索 - 关键词提取、多目录搜索、会话知识库
- [x] 用户画像与个性化 - 行为分析、智能推荐

### 新增能力（开发中）
- [x] WPS 本地集成 - 文档处理、Word/Excel 操作
- [x] 配置中心 - 公共配置、个人配置
- [x] Skill 动态生成 - 基于 LLM 生成 Skill 代码
- [x] 系统集成 - OA/ERP/CRM 适配器
- [x] 权限管理 - 用户认证、角色权限

## 快速开始

### 后端启动
```bash
cd d:\work_document\oneSystem\backend
pip install -r requirements.txt
python app.py
```

### 前端启动
```bash
cd d:\work_document\oneSystem\frontend
npm install
npm run dev
```

### 访问地址
- 后端服务: http://localhost:5000
- 前端页面: http://localhost:5173

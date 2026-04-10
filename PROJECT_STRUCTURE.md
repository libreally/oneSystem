# 智能办公平台 - 一系统

## 项目结构

```
/workspace
├── README.md              # 项目需求文档
├── ai-v1.html            # 前端页面
├── backend/              # 后端服务
│   ├── app.py           # Flask应用入口
│   ├── config.py        # 配置文件
│   ├── models/          # 数据模型
│   ├── routes/          # API路由
│   ├── skills/          # Skills能力模块
│   ├── services/        # 业务服务
│   └── utils/           # 工具函数
└── frontend/            # 前端资源
    └── static/          # 静态文件
```

## 功能模块优先级

### 第一阶段：基础架构（当前实现）
- [x] Flask后端框架
- [ ] 基础API接口
- [ ] Skills管理基础功能

### 第二阶段：核心Skills
- [ ] 文档处理Skill
- [ ] 敏感词检查Skill
- [ ] 数据合并Skill

### 第三阶段：配置中心
- [ ] 公文模板配置
- [ ] 敏感词库配置
- [ ] 督办规则配置

### 第四阶段：定时调度
- [ ] 定时任务管理
- [ ] 自动报告生成

### 第五阶段：本地集成
- [ ] 本地文件检索
- [ ] WPS集成

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python backend/app.py
```

## API文档

详见 `docs/api.md`

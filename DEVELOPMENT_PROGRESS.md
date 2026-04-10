# 智能办公平台 - 一系统 开发进度

## 已完成模块

### ✅ 核心架构
- [x] Flask 后端框架搭建
- [x] 7 个路由蓝图（API、Skills、任务、配置、调度、文件检索、用户画像）
- [x] 服务层设计（AI 助手、Skill 引擎、定时调度、文件检索、用户画像）
- [x] Skills 能力模块体系

### ✅ AI 助手服务 (`backend/services/ai_service.py`)
- [x] 意图识别（正则模式匹配 5 类意图）
- [x] 参数提取与验证
- [x] 缺失参数补充询问机制
- [x] Skill 调度执行

### ✅ Skills 能力体系
- [x] **文档处理 Skill** (`document_skill.py`)
  - 公文转换（通知、报告、请示等）
  - 格式调整
  - 文档生成
- [x] **敏感词检查 Skill** (`sensitive_word_skill.py`)
  - 敏感词检测
  - 敏感词替换
  - 敏感词标记
- [x] **数据合并 Skill** (`data_merge_skill.py`)
  - Excel/CSV 文件合并
  - 数据比对
  - 差异分析

### ✅ 定时调度中心 (`backend/services/scheduler_service.py`)
- [x] 定时任务管理（CRUD、启用/禁用）
- [x] 多种重复类型：一次、每小时、每天、每周、每月、自定义
- [x] 每日报告自动生成
- [x] 定时提醒功能
- [x] 后台线程运行

### ✅ 本地文件检索 (`backend/services/file_retrieval_service.py`)
- [x] 关键词自动提取
- [x] 多目录搜索（Documents、Desktop、Downloads 等）
- [x] 相关度评分排序
- [x] 会话知识库管理
- [x] 文件内容读取

### ✅ 用户画像与个性化 (新增)
- [x] **用户画像服务** (`backend/services/user_profile_service.py`)
  - 用户偏好管理（默认文档类型、敏感词级别、主题等）
  - 使用行为记录与分析
  - 常用技能统计
  - 个性化推荐算法
  - 数据持久化（JSON 存储）
- [x] **用户画像 API** (`backend/routes/user_profile_routes.py`)
  - GET `/api/user-profile/<user_id>` - 获取用户画像
  - PUT `/api/user-profile/<user_id>/preferences` - 更新偏好
  - GET `/api/user-profile/<user_id>/recommendations` - 获取推荐
  - GET `/api/user-profile/<user_id>/statistics` - 获取统计
  - DELETE `/api/user-profile/<user_id>` - 删除画像
  - POST `/api/user-profile/<user_id>/usage` - 记录使用行为
- [x] **集成到聊天接口**
  - 自动记录用户使用行为
  - 基于画像的个性化推荐
  - 时间相关的智能推荐（如周五推荐周报）

### ✅ API 接口完整实现
- [x] `/api/chat` - AI 聊天（已集成用户画像）
- [x] `/api/skills/*` - Skill 管理
- [x] `/api/scheduler/*` - 定时任务
- [x] `/api/files/*` - 文件检索
- [x] `/api/user-profile/*` - 用户画像（新增）
- [x] `/api/recommendations` - 智能推荐（已升级为个性化推荐）

### ✅ 配置数据
- [x] 敏感词库模板 (`backend/data/sensitive_words/words.txt`)
- [x] 公文模板（通知、报告）(`backend/data/templates/`)
- [x] 用户画像存储目录 (`backend/data/user_profiles/`)

## 待实现模块（按优先级排序）

### 🔄 中等优先级
- [ ] **数据库持久化**
  - 使用 SQLite/PostgreSQL 替代 JSON 存储
  - 用户数据、任务历史、执行记录持久化
  - 数据迁移脚本

- [ ] **前端界面完善**
  - 对接所有 API 接口
  - 用户画像展示与管理界面
  - 个性化推荐展示
  - 使用统计可视化

- [ ] **Skill 动态生成能力**
  - 基于 LLM 的动态 Skill 生成
  - Skill 组合编排
  - 自定义 Skill 注册

### 📅 低优先级（最后实现）
- [ ] **WPS 本地集成**
  - WPS Office SDK 集成
  - 本地文档直接编辑
  - WPS 插件开发
  - 实时协作编辑

- [ ] **高级功能**
  - 多用户权限管理
  - 团队协作功能
  - 审计日志
  - 数据导出/导入

## 技术栈

- **后端**: Python 3.12 + Flask
- **数据处理**: python-docx, pandas, openpyxl
- **定时任务**: APScheduler
- **文件检索**: 原生 Python + 关键词匹配
- **数据存储**: JSON 文件（临时）→ 待迁移至数据库
- **前端**: HTML5 + CSS3 + JavaScript (ai-v1.html)

## 快速启动

```bash
cd /workspace
pip install -r requirements.txt
python backend/app.py
```

访问地址：http://localhost:5000

## API 测试示例

### 1. 健康检查
```bash
curl http://localhost:5000/api/health
```

### 2. AI 聊天
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我检查这篇材料的敏感词", "user_id": "user_001"}'
```

### 3. 获取用户画像
```bash
curl http://localhost:5000/api/user-profile/user_001
```

### 4. 获取个性化推荐
```bash
curl "http://localhost:5000/api/recommendations?user_id=user_001"
```

### 5. 更新用户偏好
```bash
curl -X PUT http://localhost:5000/api/user-profile/user_001/preferences \
  -H "Content-Type: application/json" \
  -d '{"key": "default_doc_type", "value": "报告"}'
```

## 下一步计划

1. **完善前端对接** - 将用户画像和个性化推荐集成到 ai-v1.html
2. **数据库迁移** - 引入 SQLite 进行数据持久化
3. **增强意图识别** - 引入更智能的 NLP 模型
4. **WPS 集成准备** - 调研 WPS SDK，设计集成方案

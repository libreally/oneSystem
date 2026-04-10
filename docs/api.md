# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`

---

## 1. 健康检查

### GET /health

检查服务状态。

**响应示例:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "service": "一系统 AI 助手"
}
```

---

## 2. AI 聊天

### POST /chat

发送消息给 AI 助手。

**请求体:**
```json
{
  "message": "帮我生成周报"
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "reply": "收到您的消息：帮我生成周报",
    "suggestions": [
      "帮我生成周报",
      "检查敏感词",
      "合并 Excel 表格"
    ]
  }
}
```

---

## 3. Skills 管理

### GET /skills

获取所有可用 Skills。

**响应示例:**
```json
{
  "success": true,
  "data": [
    {
      "skill_id": "doc_processor",
      "name": "文档处理",
      "description": "支持公文转换、格式调整、文档生成等功能",
      "category": "文档处理"
    },
    {
      "skill_id": "sensitive_word_checker",
      "name": "敏感词检查",
      "description": "支持文档敏感词检测、替换、标记等功能",
      "category": "敏感词检查"
    }
  ]
}
```

### GET /skills/{skill_id}

获取指定 Skill 信息。

### POST /skills/{skill_id}/execute

执行 Skill。

**请求体:**
```json
{
  "params": {
    "action": "convert_to_official",
    "content": "这是正文内容",
    "doc_type": "通知",
    "output_path": "output.docx"
  }
}
```

**响应示例:**
```json
{
  "success": true,
  "message": "公文转换成功",
  "file_path": "/path/to/output.docx",
  "data": {
    "doc_type": "通知",
    "output_path": "output.docx"
  }
}
```

---

## 4. 任务管理

### GET /tasks

获取任务列表。

**查询参数:**
- `status`: 任务状态筛选 (pending, in_progress, completed)
- `priority`: 优先级筛选 (high, medium, low)

### GET /tasks/summary

获取任务汇总。

**响应示例:**
```json
{
  "success": true,
  "data": {
    "total": 25,
    "pending": 8,
    "in_progress": 10,
    "completed": 5,
    "overdue": 2,
    "high_priority": 3
  }
}
```

### GET /tasks/work-summary

获取工作总结。

**查询参数:**
- `period`: 周期 (week, month)

---

## 5. 配置中心

### GET /config/{config_type}

获取指定类型配置。

**路径参数:**
- `config_type`: 配置类型 (templates, sensitive_words, rules)

**查询参数:**
- `scope`: 范围 (all, public, personal)
- `user_id`: 用户 ID

### POST /config/{config_type}

保存配置。

**请求体:**
```json
{
  "key": "my_template",
  "value": {"font": "宋体", "size": 14},
  "scope": "personal",
  "description": "我的个人模板"
}
```

### DELETE /config/{config_type}/{config_id}

删除配置。

---

## 6. 错误响应

所有接口在发生错误时返回统一格式:

```json
{
  "success": false,
  "message": "错误描述",
  "errors": ["详细错误列表"]
}
```

**常见状态码:**
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

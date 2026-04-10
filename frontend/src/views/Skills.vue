<template>
  <div class="page active">
    <div class="card">
      <div class="card-title">
        <span>🛠️ Skills 能力库</span>
        <div>
          <button class="btn btn-secondary">导入 Skill</button>
          <button class="btn btn-primary">+ 创建新 Skill</button>
        </div>
      </div>

      <div class="skill-card">
        <div class="skill-header">
          <div>
            <div class="skill-name">📝 公文格式转换</div>
            <div class="skill-desc">将普通文档转换为标准公文格式，支持红头文件、发文号、签发人等要素</div>
          </div>
          <span class="badge badge-success">已启用</span>
        </div>
        <div class="skill-meta">
          <span>调用次数：1,234</span>
          <span>版本：v2.1</span>
          <span>更新时间：2024-01-15</span>
        </div>
      </div>

      <div class="skill-card">
        <div class="skill-header">
          <div>
            <div class="skill-name">🔍 敏感词检查</div>
            <div class="skill-desc">自动检测文档中的敏感词汇，支持自定义词库和正则表达式匹配</div>
          </div>
          <span class="badge badge-success">已启用</span>
        </div>
        <div class="skill-meta">
          <span>调用次数：3,456</span>
          <span>版本：v1.8</span>
          <span>更新时间：2024-01-10</span>
        </div>
      </div>

      <div class="skill-card">
        <div class="skill-header">
          <div>
            <div class="skill-name">📊 Excel 数据合并</div>
            <div class="skill-desc">合并多个 Excel 表格，支持按指定字段匹配、数据透视和统计分析</div>
          </div>
          <span class="badge badge-success">已启用</span>
        </div>
        <div class="skill-meta">
          <span>调用次数：892</span>
          <span>版本：v1.5</span>
          <span>更新时间：2024-01-08</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.page { display: block; }
.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.skill-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  transition: all 0.3s;
  cursor: pointer;
}
.skill-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: rgb(0, 101, 105);
}
.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}
.skill-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
.skill-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
}
.skill-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
}
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
.badge-success {
  background: #f6ffed;
  color: #52c41a;
}
.badge-warning {
  background: #fff7e6;
  color: #fa8c16;
}
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}
.btn-primary {
  background: rgb(0, 101, 105);
  color: white;
}
.btn-primary:hover {
  background: rgb(0, 80, 84);
}
.btn-secondary {
  background: #f5f7fa;
  color: #333;
}
.btn-secondary:hover {
  background: #e8e8e8;
}
</style>

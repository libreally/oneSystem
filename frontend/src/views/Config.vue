<template>
  <div class="page active">
    <div class="card">
      <div class="card-title">⚙️ 配置中心</div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div class="skill-card">
          <div class="skill-name">📄 公文模板配置</div>
          <div class="skill-desc">管理公文类型、标题格式、字体字号、红头样式等</div>
        </div>
        <div class="skill-card">
          <div class="skill-name">🚫 敏感词库配置</div>
          <div class="skill-desc">维护敏感词库、分类管理、处理规则设置</div>
        </div>
        <div class="skill-card">
          <div class="skill-name">⏱️ 督办规则配置</div>
          <div class="skill-desc">配置任务状态机、流转路径、提醒规则</div>
        </div>
        <div class="skill-card">
          <div class="skill-name">🎯 智能推荐规则</div>
          <div class="skill-desc">设置推荐触发条件、展示规则、推荐对象</div>
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
}
.skill-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}
.skill-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: rgb(0, 101, 105);
}
.skill-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}
.skill-desc {
  font-size: 13px;
  color: #666;
}
</style>

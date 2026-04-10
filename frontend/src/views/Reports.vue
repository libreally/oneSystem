<template>
  <div class="page active">
    <div class="card">
      <div class="card-title">
        <span>📈 报表中心</span>
        <button class="btn btn-primary">生成新报表</button>
      </div>
      <div class="dashboard-grid">
        <div class="stat-card">
          <div class="stat-label">本周工作量</div>
          <div class="stat-value">28</div>
          <div>完成任务数</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">平均处理时长</div>
          <div class="stat-value">2.3h</div>
          <div>比上周缩短 15%</div>
        </div>
        <div class="stat-card purple">
          <div class="stat-label">Skill 调用次数</div>
          <div class="stat-value">156</div>
          <div>本周累计</div>
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
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}
.stat-card {
  background: linear-gradient(135deg, rgb(0, 101, 105) 0%, rgb(0, 130, 136) 100%);
  color: white;
  padding: 20px;
  border-radius: 8px;
}
.stat-card.success {
  background: linear-gradient(135deg, rgb(0, 80, 84) 0%, rgb(0, 101, 105) 100%);
}
.stat-card.purple {
  background: linear-gradient(135deg, rgb(0, 110, 115) 0%, rgb(0, 101, 105) 100%);
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin: 10px 0;
}
.stat-label {
  font-size: 14px;
  opacity: 0.9;
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
</style>

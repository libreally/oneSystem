<template>
  <div class="page active">
    <div class="card">
      <div class="card-title">
        <span>⏰ 定时任务管理</span>
        <button class="btn btn-primary">+ 新建任务</button>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>任务名称</th>
            <th>执行周期</th>
            <th>下次执行时间</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>📊 自动生成周报</td>
            <td>每周五 17:00</td>
            <td>2024-01-19 17:00</td>
            <td><span class="badge badge-success">运行中</span></td>
            <td>
              <button class="btn btn-secondary">编辑</button>
              <button class="btn btn-secondary">暂停</button>
            </td>
          </tr>
          <tr>
            <td>📅 月度报告汇总</td>
            <td>每月最后一天 18:00</td>
            <td>2024-01-31 18:00</td>
            <td><span class="badge badge-success">运行中</span></td>
            <td>
              <button class="btn btn-secondary">编辑</button>
              <button class="btn btn-secondary">暂停</button>
            </td>
          </tr>
        </tbody>
      </table>
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
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}
.data-table th {
  background: #fafafa;
  font-weight: 600;
  font-size: 14px;
}
.data-table tr:hover {
  background: #f5f7fa;
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
  margin-right: 5px;
}
.btn-primary {
  background: rgb(0, 101, 105);
  color: white;
}
.btn-secondary {
  background: #f5f7fa;
  color: #333;
}
</style>

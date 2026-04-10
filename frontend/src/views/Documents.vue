<template>
  <div class="page active">
    <div class="card">
      <div class="card-title">
        <span>📄 文档管理</span>
        <button class="btn btn-primary">连接 WPS</button>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>文件名</th>
            <th>类型</th>
            <th>修改时间</th>
            <th>大小</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>📄 2024 年度工作计划.docx</td>
            <td>Word 文档</td>
            <td>2024-01-15 14:30</td>
            <td>256 KB</td>
            <td><span class="badge badge-success">已处理</span></td>
            <td>
              <button class="btn btn-secondary">打开</button>
              <button class="btn btn-secondary">转换</button>
            </td>
          </tr>
          <tr>
            <td>📊 Q1 数据统计.xlsx</td>
            <td>Excel 表格</td>
            <td>2024-01-14 16:20</td>
            <td>1.2 MB</td>
            <td><span class="badge badge-warning">待检查</span></td>
            <td>
              <button class="btn btn-secondary">打开</button>
              <button class="btn btn-secondary">合并</button>
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

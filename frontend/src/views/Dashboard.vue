<template>
  <div class="page active">
    <!-- 统计卡片 -->
    <div class="dashboard-grid">
      <div class="stat-card">
        <div class="stat-label">今日待办</div>
        <div class="stat-value">12</div>
        <div>3 项即将超期</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-label">风险提醒</div>
        <div class="stat-value">5</div>
        <div>需立即处理</div>
      </div>
      <div class="stat-card success">
        <div class="stat-label">本周已完成</div>
        <div class="stat-value">28</div>
        <div>效率提升 15%</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-label">可用 Skills</div>
        <div class="stat-value">45</div>
        <div>8 个新增</div>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- 待办任务 -->
      <div class="card">
        <div class="card-title">
          <span>📋 今日待办</span>
          <button class="btn btn-secondary" @click="viewAllTasks">查看全部</button>
        </div>
        <ul class="task-list">
          <li class="task-item">
            <div class="task-priority priority-high"></div>
            <div class="task-content">
              <div class="task-title">审核 Q1 财务报告</div>
              <div class="task-meta">
                <span class="task-tag">财务</span>
                <span>今日 17:00 截止</span>
              </div>
            </div>
          </li>
          <li class="task-item">
            <div class="task-priority priority-high"></div>
            <div class="task-content">
              <div class="task-title">完成项目进度汇报</div>
              <div class="task-meta">
                <span class="task-tag">项目</span>
                <span>今日 16:00 截止</span>
              </div>
            </div>
          </li>
          <li class="task-item">
            <div class="task-priority priority-medium"></div>
            <div class="task-content">
              <div class="task-title">整理会议纪要并分发</div>
              <div class="task-meta">
                <span class="task-tag">行政</span>
                <span>今天</span>
              </div>
            </div>
          </li>
          <li class="task-item">
            <div class="task-priority priority-low"></div>
            <div class="task-content">
              <div class="task-title">更新部门通讯录</div>
              <div class="task-meta">
                <span class="task-tag">人事</span>
                <span>本周</span>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- 智能推荐 -->
      <div class="card">
        <div class="card-title">
          <span>🎯 智能推荐</span>
        </div>
        <div class="service-grid">
          <div class="service-card" @click="quickAction('公文转换')">
            <div class="service-icon">📝</div>
            <div class="service-name">公文转换</div>
          </div>
          <div class="service-card" @click="quickAction('敏感词检查')">
            <div class="service-icon">🔍</div>
            <div class="service-name">敏感词检查</div>
          </div>
          <div class="service-card" @click="quickAction('生成周报')">
            <div class="service-icon">📊</div>
            <div class="service-name">生成周报</div>
          </div>
          <div class="service-card" @click="quickAction('数据合并')">
            <div class="service-icon">📑</div>
            <div class="service-name">数据合并</div>
          </div>
          <div class="service-card" @click="quickAction('督办任务')">
            <div class="service-icon">⏱️</div>
            <div class="service-name">督办任务</div>
          </div>
          <div class="service-card" @click="quickAction('文件整理')">
            <div class="service-icon">📁</div>
            <div class="service-name">文件整理</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 工作总结和最近活动 -->
    <div class="dashboard-grid">
      <div class="card">
        <div class="card-title">
          <span>📝 本周工作总结</span>
          <button class="btn btn-primary" @click="generateWeeklyReport">自动生成</button>
        </div>
        <div class="timeline">
          <div class="timeline-item">
            <div class="timeline-time">周一</div>
            <div class="timeline-content" @click="editTimeline($event)">完成项目需求评审，输出评审报告</div>
          </div>
          <div class="timeline-item">
            <div class="timeline-time">周二</div>
            <div class="timeline-content" @click="editTimeline($event)">处理公文 15 份，完成敏感词检查</div>
          </div>
          <div class="timeline-item">
            <div class="timeline-time">周三</div>
            <div class="timeline-content" @click="editTimeline($event)">参加部门例会，整理会议纪要</div>
          </div>
          <div class="timeline-item">
            <div class="timeline-time">周四</div>
            <div class="timeline-content" @click="editTimeline($event)">完成数据统计分析，生成报表</div>
          </div>
          <div class="timeline-item">
            <div class="timeline-time">周五</div>
            <div class="timeline-content" @click="editTimeline($event)">推进项目进度，协调资源分配</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>🔔 风险提醒</span>
        </div>
        <ul class="task-list">
          <li class="task-item">
            <div class="task-priority priority-high"></div>
            <div class="task-content">
              <div class="task-title">任务"年度预算编制"即将超期</div>
              <div class="task-meta">剩余时间：2 小时</div>
            </div>
            <span class="badge badge-danger">紧急</span>
          </li>
          <li class="task-item">
            <div class="task-priority priority-medium"></div>
            <div class="task-content">
              <div class="task-title">3 份公文待签发</div>
              <div class="task-meta">已停留超过 24 小时</div>
            </div>
            <span class="badge badge-warning">警告</span>
          </li>
          <li class="task-item">
            <div class="task-priority priority-medium"></div>
            <div class="task-content">
              <div class="task-title">周报未提交</div>
              <div class="task-meta">截止今日 18:00</div>
            </div>
            <span class="badge badge-warning">提醒</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()

const quickAction = (action) => {
  chatStore.toggleChatWindow()
  setTimeout(() => {
    chatStore.sendMessage(`帮我${action}`)
  }, 300)
}

const viewAllTasks = () => {
  alert('跳转到任务列表页面')
}

const generateWeeklyReport = () => {
  quickAction('生成周报')
}

const editTimeline = (event) => {
  const content = event.target
  content.setAttribute('contenteditable', 'true')
  content.classList.add('editing')
  content.focus()
  
  content.addEventListener('blur', () => {
    content.setAttribute('contenteditable', 'false')
    content.classList.remove('editing')
    if (!content.textContent.trim()) {
      content.textContent = '点击编辑内容'
    }
  }, { once: true })
}
</script>

<style scoped>
.page { display: block; }

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

.stat-card.warning {
  background: linear-gradient(135deg, rgb(0, 101, 105) 0%, rgb(30, 120, 125) 100%);
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

.task-list {
  list-style: none;
}

.task-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.task-item:hover {
  background: #f5f7fa;
  margin: 0 -12px;
  padding: 12px;
}

.task-item:last-child {
  border-bottom: none;
}

.task-priority {
  width: 4px;
  height: 40px;
  border-radius: 2px;
  flex-shrink: 0;
}

.priority-high { background: #f5222d; }
.priority-medium { background: #fa8c16; }
.priority-low { background: #52c41a; }

.task-content {
  flex: 1;
}

.task-title {
  font-size: 14px;
  margin-bottom: 4px;
}

.task-meta {
  font-size: 12px;
  color: #999;
}

.task-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: #f5f7fa;
  color: #666;
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}

.service-card {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.service-card:hover {
  background: rgb(0, 101, 105);
  color: white;
  transform: translateY(-2px);
}

.service-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.service-name {
  font-size: 13px;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline-item {
  position: relative;
  padding-bottom: 20px;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -26px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgb(0, 101, 105);
  border: 2px solid white;
  box-shadow: 0 0 0 2px rgb(0, 101, 105);
}

.timeline-item::after {
  content: '';
  position: absolute;
  left: -21px;
  top: 20px;
  width: 2px;
  height: calc(100% - 20px);
  background: #e8e8e8;
}

.timeline-item:last-child::after {
  display: none;
}

.timeline-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.timeline-content {
  font-size: 14px;
  color: #333;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.timeline-content:hover {
  background: rgba(0, 101, 105, 0.05);
}

.timeline-content.editing {
  background: rgba(0, 101, 105, 0.1);
  outline: 2px solid rgb(0, 101, 105);
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-danger {
  background: #fff1f0;
  color: #f5222d;
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

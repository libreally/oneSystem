<template>
  <div class="tasks-container">
    <div class="tasks-header">
      <h1>任务管理</h1>
      <div class="tasks-actions">
        <button class="btn btn-primary" @click="showCreateTaskDialog = true">创建任务</button>
        <button class="btn btn-secondary" @click="generateWorkSummary">生成工作摘要</button>
      </div>
    </div>
    
    <div class="tasks-filters">
      <select v-model="filterStatus" class="filter-select">
        <option value="">所有状态</option>
        <option value="pending">待处理</option>
        <option value="in_progress">进行中</option>
        <option value="completed">已完成</option>
      </select>
      <input 
        v-model="filterKeyword" 
        type="text" 
        placeholder="搜索任务..." 
        class="filter-input"
      />
    </div>
    
    <div class="tasks-list">
      <div 
        v-for="task in filteredTasks" 
        :key="task.task_id" 
        :class="['task-card', task.status]"
      >
        <div class="task-header">
          <h3>{{ task.title }}</h3>
          <span class="task-status" :data-status="task.status">{{ getStatusText(task.status) }}</span>
        </div>
        <div class="task-content">
          <p>{{ task.description }}</p>
          <div class="task-meta">
            <span class="task-priority" :data-priority="task.priority">{{ getPriorityText(task.priority) }}</span>
            <span class="task-deadline">截止: {{ formatDate(task.deadline) }}</span>
          </div>
        </div>
        <div class="task-actions">
          <button class="btn btn-sm btn-primary" @click="completeTask(task.task_id)">
            完成
          </button>
          <button class="btn btn-sm btn-secondary" @click="editTask(task)">
            编辑
          </button>
          <button class="btn btn-sm btn-danger" @click="deleteTask(task.task_id)">
            删除
          </button>
        </div>
      </div>
      <div v-if="filteredTasks.length === 0" class="empty-state">
        <p>暂无任务</p>
      </div>
    </div>
    
    <!-- 任务统计 -->
    <div class="tasks-summary">
      <div class="summary-card">
        <h3>任务统计</h3>
        <div class="summary-stats">
          <div class="stat-item">
            <span class="stat-value">{{ summaryData.total || 0 }}</span>
            <span class="stat-label">总任务</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ summaryData.pending || 0 }}</span>
            <span class="stat-label">待处理</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ summaryData.in_progress || 0 }}</span>
            <span class="stat-label">进行中</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ summaryData.completed || 0 }}</span>
            <span class="stat-label">已完成</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建/编辑任务对话框 -->
    <div v-if="showCreateTaskDialog || showEditTaskDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>{{ showEditTaskDialog ? '编辑任务' : '创建任务' }}</h2>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-content">
          <form @submit.prevent="saveTask">
            <div class="form-group">
              <label>任务标题</label>
              <input 
                v-model="taskForm.title" 
                type="text" 
                required 
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>任务描述</label>
              <textarea 
                v-model="taskForm.description" 
                rows="3" 
                class="form-textarea"
              ></textarea>
            </div>
            <div class="form-group">
              <label>优先级</label>
              <select v-model="taskForm.priority" class="form-select">
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
              </select>
            </div>
            <div class="form-group">
              <label>截止日期</label>
              <input 
                v-model="taskForm.deadline" 
                type="date" 
                required 
                class="form-input"
              />
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeDialog">取消</button>
              <button type="submit" class="btn btn-primary">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { taskApi } from '@/api/modules';

export default {
  name: 'Tasks',
  setup() {
    const tasks = ref([]);
    const summaryData = ref({});
    const filterStatus = ref('');
    const filterKeyword = ref('');
    const showCreateTaskDialog = ref(false);
    const showEditTaskDialog = ref(false);
    const currentTaskId = ref(null);
    const taskForm = ref({
      title: '',
      description: '',
      priority: 'medium',
      deadline: new Date().toISOString().split('T')[0]
    });
    
    // 获取任务列表
    const fetchTasks = async () => {
      try {
        const response = await taskApi.getAll();
        tasks.value = response.data.tasks || [];
      } catch (error) {
        console.error('获取任务列表失败:', error);
      }
    };
    
    // 获取任务统计
    const fetchTaskSummary = async () => {
      try {
        const response = await taskApi.getSummary();
        summaryData.value = response.data || {};
      } catch (error) {
        console.error('获取任务统计失败:', error);
      }
    };
    
    // 过滤任务
    const filteredTasks = computed(() => {
      return tasks.value.filter(task => {
        const statusMatch = !filterStatus.value || task.status === filterStatus.value;
        const keywordMatch = !filterKeyword.value || 
          task.title.toLowerCase().includes(filterKeyword.value.toLowerCase()) ||
          task.description.toLowerCase().includes(filterKeyword.value.toLowerCase());
        return statusMatch && keywordMatch;
      });
    });
    
    // 完成任务
    const completeTask = async (taskId) => {
      try {
        await taskApi.complete(taskId);
        fetchTasks();
        fetchTaskSummary();
      } catch (error) {
        console.error('完成任务失败:', error);
      }
    };
    
    // 编辑任务
    const editTask = (task) => {
      currentTaskId.value = task.task_id;
      taskForm.value = {
        title: task.title,
        description: task.description,
        priority: task.priority,
        deadline: task.deadline.split('T')[0]
      };
      showEditTaskDialog.value = true;
    };
    
    // 删除任务
    const deleteTask = async (taskId) => {
      if (confirm('确定要删除这个任务吗？')) {
        try {
          await taskApi.delete(taskId);
          fetchTasks();
          fetchTaskSummary();
        } catch (error) {
          console.error('删除任务失败:', error);
        }
      }
    };
    
    // 保存任务
    const saveTask = async () => {
      try {
        if (showEditTaskDialog.value) {
          await taskApi.update(currentTaskId.value, taskForm.value);
        } else {
          await taskApi.create(taskForm.value);
        }
        closeDialog();
        fetchTasks();
        fetchTaskSummary();
      } catch (error) {
        console.error('保存任务失败:', error);
      }
    };
    
    // 关闭对话框
    const closeDialog = () => {
      showCreateTaskDialog.value = false;
      showEditTaskDialog.value = false;
      currentTaskId.value = null;
      taskForm.value = {
        title: '',
        description: '',
        priority: 'medium',
        deadline: new Date().toISOString().split('T')[0]
      };
    };
    
    // 生成工作摘要
    const generateWorkSummary = async () => {
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 7);
      const endDate = new Date();
      
      try {
        const response = await taskApi.generateWorkSummary(
          startDate.toISOString().split('T')[0],
          endDate.toISOString().split('T')[0]
        );
        alert('工作摘要生成成功:\n' + response.data.summary);
      } catch (error) {
        console.error('生成工作摘要失败:', error);
      }
    };
    
    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        'pending': '待处理',
        'in_progress': '进行中',
        'completed': '已完成'
      };
      return statusMap[status] || status;
    };
    
    // 获取优先级文本
    const getPriorityText = (priority) => {
      const priorityMap = {
        'low': '低优先级',
        'medium': '中优先级',
        'high': '高优先级'
      };
      return priorityMap[priority] || priority;
    };
    
    // 格式化日期
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('zh-CN');
    };
    
    // 初始化
    onMounted(() => {
      fetchTasks();
      fetchTaskSummary();
    });
    
    return {
      tasks,
      summaryData,
      filterStatus,
      filterKeyword,
      showCreateTaskDialog,
      showEditTaskDialog,
      taskForm,
      filteredTasks,
      completeTask,
      editTask,
      deleteTask,
      saveTask,
      closeDialog,
      generateWorkSummary,
      getStatusText,
      getPriorityText,
      formatDate
    };
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.tasks-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tasks-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.tasks-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
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

.btn-danger {
  background: #fff1f0;
  color: #f5222d;
}

.btn-danger:hover {
  background: #ffccc7;
}

.tasks-filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.filter-select, .filter-input {
  padding: 10px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
}

.filter-select:focus, .filter-input:focus {
  outline: none;
  border-color: rgb(0, 101, 105);
  box-shadow: 0 0 0 2px rgba(0,101,105,0.1);
}

.filter-select {
  min-width: 150px;
}

.filter-input {
  flex: 1;
  max-width: 400px;
}

.tasks-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.task-card {
  background-color: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  transition: all 0.3s;
  cursor: pointer;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: rgb(0, 101, 105);
  transform: translateY(-2px);
}

.task-card.pending {
  border-left: 4px solid #fa8c16;
}

.task-card.in_progress {
  border-left: 4px solid #1890ff;
}

.task-card.completed {
  border-left: 4px solid #52c41a;
  opacity: 0.9;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.task-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.task-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.task-status[data-status="pending"] {
  background: #fff7e6;
  color: #fa8c16;
}

.task-status[data-status="in_progress"] {
  background: #e6f7ff;
  color: #1890ff;
}

.task-status[data-status="completed"] {
  background: #f6ffed;
  color: #52c41a;
}

.task-content {
  margin-bottom: 15px;
}

.task-content p {
  margin: 0 0 10px 0;
  color: #666;
  line-height: 1.5;
  font-size: 14px;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.task-priority {
  padding: 2px 8px;
  border-radius: 4px;
  background: #f5f7fa;
}

.task-priority[data-priority="high"] {
  background: #fff1f0;
  color: #f5222d;
}

.task-priority[data-priority="medium"] {
  background: #fff7e6;
  color: #fa8c16;
}

.task-priority[data-priority="low"] {
  background: #f6ffed;
  color: #52c41a;
}

.task-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.tasks-summary {
  background-color: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.summary-card h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: linear-gradient(135deg, rgb(0, 101, 105) 0%, rgb(0, 130, 136) 100%);
  border-radius: 8px;
  color: white;
}

.stat-value {
  display: block;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: #999;
  background-color: #fafafa;
  border: 1px dashed #e8e8e8;
  border-radius: 8px;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.dialog {
  background-color: #fff;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e8e8e8;
}

.dialog-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  line-height: 1;
}

.dialog-close:hover {
  color: #333;
}

.dialog-content {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.form-input, .form-textarea, .form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
  font-family: inherit;
}

.form-input:focus, .form-textarea:focus, .form-select:focus {
  outline: none;
  border-color: rgb(0, 101, 105);
  box-shadow: 0 0 0 2px rgba(0,101,105,0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>

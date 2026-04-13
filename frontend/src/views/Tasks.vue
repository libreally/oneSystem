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
          <span class="task-status">{{ getStatusText(task.status) }}</span>
        </div>
        <div class="task-content">
          <p>{{ task.description }}</p>
          <div class="task-meta">
            <span class="task-priority">{{ getPriorityText(task.priority) }}</span>
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
.tasks-container {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.tasks-header h1 {
  margin: 0;
  font-size: 1.75rem;
  color: #333;
}

.tasks-actions {
  display: flex;
  gap: 0.75rem;
}

.tasks-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.filter-select, .filter-input {
  padding: 0.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 1rem;
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
  gap: 1rem;
  margin-bottom: 2rem;
}

.task-card {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.task-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.task-card.pending {
  border-left: 4px solid #ffc107;
}

.task-card.in_progress {
  border-left: 4px solid #2196f3;
}

.task-card.completed {
  border-left: 4px solid #4caf50;
  opacity: 0.8;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.task-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: #333;
  flex: 1;
}

.task-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.task-status:contains('待处理') {
  background-color: #fff3cd;
  color: #856404;
}

.task-status:contains('进行中') {
  background-color: #cce7ff;
  color: #004085;
}

.task-status:contains('已完成') {
  background-color: #d4edda;
  color: #155724;
}

.task-content {
  margin-bottom: 1rem;
}

.task-content p {
  margin: 0 0 0.75rem 0;
  color: #666;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #888;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.tasks-summary {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary-card h3 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  color: #333;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #2196f3;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem;
  color: #888;
  background-color: #f9f9f9;
  border: 1px dashed #e0e0e0;
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
  z-index: 1000;
}

.dialog {
  background-color: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.dialog-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #333;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #888;
  padding: 0;
  line-height: 1;
}

.dialog-content {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-input, .form-textarea, .form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #2196f3;
  color: white;
}

.btn-primary:hover {
  background-color: #1976d2;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #e0e0e0;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover {
  background-color: #d32f2f;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}
</style>

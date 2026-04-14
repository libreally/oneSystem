<template>
  <div class="page active">
    <div class="card">
      <div class="card-title">
        <span>⏰ 定时任务管理</span>
        <button class="btn btn-primary" @click="showCreateModal = true">+ 新建任务</button>
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
        <tbody v-if="tasks.length > 0">
          <tr v-for="task in tasks" :key="task.task_id">
            <td>{{ task.name }}</td>
            <td>{{ formatRepeatType(task) }}</td>
            <td>{{ formatDateTime(task.next_execution) }}</td>
            <td>
              <span :class="['badge', task.enabled ? 'badge-success' : 'badge-warning']">
                {{ task.enabled ? '运行中' : '已暂停' }}
              </span>
            </td>
            <td>
              <button class="btn btn-secondary" @click="editTask(task)">编辑</button>
              <button class="btn btn-secondary" @click="toggleTaskStatus(task)">
                {{ task.enabled ? '暂停' : '启用' }}
              </button>
              <button class="btn btn-secondary" @click="executeTask(task.task_id)">执行</button>
              <button class="btn btn-danger" @click="deleteTask(task.task_id)">删除</button>
              <button class="btn btn-secondary" @click="viewHistory(task.task_id)">历史</button>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td colspan="5" class="text-center">暂无任务</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新建任务模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>新建定时任务</h3>
          <button class="btn-close" @click="closeCreateModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createTask">
            <div class="form-group">
              <label>任务名称 *</label>
              <input type="text" v-model="newTask.name" required placeholder="请输入任务名称">
            </div>
            <div class="form-group">
              <label>任务描述</label>
              <textarea v-model="newTask.description" placeholder="请输入任务描述"></textarea>
            </div>
            <div class="form-group">
              <label>执行周期 *</label>
              <select v-model="newTask.repeat_type" required>
                <option value="once">仅执行一次</option>
                <option value="daily">每天</option>
                <option value="weekly">每周</option>
                <option value="monthly">每月</option>
                <option value="hourly">每小时</option>
                <option value="custom">自定义间隔</option>
              </select>
            </div>
            
            <!-- 时间设置 -->
            <div class="form-group" v-if="newTask.repeat_type !== 'once'">
              <label>执行时间</label>
              <div class="time-setting">
                <input type="number" v-model="newTask.hour" min="0" max="23" placeholder="时">
                <span>:</span>
                <input type="number" v-model="newTask.minute" min="0" max="59" placeholder="分">
              </div>
            </div>
            
            <!-- 周设置 -->
            <div class="form-group" v-if="newTask.repeat_type === 'weekly'">
              <label>星期几</label>
              <select v-model="newTask.day_of_week">
                <option value="0">周一</option>
                <option value="1">周二</option>
                <option value="2">周三</option>
                <option value="3">周四</option>
                <option value="4">周五</option>
                <option value="5">周六</option>
                <option value="6">周日</option>
              </select>
            </div>
            
            <!-- 月设置 -->
            <div class="form-group" v-if="newTask.repeat_type === 'monthly'">
              <label>每月几号</label>
              <input type="number" v-model="newTask.day_of_month" min="1" max="31">
            </div>
            
            <!-- 自定义间隔设置 -->
            <div class="form-group" v-if="newTask.repeat_type === 'custom'">
              <label>间隔时间（分钟）</label>
              <input type="number" v-model="newTask.interval_minutes" min="1">
            </div>
            
            <div class="form-group">
              <label>执行动作</label>
              <input type="text" v-model="newTask.action" placeholder="请输入执行动作">
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeCreateModal">取消</button>
              <button type="submit" class="btn btn-primary">创建任务</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 编辑任务模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑定时任务</h3>
          <button class="btn-close" @click="closeEditModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateTask">
            <div class="form-group">
              <label>任务名称 *</label>
              <input type="text" v-model="editTaskData.name" required placeholder="请输入任务名称">
            </div>
            <div class="form-group">
              <label>任务描述</label>
              <textarea v-model="editTaskData.description" placeholder="请输入任务描述"></textarea>
            </div>
            <div class="form-group">
              <label>执行周期 *</label>
              <select v-model="editTaskData.repeat_type" required>
                <option value="once">仅执行一次</option>
                <option value="daily">每天</option>
                <option value="weekly">每周</option>
                <option value="monthly">每月</option>
                <option value="hourly">每小时</option>
                <option value="custom">自定义间隔</option>
              </select>
            </div>
            
            <!-- 时间设置 -->
            <div class="form-group" v-if="editTaskData.repeat_type !== 'once'">
              <label>执行时间</label>
              <div class="time-setting">
                <input type="number" v-model="editTaskData.hour" min="0" max="23" placeholder="时">
                <span>:</span>
                <input type="number" v-model="editTaskData.minute" min="0" max="59" placeholder="分">
              </div>
            </div>
            
            <!-- 周设置 -->
            <div class="form-group" v-if="editTaskData.repeat_type === 'weekly'">
              <label>星期几</label>
              <select v-model="editTaskData.day_of_week">
                <option value="0">周一</option>
                <option value="1">周二</option>
                <option value="2">周三</option>
                <option value="3">周四</option>
                <option value="4">周五</option>
                <option value="5">周六</option>
                <option value="6">周日</option>
              </select>
            </div>
            
            <!-- 月设置 -->
            <div class="form-group" v-if="editTaskData.repeat_type === 'monthly'">
              <label>每月几号</label>
              <input type="number" v-model="editTaskData.day_of_month" min="1" max="31">
            </div>
            
            <!-- 自定义间隔设置 -->
            <div class="form-group" v-if="editTaskData.repeat_type === 'custom'">
              <label>间隔时间（分钟）</label>
              <input type="number" v-model="editTaskData.interval_minutes" min="1">
            </div>
            
            <div class="form-group">
              <label>执行动作</label>
              <input type="text" v-model="editTaskData.action" placeholder="请输入执行动作">
            </div>
            
            <div class="form-group">
              <label>状态</label>
              <select v-model="editTaskData.enabled">
                <option value="true">启用</option>
                <option value="false">禁用</option>
              </select>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeEditModal">取消</button>
              <button type="submit" class="btn btn-primary">更新任务</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 任务历史模态框 -->
    <div v-if="showHistoryModal" class="modal-overlay" @click="closeHistoryModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>任务执行历史</h3>
          <button class="btn-close" @click="closeHistoryModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="taskHistory.length > 0">
            <table class="history-table">
              <thead>
                <tr>
                  <th>执行时间</th>
                  <th>状态</th>
                  <th>结果</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in taskHistory" :key="item.execution_id">
                  <td>{{ formatDateTime(item.start_time) }}</td>
                  <td>
                    <span :class="['badge', item.status === 'success' ? 'badge-success' : 'badge-warning']">
                      {{ item.status === 'success' ? '成功' : '失败' }}
                    </span>
                  </td>
                  <td class="result-cell">
                    <div class="result-content">{{ formatResult(item.result, item.error) }}</div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center">
            暂无执行历史
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { scheduleApi } from '../api/modules';

const tasks = ref([]);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showHistoryModal = ref(false);
const newTask = ref({
  name: '',
  description: '',
  repeat_type: 'daily',
  hour: 9,
  minute: 0,
  day_of_week: 0,
  day_of_month: 1,
  interval_minutes: 60,
  action: '',
  params: {}
});
const editTaskData = ref({
  task_id: '',
  name: '',
  description: '',
  repeat_type: 'daily',
  hour: 9,
  minute: 0,
  day_of_week: 0,
  day_of_month: 1,
  interval_minutes: 60,
  action: '',
  params: {},
  enabled: true
});
const taskHistory = ref([]);

onMounted(() => {
  loadTasks();
});

const loadTasks = async () => {
  try {
    const response = await scheduleApi.getAll();
    if (response.success) {
      tasks.value = response.data.tasks;
    }
  } catch (error) {
    console.error('加载任务失败:', error);
  }
};

const formatRepeatType = (task) => {
  const { repeat_type, hour, minute, day_of_week, day_of_month, interval_minutes } = task;
  
  switch (repeat_type) {
    case 'once':
      return '仅执行一次';
    case 'daily':
      return `每天 ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    case 'weekly':
      const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
      return `每周${weekdays[day_of_week]} ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    case 'monthly':
      return `每月${day_of_month}日 ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    case 'hourly':
      return `每小时 ${minute.toString().padStart(2, '0')}分`;
    case 'custom':
      return `每${interval_minutes}分钟`;
    default:
      return repeat_type;
  }
};

const formatDateTime = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

const formatResult = (result, error) => {
  if (error) {
    return error;
  }
  if (!result) {
    return '-';
  }
  
  // 如果 result 是字符串，直接返回
  if (typeof result === 'string') {
    return result;
  }
  
  // 如果 result 是对象，检查是否包含 llm_response 字段
  if (result.llm_response) {
    return result.llm_response;
  }
  
  // 其他情况，使用 JSON.stringify 并美化
  return JSON.stringify(result, null, 2);
};

const toggleTaskStatus = async (task) => {
  try {
    if (task.enabled) {
      await scheduleApi.disable(task.task_id);
    } else {
      await scheduleApi.enable(task.task_id);
    }
    await loadTasks();
  } catch (error) {
    console.error('切换任务状态失败:', error);
  }
};

const deleteTask = async (taskId) => {
  if (confirm('确定要删除这个任务吗？')) {
    try {
      await scheduleApi.deleteTask(taskId);
      await loadTasks();
    } catch (error) {
      console.error('删除任务失败:', error);
    }
  }
};

const editTask = (task) => {
  // 填充编辑表单数据
  editTaskData.value = {
    task_id: task.task_id,
    name: task.name,
    description: task.description,
    repeat_type: task.repeat_type,
    hour: task.hour,
    minute: task.minute,
    day_of_week: task.day_of_week,
    day_of_month: task.day_of_month,
    interval_minutes: task.interval_minutes,
    action: task.action,
    params: task.params || {},
    enabled: task.enabled
  };
  showEditModal.value = true;
};

const viewHistory = async (taskId) => {
  try {
    const response = await scheduleApi.getHistory(taskId);
    if (response.success) {
      taskHistory.value = response.data.history;
      showHistoryModal.value = true;
    }
  } catch (error) {
    console.error('加载历史失败:', error);
  }
};

const closeCreateModal = () => {
  showCreateModal.value = false;
  // 重置表单
  newTask.value = {
    name: '',
    description: '',
    repeat_type: 'daily',
    hour: 9,
    minute: 0,
    day_of_week: 0,
    day_of_month: 1,
    interval_minutes: 60,
    action: '',
    params: {}
  };
};

const closeEditModal = () => {
  showEditModal.value = false;
};

const closeHistoryModal = () => {
  showHistoryModal.value = false;
  taskHistory.value = [];
};

const createTask = async () => {
  try {
    console.log('开始创建任务:', newTask.value);
    const response = await scheduleApi.create(newTask.value);
    console.log('创建任务响应:', response);
    if (response && response.success) {
      await loadTasks();
      closeCreateModal();
      console.log('任务创建成功');
    } else {
      alert('创建任务失败: ' + (response?.message || '未知错误'));
      console.error('创建任务失败:', response);
    }
  } catch (error) {
    console.error('创建任务失败:', error);
    console.error('错误详情:', error.response);
    alert('创建任务失败，请稍后重试');
  }
};

const updateTask = async () => {
  try {
    // 由于后端没有提供更新任务的API，我们需要先删除旧任务，再创建新任务
    await scheduleApi.deleteTask(editTaskData.value.task_id);
    
    // 创建新任务（使用相同的task_id）
    const taskData = {
      ...editTaskData.value,
      task_id: editTaskData.value.task_id
    };
    const response = await scheduleApi.create(taskData);
    
    if (response.success) {
      loadTasks();
      closeEditModal();
    } else {
      alert('更新任务失败: ' + response.message);
    }
  } catch (error) {
    console.error('更新任务失败:', error);
    alert('更新任务失败，请稍后重试');
  }
};

const executeTask = async (taskId) => {
  try {
    console.log('开始执行任务:', taskId);
    const response = await scheduleApi.execute(taskId);
    console.log('执行任务响应:', response);
    if (response.success) {
      alert('任务执行成功');
      // 刷新任务历史
      await viewHistory(taskId);
    } else {
      alert('任务执行失败: ' + response.message);
      console.error('执行任务失败:', response);
    }
  } catch (error) {
    console.error('执行任务失败:', error);
    console.error('错误详情:', error.response);
    alert('执行任务失败，请稍后重试');
  }
};
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
.btn-danger {
  background: #ff4d4f;
  color: white;
}
.text-center {
  text-align: center;
  padding: 20px;
  color: #999;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e8e8e8;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 20px;
}

/* 历史表格样式 */
.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.history-table th {
  background: #fafafa;
  font-weight: 600;
  font-size: 14px;
}

.history-table tr:hover {
  background: #f5f7fa;
}

/* 结果列样式 */
.history-table td:nth-child(3) {
  min-width: 300px;
  max-width: 500px;
  overflow: hidden;
}

.result-cell {
  padding: 0;
}

.result-content {
  padding: 12px;
  overflow-x: auto;
  overflow-y: auto;
  max-height: 200px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: rgb(0, 101, 105);
  box-shadow: 0 0 0 2px rgba(0, 101, 105, 0.2);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.time-setting {
  display: flex;
  align-items: center;
  gap: 10px;
}

.time-setting input {
  flex: 1;
  max-width: 80px;
}

.time-setting span {
  font-size: 16px;
  font-weight: 600;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e8e8e8;
}

/* 历史表格样式 */
.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.history-table th,
.history-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.history-table th {
  background: #fafafa;
  font-weight: 600;
}

.history-table tr:hover {
  background: #f5f7fa;
}

.history-table td:last-child {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

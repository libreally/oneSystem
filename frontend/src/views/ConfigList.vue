<template>
  <div class="page active">
    <div class="card">
      <div class="card-header">
        <button @click="goBack" class="back-btn">← 返回</button>
        <h2 class="card-title">⚙️ {{ getCategoryName(category) }}配置</h2>
        <button @click="showCreateForm" class="create-btn">
          + 新建配置
        </button>
      </div>
      
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="configs.length === 0" class="empty-state">
        暂无配置，请点击"新建配置"按钮创建
      </div>
      <div v-else class="config-grid">
        <div 
          v-for="config in configs" 
          :key="config.data._metadata?.config_name || Math.random()"
          @click="viewConfigDetail(config)"
          class="config-card"
        >
          <div class="config-card-header">
            <h4 class="config-card-name">{{ config.data._metadata?.config_name || '未命名配置' }}</h4>
            <span class="config-type-badge">{{ config.type === 'personal' ? '个人' : '公共' }}</span>
          </div>
          <div class="config-card-meta">
            <span class="config-time">{{ formatTime(config.data._metadata?.updated_at) }}</span>
          </div>
          <div v-if="config.data.description" class="config-card-desc">
            {{ config.data.description }}
          </div>
          <div class="config-card-actions">
            <button @click.stop="editConfig(config)" class="action-btn edit-btn">编辑</button>
            <button @click.stop="deleteConfig(config)" class="action-btn delete-btn">删除</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建/编辑配置对话框 -->
    <div v-if="showCreateDialog || showEditDialog" class="dialog-overlay">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ showEditDialog ? '编辑配置' : '新建配置' }}</h3>
          <button @click="closeDialog" class="close-btn">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>配置名称</label>
            <input v-model="configForm.config_name" type="text" placeholder="请输入配置名称" />
          </div>
          <div class="form-group">
            <label>配置类型</label>
            <select v-model="configForm.config_type" disabled>
              <option value="document_template">📄 公文模板</option>
              <option value="sensitive_word">🚫 敏感词库</option>
              <option value="supervision_rule">⏱️ 督办规则</option>
              <option value="recommendation_rule">🎯 智能推荐规则</option>
              <option value="scheduler">⏰ 调度器配置</option>
              <option value="user_preference">👤 用户偏好</option>
            </select>
          </div>
          <div class="form-group">
            <label>配置内容</label>
            <textarea v-model="configForm.config_data" rows="10" placeholder="请输入JSON格式的配置内容"></textarea>
          </div>
          <div class="form-group">
            <label>自然语言描述</label>
            <textarea v-model="configForm.description" rows="4" placeholder="请用自然语言描述此配置的用途和功能"></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="closeDialog" class="cancel-btn">取消</button>
          <button @click="saveConfig" class="save-btn">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../api/index.js';

const route = useRoute();
const router = useRouter();

const configCategories = [
  {
    value: 'document_template',
    icon: '📄',
    name: '公文模板',
    description: '管理公文类型、标题格式、字体字号、红头样式等'
  },
  {
    value: 'sensitive_word',
    icon: '🚫',
    name: '敏感词库',
    description: '维护敏感词库、分类管理、处理规则设置'
  },
  {
    value: 'supervision_rule',
    icon: '⏱️',
    name: '督办规则',
    description: '配置任务状态机、流转路径、提醒规则'
  },
  {
    value: 'recommendation_rule',
    icon: '🎯',
    name: '智能推荐规则',
    description: '设置推荐触发条件、展示规则、推荐对象'
  },
  {
    value: 'scheduler',
    icon: '⏰',
    name: '调度器配置',
    description: '配置定时任务、重复规则、执行参数'
  },
  {
    value: 'user_preference',
    icon: '👤',
    name: '用户偏好',
    description: '设置用户界面偏好、默认行为、通知设置'
  }
];

const category = computed(() => route.params.category || '');
const configs = ref([]);
const loading = ref(false);
const showCreateDialog = ref(false);
const showEditDialog = ref(false);

const configForm = ref({
  config_type: '',
  config_name: '',
  config_data: '',
  description: ''
});

const loadConfigs = async () => {
  if (!category.value) return;
  
  loading.value = true;
  try {
    const response = await apiClient.get(`/config/list/${category.value}`, {
      params: { user_id: '1' } // 暂时使用固定用户ID
    });
    if (response.success) {
      configs.value = response.data;
    }
  } catch (error) {
    console.error('加载配置失败:', error);
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.push('/config');
};

const showCreateForm = () => {
  // 获取默认配置
  const defaultConfig = getDefaultConfig(category.value);
  configForm.value = {
    config_type: category.value,
    config_name: '',
    config_data: JSON.stringify(defaultConfig, null, 2),
    description: ''
  };
  showCreateDialog.value = true;
  showEditDialog.value = false;
};

const getDefaultConfig = (configType) => {
  const defaultConfigs = {
    'document_template': {
      'title_format': '【{title}】',
      'font': 'SimSun',
      'font_size': 12,
      'line_spacing': 1.5,
      'margin': {
        'top': 2.54,
        'bottom': 2.54,
        'left': 3.17,
        'right': 3.17
      },
      'header': '',
      'footer': '',
      'signature': ''
    },
    'sensitive_word': {
      'words': [],
      'categories': ['政治', '色情', '暴力'],
      'action': 'mark',
      'replace_with': '[敏感词]'
    },
    'supervision_rule': {
      'states': ['待处理', '处理中', '已完成', '已驳回'],
      'transitions': {
        '待处理': ['处理中'],
        '处理中': ['已完成', '已驳回'],
        '已驳回': ['处理中']
      },
      'deadline_days': 7,
      'reminder_days': 3
    },
    'recommendation_rule': {
      'triggers': {
        'time': [],
        'keywords': [],
        'actions': []
      },
      'priority': 'medium'
    },
    'scheduler': {
      'repeat_types': ['once', 'daily', 'weekly', 'monthly'],
      'default_time': '09:00',
      'max_retries': 3,
      'retry_interval': 60
    },
    'user_preference': {
      'preferences': {
        'default_doc_type': '通知',
        'auto_save': true,
        'notification_enabled': true
      }
    }
  };
  return defaultConfigs[configType] || {};
};

const viewConfigDetail = (config) => {
  const configType = config.data._metadata?.config_type || category.value;
  const configName = config.data._metadata?.config_name || '';
  router.push(`/config/${configType}/${configName}`);
};

const editConfig = (config) => {
  configForm.value = {
    config_type: config.data._metadata?.config_type || category.value,
    config_name: config.data._metadata?.config_name || '',
    config_data: JSON.stringify(config.data, null, 2),
    description: config.data.description || ''
  };
  showEditDialog.value = true;
  showCreateDialog.value = false;
};

const deleteConfig = async (config) => {
  if (confirm('确定要删除这个配置吗？')) {
    try {
      const configType = config.data._metadata?.config_type || category.value;
      const configName = config.data._metadata?.config_name || '';
      const response = await apiClient.delete(`/config/${configType}/${configName}`, {
        params: { user_id: '1' }
      });
      if (response.success) {
        loadConfigs();
      }
    } catch (error) {
      console.error('删除配置失败:', error);
    }
  }
};

const saveConfig = async () => {
  try {
    let response;
    const configData = JSON.parse(configForm.value.config_data);
    
    // 添加自然语言描述
    if (configForm.value.description) {
      configData.description = configForm.value.description;
    }
    
    if (showEditDialog.value) {
      // 编辑配置
      response = await apiClient.post(`/config/${configForm.value.config_type}/${configForm.value.config_name}`, {
        user_id: '1',
        config_data: configData
      });
    } else {
      // 创建配置
      response = await apiClient.post(`/config/${configForm.value.config_type}/${configForm.value.config_name}`, {
        user_id: '1',
        config_data: configData
      });
    }
    
    if (response.success) {
      closeDialog();
      loadConfigs();
    }
  } catch (error) {
    console.error('保存配置失败:', error);
  }
};

const closeDialog = () => {
  showCreateDialog.value = false;
  showEditDialog.value = false;
};

const formatTime = (timeString) => {
  if (!timeString) return '未知时间';
  const date = new Date(timeString);
  return date.toLocaleString();
};

const getCategoryName = (categoryValue) => {
  const category = configCategories.find(c => c.value === categoryValue);
  return category ? category.name : categoryValue;
};

onMounted(() => {
  loadConfigs();
});
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

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8e8e8;
}
.back-btn {
  background: none;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 6px 12px;
  margin-right: 16px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}
.back-btn:hover {
  border-color: rgb(0, 101, 105);
  color: rgb(0, 101, 105);
}
.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  flex: 1;
}
.create-btn {
  padding: 8px 16px;
  background: rgb(0, 101, 105);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}
.create-btn:hover {
  background: rgb(0, 81, 85);
}

/* 加载和空状态 */
.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}
.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
  border: 1px dashed #e8e8e8;
  border-radius: 4px;
}

/* 配置网格 */
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}
.config-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
}
.config-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: rgb(0, 101, 105);
}
.config-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}
.config-card-name {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  flex: 1;
}
.config-card-meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}
.config-card-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
  line-height: 1.4;
}
.config-card-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 按钮样式 */
.action-btn {
  padding: 4px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}
.edit-btn {
  background: #f0f9ff;
  color: #1677ff;
  border-color: #91d5ff;
}
.edit-btn:hover {
  background: #e6f7ff;
}
.delete-btn {
  background: #fff1f0;
  color: #ff4d4f;
  border-color: #ffb3b3;
}
.delete-btn:hover {
  background: #fff2f0;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.dialog {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e8e8e8;
}
.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}
.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
}
.dialog-body {
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-group textarea {
  font-family: monospace;
  resize: vertical;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e8e8e8;
  background: #fafafa;
}
.cancel-btn {
  padding: 8px 16px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}
.save-btn {
  padding: 8px 16px;
  background: rgb(0, 101, 105);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}
.save-btn:hover {
  background: rgb(0, 81, 85);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .create-btn {
    align-self: flex-end;
  }
}
</style>
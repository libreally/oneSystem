<template>
  <div class="page active">
    <div class="card config-detail">
      <div class="detail-header">
        <button @click="goBack" class="back-btn">← 返回</button>
        <h3>{{ config?.data._metadata?.config_name || '配置详情' }}</h3>
        <div class="detail-actions">
          <button @click="importConfig" class="action-btn import-btn">📤 导入</button>
          <button @click="exportConfig" class="action-btn export-btn">📥 导出</button>
          <button @click="editConfig" class="action-btn edit-btn">编辑</button>
          <button @click="deleteConfig" class="action-btn delete-btn">删除</button>
        </div>
      </div>
      
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="!config" class="empty-state">
        配置不存在
      </div>
      <div v-else class="detail-body">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>配置类型</label>
              <span>{{ getCategoryName(config.data._metadata?.config_type) }}</span>
            </div>
            <div class="info-item">
              <label>配置名称</label>
              <span>{{ config.data._metadata?.config_name }}</span>
            </div>
            <div class="info-item">
              <label>类型</label>
              <span>{{ config.type === 'personal' ? '个人配置' : '公共配置' }}</span>
            </div>
            <div class="info-item">
              <label>更新时间</label>
              <span>{{ formatTime(config.data._metadata?.updated_at) }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="config.data.description" class="detail-section">
          <h4>配置描述</h4>
          <div class="description-content">
            {{ config.data.description }}
          </div>
        </div>
        
        <div v-if="config.data.templates && config.data.templates.length > 0" class="detail-section">
          <h4>模板文件</h4>
          <div class="templates-list">
            <div v-for="(template, index) in config.data.templates" :key="index" class="template-item">
              <div class="template-type">{{ getTemplateTypeName(template.type) }}</div>
              <div class="template-path">{{ template.path }}</div>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>配置内容</h4>
          <div class="config-content">
            <pre>{{ JSON.stringify(addCommentsToConfig(config.data), null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑配置对话框 -->
    <div v-if="showEditDialog" class="dialog-overlay">
      <div class="dialog">
        <div class="dialog-header">
          <h3>编辑配置</h3>
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
          <div class="form-group">
            <label>模板文件</label>
            <div class="template-files">
              <div v-for="(template, index) in configForm.templates" :key="index" class="template-item">
                <input v-model="template.path" type="text" placeholder="模板文件路径" />
                <select v-model="template.type">
                  <option value="word">Word</option>
                  <option value="excel">Excel</option>
                  <option value="pdf">PDF</option>
                  <option value="other">其他</option>
                </select>
                <button @click="removeTemplate(index)" class="remove-btn">×</button>
              </div>
              <button @click="addTemplate" class="add-btn">+ 添加模板</button>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="closeDialog" class="cancel-btn">取消</button>
          <button @click="saveConfig" class="save-btn">保存</button>
        </div>
      </div>
    </div>
    
    <!-- 导入配置对话框 -->
    <div v-if="showImportDialog" class="dialog-overlay">
      <div class="dialog">
        <div class="dialog-header">
          <h3>导入配置</h3>
          <button @click="closeImportExportDialog" class="close-btn">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>配置名称</label>
            <input v-model="importForm.config_name" type="text" placeholder="请输入配置名称" />
          </div>
          <div class="form-group">
            <label>配置类型</label>
            <select v-model="importForm.config_type" disabled>
              <option value="document_template">📄 公文模板</option>
              <option value="sensitive_word">🚫 敏感词库</option>
              <option value="supervision_rule">⏱️ 督办规则</option>
              <option value="recommendation_rule">🎯 智能推荐规则</option>
              <option value="scheduler">⏰ 调度器配置</option>
              <option value="user_preference">👤 用户偏好</option>
            </select>
          </div>
          <div class="form-group">
            <label>文件路径</label>
            <input v-model="importForm.file_path" type="text" placeholder="请输入配置文件路径" />
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="closeImportExportDialog" class="cancel-btn">取消</button>
          <button @click="saveImportConfig" class="save-btn">导入</button>
        </div>
      </div>
    </div>
    
    <!-- 导出配置对话框 -->
    <div v-if="showExportDialog" class="dialog-overlay">
      <div class="dialog">
        <div class="dialog-header">
          <h3>导出配置</h3>
          <button @click="closeImportExportDialog" class="close-btn">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>配置名称</label>
            <input v-model="exportForm.config_name" type="text" placeholder="请输入配置名称" />
          </div>
          <div class="form-group">
            <label>配置类型</label>
            <select v-model="exportForm.config_type" disabled>
              <option value="document_template">📄 公文模板</option>
              <option value="sensitive_word">🚫 敏感词库</option>
              <option value="supervision_rule">⏱️ 督办规则</option>
              <option value="recommendation_rule">🎯 智能推荐规则</option>
              <option value="scheduler">⏰ 调度器配置</option>
              <option value="user_preference">👤 用户偏好</option>
            </select>
          </div>
          <div class="form-group">
            <label>输出路径</label>
            <input v-model="exportForm.output_path" type="text" placeholder="请输入输出文件路径" />
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="closeImportExportDialog" class="cancel-btn">取消</button>
          <button @click="saveExportConfig" class="save-btn">导出</button>
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

const config = ref(null);
const loading = ref(false);
const showEditDialog = ref(false);
const showImportDialog = ref(false);
const showExportDialog = ref(false);

const configForm = ref({
  config_type: '',
  config_name: '',
  config_data: '',
  description: '',
  templates: []
});

const importForm = ref({
  config_type: '',
  config_name: '',
  file_path: ''
});

const exportForm = ref({
  config_type: '',
  config_name: '',
  output_path: ''
});

const loadConfig = async () => {
  const { configType, configName } = route.params;
  if (!configType || !configName) return;
  
  loading.value = true;
  try {
    const response = await apiClient.get(`/config/${configType}/${configName}`, {
      params: { user_id: '1' }
    });
    if (response.success) {
      config.value = {
        type: 'personal', // 暂时默认为个人配置
        data: response.data
      };
    }
  } catch (error) {
    console.error('加载配置失败:', error);
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  const { configType } = route.params;
  router.push(`/config/${configType}`);
};

const editConfig = () => {
  if (!config.value) return;
  
  configForm.value = {
    config_type: config.value.data._metadata?.config_type || '',
    config_name: config.value.data._metadata?.config_name || '',
    config_data: JSON.stringify(config.value.data, null, 2),
    description: config.value.data.description || '',
    templates: config.value.data.templates || []
  };
  showEditDialog.value = true;
};

const deleteConfig = async () => {
  if (!config.value) return;
  
  if (confirm('确定要删除这个配置吗？')) {
    try {
      const configType = config.value.data._metadata?.config_type;
      const configName = config.value.data._metadata?.config_name;
      const response = await apiClient.delete(`/config/${configType}/${configName}`, {
        params: { user_id: '1' }
      });
      if (response.success) {
        router.push(`/config/${configType}`);
      }
    } catch (error) {
      console.error('删除配置失败:', error);
    }
  }
};

const addTemplate = () => {
  configForm.value.templates.push({ path: '', type: 'word' });
};

const removeTemplate = (index) => {
  configForm.value.templates.splice(index, 1);
};

const saveConfig = async () => {
  try {
    const configData = JSON.parse(configForm.value.config_data);
    
    // 添加自然语言描述
    if (configForm.value.description) {
      configData.description = configForm.value.description;
    }
    
    // 添加模板文件
    if (configForm.value.templates.length > 0) {
      configData.templates = configForm.value.templates;
    }
    
    const response = await apiClient.post(`/config/${configForm.value.config_type}/${configForm.value.config_name}`, {
      user_id: '1',
      config_data: configData
    });
    
    if (response.success) {
      closeDialog();
      loadConfig();
    }
  } catch (error) {
    console.error('保存配置失败:', error);
  }
};

const closeDialog = () => {
  showEditDialog.value = false;
};

const importConfig = () => {
  if (!config.value) return;
  
  importForm.value = {
    config_type: config.value.data._metadata?.config_type || '',
    config_name: '',
    file_path: ''
  };
  showImportDialog.value = true;
};

const exportConfig = () => {
  if (!config.value) return;
  
  exportForm.value = {
    config_type: config.value.data._metadata?.config_type || '',
    config_name: config.value.data._metadata?.config_name || '',
    output_path: ''
  };
  showExportDialog.value = true;
};

const saveImportConfig = async () => {
  try {
    const response = await apiClient.post('/config/import', {
      config_type: importForm.value.config_type,
      config_name: importForm.value.config_name,
      file_path: importForm.value.file_path,
      user_id: '1'
    });
    if (response.success) {
      closeImportExportDialog();
    }
  } catch (error) {
    console.error('导入配置失败:', error);
  }
};

const saveExportConfig = async () => {
  try {
    const response = await apiClient.post('/config/export', {
      config_type: exportForm.value.config_type,
      config_name: exportForm.value.config_name,
      output_path: exportForm.value.output_path,
      user_id: '1'
    });
    if (response.success) {
      closeImportExportDialog();
    }
  } catch (error) {
    console.error('导出配置失败:', error);
  }
};

const closeImportExportDialog = () => {
  showImportDialog.value = false;
  showExportDialog.value = false;
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

const getTemplateTypeName = (templateType) => {
  const typeNames = {
    'word': 'Word',
    'excel': 'Excel',
    'pdf': 'PDF',
    'other': '其他'
  };
  return typeNames[templateType] || templateType;
};

const addCommentsToConfig = (configData) => {
  if (!configData || typeof configData !== 'object') return configData;
  
  const comments = {
    'document_template': {
      'title_format': '标题格式，支持{title}占位符',
      'font': '字体名称',
      'font_size': '字体大小',
      'line_spacing': '行间距',
      'margin': '页边距设置',
      'margin.top': '上边距',
      'margin.bottom': '下边距',
      'margin.left': '左边距',
      'margin.right': '右边距',
      'header': '页眉内容',
      'footer': '页脚内容',
      'signature': '签名信息'
    },
    'sensitive_word': {
      'words': '敏感词列表',
      'categories': '敏感词分类',
      'action': '处理动作（mark/block）',
      'replace_with': '替换文本'
    },
    'supervision_rule': {
      'states': '状态列表',
      'transitions': '状态流转规则',
      'deadline_days': '截止天数',
      'reminder_days': '提醒天数'
    },
    'recommendation_rule': {
      'triggers': '触发条件',
      'triggers.time': '时间触发条件',
      'triggers.keywords': '关键词触发条件',
      'triggers.actions': '动作触发条件',
      'priority': '优先级'
    },
    'scheduler': {
      'repeat_types': '重复类型',
      'default_time': '默认执行时间',
      'max_retries': '最大重试次数',
      'retry_interval': '重试间隔（秒）'
    },
    'user_preference': {
      'preferences': '用户偏好设置',
      'preferences.default_doc_type': '默认文档类型',
      'preferences.auto_save': '自动保存',
      'preferences.notification_enabled': '通知启用状态'
    }
  };
  
  const configType = configData._metadata?.config_type;
  const configComments = configType ? comments[configType] : {};
  
  const addComments = (obj, path = '') => {
    if (typeof obj !== 'object' || obj === null) return obj;
    
    const result = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const currentPath = path ? `${path}.${key}` : key;
        const comment = configComments[currentPath];
        
        if (comment) {
          result[`${key} // ${comment}`] = addComments(obj[key], currentPath);
        } else {
          result[key] = addComments(obj[key], currentPath);
        }
      }
    }
    return result;
  };
  
  return addComments(configData);
};

onMounted(() => {
  loadConfig();
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

/* 配置详情样式 */
.config-detail {
  margin-top: 20px;
}
.detail-header {
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
.detail-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
}
.detail-actions {
  display: flex;
  gap: 8px;
}
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
.detail-section {
  margin-bottom: 24px;
}
.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}
.info-item {
  background: #fafafa;
  padding: 12px;
  border-radius: 4px;
}
.info-item label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}
.info-item span {
  font-size: 14px;
  color: #333;
}
.description-content {
  background: #fafafa;
  padding: 16px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.4;
  color: #333;
}
.templates-list {
  background: #fafafa;
  padding: 16px;
  border-radius: 4px;
}
.template-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}
.template-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}
.template-type {
  background: rgb(0, 101, 105);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  margin-right: 12px;
  min-width: 60px;
  text-align: center;
}
.template-path {
  flex: 1;
  font-size: 14px;
  color: #333;
  word-break: break-all;
}
.config-content {
  background: #fafafa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}
.config-content pre {
  margin: 0;
  font-size: 13px;
  line-height: 1.4;
  color: #333;
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
.import-btn {
  background: #f6ffed;
  color: #52c41a;
  border-color: #b7eb8f;
}
.import-btn:hover {
  background: #f6ffed;
}
.export-btn {
  background: #e6f7ff;
  color: #1890ff;
  border-color: #91d5ff;
}
.export-btn:hover {
  background: #e6f7ff;
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

/* 模板文件样式 */
.template-files {
  margin-top: 8px;
}
.template-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}
.template-item input {
  flex: 2;
}
.template-item select {
  flex: 1;
}
.remove-btn {
  background: #fff1f0;
  color: #ff4d4f;
  border: 1px solid #ffb3b3;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
}
.remove-btn:hover {
  background: #fff2f0;
}
.add-btn {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 8px;
}
.add-btn:hover {
  background: #f6ffed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .detail-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
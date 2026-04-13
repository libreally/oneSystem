<template>
  <div class="page active">
    <div class="card">
      <div class="card-title">
        <span>🛠️ Skills 能力库</span>
        <div>
          <button class="btn btn-secondary" @click="importSkill">导入 Skill</button>
          <button class="btn btn-primary" @click="showCreateDialog = true">+ 创建新 Skill</button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <!-- 错误提示 -->
      <div v-else-if="error" class="error-message">
        <span>{{ error }}</span>
        <button class="btn btn-sm" @click="fetchSkills">重试</button>
      </div>

      <!-- 技能列表 -->
      <div v-else class="skill-list">
        <div 
          v-for="skill in skills" 
          :key="skill.id || skill.skill_id || skill.name"
          class="skill-card"
          @click="selectSkill(skill)"
        >
          <div class="skill-header">
            <div>
              <div class="skill-name">{{ getSkillIcon(skill) }} {{ skill.name }}</div>
              <div class="skill-desc">{{ skill.description }}</div>
            </div>
            <span class="badge badge-success">已启用</span>
          </div>
          <div class="skill-meta">
            <span>分类：{{ skill.category || '其他' }}</span>
            <span>版本：{{ skill.version || '1.0.0' }}</span>
            <span v-if="skill.created_at">创建时间：{{ formatDate(skill.created_at) }}</span>
            <span v-else-if="skill.registered_at">注册时间：{{ formatDate(skill.registered_at) }}</span>
          </div>
          <div class="skill-actions">
            <button class="btn btn-sm btn-primary" @click.stop="editSkill(skill)">编辑</button>
            <button class="btn btn-sm btn-danger" @click.stop="deleteSkill(skill)">删除</button>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="skills.length === 0" class="empty-state">
          <span>暂无技能，点击 "创建新 Skill" 开始添加</span>
        </div>
      </div>
    </div>

    <!-- 创建技能对话框 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click="showCreateDialog = false">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>创建新 Skill</h3>
          <button class="dialog-close" @click="showCreateDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <form @submit.prevent="handleCreateSkill">
            <div class="form-group">
              <label>技能 ID</label>
              <input 
                type="text" 
                v-model="newSkill.skill_id" 
                placeholder="请输入技能唯一标识"
                required
              >
            </div>
            <div class="form-group">
              <label>技能名称</label>
              <input 
                type="text" 
                v-model="newSkill.name" 
                placeholder="请输入技能名称"
                required
              >
            </div>
            <div class="form-group">
              <label>技能描述</label>
              <textarea 
                v-model="newSkill.description" 
                placeholder="请输入技能描述"
                rows="3"
                required
              ></textarea>
            </div>
            <div class="form-group">
              <label>分类</label>
              <select v-model="newSkill.category">
                <option value="文档处理">文档处理</option>
                <option value="敏感词检查">敏感词检查</option>
                <option value="数据合并">数据合并</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>版本</label>
              <input 
                type="text" 
                v-model="newSkill.version" 
                placeholder="例如：1.0.0"
                value="1.0.0"
              >
            </div>
            <div class="form-group">
              <label>技能代码（可选）</label>
              <textarea 
                v-model="newSkill.code" 
                placeholder="请输入技能代码（Python）"
                rows="5"
              ></textarea>
            </div>
            <div class="dialog-footer">
              <button type="button" class="btn btn-secondary" @click="showCreateDialog = false">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                {{ isSubmitting ? '提交中...' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 编辑技能对话框 -->
    <div v-if="showEditDialog" class="dialog-overlay" @click="showEditDialog = false">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>编辑 Skill</h3>
          <button class="dialog-close" @click="showEditDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <form @submit.prevent="handleEditSkill">
            <div class="form-group">
              <label>技能 ID</label>
              <input 
                type="text" 
                v-model="editSkillForm.skill_id" 
                placeholder="请输入技能唯一标识"
                required
                disabled
              >
            </div>
            <div class="form-group">
              <label>技能名称</label>
              <input 
                type="text" 
                v-model="editSkillForm.name" 
                placeholder="请输入技能名称"
                required
              >
            </div>
            <div class="form-group">
              <label>技能描述</label>
              <textarea 
                v-model="editSkillForm.description" 
                placeholder="请输入技能描述"
                rows="3"
                required
              ></textarea>
            </div>
            <div class="form-group">
              <label>分类</label>
              <select v-model="editSkillForm.category">
                <option value="文档处理">文档处理</option>
                <option value="敏感词检查">敏感词检查</option>
                <option value="数据合并">数据合并</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>版本</label>
              <input 
                type="text" 
                v-model="editSkillForm.version" 
                placeholder="例如：1.0.0"
              >
            </div>
            <div class="form-group">
              <label>技能代码（可选）</label>
              <textarea 
                v-model="editSkillForm.code" 
                placeholder="请输入技能代码（Python）"
                rows="5"
              ></textarea>
            </div>
            <div class="dialog-footer">
              <button type="button" class="btn btn-secondary" @click="showEditDialog = false">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                {{ isSubmitting ? '提交中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useSkillStore } from '@/stores/skill';

const skillStore = useSkillStore();
const skills = ref([]);
const isLoading = ref(false);
const error = ref(null);
const showCreateDialog = ref(false);
const showEditDialog = ref(false);
const isSubmitting = ref(false);
const newSkill = ref({
  skill_id: '',
  name: '',
  description: '',
  category: '其他',
  version: '1.0.0',
  code: ''
});
const editSkillForm = ref({
  skill_id: '',
  name: '',
  description: '',
  category: '其他',
  version: '1.0.0',
  code: ''
});

// 加载技能列表
const fetchSkills = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    console.log('开始获取技能列表');
    const data = await skillStore.fetchSkills();
    console.log('获取技能列表成功:', data);
    skills.value = data;
    console.log('技能列表长度:', skills.value.length);
  } catch (err) {
    console.error('获取技能列表失败:', err);
    error.value = `加载技能失败：${err.message || '未知错误'}`;
  } finally {
    isLoading.value = false;
  }
};

// 选择技能
const selectSkill = (skill) => {
  skillStore.setSelectedSkill(skill);
  // 这里可以添加跳转到技能详情页的逻辑
  console.log('Selected skill:', skill);
};

// 处理创建技能
const handleCreateSkill = async () => {
  try {
    isSubmitting.value = true;
    error.value = null;
    
    // 调用技能注册 API
    await skillStore.registerSkill(newSkill.value);
    
    // 关闭对话框并刷新列表
    showCreateDialog.value = false;
    resetNewSkillForm();
    fetchSkills();
  } catch (err) {
    error.value = `创建技能失败：${err.message || '未知错误'}`;
  } finally {
    isSubmitting.value = false;
  }
};

// 重置创建技能表单
const resetNewSkillForm = () => {
  newSkill.value = {
    skill_id: '',
    name: '',
    description: '',
    category: '其他',
    version: '1.0.0',
    code: ''
  };
};

// 编辑技能
const editSkill = (skill) => {
  // 填充编辑表单数据
  editSkillForm.value = {
    skill_id: skill.id || skill.skill_id || skill.name,
    name: skill.name,
    description: skill.description,
    category: skill.category || '其他',
    version: skill.version || '1.0.0',
    code: skill.code || ''
  };
  // 打开编辑对话框
  showEditDialog.value = true;
};

// 处理编辑技能
const handleEditSkill = async () => {
  try {
    isSubmitting.value = true;
    error.value = null;
    
    const skillId = editSkillForm.value.skill_id;
    // 调用技能更新 API
    await skillStore.updateSkill(skillId, editSkillForm.value);
    
    // 关闭对话框并刷新列表
    showEditDialog.value = false;
    fetchSkills();
  } catch (err) {
    error.value = `更新技能失败：${err.message || '未知错误'}`;
  } finally {
    isSubmitting.value = false;
  }
};

// 删除技能
const deleteSkill = (skill) => {
  if (confirm(`确定要删除技能 "${skill.name}" 吗？`)) {
    const skillId = skill.id || skill.skill_id || skill.name;
    skillStore.deleteSkill(skillId)
      .then(() => {
        fetchSkills();
      })
      .catch(err => {
        error.value = `删除技能失败：${err.message || '未知错误'}`;
      });
  }
};

// 导入技能
const importSkill = () => {
  // 这里可以添加打开导入技能对话框的逻辑
  console.log('Import skill');
};

// 获取技能图标
const getSkillIcon = (skill) => {
  const categoryIcons = {
    '文档处理': '📝',
    '敏感词检查': '🔍',
    '数据合并': '📊',
    '其他': '🛠️'
  };
  return categoryIcons[skill.category] || '🛠️';
};

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};

// 页面加载时获取技能列表
onMounted(() => {
  // 先使用模拟数据测试页面显示
  skills.value = [
    {
      name: "公文格式转换",
      description: "将普通文档转换为标准公文格式，支持红头文件、发文号、签发人等要素",
      category: "文档处理",
      version: "v2.1",
      created_at: "2024-01-15T00:00:00"
    },
    {
      name: "敏感词检查",
      description: "自动检测文档中的敏感词汇，支持自定义词库和正则表达式匹配",
      category: "敏感词检查",
      version: "v1.8",
      created_at: "2024-01-10T00:00:00"
    },
    {
      name: "Excel 数据合并",
      description: "合并多个 Excel 表格，支持按指定字段匹配、数据透视和统计分析",
      category: "数据合并",
      version: "v1.5",
      created_at: "2024-01-08T00:00:00"
    }
  ];
  // 然后尝试从后端获取数据
  fetchSkills();
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
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.skill-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  transition: all 0.3s;
  cursor: pointer;
}
.skill-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: rgb(0, 101, 105);
}
.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}
.skill-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
.skill-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
}
.skill-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
  margin-bottom: 15px;
  flex-wrap: wrap;
}
.skill-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
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
}
.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
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
  color: #ff4d4f;
}
.btn-danger:hover {
  background: #ffccc7;
}
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #666;
}
.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid rgb(0, 101, 105);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.error-message {
  background: #fff1f0;
  border: 1px solid #ffccc7;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ff4d4f;
}
.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #999;
  font-size: 14px;
}

/* 对话框样式 */
.dialog-overlay {
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

.dialog-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s;
}

.dialog-close:hover {
  background: #f5f5f5;
  color: #333;
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
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: rgb(0, 101, 105);
  box-shadow: 0 0 0 2px rgba(0, 101, 105, 0.2);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  margin-top: 15px;
}
</style>

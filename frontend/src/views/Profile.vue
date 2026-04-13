<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1>个人中心</h1>
    </div>
    
    <div class="profile-content">
      <div class="profile-card">
        <h2>个人信息</h2>
        <div class="profile-info">
          <div class="info-item">
            <label>用户名</label>
            <span>{{ userProfile.username || '未设置' }}</span>
          </div>
          <div class="info-item">
            <label>邮箱</label>
            <span>{{ userProfile.email || '未设置' }}</span>
          </div>
          <div class="info-item">
            <label>上次登录</label>
            <span>{{ formatDate(userProfile.last_login) || '未登录' }}</span>
          </div>
          <div class="info-item">
            <label>注册时间</label>
            <span>{{ formatDate(userProfile.created_at) || '未知' }}</span>
          </div>
        </div>
        <button class="btn btn-primary" @click="showEditProfileDialog = true">编辑信息</button>
      </div>
      
      <div class="profile-card">
        <h2>使用统计</h2>
        <div class="usage-stats">
          <div class="stat-card">
            <span class="stat-value">{{ usageStats.total_chats || 0 }}</span>
            <span class="stat-label">总对话数</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ usageStats.total_skills || 0 }}</span>
            <span class="stat-label">使用技能数</span>
            <span class="stat-trend" :class="{ 'positive': usageStats.skill_trend > 0, 'negative': usageStats.skill_trend < 0 }">
              {{ usageStats.skill_trend > 0 ? '↑' : usageStats.skill_trend < 0 ? '↓' : '→' }}
            </span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ usageStats.average_response_time || 0 }}s</span>
            <span class="stat-label">平均响应时间</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ usageStats.active_days || 0 }}</span>
            <span class="stat-label">活跃天数</span>
          </div>
        </div>
      </div>
      
      <div class="profile-card">
        <h2>技能偏好</h2>
        <div class="skill-preferences">
          <div v-for="(preference, index) in skillPreferences" :key="index" class="preference-item">
            <span class="preference-name">{{ preference.skill_name }}</span>
            <div class="preference-score">
              <div class="score-bar" :style="{ width: (preference.score * 100) + '%' }"></div>
            </div>
            <span class="preference-value">{{ Math.round(preference.score * 100) }}%</span>
          </div>
          <div v-if="skillPreferences.length === 0" class="empty-state">
            <p>暂无技能偏好数据</p>
          </div>
        </div>
      </div>
      
      <div class="profile-card">
        <h2>推荐技能</h2>
        <div class="recommendations">
          <div v-for="(recommendation, index) in recommendations" :key="index" class="recommendation-item">
            <h3>{{ recommendation.skill_name }}</h3>
            <p>{{ recommendation.description }}</p>
            <div class="recommendation-meta">
              <span class="recommendation-score">匹配度: {{ Math.round(recommendation.match_score * 100) }}%</span>
              <button class="btn btn-sm btn-primary">使用</button>
            </div>
          </div>
          <div v-if="recommendations.length === 0" class="empty-state">
            <p>暂无推荐技能</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑个人信息对话框 -->
    <div v-if="showEditProfileDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>编辑个人信息</h2>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-content">
          <form @submit.prevent="saveProfile">
            <div class="form-group">
              <label>用户名</label>
              <input 
                v-model="profileForm.username" 
                type="text" 
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>邮箱</label>
              <input 
                v-model="profileForm.email" 
                type="email" 
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>密码</label>
              <input 
                v-model="profileForm.password" 
                type="password" 
                placeholder="留空表示不修改" 
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
import { ref, onMounted } from 'vue';
import { userApi } from '@/api/modules';

export default {
  name: 'Profile',
  setup() {
    const userProfile = ref({});
    const usageStats = ref({});
    const skillPreferences = ref([]);
    const recommendations = ref([]);
    const showEditProfileDialog = ref(false);
    const profileForm = ref({
      username: '',
      email: '',
      password: ''
    });
    
    // 获取用户个人资料
    const fetchUserProfile = async () => {
      try {
        const response = await userApi.getProfile();
        userProfile.value = response.data || {};
      } catch (error) {
        console.error('获取个人资料失败:', error);
      }
    };
    
    // 获取使用统计
    const fetchUsageStats = async () => {
      try {
        const response = await userApi.getUsageStats();
        usageStats.value = response.data || {};
      } catch (error) {
        console.error('获取使用统计失败:', error);
      }
    };
    
    // 获取技能偏好
    const fetchSkillPreferences = async () => {
      try {
        const response = await userApi.getSkillPrefs();
        skillPreferences.value = response.data.preferences || [];
      } catch (error) {
        console.error('获取技能偏好失败:', error);
      }
    };
    
    // 获取推荐技能
    const fetchRecommendations = async () => {
      try {
        const response = await userApi.getRecommendations();
        recommendations.value = response.data.recommendations || [];
      } catch (error) {
        console.error('获取推荐技能失败:', error);
      }
    };
    
    // 保存个人资料
    const saveProfile = async () => {
      try {
        await userApi.updateProfile(profileForm.value);
        closeDialog();
        fetchUserProfile();
      } catch (error) {
        console.error('保存个人资料失败:', error);
      }
    };
    
    // 关闭对话框
    const closeDialog = () => {
      showEditProfileDialog.value = false;
      profileForm.value = {
        username: userProfile.value.username || '',
        email: userProfile.value.email || '',
        password: ''
      };
    };
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return null;
      return new Date(dateString).toLocaleString('zh-CN');
    };
    
    // 初始化
    onMounted(() => {
      fetchUserProfile();
      fetchUsageStats();
      fetchSkillPreferences();
      fetchRecommendations();
    });
    
    return {
      userProfile,
      usageStats,
      skillPreferences,
      recommendations,
      showEditProfileDialog,
      profileForm,
      saveProfile,
      closeDialog,
      formatDate
    };
  }
};
</script>

<style scoped>
.profile-container {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: 2rem;
}

.profile-header h1 {
  margin: 0;
  font-size: 2rem;
  color: #333;
}

.profile-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.profile-card {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.profile-card h2 {
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  color: #333;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 0.75rem;
}

.profile-info {
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item label {
  font-weight: 600;
  color: #666;
}

.info-item span {
  color: #333;
}

.usage-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-card {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  position: relative;
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

.stat-trend {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
}

.stat-trend.positive {
  color: #4caf50;
}

.stat-trend.negative {
  color: #f44336;
}

.skill-preferences {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preference-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.preference-name {
  flex: 1;
  font-weight: 600;
  color: #333;
}

.preference-score {
  flex: 2;
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.score-bar {
  height: 100%;
  background-color: #4caf50;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.preference-value {
  width: 60px;
  text-align: right;
  font-weight: 600;
  color: #666;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-item {
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #2196f3;
}

.recommendation-item h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  color: #333;
}

.recommendation-item p {
  margin: 0 0 1rem 0;
  color: #666;
  font-size: 0.875rem;
  line-height: 1.4;
}

.recommendation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.recommendation-score {
  color: #666;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 2rem;
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
  border-bottom: none;
  padding-bottom: 0;
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

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
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

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}
</style>

<template>
  <div class="page active">
    <div class="card">
      <div class="card-title">⚙️ 配置中心</div>
      
      <!-- 配置分类列表 -->
      <div class="config-categories">
        <div 
          v-for="category in configCategories" 
          :key="category.value"
          @click="selectCategory(category.value)"
          class="category-card"
        >
          <div class="category-icon">{{ category.icon }}</div>
          <div class="category-name">{{ category.name }}</div>
          <div class="category-desc">{{ category.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api/index.js';

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



const selectCategory = (category) => {
  router.push(`/config/${category}`);
};

const getCategoryName = (categoryValue) => {
  const category = configCategories.find(c => c.value === categoryValue);
  return category ? category.name : categoryValue;
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
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

/* 配置分类样式 */
.config-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 30px;
}
.category-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}
.category-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: rgb(0, 101, 105);
}
.category-card.active {
  border-color: rgb(0, 101, 105);
  background: rgba(0, 101, 105, 0.05);
}
.category-icon {
  font-size: 24px;
  margin-bottom: 12px;
}
.category-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}
.category-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .config-categories {
    grid-template-columns: 1fr;
  }
}
</style>

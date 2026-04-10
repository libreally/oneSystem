import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { skillApi } from '@/api/modules';

export const useSkillStore = defineStore('skill', () => {
  // State
  const skills = ref([]);
  const selectedSkill = ref(null);
  const executionLogs = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // Getters
  const availableSkills = computed(() => {
    return skills.value.filter(s => s.status === 'active');
  });

  const skillCategories = computed(() => {
    const categories = {};
    skills.value.forEach(skill => {
      const category = skill.category || 'Other';
      if (!categories[category]) {
        categories[category] = [];
      }
      categories[category].push(skill);
    });
    return categories;
  });

  // Actions
  async function fetchSkills() {
    try {
      isLoading.value = true;
      const data = await skillApi.getAll();
      skills.value = data.skills || [];
      return skills.value;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchSkillById(skillId) {
    try {
      isLoading.value = true;
      const data = await skillApi.getById(skillId);
      selectedSkill.value = data.skill;
      return data.skill;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function executeSkill(skillId, params) {
    try {
      isLoading.value = true;
      error.value = null;
      const data = await skillApi.execute(skillId, params);
      
      // Add to logs
      executionLogs.value.unshift({
        skillId,
        skillName: skills.value.find(s => s.id === skillId)?.name || 'Unknown',
        result: data.result,
        status: 'success',
        timestamp: new Date().toISOString()
      });

      return data;
    } catch (err) {
      error.value = err.message;
      executionLogs.value.unshift({
        skillId,
        skillName: skills.value.find(s => s.id === skillId)?.name || 'Unknown',
        result: null,
        status: 'failed',
        error: err.message,
        timestamp: new Date().toISOString()
      });
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function registerSkill(skillData) {
    try {
      isLoading.value = true;
      const data = await skillApi.register(skillData);
      skills.value.unshift(data.skill);
      return data.skill;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateSkill(skillId, skillData) {
    try {
      isLoading.value = true;
      const data = await skillApi.update(skillId, skillData);
      const index = skills.value.findIndex(s => s.id === skillId);
      if (index !== -1) {
        skills.value[index] = data.skill;
      }
      return data.skill;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteSkill(skillId) {
    try {
      isLoading.value = true;
      await skillApi.delete(skillId);
      skills.value = skills.value.filter(s => s.id !== skillId);
      if (selectedSkill.value?.id === skillId) {
        selectedSkill.value = null;
      }
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchLogs(skillId, limit = 50) {
    try {
      const data = await skillApi.getLogs(skillId, limit);
      executionLogs.value = data.logs || [];
      return executionLogs.value;
    } catch (err) {
      error.value = err.message;
      throw err;
    }
  }

  function setSelectedSkill(skill) {
    selectedSkill.value = skill;
  }

  function resetError() {
    error.value = null;
  }

  return {
    // State
    skills,
    selectedSkill,
    executionLogs,
    isLoading,
    error,
    // Getters
    availableSkills,
    skillCategories,
    // Actions
    fetchSkills,
    fetchSkillById,
    executeSkill,
    registerSkill,
    updateSkill,
    deleteSkill,
    fetchLogs,
    setSelectedSkill,
    resetError
  };
});

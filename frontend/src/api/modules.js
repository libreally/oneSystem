import apiClient from './index';

export const chatApi = {
  // Send message and get response
  sendMessage(message, sessionId = null) {
    return apiClient.post('/chat', { message, session_id: sessionId });
  },

  // Get chat history
  getHistory(sessionId, limit = 20) {
    return apiClient.get(`/chat/history/${sessionId}`, { params: { limit } });
  },

  // Get all sessions
  getSessions() {
    return apiClient.get('/chat/sessions');
  },

  // Create new session
  createSession(title = 'New Chat') {
    return apiClient.post('/chat/sessions', { title });
  },

  // Delete session
  deleteSession(sessionId) {
    return apiClient.delete(`/chat/sessions/${sessionId}`);
  },

  // Clear context
  clearContext(sessionId) {
    return apiClient.post(`/chat/sessions/${sessionId}/clear`);
  }
};

export const skillApi = {
  // Get all skills
  getAll() {
    return apiClient.get('/skills');
  },

  // Get skill by ID
  getById(skillId) {
    return apiClient.get(`/skills/${skillId}`);
  },

  // Execute skill
  execute(skillId, params) {
    return apiClient.post(`/skills/${skillId}/execute`, params);
  },

  // Register new skill
  register(skillData) {
    return apiClient.post('/skills/register', skillData);
  },

  // Update skill
  update(skillId, skillData) {
    return apiClient.put(`/skills/${skillId}`, skillData);
  },

  // Delete skill
  delete(skillId) {
    return apiClient.delete(`/skills/${skillId}`);
  },

  // Get skill execution logs
  getLogs(skillId, limit = 50) {
    return apiClient.get(`/skills/${skillId}/logs`, { params: { limit } });
  }
};

export const scheduleApi = {
  // Get all scheduled tasks
  getAll() {
    return apiClient.get('/schedule');
  },

  // Get task by ID
  getById(taskId) {
    return apiClient.get(`/schedule/${taskId}`);
  },

  // Create task
  create(taskData) {
    return apiClient.post('/schedule', taskData);
  },

  // Update task
  update(taskId, taskData) {
    return apiClient.put(`/schedule/${taskId}`, taskData);
  },

  // Delete task
  delete(taskId) {
    return apiClient.delete(`/schedule/${taskId}`);
  },

  // Enable task
  enable(taskId) {
    return apiClient.post(`/schedule/${taskId}/enable`);
  },

  // Disable task
  disable(taskId) {
    return apiClient.post(`/schedule/${taskId}/disable`);
  },

  // Run task immediately
  runNow(taskId) {
    return apiClient.post(`/schedule/${taskId}/run`);
  }
};

export const taskApi = {
  // Get all tasks
  getAll(filters = {}) {
    return apiClient.get('/tasks', { params: filters });
  },

  // Get task by ID
  getById(taskId) {
    return apiClient.get(`/tasks/${taskId}`);
  },

  // Create task
  create(taskData) {
    return apiClient.post('/tasks', taskData);
  },

  // Update task
  update(taskId, taskData) {
    return apiClient.put(`/tasks/${taskId}`, taskData);
  },

  // Delete task
  delete(taskId) {
    return apiClient.delete(`/tasks/${taskId}`);
  },

  // Complete task
  complete(taskId) {
    return apiClient.post(`/tasks/${taskId}/complete`);
  },

  // Get task summary
  getSummary() {
    return apiClient.get('/tasks/summary');
  },

  // Generate work summary
  generateWorkSummary(startDate, endDate) {
    return apiClient.get('/tasks/work-summary', { params: { start_date: startDate, end_date: endDate } });
  }
};

export const configApi = {
  // Get all configs
  getAll(type = null) {
    const params = type ? { type } : {};
    return apiClient.get('/config', { params });
  },

  // Get config by key
  getByKey(key) {
    return apiClient.get(`/config/${key}`);
  },

  // Create/Update config
  save(configData) {
    return apiClient.post('/config', configData);
  },

  // Delete config
  delete(key) {
    return apiClient.delete(`/config/${key}`);
  },

  // Get user preferences
  getUserPreference() {
    return apiClient.get('/config/user-preference');
  },

  // Update user preferences
  updateUserPreference(prefs) {
    return apiClient.post('/config/user-preference', prefs);
  }
};

export const documentApi = {
  // Search documents
  search(query, directories = [], limit = 20) {
    return apiClient.post('/documents/search', { query, directories, limit });
  },

  // Get recent searches
  getRecentSearches(limit = 10) {
    return apiClient.get('/documents/recent', { params: { limit } });
  },

  // Clear search history
  clearHistory() {
    return apiClient.post('/documents/clear-history');
  },

  // Get session knowledge base
  getSessionKnowledge(sessionId) {
    return apiClient.get(`/documents/knowledge/${sessionId}`);
  },

  // Add to knowledge base
  addToKnowledge(sessionId, docIds) {
    return apiClient.post(`/documents/knowledge/${sessionId}`, { doc_ids: docIds });
  }
};

export const reportApi = {
  // Generate report
  generate(reportType, params) {
    return apiClient.post('/reports/generate', { report_type: reportType, params });
  },

  // Get report history
  getHistory(limit = 20) {
    return apiClient.get('/reports/history', { params: { limit } });
  },

  // Download report
  download(reportId) {
    return apiClient.get(`/reports/${reportId}/download`, { responseType: 'blob' });
  }
};

export const userApi = {
  // Get current user profile
  getProfile() {
    return apiClient.get('/user/profile');
  },

  // Update profile
  updateProfile(profileData) {
    return apiClient.put('/user/profile', profileData);
  },

  // Get usage statistics
  getUsageStats(days = 30) {
    return apiClient.get('/user/usage-stats', { params: { days } });
  },

  // Get skill preferences
  getSkillPrefs() {
    return apiClient.get('/user/skill-preferences');
  },

  // Update skill preferences
  updateSkillPrefs(prefs) {
    return apiClient.post('/user/skill-preferences', prefs);
  },

  // Get recommendations
  getRecommendations(limit = 5) {
    return apiClient.get('/user/recommendations', { params: { limit } });
  }
};

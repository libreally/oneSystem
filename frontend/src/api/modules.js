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

export const wpsApi = {
  // Get active WPS document
  getActiveDocument() {
    return apiClient.get('/wps/active');
  },

  // Open WPS file
  openFile(filePath) {
    return apiClient.post('/wps/open', { file_path: filePath });
  },

  // Get document content
  getDocumentContent(documentType, filePath = null) {
    return apiClient.post('/wps/content', { document_type: documentType, file_path: filePath });
  },

  // Get document tables
  getDocumentTables(filePath = null) {
    return apiClient.post('/wps/tables', { file_path: filePath });
  },

  // Extract text from document
  extractText(filePath = null) {
    return apiClient.post('/wps/extract-text', { file_path: filePath });
  },

  // Extract tables from document
  extractTables(filePath = null) {
    return apiClient.post('/wps/extract-tables', { file_path: filePath });
  },

  // Process document
  processDocument(filePath, processType) {
    return apiClient.post('/wps/process', { file_path: filePath, process_type: processType });
  }
};

export const skillGeneratorApi = {
  // Generate skill from description
  generateFromDescription(description) {
    return apiClient.post('/skill-generator/generate', { description });
  },

  // Generate skill template
  generateTemplate(skillType, params = {}) {
    return apiClient.post('/skill-generator/template', { skill_type: skillType, params });
  },

  // Generate input/output definitions
  generateIO(skillType, description) {
    return apiClient.post('/skill-generator/io', { skill_type: skillType, description });
  },

  // Validate generated skill
  validateSkill(skillData) {
    return apiClient.post('/skill-generator/validate', skillData);
  }
};

export const integrationApi = {
  // Get all integrations
  getAll() {
    return apiClient.get('/integration');
  },

  // Get integration by type
  getByType(integrationType) {
    return apiClient.get(`/integration/${integrationType}`);
  },

  // Test integration connection
  testConnection(integrationType, config) {
    return apiClient.post(`/integration/${integrationType}/test`, config);
  },

  // Execute integration action
  executeAction(integrationType, action, params) {
    return apiClient.post(`/integration/${integrationType}/execute`, { action, params });
  },

  // Sync data from integration
  syncData(integrationType, syncType, params = {}) {
    return apiClient.post(`/integration/${integrationType}/sync`, { sync_type: syncType, params });
  }
};

export const permissionApi = {
  // User login
  login(username, password) {
    return apiClient.post('/permission/login', { username, password });
  },

  // Check permission
  checkPermission(userId, permission) {
    return apiClient.post('/permission/check', { user_id: userId, permission });
  },

  // List all users
  listUsers() {
    return apiClient.get('/permission/users');
  },

  // Create user
  createUser(username, password, role = 'user') {
    return apiClient.post('/permission/users', { username, password, role });
  },

  // Update user role
  updateUserRole(userId, role) {
    return apiClient.put(`/permission/users/${userId}/role`, { role });
  },

  // Delete user
  deleteUser(userId) {
    return apiClient.delete(`/permission/users/${userId}`);
  },

  // List all roles
  listRoles() {
    return apiClient.get('/permission/roles');
  },

  // Update role permissions
  updateRolePermissions(roleType, permissions) {
    return apiClient.put(`/permission/roles/${roleType}/permissions`, { permissions });
  }
};

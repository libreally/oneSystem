import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { chatApi } from '@/api/modules';

export const useChatStore = defineStore('chat', () => {
  // State
  const sessions = ref([]);
  const currentSessionId = ref(null);
  const messages = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const isChatWindowOpen = ref(false);

  // Getters
  const currentSession = computed(() => {
    return sessions.value.find(s => s.id === currentSessionId.value);
  });

  const hasMessages = computed(() => messages.value.length > 0);

  // Actions
  async function fetchSessions() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await chatApi.getSessions();
      sessions.value = response.sessions || [];
      
      // 如果没有会话，创建一个新会话
      if (sessions.value.length === 0) {
        await createSession('新对话');
      } 
      // 如果有会话但没有当前会话，设置第一个会话为当前会话
      else if (!currentSessionId.value) {
        currentSessionId.value = sessions.value[0].id;
        await loadMessages(currentSessionId.value);
      }
      
      return sessions.value;
    } catch (err) {
      console.error('Fetch sessions failed:', err);
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createSession(title = '新对话') {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await chatApi.createSession(title);
      const newSession = response.session;
      
      // 添加到会话列表
      sessions.value.unshift(newSession);
      
      // 设置为当前会话
      currentSessionId.value = newSession.id;
      messages.value = newSession.messages || [];
      
      return newSession;
    } catch (err) {
      console.error('Create session failed:', err);
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMessages(sessionId) {
    isLoading.value = true;
    error.value = null;

    try {
      currentSessionId.value = sessionId;
      const response = await chatApi.getHistory(sessionId);
      messages.value = response.messages || [];
      return messages.value;
    } catch (err) {
      console.error('Load messages failed:', err);
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function sendMessage(content) {
    if (!content.trim()) return;

    isLoading.value = true;
    error.value = null;

    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      status: 'sending'
    };
    messages.value.push(userMessage);

    try {
      console.log('Sending message:', content);
      const data = await chatApi.sendMessage(content, 'default_user', currentSessionId.value);
      console.log('Received response:', data);
      
      // Update user message status
      userMessage.status = 'delivered';
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response || data.message || '抱歉，处理您的请求时遇到错误。',
        timestamp: new Date().toISOString(),
        suggestions: data.suggestions || []
      };
      messages.value.push(aiMessage);
      console.log('Added AI message:', aiMessage);

      // 更新会话列表
      await fetchSessions();

      return aiMessage;
    } catch (err) {
      console.error('Send message failed:', err);
      error.value = err.message;
      // Update user message status
      userMessage.status = 'failed';
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '抱歉，处理您的请求时遇到错误，请稍后重试。',
        timestamp: new Date().toISOString(),
        is_error: true
      };
      messages.value.push(errorMessage);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteSession(sessionId) {
    isLoading.value = true;
    error.value = null;

    try {
      await chatApi.deleteSession(sessionId);
      
      // 从会话列表中移除
      sessions.value = sessions.value.filter(s => s.id !== sessionId);
      
      // 如果删除的是当前会话，设置第一个会话为当前会话
      if (currentSessionId.value === sessionId) {
        if (sessions.value.length > 0) {
          currentSessionId.value = sessions.value[0].id;
          await loadMessages(currentSessionId.value);
        } else {
          currentSessionId.value = null;
          messages.value = [];
        }
      }
      
      return true;
    } catch (err) {
      console.error('Delete session failed:', err);
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function clearContext() {
    if (!currentSessionId.value) return;
    
    isLoading.value = true;
    error.value = null;

    try {
      await chatApi.clearContext(currentSessionId.value);
      messages.value = [];
      return true;
    } catch (err) {
      console.error('Clear context failed:', err);
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function setCurrentSession(sessionId) {
    currentSessionId.value = sessionId;
    loadMessages(sessionId);
  }

  function clearMessages() {
    messages.value = [];
  }

  function resetError() {
    error.value = null;
  }

  function toggleChatWindow() {
    isChatWindowOpen.value = !isChatWindowOpen.value;
  }

  function openChatWindow() {
    isChatWindowOpen.value = true;
  }

  function closeChatWindow() {
    isChatWindowOpen.value = false;
  }

  return {
    // State
    sessions,
    currentSessionId,
    messages,
    isLoading,
    error,
    isChatWindowOpen,
    // Getters
    currentSession,
    hasMessages,
    // Actions
    fetchSessions,
    createSession,
    loadMessages,
    sendMessage,
    deleteSession,
    clearContext,
    setCurrentSession,
    clearMessages,
    resetError,
    toggleChatWindow,
    openChatWindow,
    closeChatWindow
  };
});

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

  // Getters
  const currentSession = computed(() => {
    return sessions.value.find(s => s.id === currentSessionId.value);
  });

  const hasMessages = computed(() => messages.value.length > 0);

  // Actions
  async function fetchSessions() {
    try {
      const data = await chatApi.getSessions();
      sessions.value = data.sessions || [];
      if (sessions.value.length > 0 && !currentSessionId.value) {
        currentSessionId.value = sessions.value[0].id;
        await loadMessages(currentSessionId.value);
      }
      return sessions.value;
    } catch (err) {
      error.value = err.message;
      throw err;
    }
  }

  async function createSession(title = 'New Chat') {
    try {
      const data = await chatApi.createSession(title);
      sessions.value.unshift(data.session);
      currentSessionId.value = data.session.id;
      messages.value = [];
      return data.session;
    } catch (err) {
      error.value = err.message;
      throw err;
    }
  }

  async function loadMessages(sessionId) {
    try {
      currentSessionId.value = sessionId;
      const data = await chatApi.getHistory(sessionId);
      messages.value = data.messages || [];
      return messages.value;
    } catch (err) {
      error.value = err.message;
      throw err;
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
      timestamp: new Date().toISOString()
    };
    messages.value.push(userMessage);

    try {
      const data = await chatApi.sendMessage(content, currentSessionId.value);
      
      // Update session ID if it's a new session
      if (data.session_id && !currentSessionId.value) {
        currentSessionId.value = data.session_id;
      }

      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        suggestions: data.suggestions || []
      };
      messages.value.push(aiMessage);

      // Update session list if needed
      if (!sessions.value.find(s => s.id === currentSessionId.value)) {
        await fetchSessions();
      }

      return aiMessage;
    } catch (err) {
      error.value = err.message;
      // Remove the user message on error
      messages.value.pop();
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteSession(sessionId) {
    try {
      await chatApi.deleteSession(sessionId);
      sessions.value = sessions.value.filter(s => s.id !== sessionId);
      
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = sessions.value.length > 0 ? sessions.value[0].id : null;
        messages.value = currentSessionId.value ? [] : messages.value;
        if (currentSessionId.value) {
          await loadMessages(currentSessionId.value);
        }
      }
    } catch (err) {
      error.value = err.message;
      throw err;
    }
  }

  async function clearContext() {
    if (!currentSessionId.value) return;
    
    try {
      await chatApi.clearContext(currentSessionId.value);
      messages.value = [];
    } catch (err) {
      error.value = err.message;
      throw err;
    }
  }

  function setCurrentSession(sessionId) {
    currentSessionId.value = sessionId;
    loadMessages(sessionId);
  }

  function resetError() {
    error.value = null;
  }

  return {
    // State
    sessions,
    currentSessionId,
    messages,
    isLoading,
    error,
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
    resetError
  };
});

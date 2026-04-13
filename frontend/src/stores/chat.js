import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { chatApi } from '@/api/modules';

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const isChatWindowOpen = ref(false);

  // Getters
  const hasMessages = computed(() => messages.value.length > 0);

  // Actions
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
      console.log('Sending message:', content);
      const data = await chatApi.sendMessage(content);
      console.log('Received response:', data);
      
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

      return aiMessage;
    } catch (err) {
      console.error('Send message failed:', err);
      error.value = err.message;
      // Remove the user message on error
      messages.value.pop();
      throw err;
    } finally {
      isLoading.value = false;
    }
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
    messages,
    isLoading,
    error,
    isChatWindowOpen,
    // Getters
    hasMessages,
    // Actions
    sendMessage,
    clearMessages,
    resetError,
    toggleChatWindow,
    openChatWindow,
    closeChatWindow
  };
});

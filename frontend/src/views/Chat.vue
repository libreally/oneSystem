<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1>AI 助手</h1>
      <div class="chat-actions">
        <button class="btn btn-primary" @click="newChat">新对话</button>
        <button class="btn btn-secondary" @click="clearContext">清空上下文</button>
      </div>
    </div>
    
    <div class="chat-body">
      <div class="chat-messages" ref="messagesContainer">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.role]"
        >
          <div class="message-content">
            <div class="message-header">
              <span class="message-role">{{ message.role === 'user' ? '我' : 'AI' }}</span>
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div class="message-text">{{ message.content }}</div>
          </div>
        </div>
        <div v-if="loading" class="message ai">
          <div class="message-content">
            <div class="message-header">
              <span class="message-role">AI</span>
              <span class="message-time">{{ formatTime(new Date()) }}</span>
            </div>
            <div class="message-text loading">
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-input">
        <textarea 
          v-model="inputMessage" 
          @keyup.enter.exact="sendMessage" 
          @keyup.enter.shift="inputMessage += '\n'" 
          placeholder="输入您的问题..." 
          rows="1"
          ref="inputTextarea"
        ></textarea>
        <button class="btn btn-primary" @click="sendMessage" :disabled="!inputMessage.trim() || loading">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue';
import { chatApi } from '@/api/modules';

export default {
  name: 'Chat',
  setup() {
    const inputMessage = ref('');
    const messages = ref([]);
    const loading = ref(false);
    const messagesContainer = ref(null);
    const inputTextarea = ref(null);
    const sessionId = ref(null);
    
    // 新对话
    const newChat = async () => {
      try {
        const response = await chatApi.createSession('新对话');
        sessionId.value = response.data.session_id;
        messages.value = [];
      } catch (error) {
        console.error('创建新对话失败:', error);
      }
    };
    
    // 清空上下文
    const clearContext = async () => {
      if (!sessionId.value) return;
      
      try {
        await chatApi.clearContext(sessionId.value);
        messages.value = [];
      } catch (error) {
        console.error('清空上下文失败:', error);
      }
    };
    
    // 发送消息
    const sendMessage = async () => {
      if (!inputMessage.value.trim() || loading.value) return;
      
      const message = inputMessage.value.trim();
      inputMessage.value = '';
      
      // 添加用户消息
      messages.value.push({
        role: 'user',
        content: message,
        timestamp: new Date()
      });
      
      // 滚动到底部
      scrollToBottom();
      
      loading.value = true;
      
      try {
        // 如果没有会话 ID，创建一个新的
        if (!sessionId.value) {
          const response = await chatApi.createSession('新对话');
          sessionId.value = response.data.session_id;
        }
        
        // 发送消息
        const response = await chatApi.sendMessage(message, sessionId.value);
        
        // 添加 AI 回复
        messages.value.push({
          role: 'ai',
          content: response.data.response,
          timestamp: new Date()
        });
      } catch (error) {
        console.error('发送消息失败:', error);
        // 添加错误消息
        messages.value.push({
          role: 'ai',
          content: '抱歉，处理您的请求时出现错误，请稍后重试。',
          timestamp: new Date()
        });
      } finally {
        loading.value = false;
        // 滚动到底部
        scrollToBottom();
      }
    };
    
    // 滚动到底部
    const scrollToBottom = async () => {
      await nextTick();
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    };
    
    // 格式化时间
    const formatTime = (date) => {
      return new Date(date).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    // 自动调整文本框高度
    watch(inputMessage, () => {
      if (inputTextarea.value) {
        inputTextarea.value.style.height = 'auto';
        inputTextarea.value.style.height = Math.min(inputTextarea.value.scrollHeight, 150) + 'px';
      }
    });
    
    // 初始化
    onMounted(() => {
      newChat();
    });
    
    return {
      inputMessage,
      messages,
      loading,
      messagesContainer,
      inputTextarea,
      newChat,
      clearContext,
      sendMessage,
      formatTime
    };
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.chat-header {
  padding: 20px;
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.chat-actions {
  display: flex;
  gap: 10px;
}

.chat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
  transition: all 0.3s;
}

.message.user {
  align-self: flex-end;
  background: linear-gradient(135deg, rgb(0, 101, 105) 0%, rgb(0, 130, 136) 100%);
  color: white;
}

.message.ai {
  align-self: flex-start;
  background-color: #fff;
  color: #333;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.message:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  opacity: 0.8;
}

.message-role {
  font-weight: 600;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
}

.message-text {
  line-height: 1.6;
  font-size: 14px;
}

.message-text.loading {
  display: flex;
  align-items: center;
  gap: 6px;
}

.loading-dot {
  width: 8px;
  height: 8px;
  background-color: rgb(0, 101, 105);
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out both;
}

.loading-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes pulse {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.chat-input {
  padding: 20px;
  background-color: #fff;
  border-top: 1px solid #e8e8e8;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e8e8e8;
  border-radius: 20px;
  resize: none;
  font-size: 14px;
  font-family: inherit;
  min-height: 44px;
  max-height: 150px;
  overflow-y: auto;
  transition: all 0.3s;
}

.chat-input textarea:focus {
  outline: none;
  border-color: rgb(0, 101, 105);
  box-shadow: 0 0 0 2px rgba(0, 101, 105, 0.1);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: rgb(0, 101, 105);
  color: white;
}

.btn-primary:hover {
  background: rgb(0, 80, 84);
  box-shadow: 0 4px 12px rgba(0, 101, 105, 0.3);
}

.btn-primary:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-secondary {
  background: #f5f7fa;
  color: #333;
  border: 1px solid #e8e8e8;
}

.btn-secondary:hover {
  background: #e8e8e8;
}
</style>

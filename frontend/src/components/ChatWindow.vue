<template>
  <div class="ai-chat-window">
    <div class="ai-chat-header">
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 24px;">🤖</span>
        <div>
          <div style="font-weight: 600;">AI 助手</div>
          <div style="font-size: 12px; opacity: 0.9;">在线 | 随时为您服务</div>
        </div>
      </div>
      <div style="display: flex; gap: 10px;">
        <button @click="clearHistory" style="background: none; border: none; color: white; font-size: 14px; cursor: pointer; padding: 4px 8px; border-radius: 4px;">清空历史</button>
        <button @click="closeChat" style="background: none; border: none; color: white; font-size: 20px; cursor: pointer;">✕</button>
      </div>
    </div>
    
    <div class="ai-chat-body" ref="chatBodyRef">
      <div 
        v-for="message in chatStore.messages" 
        :key="message.id"
        class="message" 
        :class="message.role === 'user' ? 'user' : 'ai'"
      >
        <div class="message-avatar" :class="message.role === 'user' ? 'user-avatar-chat' : 'ai-avatar'">
          {{ message.role === 'user' ? '张' : '🤖' }}
        </div>
        <div class="message-wrapper">
          <div class="message-content">{{ message.content }}</div>
          <div class="message-footer">
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
          </div>
        </div>
      </div>
      <div v-if="chatStore.isLoading" class="message ai loading">
        <div class="message-avatar ai-avatar">🤖</div>
        <div class="message-content">
          <div class="loading-indicator">
            <span class="loading-dot"></span>
            <span class="loading-dot"></span>
            <span class="loading-dot"></span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="ai-chat-input">
      <input 
        type="text" 
        placeholder="输入您的需求，例如：帮我生成周报、检查敏感词..." 
        v-model="inputMessage"
        @keypress="handleKeypress"
      >
      <button class="send-btn" @click="sendMessage">➤</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import { formatDate } from '@/utils/helpers'

const chatStore = useChatStore()
const inputMessage = ref('')
const chatBodyRef = ref(null)

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  try {
    await chatStore.sendMessage(inputMessage.value)
    inputMessage.value = ''
  } catch (error) {
    console.error('Send message failed:', error)
  }
}

const handleKeypress = (event) => {
  if (event.key === 'Enter') {
    sendMessage()
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return formatDate(timestamp, 'HH:mm')
}

const closeChat = () => {
  const fab = document.querySelector('.ai-fab')
  if (fab) fab.style.display = 'flex'
}

const clearHistory = async () => {
  if (confirm('确定要清空当前会话历史吗？')) {
    try {
      await chatStore.clearContext()
    } catch (error) {
      console.error('Clear history failed:', error)
    }
  }
}

watch(() => chatStore.messages.length, () => {
  nextTick(() => {
    if (chatBodyRef.value) {
      chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
    }
  })
})
</script>

<style scoped>
.ai-chat-window {
  position: fixed;
  right: 30px;
  bottom: 100px;
  width: 730px;
  height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  overflow: hidden;
}

.ai-chat-window.contact-panel-active .ai-chat-body {
  margin-left: 280px;
}

.ai-chat-header {
  background: linear-gradient(135deg, rgb(0, 101, 105) 0%, rgb(0, 130, 136) 100%);
  color: white;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.contact-panel {
  position: absolute;
  left: 0;
  top: 0;
  width: 280px;
  height: 100%;
  background: white;
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  z-index: 1001;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}

.contact-panel.active {
  transform: translateX(0);
}

.contact-panel-header {
  background: #f5f7fa;
  border-bottom: 1px solid #e8e8e8;
}

.contact-list {
  list-style: none;
}

.contact-item {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.contact-item:hover {
  background: #f5f7fa;
  margin: 0 -15px;
  padding: 15px;
}

.contact-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgb(0, 101, 105) 0%, rgb(0, 130, 136) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.contact-info {
  flex: 1;
  min-width: 0;
}

.contact-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.contact-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
}

.contact-status.online {
  background: #f6ffed;
  color: #52c41a;
}

.contact-status.offline {
  background: #fff1f0;
  color: #f5222d;
}

.contact-status.busy {
  background: #fff7e6;
  color: #fa8c16;
}

.ai-chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
}

.message {
  margin-bottom: 12px;
  display: flex;
  gap: 10px;
  position: relative;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(0,0,0,0.1);
}

.ai-avatar {
  background: linear-gradient(135deg, rgb(0, 101, 105) 0%, rgb(0, 130, 136) 100%);
  color: white;
}

.user-avatar-chat {
  background: #52c41a;
  color: white;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  position: relative;
}

.message.user .message-content {
  background: rgb(0, 101, 105);
  color: white;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 18px;
}

.message.ai .message-content {
  background: white;
  color: #333;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 18px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.message-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  line-height: 1;
  font-size: 11px;
}

.message.user .message-footer {
  justify-content: flex-start;
  padding-right: 10px;
}

.message.ai .message-footer {
  justify-content: flex-end;
  padding-left: 10px;
}

.message-time {
  color: rgba(153,153,153,0.8);
}

.message-status {
  font-size: 10px;
  color: rgba(0,101,105,0.8);
}

.message-status.sending {
  color: rgba(153,153,153,0.8);
}

.message-status.delivered {
  color: rgba(0,101,105,0.8);
}

.message-status.read {
  color: rgba(0,101,105,1);
}

.loading-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.loading-dot {
  width: 8px;
  height: 8px;
  background: rgb(0, 101, 105);
  border-radius: 50%;
  animation: loading 1.4s infinite ease-in-out both;
}

.loading-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.ai-chat-input {
  padding: 15px;
  border-top: 1px solid #e8e8e8;
  display: flex;
  gap: 10px;
}

.ai-chat-input input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #e8e8e8;
  border-radius: 20px;
  outline: none;
  font-size: 14px;
}

.ai-chat-input input:focus {
  border-color: rgb(0, 101, 105);
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgb(0, 101, 105);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.send-btn:hover {
  background: rgb(0, 80, 84);
  transform: scale(1.05);
}
</style>

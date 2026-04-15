<template>
  <div class="ai-chat-window">
    <div class="ai-chat-header">
      <div style="display: flex; align-items: center; gap: 10px;">
        <button @click="toggleContactPanel" style="background: none; border: none; color: white; font-size: 18px; cursor: pointer;">☰</button>
        <span style="font-size: 24px;">{{ currentChatAvatar }}</span>
        <div>
          <div style="font-weight: 600;">{{ currentChatTitle }}</div>
          <div style="font-size: 12px; opacity: 0.9;">{{ currentChatStatus }}</div>
        </div>
      </div>
      <div style="display: flex; gap: 10px;">
        <button @click="clearHistory" style="background: none; border: none; color: white; font-size: 14px; cursor: pointer; padding: 4px 8px; border-radius: 4px;">清空历史</button>
        <button @click="closeChat" style="background: none; border: none; color: white; font-size: 20px; cursor: pointer;">✕</button>
      </div>
    </div>
    
    <div class="chat-container" :class="{ 'contact-panel-active': isContactPanelOpen }">
      <!-- 联系人列表面板 -->
      <div class="contact-panel">
        <div class="contact-panel-header">
          <div style="font-weight: 600; padding: 15px;">联系人</div>
        </div>
        <div class="contact-list">
          <div class="contact-item" @click="switchToChat('ai')">
            <div class="contact-avatar">🤖</div>
            <div class="contact-info">
              <div class="contact-name">AI自动化助手</div>
              <div class="contact-status online">在线</div>
            </div>
          </div>
          <div class="contact-item" @click="switchToChat('李四')">
            <div class="contact-avatar">李</div>
            <div class="contact-info">
              <div class="contact-name">李四</div>
              <div class="contact-status online">在线</div>
            </div>
          </div>
          <div class="contact-item" @click="switchToChat('王五')">
            <div class="contact-avatar">王</div>
            <div class="contact-info">
              <div class="contact-name">王五</div>
              <div class="contact-status offline">离线</div>
            </div>
          </div>
          <div class="contact-item" @click="switchToChat('赵六')">
            <div class="contact-avatar">赵</div>
            <div class="contact-info">
              <div class="contact-name">赵六</div>
              <div class="contact-status online">在线</div>
            </div>
          </div>
          <div class="contact-item" @click="switchToChat('孙七')">
            <div class="contact-avatar">孙</div>
            <div class="contact-info">
              <div class="contact-name">孙七</div>
              <div class="contact-status busy">忙碌</div>
            </div>
          </div>
          <div class="contact-item" @click="switchToChat('周八')">
            <div class="contact-avatar">周</div>
            <div class="contact-info">
              <div class="contact-name">周八</div>
              <div class="contact-status online">在线</div>
            </div>
          </div>
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
            <div class="message-content" v-if="message.role === 'assistant'" v-html="renderMarkdown(message.content)"></div>
            <div class="message-content" v-else>{{ message.content }}</div>
            <div class="message-footer">
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              <span v-if="message.role === 'user'" class="message-status delivered">已送达</span>
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
import { ref, nextTick, watch, computed, onMounted } from 'vue'
import { useChatStore } from '../stores/chat'
import { formatDate } from '@/utils/helpers'
import MarkdownIt from 'markdown-it'

const chatStore = useChatStore()
const md = new MarkdownIt({ html: true, breaks: true, linkify: true })
const inputMessage = ref('')
const chatBodyRef = ref(null)
const isContactPanelOpen = ref(false)
const currentChat = ref('ai')

// 初始化组件
onMounted(async () => {
  try {
    // 加载会话列表
    await chatStore.fetchSessions()
    
    // 如果没有会话，创建一个新会话
    if (chatStore.sessions.length === 0) {
      await chatStore.createSession('AI自动化助手')
    } else if (!chatStore.currentSessionId) {
      // 如果有会话但没有当前会话，设置第一个会话为当前会话
      chatStore.currentSessionId = chatStore.sessions[0].id
      await chatStore.loadMessages(chatStore.currentSessionId)
    }
  } catch (error) {
    console.error('初始化聊天窗口失败:', error)
  }
})

const currentChatAvatar = computed(() => {
  return currentChat.value === 'ai' ? '🤖' : currentChat.value.charAt(0)
})

const currentChatTitle = computed(() => {
  return currentChat.value === 'ai' ? 'AI自动化助手' : currentChat.value
})

const currentChatStatus = computed(() => {
  if (currentChat.value === 'ai') {
    return '在线 | 随时为您服务'
  } else {
    return '在线 | 正在聊天'
  }
})

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  const message = inputMessage.value
  inputMessage.value = ''
  try {
    await chatStore.sendMessage(message)
  } catch (error) {
    console.error('Send message failed:', error)
    inputMessage.value = message
  }
}

const handleKeypress = (event) => {
  if (event.key === 'Enter') {
    sendMessage()
  }
}

const toggleContactPanel = () => {
  isContactPanelOpen.value = !isContactPanelOpen.value
}

const switchToChat = async (name) => {
    currentChat.value = name
    isContactPanelOpen.value = false
    
    try {
      // 加载会话列表
      await chatStore.fetchSessions()
      
      // 查找或创建对应用户的会话
      let targetSession = chatStore.sessions.find(session => session.title === name)
      
      if (!targetSession) {
        // 如果没有会话，创建一个新会话
        targetSession = await chatStore.createSession(name)
      } else {
        // 如果有会话，加载对应的消息
        await chatStore.loadMessages(targetSession.id)
        console.log('加载历史消息:', chatStore.messages)
      }
      // 确保当前会话ID被更新
      chatStore.currentSessionId = targetSession.id
    } catch (error) {
      console.error('加载聊天历史失败:', error)
      // 如果加载失败，添加欢迎消息
      chatStore.clearMessages()
      if (currentChat.value === 'ai') {
        chatStore.messages.push({
          id: Date.now(),
          role: 'assistant',
          content: '您好！我是AI自动化助手，可以帮您：\n• 处理公文和文档\n• 生成报表和总结\n• 管理任务和督办\n• 数据统计和分析\n\n请直接告诉我您的需求，例如：\n"帮我生成周报"\n"检查这个文件的敏感词"\n"合并这两个Excel表格"',
          timestamp: new Date().toISOString()
        })
      } else {
        chatStore.messages.push({
          id: Date.now(),
          role: 'assistant',
          content: `您好！我是${currentChat.value}，有什么可以帮您的吗？`,
          timestamp: new Date().toISOString()
        })
      }
    }
  }

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return formatDate(timestamp, 'HH:mm')
}

const closeChat = () => {
  chatStore.closeChatWindow()
}

const clearHistory = async () => {
  if (confirm('确定要清空当前会话历史吗？')) {
    await chatStore.clearMessages()
  }
}


const renderMarkdown = (content) => {
  return md.render(content)
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

.chat-container {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
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
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
}

.contact-list {
  flex: 1;
  overflow-y: auto;
  list-style: none;
  padding: 0;
  margin: 0;
}

.chat-container.contact-panel-active .contact-panel {
  transform: translateX(0);
}

.chat-container.contact-panel-active .ai-chat-body {
  margin-left: 280px;
}

.ai-chat-header {
  background: linear-gradient(135deg, rgb(0, 101, 105) 0%, rgb(0, 130, 136) 100%);
  color: white;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1002;
  position: relative;
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

/* Markdown 样式 */
.message-content h1, .message-content h2, .message-content h3, .message-content h4, .message-content h5, .message-content h6 {
  margin: 10px 0 5px 0;
  font-weight: 600;
}

.message-content h1 {
  font-size: 18px;
}

.message-content h2 {
  font-size: 16px;
}

.message-content h3 {
  font-size: 14px;
}

.message-content p {
  margin: 5px 0;
}

.message-content ul, .message-content ol {
  margin: 5px 0;
  padding-left: 20px;
}

.message-content li {
  margin: 2px 0;
}

.message-content code {
  background: #f5f5f5;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 12px;
}

.message-content pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
  margin: 5px 0;
}

.message-content pre code {
  background: none;
  padding: 0;
}

.message-content blockquote {
  border-left: 3px solid rgb(0, 101, 105);
  padding-left: 10px;
  margin: 5px 0;
  color: #666;
}

.message-content table {
  border-collapse: collapse;
  margin: 5px 0;
  width: 100%;
}

.message-content th, .message-content td {
  border: 1px solid #ddd;
  padding: 5px;
  text-align: left;
}

.message-content th {
  background: #f5f5f5;
  font-weight: 600;
}

.message-content a {
  color: rgb(0, 101, 105);
  text-decoration: none;
}

.message-content a:hover {
  text-decoration: underline;
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
  position: relative;
  z-index: 999;
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

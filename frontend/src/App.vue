<template>
  <div class="container">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">智</div>
        <span>一系统</span>
      </div>
      <nav class="nav-menu">
        <router-link to="/" class="nav-item" active-class="active">
          <span>📊</span>
          <span>统一工作台</span>
        </router-link>
        <router-link to="/skills" class="nav-item" active-class="active">
          <span>🛠️</span>
          <span>Skills 管理</span>
        </router-link>
        <router-link to="/config" class="nav-item" active-class="active">
          <span>⚙️</span>
          <span>配置中心</span>
        </router-link>
        <router-link to="/schedule" class="nav-item" active-class="active">
          <span>⏰</span>
          <span>定时调度</span>
        </router-link>
        <router-link to="/documents" class="nav-item" active-class="active">
          <span>📄</span>
          <span>文档管理</span>
        </router-link>
        <router-link to="/reports" class="nav-item" active-class="active">
          <span>📈</span>
          <span>报表中心</span>
        </router-link>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部栏 -->
      <header class="header">
        <div class="search-box">
          <input 
            type="text" 
            placeholder="输入自然语言指令，例如：帮我生成周报、检查敏感词..." 
            v-model="searchText"
            @keypress="handleSearchKeypress"
          >
        </div>
        <div class="user-info">
          <span>🔔</span>
          <span>📧</span>
          <div class="user-avatar">张</div>
          <span>张三</span>
        </div>
      </header>

      <!-- 路由视图 -->
      <router-view />
    </main>

    <!-- AI 助手悬浮按钮 -->
    <button class="ai-fab" @click="toggleChatWindow" title="AI 助手">
      🤖
    </button>

    <!-- 聊天窗口组件 -->
    <ChatWindow v-if="chatStore.isChatWindowOpen" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useChatStore } from '../stores/chat'
import ChatWindow from '../components/ChatWindow.vue'

const chatStore = useChatStore()
const searchText = ref('')

const toggleChatWindow = () => {
  chatStore.toggleChatWindow()
}

const handleSearchKeypress = (event) => {
  if (event.key === 'Enter' && searchText.value.trim()) {
    const command = searchText.value.trim()
    chatStore.toggleChatWindow()
    setTimeout(() => {
      chatStore.sendMessage(command)
    }, 300)
    searchText.value = ''
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.container {
  display: flex;
  min-height: 100vh;
}

/* 侧边栏 */
.sidebar {
  width: 240px;
  background: rgb(0, 101, 105);
  color: white;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  transition: all 0.3s;
}

.logo {
  padding: 20px;
  font-size: 20px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: #536dfe;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-menu {
  padding: 20px 0;
}

.nav-item {
  padding: 15px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s;
  border-left: 3px solid transparent;
  text-decoration: none;
  color: white;
}

.nav-item:hover, .nav-item.active {
  background: rgba(255,255,255,0.1);
  border-left-color: rgb(0, 101, 105);
}

/* 主内容区 */
.main-content {
  flex: 1;
  margin-left: 240px;
  padding: 20px;
}

.header {
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  flex: 1;
  max-width: 600px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 10px 40px 10px 15px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
}

.search-box input:focus {
  outline: none;
  border-color: rgb(0, 101, 105);
  box-shadow: 0 0 0 2px rgba(0,101,105,0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgb(0, 101, 105);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

/* AI 助手按钮 */
.ai-fab {
  position: fixed;
  right: 30px;
  bottom: 30px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgb(0, 101, 105) 0%, rgb(0, 130, 136) 100%);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,101,105,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.3s;
  z-index: 1000;
}

.ai-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0,101,105,0.6);
}
</style>

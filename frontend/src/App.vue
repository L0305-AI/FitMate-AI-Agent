<template>
  <!-- ================= 登录页 ================= -->
  <div v-if="!isLoggedIn" class="login-container">
    <div class="login-box">
      <h2>🏋️ FitMate 智能健身助理</h2>
      <p>{{ isRegistering ? '创建一个新账号' : '欢迎回来，请输入账号密码' }}</p>
      
      <div class="auth-tabs">
        <div :class="['auth-tab', { active: !isRegistering }]" @click="isRegistering = false">登录</div>
        <div :class="['auth-tab', { active: isRegistering }]" @click="isRegistering = true">注册</div>
      </div>

      <input v-model="loginUsername" type="text" placeholder="请输入用户名" />
      <input v-model="loginPassword" type="password" placeholder="请输入密码" style="margin-top: 15px;" @keyup.enter="handleAuth" />
      
      <button v-if="!isRegistering" @click="handleAuth" style="margin-top: 20px;">登 录</button>
      <button v-else @click="handleAuth" style="margin-top: 20px; background: #10b981;">注 册</button>
    </div>
  </div>

  <!-- ================= 主应用布局 ================= -->
  <div v-else class="main-layout">
    <!-- 顶部导航 -->
    <header class="top-nav">
      <div class="logo-area">
        <span class="logo-icon">🤖</span> 
        <span class="logo-text">FitMate 智能助理</span>
      </div>
      <div class="user-area" @mouseenter="showDropdown = true" @mouseleave="showDropdown = false">
        <div class="user-avatar">👤</div>
        <span class="user-name">{{ currentUserId }}</span>
        <transition name="fade">
          <div v-if="showDropdown" class="dropdown-menu">
            <div class="dropdown-item" @click="activeTab = 'profile'; showDropdown = false">👤 个人档案</div>
            <div class="dropdown-divider"></div>
            <div class="dropdown-item logout-text" @click="handleLogout">🚪 退出登录</div>
          </div>
        </transition>
      </div>
    </header>

    <!-- 主体内容 -->
    <div class="body-container">
      <!-- 左侧侧边栏 -->
      <aside class="left-sidebar">
        <div :class="['nav-item', { active: activeTab === 'chat' }]" @click="activeTab = 'chat'">💬 智能对话</div>
        <div :class="['nav-item', { active: activeTab === 'dashboard' }]" @click="activeTab = 'dashboard'">📈 健康看板</div>
        <div :class="['nav-item', { active: activeTab === 'recipes' }]" @click="activeTab = 'recipes'">🥗 饮食计划</div>
        <div :class="['nav-item', { active: activeTab === 'profile' }]" @click="activeTab = 'profile'">📋 个人档案</div>
      </aside>

      <!-- 右侧内容区（组件动态切换） -->
      <main class="content-area">
        <ChatView v-show="activeTab === 'chat'" :user-id="currentUserId" @diet-recorded="onDietRecorded" />
        <DashboardView v-show="activeTab === 'dashboard'" :user-id="currentUserId" :profile="profile" />
        <DietView v-show="activeTab === 'recipes'" :user-id="currentUserId" ref="dietViewRef" />
        <ProfileView v-show="activeTab === 'profile'" :user-id="currentUserId" :profile="profile" @update-profile="onProfileUpdate" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import ChatView from './components/ChatView.vue'
import DashboardView from './components/DashboardView.vue'
import DietView from './components/DietView.vue'
import ProfileView from './components/ProfileView.vue'

// 登录状态
const isLoggedIn = ref(false)
const isRegistering = ref(false)
const loginUsername = ref('')
const loginPassword = ref('')
const currentUserId = ref('')
const showDropdown = ref(false)
const activeTab = ref('chat')

// 全局共享数据
const profile = ref({ height_cm: '', weight_kg: '', age: '', gender: '男', allergy: '', injury: '' })
const dietViewRef = ref(null)

const handleAuth = async () => {
  if (!loginUsername.value.trim() || !loginPassword.value.trim()) return alert('请输入用户名和密码')
  const url = isRegistering.value ? 'http://127.0.0.1:8001/api/register' : 'http://127.0.0.1:8001/api/login'
  try {
    await axios.post(url, { username: loginUsername.value.trim(), password: loginPassword.value.trim() })
    if (isRegistering.value) {
      alert('✅ 注册成功！请直接登录')
      isRegistering.value = false
      return
    }
    currentUserId.value = loginUsername.value.trim()
    isLoggedIn.value = true
    activeTab.value = 'chat'
    fetchProfile()
    if (Notification && Notification.permission !== "granted") Notification.requestPermission();
  } catch (error) {
    alert(error.response?.data?.detail || '网络错误')
  }
}

const fetchProfile = async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:8001/api/profile/${currentUserId.value}`)
    if (res.data) profile.value = { ...profile.value, ...res.data }
  } catch (e) { console.error(e) }
}

const handleLogout = () => {
  isLoggedIn.value = false
  loginUsername.value = ''
  loginPassword.value = ''
  currentUserId.value = ''
  showDropdown.value = false
}

// 接收子组件通知，实现联动刷新
const onDietRecorded = () => {
  if (dietViewRef.value) dietViewRef.value.fetchDietLogs()
}
const onProfileUpdate = (newProfile) => {
  profile.value = { ...newProfile }
}
</script>

<style>
/* ====== 全局重置与基础变量 ====== */
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { font-family: sans-serif; background-color: #f5f7fa; height: 100vh; width: 100vw; overflow: hidden; }

/* ====== 登录页 ====== */
.login-container { position: fixed; top: 0; left: 0; right: 0; bottom: 0; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #e0f2fe, #f0f2f5); }
.login-box { background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); width: 400px; max-width: 90%; text-align: center; }
.login-box h2 { color: #1e293b; margin-bottom: 10px; }
.login-box p { color: #64748b; font-size: 0.9rem; margin-bottom: 20px; }
.login-box input { width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; background: #f8fafc; }
.login-box input:focus { border-color: #3b82f6; background: white; }
.login-box button { width: 100%; padding: 12px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: bold; }
.auth-tabs { display: flex; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; }
.auth-tab { flex: 1; text-align: center; padding: 10px; cursor: pointer; color: #64748b; font-weight: bold; border-bottom: 2px solid transparent; transition: all 0.3s; }
.auth-tab:hover { color: #3b82f6; }
.auth-tab.active { color: #3b82f6; border-bottom-color: #3b82f6; }

/* ====== 主框架布局 ====== */
.main-layout { display: flex; flex-direction: column; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: #f5f7fa; }
.top-nav { height: 60px; background: white; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; padding: 0 24px; flex-shrink: 0; }
.logo-area { display: flex; align-items: center; gap: 10px; font-size: 1.2rem; font-weight: bold; color: #1e293b; }
.logo-icon { font-size: 1.5rem; }
.user-area { position: relative; display: flex; align-items: center; gap: 10px; cursor: pointer; padding: 8px 12px; border-radius: 8px; transition: background 0.2s; }
.user-area:hover { background: #f1f5f9; }
.user-avatar { width: 36px; height: 36px; background: #e0f2fe; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: #0284c7; }
.user-name { font-weight: 500; color: #333; }
.dropdown-menu { position: absolute; top: 100%; right: 0; margin-top: 8px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 160px; padding: 8px 0; z-index: 100; }
.dropdown-item { padding: 10px 16px; display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: #475569; transition: background 0.2s; cursor: pointer; }
.dropdown-item:hover { background: #f1f5f9; color: #3b82f6; }
.dropdown-divider { height: 1px; background: #e2e8f0; margin: 8px 0; }
.logout-text:hover { color: #ef4444; background: #fef2f2; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.body-container { display: flex; flex: 1; overflow: hidden; }
.left-sidebar { width: 220px; background: white; border-right: 1px solid #e2e8f0; padding: 20px 10px; display: flex; flex-direction: column; gap: 8px; flex-shrink: 0; }
.nav-item { padding: 12px 16px; border-radius: 8px; cursor: pointer; color: #475569; font-weight: 500; transition: all 0.2s; display: flex; align-items: center; gap: 10px; }
.nav-item:hover { background: #f1f5f9; }
.nav-item.active { background: #e0f2fe; color: #0284c7; font-weight: bold; }
.content-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 16px; background: #f5f7fa; }

/* 共用按钮样式 */
.primary-btn { background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.2s; }
.primary-btn:hover { background: #2563eb; }
.save-btn { width: 100%; padding: 14px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 1rem; }
.save-btn:hover { background: #059669; }
</style>
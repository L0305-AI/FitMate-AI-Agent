<template>
  <div class="chat-page">
    <div class="chat-window" ref="chatWindow">
      <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
        <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="bubble" v-html="renderMarkdown(msg.content)"></div>
      </div>
    </div>
    <div class="input-area">
      <input type="text" v-model="userInput" @keyup.enter="sendMessage" placeholder="告诉我你的身高体重，或者让我记录饮食..." />
      <button @click="sendMessage" :disabled="!userInput.trim()">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { marked } from 'marked'
import axios from 'axios'

const props = defineProps(['userId'])
const emit = defineEmits(['dietRecorded'])

const userInput = ref('')
const messages = ref([{ role: 'assistant', content: `你好！我是你的专属健身助理。你可以让我帮你记录饮食，或者问我健身问题。` }])
const chatWindow = ref(null)

const renderMarkdown = (text) => text ? marked.parse(text) : ''

const scrollToBottom = async () => {
  await nextTick()
  if (chatWindow.value) chatWindow.value.scrollTop = chatWindow.value.scrollHeight
}

const sendMessage = async () => {
  if (!userInput.value.trim()) return
  const userMsg = userInput.value
  userInput.value = ''
  
  messages.value.push({ role: 'user', content: userMsg })
  const aiMessageIndex = messages.value.push({ role: 'assistant', content: '🤔 正在思考...' }) - 1
  scrollToBottom()

  try {
    const history = messages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }))
    const response = await fetch('http://127.0.0.1:8001/api/chat_stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: props.userId, message: userMsg, history: history })
    })

    if (!response.ok) throw new Error('网络请求失败')
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let fullContent = ''
    let lastUpdateTime = Date.now()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunkText = decoder.decode(value, { stream: true })
      if (fullContent === '') messages.value[aiMessageIndex].content = ''
      fullContent += chunkText
      const now = Date.now()
      if (now - lastUpdateTime > 50) {
        messages.value[aiMessageIndex].content = fullContent
        lastUpdateTime = now
        scrollToBottom()
      }
    }
    messages.value[aiMessageIndex].content = fullContent
    scrollToBottom()

    // 1. 捕获定时提醒
    const timeRegex = /([0-1]?[0-9]|2[0-3])[:：][0-5][0-9]/g; 
    const matchedTimes = fullContent.match(timeRegex);
    if (matchedTimes && matchedTimes.length > 0) {
      setupFrontendReminder(matchedTimes[0].replace('：', ':'));
    }

    // 2. 捕获隐藏的饮食记录 JSON
    const dietMatch = fullContent.match(/\[DIET_LOG:\s*(\{.*?\})\s*\]/);
    if (dietMatch) {
      const dietData = JSON.parse(dietMatch[1]);
      await axios.post('http://127.0.0.1:8001/api/diet_logs', {
        user_id: props.userId,
        food_name: dietData.food_name,   
        calories: Number(dietData.calories),     
        meal_type: dietData.meal_type || '加餐'
      });
      emit('dietRecorded'); // 通知父组件刷新饮食计划页面
      
      // 从屏幕隐藏 JSON
      messages.value[aiMessageIndex].content = fullContent.replace(dietMatch[0], '').trim();
    }
  } catch (error) {
    messages.value[aiMessageIndex].content = '哎呀，网络开小差了。'
  }
}

const setupFrontendReminder = (targetTime) => {
  const now = new Date();
  const [hours, minutes] = targetTime.split(':').map(Number);
  const targetDate = new Date();
  targetDate.setHours(hours, minutes, 0, 0);
  if (targetDate <= now) targetDate.setDate(targetDate.getDate() + 1);
  
  const delay = targetDate.getTime() - now.getTime();
  setTimeout(() => {
    if (Notification.permission === "granted") {
      new Notification("FitMate 健康提醒", { body: `到时间啦！您预约的 ${targetTime} 的提醒该执行了。` });
    } else {
      alert(`⏰ 到时间啦！您预约的 ${targetTime} 的提醒该执行了。`);
    }
  }, delay);
}
</script>

<style scoped>
.chat-page { display: flex; flex-direction: column; height: 100%; background: white; border-radius: 12px; overflow: hidden; }
.chat-window { flex: 1; padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; }
.message { display: flex; gap: 12px; max-width: 85%; align-items: flex-start; }
.message.user { align-self: flex-end; flex-direction: row-reverse; }
.message.assistant { align-self: flex-start; width: 100%; }
.avatar { width: 40px; height: 40px; border-radius: 50%; background: #e2e8f0; display: flex; justify-content: center; align-items: center; font-size: 1.2rem; flex-shrink: 0; }
.bubble { padding: 14px 18px; border-radius: 12px; font-size: 0.95rem; line-height: 1.6; word-break: break-word; text-align: left; background: #f1f5f9; color: #1e293b; border-top-left-radius: 2px; width: fit-content; max-width: 100%; }
.message.user .bubble { background: #3b82f6; color: white; border-top-right-radius: 2px; border-top-left-radius: 12px; }
.input-area { padding: 20px; background: white; border-top: 1px solid #e2e8f0; display: flex; gap: 12px; }
.input-area input { flex: 1; padding: 14px 20px; border: 1px solid #cbd5e1; border-radius: 24px; outline: none; font-size: 1rem; background: #f8fafc; }
.input-area button { padding: 0 28px; background: #3b82f6; color: white; border: none; border-radius: 24px; cursor: pointer; font-weight: bold; font-size: 1rem; }
.input-area button:disabled { background: #cbd5e1; cursor: not-allowed; }
/* Markdown 美化 */
.bubble table { border-collapse: collapse; width: 100%; margin: 10px 0; }
.bubble th, .bubble td { border: 1px solid #cbd5e1; padding: 8px; text-align: left; }
.bubble th { background-color: #e2e8f0; font-weight: bold; }
.bubble strong { font-weight: 700; color: #0f172a; }
</style>
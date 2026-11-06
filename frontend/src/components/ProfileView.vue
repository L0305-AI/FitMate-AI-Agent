<template>
  <div class="profile-page">
    <div class="profile-card">
      <h2>📋 个人长期记忆档案</h2>
      <p class="subtitle">此处的数据会持久化保存到数据库，AI 将在对话中自动读取。</p>
      <div class="form-grid">
        <div class="form-item">
          <label>身高 (cm)</label>
          <input v-model="localProfile.height_cm" type="number" placeholder="如：175" />
        </div>
        <div class="form-item">
          <label>体重 (kg)</label>
          <input v-model="localProfile.weight_kg" type="number" placeholder="如：80" />
        </div>
        <div class="form-item">
          <label>年龄</label>
          <input v-model="localProfile.age" type="number" placeholder="如：25" />
        </div>
        <div class="form-item">
          <label>性别</label>
          <select v-model="localProfile.gender">
            <option value="男">男</option>
            <option value="女">女</option>
          </select>
        </div>
        <div class="form-item">
          <label>过敏史</label>
          <input v-model="localProfile.allergy" placeholder="如：花生、乳糖" />
        </div>
        <div class="form-item">
          <label>伤病/疼痛</label>
          <input v-model="localProfile.injury" placeholder="如：腰肌劳损" />
        </div>
      </div>
      <button class="save-btn" @click="saveProfile">保存更新</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps(['profile', 'userId'])
const emit = defineEmits(['updateProfile'])
const localProfile = ref({ ...props.profile })

watch(() => props.profile, (newVal) => { localProfile.value = { ...newVal } }, { deep: true })

const saveProfile = async () => {
  try {
    const p = localProfile.value
    const params = new URLSearchParams()
    if (p.height_cm) params.append('height_cm', p.height_cm)
    if (p.weight_kg) params.append('weight_kg', p.weight_kg)
    if (p.age) params.append('age', p.age)
    if (p.gender) params.append('gender', p.gender)
    if (p.allergy) params.append('allergy', p.allergy)
    if (p.injury) params.append('injury', p.injury)
    
    await axios.post(`http://127.0.0.1:8001/api/profile/${props.userId}?${params.toString()}`)
    alert('✅ 档案已成功更新到数据库！')
    emit('updateProfile', p)
  } catch (e) { alert('保存失败，请检查后端') }
}
</script>

<style scoped>
.profile-page { display: flex; justify-content: center; padding-top: 20px; height: 100%; overflow-y: auto; }
.profile-card { background: white; width: 100%; max-width: 700px; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
.profile-card h2 { color: #1e293b; margin-bottom: 8px; }
.profile-card .subtitle { color: #64748b; font-size: 0.9rem; margin-bottom: 30px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
.form-item label { display: block; font-size: 0.9rem; color: #475569; margin-bottom: 8px; font-weight: 500; }
.form-item input, .form-item select { width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; outline: none; background: #f8fafc; }
.form-item input:focus, .form-item select:focus { border-color: #3b82f6; background: white; }
.save-btn { width: 100%; padding: 14px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 1rem; }
.save-btn:hover { background: #059669; }
</style>
<template>
  <div class="recipes-page">
    <div class="recipes-header">
      <h2>🥗 饮食计划</h2>
      <div class="recipe-tabs">
        <div :class="['recipe-tab', { active: recipeTab === 'menu' }]" @click="recipeTab = 'menu'">📖 食谱库</div>
        <div :class="['recipe-tab', { active: recipeTab === 'diet' }]" @click="recipeTab = 'diet'; fetchDietLogs()">📝 今日打卡</div>
      </div>
    </div>

    <!-- 食谱库 -->
    <div v-show="recipeTab === 'menu'" class="tab-content">
      <div style="display: flex; gap: 10px; margin-bottom: 20px; justify-content: flex-end;">
        <button class="primary-btn" style="background: #10b981;" @click="showAddRecipe = true">➕ 添加食谱</button>
      </div>
      
      <div v-if="showAddRecipe" class="add-recipe-form">
        <h3>添加新食谱</h3>
        <input v-model="newRecipe.title" placeholder="食物名称 (如: 鸡胸肉)" />
        <input v-model="newRecipe.calories" type="number" placeholder="热量 (千卡)" />
        <input v-model="newRecipe.description" placeholder="描述 (如: 高蛋白、低脂)" />
        <div style="margin-top: 10px;">
          <button class="save-btn" style="width: auto; padding: 8px 16px;" @click="submitRecipe">确认添加</button>
          <button style="margin-left: 10px; background: #cbd5e1; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer;" @click="showAddRecipe = false">取消</button>
        </div>
      </div>

      <div class="recipe-grid">
        <div class="recipe-card" v-for="recipe in recipesList" :key="recipe.id">
          <div class="recipe-img">🍽️</div>
          <h4>{{ recipe.title }}</h4>
          <p>热量：约 {{ recipe.calories }} 千卡 | {{ recipe.description }}</p>
          <div style="display: flex; gap: 8px;">
            <button class="primary-btn" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #f59e0b;" @click="quickAddToDiet(recipe)">📝 打卡</button>
            <button class="delete-btn" style="flex: 1; padding: 8px; font-size: 0.85rem;" @click="deleteRecipe(recipe.id)">🗑️ 删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 今日打卡 -->
    <div v-show="recipeTab === 'diet'" class="tab-content">
      <div class="diet-header">
        <div class="total-cal-box">
          <h2>🍱 今日已摄入：<span class="total-cal">{{ todayCalories }}</span> 千卡</h2>
        </div>
        <button class="primary-btn" style="background: #f59e0b;" @click="openModal">➕ 记录饮食</button>
      </div>

      <div class="meal-grid">
        <div class="meal-card" v-for="meal in ['早餐', '午餐', '晚餐', '加餐']" :key="meal">
          <h3 class="meal-title">{{ meal }}</h3>
          <div class="meal-content">
            <div v-if="groupedDietLogs[meal].length === 0" class="empty-tip">暂无记录</div>
            <div v-else class="meal-item" v-for="log in groupedDietLogs[meal]" :key="log.id">
              <span class="food-name">{{ log.food_name }}</span>
              <div class="food-right">
                <span class="food-cal">{{ log.calories }} 千卡</span>
                <span class="del-icon" @click="deleteDietLog(log.id)">✖</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 弹窗部分 -->
    <DietModal 
      v-if="showDietModal"
      :visible="showDietModal"
      :mealType="currentMealType"
      :foods="tempFoods"
      @close="showDietModal = false"
      @update:mealType="val => currentMealType = val"
      @addRow="addTempFood"
      @removeRow="removeTempFood"
      @submit="submitMultipleDietLogs"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import DietModal from './DietModal.vue'

const props = defineProps(['userId'])

// Tab 控制
const recipeTab = ref('menu')

// 食谱库数据
const showAddRecipe = ref(false)
const newRecipe = ref({ title: '', calories: '', description: '' })
const recipesList = ref([])

const fetchRecipes = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8001/api/recipes')
    recipesList.value = res.data
  } catch (e) { console.error(e) }
}

const submitRecipe = async () => {
  if (!newRecipe.value.title || !newRecipe.value.calories) return alert('请填写完整信息')
  try {
    await axios.post('http://127.0.0.1:8001/api/recipes', { 
      title: newRecipe.value.title, 
      calories: Number(newRecipe.value.calories), 
      description: newRecipe.value.description || '暂无描述' 
    })
    alert('✅ 添加成功！')
    showAddRecipe.value = false
    newRecipe.value = { title: '', calories: '', description: '' }
    fetchRecipes()
  } catch (e) { alert('添加失败') }
}

const deleteRecipe = async (id) => {
  if (!confirm('确定要删除这个食谱吗？')) return
  try {
    await axios.delete(`http://127.0.0.1:8001/api/recipes/${id}`)
    fetchRecipes()
  } catch (e) { alert('删除失败') }
}

// 打卡数据
const dietLogs = ref([])         
const todayCalories = ref(0)     
const showDietModal = ref(false)
const currentMealType = ref('午餐')
const tempFoods = ref([{ name: '', calories: '' }])

const fetchDietLogs = async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:8001/api/diet_logs/${props.userId}`)
    dietLogs.value = res.data
    todayCalories.value = res.data.reduce((sum, item) => sum + item.calories, 0)
  } catch (e) { console.error(e) }
}

const groupedDietLogs = computed(() => {
  const groups = { '早餐': [], '午餐': [], '晚餐': [], '加餐': [] }
  dietLogs.value.forEach(log => {
    if (groups[log.meal_type]) groups[log.meal_type].push(log)
    else groups['加餐'].push(log) 
  })
  return groups
})

const openModal = () => {
  currentMealType.value = '午餐'
  tempFoods.value = [{ name: '', calories: '' }]
  showDietModal.value = true
}

const addTempFood = () => tempFoods.value.push({ name: '', calories: '' })
const removeTempFood = (index) => tempFoods.value.splice(index, 1)

const submitMultipleDietLogs = async () => {
  const validFoods = tempFoods.value.filter(f => f.name && f.calories)
  if (validFoods.length === 0) return alert('请至少填写一种食物')
  
  try {
    for (const food of validFoods) {
      await axios.post('http://127.0.0.1:8001/api/diet_logs', {
        user_id: props.userId,
        food_name: food.name,
        calories: Number(food.calories),
        meal_type: currentMealType.value
      })
    }
    alert(`✅ 成功记录 ${validFoods.length} 种食物！`)
    showDietModal.value = false
    fetchDietLogs()
  } catch (e) { alert('打卡失败') }
}

const deleteDietLog = async (id) => {
  if (!confirm('确定删除这条记录吗？')) return
  try {
    await axios.delete(`http://127.0.0.1:8001/api/diet_logs/${id}`)
    fetchDietLogs()
  } catch (e) { alert('删除失败') }
}

const quickAddToDiet = async (recipe) => {
  try {
    await axios.post('http://127.0.0.1:8001/api/diet_logs', {
      user_id: props.userId,
      food_name: recipe.title,
      calories: recipe.calories,
      meal_type: '加餐'
    })
    alert(`✅ 已将【${recipe.title}】记入今日打卡！`)
    fetchDietLogs()
  } catch (e) { alert('快捷打卡失败') }
}

onMounted(() => {
  fetchRecipes()
  fetchDietLogs()
})

// 将 fetchDietLogs 暴露给父组件，方便聊天记账后立刻刷新
defineExpose({ fetchDietLogs })
</script>

<style scoped>
.recipes-page { height: 100%; overflow-y: auto; background: white; padding: 24px; border-radius: 12px; }
.recipes-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.recipes-header h2 { color: #1e293b; }
.recipe-tabs { display: flex; background: #f1f5f9; padding: 4px; border-radius: 8px; }
.recipe-tab { padding: 8px 20px; cursor: pointer; border-radius: 6px; font-weight: bold; color: #64748b; transition: all 0.2s; }
.recipe-tab.active { background: white; color: #3b82f6; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.tab-content { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

.recipe-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.recipe-card { background: #f8fafc; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; transition: transform 0.2s; }
.recipe-card:hover { transform: translateY(-5px); }
.recipe-img { font-size: 3rem; text-align: center; margin-bottom: 15px; }
.recipe-card h4 { color: #1e293b; margin-bottom: 8px; }
.recipe-card p { color: #64748b; font-size: 0.85rem; margin-bottom: 12px; }
.delete-btn { width: 100%; padding: 8px; background-color: #fee2e2; color: #ef4444; border: 1px solid #fca5a5; border-radius: 6px; cursor: pointer; }
.delete-btn:hover { background-color: #ef4444; color: white; }
.add-recipe-form { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; margin-bottom: 20px; display: flex; flex-direction: column; gap: 10px; }
.add-recipe-form input { padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; outline: none; }

.meal-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 20px; }
.meal-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; min-height: 250px; display: flex; flex-direction: column;}
.meal-title { font-size: 1.05rem; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 12px; text-align: center; }
.meal-content { flex: 1; display: flex; flex-direction: column; gap: 10px; }
.empty-tip { text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 40px; }
.meal-item { display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 10px; border-radius: 8px; font-size: 0.9rem; }
.food-name { color: #334155; font-weight: 500; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.food-right { display: flex; align-items: center; gap: 8px; }
.food-cal { color: #f59e0b; font-weight: bold; font-size: 0.85rem; }
.del-icon { color: #cbd5e1; cursor: pointer; font-size: 0.9rem; }
.del-icon:hover { color: #ef4444; }
.diet-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.total-cal-box h2 { font-size: 1.2rem; color: #1e293b; margin: 0; }
.total-cal { color: #3b82f6; font-weight: bold; font-size: 1.4rem; }

/* 共用按钮补丁 */
.primary-btn { background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
.primary-btn:hover { background: #2563eb; }
.save-btn { width: 100%; padding: 14px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
</style>
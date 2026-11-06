<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>记录你的饮食</h3>
      
      <div class="meal-type-selector">
        <div v-for="type in ['早餐', '午餐', '晚餐', '加餐']" 
             :key="type" 
             :class="['meal-type-btn', { active: mealType === type }]"
             @click="$emit('update:mealType', type)">
          {{ type }}
        </div>
      </div>

      <div class="food-list-container">
        <div v-for="(food, index) in foods" :key="index" class="temp-food-item">
          <input v-model="food.name" placeholder="食物名称 (如: 牛肉面)" class="food-name-input" />
          <input v-model="food.calories" type="number" placeholder="热量(千卡)" class="food-cal-input" />
          <button class="remove-food-btn" @click="$emit('removeRow', index)">✖</button>
        </div>
      </div>

      <button class="add-row-btn" @click="$emit('addRow')">➕ 再加一种食物</button>

      <div class="modal-actions" style="margin-top: 20px;">
        <button class="cancel-btn" @click="$emit('close')">取消</button>
        <button class="save-btn" @click="$emit('submit')">确认打卡</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps(['visible', 'mealType', 'foods'])
defineEmits(['close', 'update:mealType', 'addRow', 'removeRow', 'submit'])
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5); backdrop-filter: blur(2px);
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}
.modal-content {
  background: white; width: 500px; max-width: 90%; padding: 30px; border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  animation: modalFadeIn 0.2s ease-out;
}
@keyframes modalFadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.modal-content h3 { margin-bottom: 20px; color: #1e293b; text-align: center; font-size: 1.2rem;}

.meal-type-selector { display: flex; gap: 8px; margin-bottom: 20px; }
.meal-type-btn {
  flex: 1; text-align: center; padding: 10px 0; border-radius: 8px;
  background: #f1f5f9; color: #64748b; cursor: pointer; font-size: 0.95rem; font-weight: 500; transition: 0.2s;
}
.meal-type-btn.active { background: #e0f2fe; color: #0284c7; border: 1px solid #7dd3fc; }

.food-list-container { display: flex; flex-direction: column; gap: 12px; max-height: 200px; overflow-y: auto; padding-right: 4px;}
.temp-food-item { display: flex; gap: 8px; align-items: center; }
.food-name-input { flex: 2; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; }
.food-cal-input { flex: 1; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; }
.food-name-input:focus, .food-cal-input:focus { border-color: #3b82f6; }
.remove-food-btn { background: none; border: none; color: #ef4444; cursor: pointer; font-size: 1.2rem; padding: 0 5px; }

.add-row-btn {
  margin-top: 12px; padding: 10px; background: #f8fafc; border: 1px dashed #cbd5e1;
  border-radius: 8px; color: #3b82f6; cursor: pointer; font-weight: 500; width: 100%; transition: 0.2s;
}
.add-row-btn:hover { background: #e0f2fe; border-color: #7dd3fc; }

.modal-actions { display: flex; gap: 12px; border-top: 1px solid #e2e8f0; padding-top: 20px;}
.cancel-btn { flex: 1; padding: 12px; background: #f1f5f9; color: #475569; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
.save-btn { flex: 1; padding: 12px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
</style>
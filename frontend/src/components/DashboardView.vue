<template>
  <div class="dashboard-page">
    <h2>📈 我的健康数据</h2>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">当前体重</div>
        <div class="stat-value">{{ profile.weight_kg || '--' }} <span class="unit">kg</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-title">BMI 指数</div>
        <div class="stat-value" :style="{ color: getBmiColor() }">{{ calculateBmi() }}</div>
        <div class="stat-desc">{{ getBmiStatus() }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">当前目标</div>
        <div class="stat-value" style="font-size: 1.2rem; color: #10b981;">科学减脂</div>
      </div>
    </div>
    <div class="chart-placeholder">
      <h3>体重趋势图</h3>
      <div id="weightChart" style="width: 100%; height: 250px;"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const props = defineProps(['profile', 'userId'])

const calculateBmi = () => {
  if (!props.profile.weight_kg || !props.profile.height_cm) return '--'
  const h = props.profile.height_cm / 100
  return (props.profile.weight_kg / (h * h)).toFixed(1)
}

const getBmiStatus = () => {
  const bmi = parseFloat(calculateBmi())
  if (isNaN(bmi)) return '暂无数据'
  if (bmi < 18.5) return '偏瘦'
  if (bmi < 24) return '正常'
  if (bmi < 28) return '超重'
  return '肥胖'
}

const getBmiColor = () => {
  const status = getBmiStatus()
  if (status === '正常') return '#10b981'
  if (status === '超重' || status === '偏瘦') return '#f59e0b'
  if (status === '肥胖') return '#ef4444'
  return '#333'
}

const renderChart = async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:8001/api/weight_history/${props.userId}`)
    const data = res.data
    await nextTick()
    const chartDom = document.getElementById('weightChart')
    if (!chartDom) return

    if (data.length === 0) {
      chartDom.innerHTML = '<div style="text-align:center; color:#94a3b8; line-height: 250px;">暂无数据，去档案里保存一次体重试试</div>'
      return
    }

    const myChart = echarts.init(chartDom)
    myChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.map(item => item.date), axisLine: { lineStyle: { color: '#cbd5e1' } } },
      yAxis: { type: 'value', name: '体重(kg)', min: 'dataMin', max: 'dataMax', splitLine: { lineStyle: { type: 'dashed' } } },
      series: [{ data: data.map(item => item.weight), type: 'line', smooth: true, itemStyle: { color: '#3b82f6' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(59,130,246,0.5)' }, { offset: 1, color: 'rgba(59,130,246,0.05)' }]) } }]
    })
  } catch (e) { console.error("加载图表失败", e) }
}

onMounted(renderChart)
watch(() => props.profile, renderChart, { deep: true })
</script>

<style scoped>
.dashboard-page { background: white; padding: 30px; border-radius: 12px; height: 100%; overflow-y: auto; }
.dashboard-page h2 { color: #1e293b; margin-bottom: 20px; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
.stat-card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; text-align: center; }
.stat-title { color: #64748b; font-size: 0.9rem; margin-bottom: 10px; }
.stat-value { font-size: 2rem; font-weight: bold; color: #1e293b; }
.unit { font-size: 1rem; font-weight: normal; color: #94a3b8; }
.stat-desc { font-size: 0.85rem; color: #94a3b8; margin-top: 6px; }
.chart-placeholder { background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 24px; height: 300px; display: flex; flex-direction: column; }
.chart-placeholder h3 { font-size: 1rem; color: #475569; margin-bottom: 20px; }
</style>
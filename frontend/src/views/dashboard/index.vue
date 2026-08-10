<template>
  <div class="dashboard">
    <!-- 欢迎卡片 -->
    <div class="welcome-banner">
      <div class="welcome-text">
        <h1>欢迎回来，{{ username }}</h1>
        <p>基于贝叶斯网络的校园舆情监测系统设计与实现</p>
      </div>
      <div class="welcome-icon">
        <el-icon :size="120"><DataAnalysis /></el-icon>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <el-card shadow="hover" class="stat-card" v-for="(s, i) in statCards" :key="i">
        <div class="stat-icon" :style="{ backgroundColor: s.iconBg }">
          <el-icon :size="28" :color="s.iconColor"><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-label">{{ s.label }}</div>
        <div class="stat-value">{{ s.value }}</div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card shadow="hover" class="chart-card">
        <template #header><span>情感分布</span></template>
        <div ref="sentimentChartEl" class="chart-box"></div>
      </el-card>
      <el-card shadow="hover" class="chart-card">
        <template #header><span>来源平台分布</span></template>
        <div ref="platformChartEl" class="chart-box"></div>
      </el-card>
    </div>

    <div class="charts-row" style="margin-top: 20px">
      <el-card shadow="hover" style="flex: 1; border-radius: 12px; border: none">
        <template #header><span>近 7 天舆情趋势</span></template>
        <div ref="trendChartEl" class="chart-box"></div>
      </el-card>
      <el-card shadow="hover" class="chart-card" style="min-width: 300px; max-width: 360px">
        <template #header>
          <span>贝叶斯风险等级分布</span>
        </template>
        <div ref="riskChartEl" class="chart-box"></div>
      </el-card>
    </div>

    <!-- 贝叶斯网络说明 -->
    <div class="charts-row" style="margin-top: 20px">
      <el-card shadow="hover" style="flex: 1; border-radius: 12px; border: none">
        <template #header><span>贝叶斯网络模型说明</span></template>
        <div class="bayes-desc">
          <div class="bayes-nodes">
            <div class="bayes-node input-node">
              <div class="node-title">输入节点</div>
              <div class="node-item">情感倾向 X₁</div>
              <div class="node-item">敏感词命中 X₂</div>
              <div class="node-item">平台影响力 X₃</div>
              <div class="node-item">发布频率 X₄</div>
            </div>
            <div class="bayes-arrow">
              <div class="arrow-label">P(Y|X₁,X₂,X₃,X₄)</div>
              <div class="arrow-line">→</div>
              <div class="arrow-formula">∝ P(Y)·∏P(Xᵢ|Y)</div>
            </div>
            <div class="bayes-node output-node">
              <div class="node-title">输出节点</div>
              <div class="node-item node-high">高风险</div>
              <div class="node-item node-medium">中风险</div>
              <div class="node-item node-low">低风险</div>
            </div>
          </div>
          <p class="bayes-note">
            系统采用朴素贝叶斯网络对舆情风险进行概率推理，综合情感倾向、敏感词命中情况、来源平台影响力及发布频率四个节点，
            通过条件概率表（CPT）计算后验概率，输出低/中/高三级风险判断，提升预警的科学性与准确性。
          </p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Document, TrendCharts, Bell, PieChart } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getStats, getSentiment, getPlatform, getTrend, getRisk } from '../../api/dashboard'

const username = ref('admin')

const stats = ref({ total: 0, today: 0, pending_warning: 0, platform_count: 0 })

const statCards = computed(() => [
  { icon: Document,     iconBg: '#e8f4fc', iconColor: '#67b8e3', label: '舆情总数',    value: stats.value.total },
  { icon: TrendCharts,  iconBg: '#fef3e2', iconColor: '#f59e0b', label: '今日新增',    value: stats.value.today },
  { icon: Bell,         iconBg: '#fce7f3', iconColor: '#ec4899', label: '待处理预警',  value: stats.value.pending_warning },
  { icon: PieChart,     iconBg: '#ede9fe', iconColor: '#8b5cf6', label: '来源平台数',  value: stats.value.platform_count },
])

const sentimentChartEl = ref(null)
const platformChartEl = ref(null)
const trendChartEl = ref(null)
const riskChartEl = ref(null)

let sentimentChart = null
let platformChart = null
let trendChart = null
let riskChart = null

// 情感颜色
const sentimentColors = {
  '正向': '#67b8e3',
  '中性': '#a0aec0',
  '负向': '#fc8181',
}

function initSentimentChart(data) {
  if (!sentimentChartEl.value) return
  sentimentChart = echarts.init(sentimentChartEl.value)
  sentimentChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, left: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '45%'],
      data: data.map(d => ({ ...d, itemStyle: { color: sentimentColors[d.name] } })),
      label: { formatter: '{b}\n{d}%' },
    }],
  })
}

function initPlatformChart(data) {
  if (!platformChartEl.value) return
  platformChart = echarts.init(platformChartEl.value)
  platformChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, left: 'center' },
    color: ['#67b8e3', '#8fc9eb', '#a8d4f0', '#c5e4f5', '#4a9ed4', '#2c7eb3', '#1a5f8a', '#0e4068'],
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '45%'],
      data,
      label: { formatter: '{b}\n{d}%' },
    }],
  })
}

function initTrendChart(data) {
  if (!trendChartEl.value) return
  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date),
      axisLine: { lineStyle: { color: '#e2e8f0' } },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
    },
    series: [{
      name: '舆情数量',
      type: 'line',
      smooth: true,
      data: data.map(d => d.count),
      lineStyle: { color: '#67b8e3', width: 2 },
      itemStyle: { color: '#67b8e3' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(103,184,227,0.3)' },
          { offset: 1, color: 'rgba(103,184,227,0.02)' },
        ]),
      },
    }],
  })
}

function initRiskChart(data) {
  if (!riskChartEl.value) return
  riskChart = echarts.init(riskChartEl.value)
  riskChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, left: 'center' },
    color: ['#67c23a', '#e6a23c', '#f56c6c'],
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '45%'],
      data: data.length
        ? data
        : [{ name: '暂无评估数据', value: 1, itemStyle: { color: '#e2e8f0' } }],
      label: { formatter: '{b}\n{d}%' },
    }],
  })
}

const handleResize = () => {
  sentimentChart?.resize()
  platformChart?.resize()
  trendChart?.resize()
  riskChart?.resize()
}

onMounted(async () => {
  try {
    const u = localStorage.getItem('user')
    if (u) username.value = JSON.parse(u).username || 'admin'
  } catch (_) {}

  try {
    const [s, sent, plat, trend, risk] = await Promise.all([
      getStats(),
      getSentiment(),
      getPlatform(),
      getTrend(),
      getRisk(),
    ])
    stats.value = s.data ?? stats.value
    initSentimentChart(sent.data?.data || [])
    initPlatformChart(plat.data?.data || [])
    initTrendChart(trend.data?.data || [])
    initRiskChart(risk.data?.data || [])
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '看板数据加载失败')
    initSentimentChart([])
    initPlatformChart([])
    initTrendChart([])
    initRiskChart([])
  }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  sentimentChart?.dispose()
  platformChart?.dispose()
  trendChart?.dispose()
  riskChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}
.welcome-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px 36px;
  background: linear-gradient(135deg, #67b8e3 0%, #8fc9eb 100%);
  border-radius: 12px;
  color: #fff;
  margin-bottom: 20px;
  overflow: hidden;
}
.welcome-text h1 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
}
.welcome-text p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}
.welcome-icon {
  opacity: 0.2;
}
.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.stat-card {
  flex: 1;
  border-radius: 12px;
  border: none;
}
.stat-card :deep(.el-card__body) {
  padding: 20px;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}
.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #334155;
}
.charts-row {
  display: flex;
  gap: 20px;
}
.chart-card {
  flex: 1;
  border-radius: 12px;
  border: none;
}
.chart-box {
  height: 280px;
  width: 100%;
}
.bayes-desc {
  padding: 4px 0;
}
.bayes-nodes {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.bayes-node {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 20px;
  min-width: 120px;
}
.node-title {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
  text-align: center;
}
.node-item {
  font-size: 13px;
  color: #334155;
  padding: 3px 0;
  text-align: center;
}
.node-high   { color: #f56c6c; font-weight: 600; }
.node-medium { color: #e6a23c; font-weight: 600; }
.node-low    { color: #67c23a; font-weight: 600; }
.input-node  { background: #f0f9ff; border-color: #67b8e3; }
.output-node { background: #fef9f0; border-color: #e6a23c; }
.bayes-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
  min-width: 120px;
}
.arrow-label  { font-size: 12px; color: #67b8e3; font-weight: 600; }
.arrow-line   { font-size: 28px; color: #94a3b8; letter-spacing: -4px; }
.arrow-formula { font-size: 11px; color: #94a3b8; }
.bayes-note {
  font-size: 13px;
  color: #64748b;
  line-height: 1.7;
  margin: 0;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 3px solid #67b8e3;
}
</style>

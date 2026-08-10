<template>
  <div class="user-home">
    <div class="welcome-card">
      <h1>欢迎，{{ username }}</h1>
      <p>校园舆情公开数据概览，仅供浏览</p>
    </div>

    <div class="stats-row">
      <el-card shadow="hover" class="stat-card" v-for="(s, i) in statCards" :key="i">
        <div class="stat-label">{{ s.label }}</div>
        <div class="stat-value">{{ s.value }}</div>
      </el-card>
    </div>

    <!-- 热门舆情 -->
    <el-card shadow="hover" class="hot-card">
      <template #header>
        <span>{{ subscribedCategories.length ? '我关心的 · ' : '' }}本周 / 本月热门舆情</span>
        <el-radio-group v-model="hotPeriod" size="small" style="margin-left: 12px" @change="loadHot">
          <el-radio-button value="week">本周</el-radio-button>
          <el-radio-button value="month">本月</el-radio-button>
        </el-radio-group>
      </template>
      <div class="hot-list" v-loading="hotLoading">
        <template v-if="hotList.length">
          <div
            v-for="item in hotList"
            :key="item.id"
            class="hot-item"
            @click="goDetail(item.id)"
          >
            <span class="hot-title">{{ item.title || '无标题' }}</span>
            <span class="hot-meta">{{ item.source_platform || '' }} · {{ item.category || '' }}</span>
            <el-tag
              :type="item.sentiment === 'positive' ? 'success' : item.sentiment === 'negative' ? 'danger' : 'info'"
              size="small"
              effect="plain"
              class="hot-tag"
            >
              {{ item.sentiment === 'positive' ? '正向' : item.sentiment === 'negative' ? '负向' : '中性' }}
            </el-tag>
          </div>
        </template>
        <el-empty v-else description="暂无近期热门" :image-size="60" />
      </div>
    </el-card>

    <div class="charts-row">
      <el-card shadow="hover" class="chart-card">
        <template #header><span>情感分布</span></template>
        <div ref="sentimentChartEl" class="chart-box"></div>
      </el-card>
      <el-card shadow="hover" class="chart-card">
        <template #header><span>近 7 天舆情趋势</span></template>
        <div ref="trendChartEl" class="chart-box"></div>
      </el-card>
    </div>

    <!-- 帮助说明 -->
    <el-collapse class="help-collapse">
      <el-collapse-item name="help">
        <template #title>
          <el-icon><QuestionFilled /></el-icon>
          <span class="help-title">使用说明</span>
        </template>
        <div class="help-content">
          <p><strong>情感标签含义：</strong></p>
          <ul>
            <li><el-tag type="success" size="small">正向</el-tag>：积极正面情绪，如称赞、满意</li>
            <li><el-tag type="danger" size="small">负向</el-tag>：消极负面情绪，如不满、批评</li>
            <li><el-tag type="info" size="small">中性</el-tag>：无明显情感倾向的客观表述</li>
          </ul>
          <p><strong>主题分类：</strong></p>
          <ul>
            <li>教学、宿舍、食堂、安全、后勤等，用于快速筛选相关领域的舆情</li>
          </ul>
          <p><strong>普通用户权限：</strong>仅可浏览公开舆情统计数据，无法进行管理操作。如需管理权限，请联系管理员。</p>
        </div>
      </el-collapse-item>
    </el-collapse>

    <el-alert
      title="说明"
      type="info"
      :closable="false"
      style="margin-top: 20px"
      description="普通用户仅可浏览公开舆情统计数据，无法进行管理操作。如需管理权限，请联系管理员。"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useRouter } from 'vue-router'
import { getStats, getSentiment, getTrend, getHotOpinions } from '../../api/dashboard'
import { getMyTopics } from '../../api/topicPreference'

const router = useRouter()
const username = ref('')
const hotPeriod = ref('week')
const hotList = ref([])
const hotLoading = ref(false)
const subscribedCategories = ref([])
const stats = ref({ total: 0, today: 0, pending_warning: 0, platform_count: 0 })

const statCards = computed(() => [
  { label: '舆情总量', value: stats.value.total },
  { label: '今日新增', value: stats.value.today },
  { label: '来源平台数', value: stats.value.platform_count },
])

const sentimentChartEl = ref(null)
const trendChartEl = ref(null)
let sentimentChart = null
let trendChart = null

const handleResize = () => {
  sentimentChart?.resize()
  trendChart?.resize()
}

const sentimentColors = { '正向': '#67b8e3', '中性': '#a0aec0', '负向': '#fc8181' }

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
      data: (data.length ? data : [{ name: '暂无数据', value: 1, itemStyle: { color: '#e2e8f0' } }])
        .map(d => ({ ...d, itemStyle: { color: sentimentColors[d.name] || d.itemStyle?.color } })),
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
      data: (data && data.length) ? data.map(d => d.date) : [],
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
      data: (data && data.length) ? data.map(d => d.count) : [],
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

onMounted(async () => {
  try {
    const u = localStorage.getItem('user')
    if (u) username.value = JSON.parse(u).username || ''
  } catch (_) {}

  try {
    const [s, sent, trend] = await Promise.all([
      getStats(),
      getSentiment(),
      getTrend(),
    ])
    stats.value = s.data ?? {}
    initSentimentChart(sent.data?.data || [])
    initTrendChart(trend.data?.data || [])
  } catch (_) {
    initSentimentChart([])
    initTrendChart([])
  }

  window.addEventListener('resize', handleResize)
  getMyTopics().then(({ data }) => {
    subscribedCategories.value = data?.categories || []
    loadHot()
  }).catch(() => loadHot())
})

const loadHot = async () => {
  hotLoading.value = true
  try {
    const params = { period: hotPeriod.value, limit: 8 }
    if (subscribedCategories.value.length) params.categories = subscribedCategories.value.join(',')
    const { data } = await getHotOpinions(params)
    hotList.value = data?.data || []
  } catch (_) {
    hotList.value = []
  } finally {
    hotLoading.value = false
  }
}

const goDetail = (id) => {
  router.push(`/user/browse/${id}`)
}

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  sentimentChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.user-home { width: 100%; }
.welcome-card {
  padding: 24px;
  background: linear-gradient(135deg, #67b8e3 0%, #8fc9eb 100%);
  border-radius: 12px;
  color: #fff;
  margin-bottom: 20px;
}
.welcome-card h1 { margin: 0 0 8px; font-size: 22px; }
.welcome-card p { margin: 0; font-size: 14px; opacity: 0.9; }
.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card {
  flex: 1;
  border-radius: 12px;
  border: none;
}
.stat-label { font-size: 14px; color: #64748b; margin-bottom: 4px; }
.stat-value { font-size: 24px; font-weight: 700; color: #334155; }
.charts-row { display: flex; gap: 20px; flex-wrap: wrap; }
.hot-card { margin-bottom: 20px; border-radius: 12px; border: none; }
.hot-list { min-height: 120px; }
.hot-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  font-size: 14px;
}
.hot-item:last-child { border-bottom: none; }
.hot-item:hover { color: #67b8e3; }
.hot-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hot-meta { font-size: 12px; color: #94a3b8; flex-shrink: 0; }
.hot-tag { flex-shrink: 0; }
.help-collapse {
  margin-top: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}
.help-title { margin-left: 8px; }
.help-content {
  padding: 16px 20px;
  font-size: 14px;
  color: #475569;
  line-height: 1.7;
}
.help-content p { margin: 12px 0 8px; }
.help-content p:first-child { margin-top: 0; }
.help-content ul { margin: 0; padding-left: 20px; }
.help-content li { margin: 4px 0; }
.chart-card { flex: 1; min-width: 280px; border-radius: 12px; border: none; }
.chart-box { height: 260px; width: 100%; }
</style>

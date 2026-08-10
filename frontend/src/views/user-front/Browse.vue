<template>
  <div class="user-browse">
    <!-- 筛选区 -->
    <div class="filter-bar">
      <el-autocomplete
        v-model="filters.keyword"
        :fetch-suggestions="fetchSearchSuggestions"
        placeholder="搜索关键词..."
        clearable
        class="filter-input"
        @keyup.enter="loadList"
        @select="(item) => { filters.keyword = item.value; loadList() }"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #default="{ item }">
          <span>{{ item.value }}</span>
          <span v-if="item.type" class="suggestion-tag">{{ item.type }}</span>
        </template>
      </el-autocomplete>
      <el-select v-model="filters.sentiment" placeholder="情感" clearable class="filter-select" @change="loadList">
        <el-option label="全部情感" value="" />
        <el-option label="正向" value="positive" />
        <el-option label="中性" value="neutral" />
        <el-option label="负向" value="negative" />
      </el-select>
      <el-select v-model="filters.source_platform" placeholder="来源平台" clearable class="filter-select" @change="loadList">
        <el-option label="全部平台" value="" />
        <el-option label="微博" value="微博" />
        <el-option label="微信" value="微信" />
        <el-option label="知乎" value="知乎" />
        <el-option label="校园官网" value="校园官网" />
        <el-option label="论坛" value="论坛" />
        <el-option label="百度新闻" value="百度新闻" />
      </el-select>
      <el-button
        v-if="subscribedCategories.length"
        :type="filters.useSubscribed ? 'primary' : 'default'"
        class="filter-btn"
        @click="toggleSubscribed"
      >
        我关心的
      </el-button>
      <el-button type="primary" class="search-btn" @click="loadList">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
      <el-button class="export-btn" @click="exportData">
        <el-icon><Download /></el-icon>
        导出
      </el-button>
    </div>

    <!-- 舆情卡片列表 -->
    <div class="opinion-list" v-loading="loading">
      <template v-if="list.length">
        <div
          v-for="item in list"
          :key="item.id"
          class="opinion-card"
          @click="openDetail(item)"
        >
          <div class="card-accent" :class="item.sentiment"></div>
          <div class="card-body">
            <div class="card-header-row">
              <h3 class="card-title">{{ item.title || '无标题' }}</h3>
              <el-button
                :type="favoriteIds.has(item.id) ? 'warning' : 'default'"
                link
                size="small"
                class="fav-btn"
                @click.stop="toggleFavorite(item)"
              >
                <el-icon><StarFilled v-if="favoriteIds.has(item.id)" /><Star v-else /></el-icon>
                {{ favoriteIds.has(item.id) ? '已收藏' : '收藏' }}
              </el-button>
            </div>
            <p class="card-excerpt">{{ (item.content || '').slice(0, 80) }}{{ (item.content || '').length > 80 ? '...' : '' }}</p>
            <div class="card-meta">
              <span class="meta-source">{{ item.source_platform || '未知' }}</span>
              <el-tag
                :type="item.sentiment === 'positive' ? 'success' : item.sentiment === 'negative' ? 'danger' : 'info'"
                size="small"
                effect="plain"
                class="meta-tag"
              >
                {{ item.sentiment === 'positive' ? '正向' : item.sentiment === 'negative' ? '负向' : '中性' }}
              </el-tag>
              <el-tag v-if="item.category" type="primary" size="small" effect="plain" class="meta-tag">
                {{ item.category }}
              </el-tag>
              <span class="meta-time">{{ formatTime(item.publish_time || item.created_at) }}</span>
            </div>
            <div class="card-footer">
              <span class="read-more">阅读全文</span>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </template>
      <el-empty v-else description="暂无舆情数据" class="empty-box" />
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="total > 0">
      <el-pagination
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        :page-sizes="[8, 16, 24]"
        layout="total, prev, pager, next, sizes"
        background
        @current-change="(val) => { page = val; loadList() }"
        @size-change="(val) => { pageSize = val; page = 1; loadList() }"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, ArrowRight, Star, StarFilled, Download } from '@element-plus/icons-vue'
import { listOpinions } from '../../api/opinion'
import { getFavoriteIds, addFavorite, removeFavorite } from '../../api/favorite'
import { getMyTopics } from '../../api/topicPreference'

const router = useRouter()

const loading = ref(false)
const favoriteIds = ref(new Set())
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(8)
const filters = ref({ keyword: '', sentiment: '', source_platform: '', useSubscribed: false })
const subscribedCategories = ref([])

const SEARCH_HISTORY_KEY = 'opinion_search_history'
const COMMON_KEYWORDS = ['食堂', '宿舍', '安全', '教学', '后勤', '图书馆', '校园']
const MAX_HISTORY = 10

function getSearchHistory() {
  try {
    const s = localStorage.getItem(SEARCH_HISTORY_KEY)
    return s ? JSON.parse(s) : []
  } catch { return [] }
}

function saveSearchKeyword(kw) {
  if (!kw || !kw.trim()) return
  const arr = getSearchHistory()
  const trimmed = kw.trim()
  const filtered = arr.filter(x => x !== trimmed)
  filtered.unshift(trimmed)
  localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(filtered.slice(0, MAX_HISTORY)))
}

const fetchSearchSuggestions = (queryString, cb) => {
  const history = getSearchHistory()
  const results = []
  if (queryString) {
    const q = queryString.toLowerCase()
    history.filter(h => h.toLowerCase().includes(q)).forEach(h => results.push({ value: h, type: '历史' }))
    COMMON_KEYWORDS.filter(k => k.includes(queryString) || queryString.includes(k)).forEach(k => results.push({ value: k, type: '常用' }))
  } else {
    history.slice(0, 5).forEach(h => results.push({ value: h, type: '历史' }))
    COMMON_KEYWORDS.slice(0, 5).forEach(k => results.push({ value: k, type: '常用' }))
  }
  cb(results)
}

function formatTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  if (isNaN(d.getTime())) return val
  const now = new Date()
  const diff = now - d
  if (diff < 86400000) return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  return d.toLocaleDateString('zh-CN')
}

const loadFavoriteIds = async () => {
  try {
    const { data } = await getFavoriteIds()
    favoriteIds.value = new Set(data.ids || [])
  } catch (_) {}
}

const toggleFavorite = async (item) => {
  try {
    if (favoriteIds.value.has(item.id)) {
      await removeFavorite(item.id)
      favoriteIds.value = new Set([...favoriteIds.value].filter(id => id !== item.id))
      ElMessage.success('已取消收藏')
    } else {
      await addFavorite(item.id)
      favoriteIds.value = new Set([...favoriteIds.value, item.id])
      ElMessage.success('收藏成功')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

const toggleSubscribed = () => {
  filters.value.useSubscribed = !filters.value.useSubscribed
  page.value = 1
  loadList()
}

const loadList = async () => {
  if (filters.value.keyword?.trim()) saveSearchKeyword(filters.value.keyword)
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      keyword: filters.value.keyword || undefined,
      sentiment: filters.value.sentiment || undefined,
      source_platform: filters.value.source_platform || undefined,
    }
    if (filters.value.useSubscribed && subscribedCategories.value.length) {
      params.categories = subscribedCategories.value.join(',')
    }
    const { data } = await listOpinions(params)
    list.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

const openDetail = (row) => {
  router.push(`/user/browse/${row.id}`)
}

function formatDateForExport(val) {
  if (!val) return ''
  const d = new Date(val)
  if (isNaN(d.getTime())) return ''
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  const s = String(d.getSeconds()).padStart(2, '0')
  const dateStr = `${y}-${m}-${day} ${h}:${min}:${s}`
  // Excel 公式 ="" 强制以文本显示，避免 ########
  return '="' + dateStr + '"'
}

const exportData = async () => {
  try {
    const params = {
      page: 1,
      page_size: Math.min(total.value, 1000),
      keyword: filters.value.keyword || undefined,
      sentiment: filters.value.sentiment || undefined,
      source_platform: filters.value.source_platform || undefined,
    }
    if (filters.value.useSubscribed && subscribedCategories.value.length) {
      params.categories = subscribedCategories.value.join(',')
    }
    const { data } = await listOpinions(params)
    const items = data.items || []
    if (!items.length) {
      ElMessage.warning('暂无数据可导出')
      return
    }
    const headers = ['ID', '标题', '内容摘要', '来源平台', '作者', '发布时间', '情感', '主题分类', '关键词']
    const escapeCsv = (s) => String(s ?? '').replace(/"/g, '""')
    const rows = items.map(o => [
      o.id,
      o.title || '',
      (o.content || '').slice(0, 200),
      o.source_platform || '',
      o.author || '',
      formatDateForExport(o.publish_time || o.created_at),
      o.sentiment === 'positive' ? '正向' : o.sentiment === 'negative' ? '负向' : '中性',
      o.category || '',
      o.keywords || '',
    ])
    const csvContent = '\uFEFF' + [
      headers.join(','),
      ...rows.map(r => r.map(c => `"${escapeCsv(c)}"`).join(',')),
    ].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `舆情数据_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '导出失败')
  }
}

onMounted(async () => {
  await loadFavoriteIds()
  try {
    const { data } = await getMyTopics()
    subscribedCategories.value = data?.categories || []
  } catch (_) {}
  loadList()
})
</script>

<style scoped>
.user-browse { width: 100%; }

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}
.filter-input {
  flex: 1;
  min-width: 180px;
  max-width: 280px;
}
.filter-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e2e8f0;
}
.filter-select {
  width: 130px;
}
.filter-input :deep(.el-input__wrapper),
.filter-input :deep(.el-autocomplete-suggestion) { border-radius: 8px; }
.suggestion-tag { font-size: 11px; color: #94a3b8; margin-left: 8px; }
.filter-select :deep(.el-input__wrapper) {
  border-radius: 8px;
}
.search-btn, .export-btn, .filter-btn {
  border-radius: 8px;
  padding: 8px 20px;
}

.opinion-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 200px;
}
.opinion-card {
  position: relative;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
}
.opinion-card:hover {
  border-color: #67b8e3;
  box-shadow: 0 4px 16px rgba(103, 184, 227, 0.15);
  transform: translateY(-2px);
}
.card-accent {
  width: 4px;
  flex-shrink: 0;
}
.card-accent.positive { background: linear-gradient(180deg, #67c23a 0%, #85ce61 100%); }
.card-accent.negative { background: linear-gradient(180deg, #f56c6c 0%, #f78989 100%); }
.card-accent.neutral,
.card-accent { background: linear-gradient(180deg, #909399 0%, #a6a9ad 100%); }
.card-body {
  flex: 1;
  padding: 20px 24px;
}
.card-header-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 8px; }
.card-title {
  flex: 1;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.fav-btn { flex-shrink: 0; }
.card-excerpt {
  margin: 0 0 12px;
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.meta-source {
  font-size: 12px;
  color: #67b8e3;
  font-weight: 500;
}
.meta-tag { margin-right: 0 !important; }
.meta-time {
  font-size: 12px;
  color: #94a3b8;
  margin-left: auto;
}
.card-footer {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #67b8e3;
  font-weight: 500;
}
.card-footer .el-icon { font-size: 14px; }

.empty-box {
  padding: 60px 0;
}

.pagination-wrap {
  margin-top: 28px;
  display: flex;
  justify-content: center;
}
.pagination-wrap :deep(.el-pagination.is-background .el-pager li.is-active) {
  background: #67b8e3;
}
</style>

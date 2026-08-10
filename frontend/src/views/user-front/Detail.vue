<template>
  <div class="opinion-detail-page">
    <div class="top-actions">
      <el-button class="back-btn" type="primary" link @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <el-button
        v-if="detail"
        :type="isFavorited ? 'warning' : 'default'"
        link
        @click="toggleFavorite"
      >
        <el-icon><StarFilled v-if="isFavorited" /><Star v-else /></el-icon>
        {{ isFavorited ? '已收藏' : '收藏' }}
      </el-button>
    </div>

    <div v-loading="loading" class="detail-wrapper">
      <article v-if="detail" class="article">
        <div class="article-header">
          <span class="sentiment-badge" :class="detail.sentiment">
            {{ detail.sentiment === 'positive' ? '正向' : detail.sentiment === 'negative' ? '负向' : '中性' }}
          </span>
          <h1 class="article-title">{{ detail.title || '无标题' }}</h1>
          <div class="article-meta">
            <span class="meta-item">
              <el-icon><Monitor /></el-icon>
              {{ detail.source_platform || '未知来源' }}
            </span>
            <span class="meta-item" v-if="detail.category">
              <el-icon><Collection /></el-icon>
              {{ detail.category }}
            </span>
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatTime(detail.publish_time || detail.created_at) }}
            </span>
            <span class="meta-item" v-if="detail.author">
              <el-icon><User /></el-icon>
              {{ detail.author }}
            </span>
          </div>
          <div class="article-tags" v-if="detail.keywords">
            <el-tag v-for="kw in keywordsList" :key="kw" size="small" effect="plain" class="tag">{{ kw }}</el-tag>
          </div>
        </div>

        <div class="article-body">
          <div class="content-text">{{ detail.content || '暂无正文内容' }}</div>
        </div>

        <div class="article-footer" v-if="detail.source_url">
          <el-link :href="detail.source_url" target="_blank" type="primary" :underline="false">
            <el-icon><Link /></el-icon>
            查看原文链接
          </el-link>
        </div>

        <div class="article-extra" v-if="detail.risk_level || detail.sentiment_score != null">
          <div class="extra-card" v-if="detail.risk_level">
            <span class="extra-label">风险评估</span>
            <el-tag
              :type="detail.risk_level === 'high' ? 'danger' : detail.risk_level === 'medium' ? 'warning' : 'success'"
              size="large"
            >
              {{ detail.risk_level === 'high' ? '高风险' : detail.risk_level === 'medium' ? '中风险' : '低风险' }}
            </el-tag>
          </div>
          <div class="extra-card" v-if="detail.sentiment_score != null">
            <span class="extra-label">情感得分</span>
            <span class="extra-value">{{ Number(detail.sentiment_score).toFixed(2) }}</span>
          </div>
        </div>
      </article>
      <el-empty v-else-if="!loading" description="未找到该舆情" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Monitor, Collection, Clock, User, Link, Star, StarFilled } from '@element-plus/icons-vue'
import { getOpinion } from '../../api/opinion'
import { getFavoriteIds, addFavorite, removeFavorite } from '../../api/favorite'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const detail = ref(null)
const isFavorited = ref(false)

const keywordsList = computed(() => {
  const kw = detail.value?.keywords
  if (!kw) return []
  return kw.split(',').map(s => s.trim()).filter(Boolean)
})

function formatTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  return isNaN(d.getTime()) ? val : d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const goBack = () => {
  router.push('/user/browse')
}

const loadDetail = async () => {
  const id = route.params.id
  if (!id) return
  loading.value = true
  try {
    const [opinionRes, favRes] = await Promise.all([
      getOpinion(id),
      getFavoriteIds(),
    ])
    detail.value = opinionRes.data
    const ids = new Set(favRes.data?.ids || [])
    isFavorited.value = ids.has(Number(id))
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '加载失败')
    detail.value = null
  } finally {
    loading.value = false
  }
}

const toggleFavorite = async () => {
  const id = detail.value?.id
  if (!id) return
  try {
    if (isFavorited.value) {
      await removeFavorite(id)
      isFavorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await addFavorite(id)
      isFavorited.value = true
      ElMessage.success('收藏成功')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

onMounted(() => loadDetail())
</script>

<style scoped>
.opinion-detail-page {
  width: 100%;
  padding-bottom: 48px;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
.back-btn {
  font-size: 14px;
  color: #67b8e3;
}
.back-btn .el-icon {
  margin-right: 4px;
  vertical-align: middle;
}

.detail-wrapper {
  min-height: 300px;
}

.article {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
}

.article-header {
  padding: 40px 48px 32px;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
  border-bottom: 1px solid #e2e8f0;
}

.sentiment-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 16px;
}
.sentiment-badge.positive {
  background: rgba(103, 194, 58, 0.15);
  color: #67c23a;
}
.sentiment-badge.negative {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
}
.sentiment-badge.neutral {
  background: rgba(144, 147, 153, 0.15);
  color: #909399;
}

.article-title {
  margin: 0 0 20px;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.4;
  letter-spacing: -0.02em;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 16px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #64748b;
}
.meta-item .el-icon {
  font-size: 16px;
  color: #94a3b8;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.article-tags .tag {
  color: #67b8e3;
  border-color: rgba(103, 184, 227, 0.5);
}

.article-body {
  padding: 36px 48px;
}

.content-text {
  font-size: 17px;
  line-height: 1.9;
  color: #334155;
  white-space: pre-wrap;
  word-break: break-word;
}

.article-footer {
  padding: 24px 48px 36px;
  border-top: 1px solid #f1f5f9;
}

.article-extra {
  display: flex;
  gap: 24px;
  padding: 24px 48px 36px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.extra-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}
.extra-label {
  font-size: 13px;
  color: #64748b;
}
.extra-value {
  font-size: 18px;
  font-weight: 600;
  color: #334155;
}

@media (max-width: 768px) {
  .article-header,
  .article-body,
  .article-footer,
  .article-extra {
    padding-left: 24px;
    padding-right: 24px;
  }
  .article-title {
    font-size: 22px;
  }
}
</style>

<template>
  <div class="user-favorites">
    <h2 class="page-title">我的收藏</h2>

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
                type="danger"
                link
                size="small"
                class="unfav-btn"
                @click.stop="handleUnfavorite(item)"
              >
                <el-icon><StarFilled /></el-icon>
                取消收藏
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
      <el-empty v-else description="暂无收藏，去舆情浏览中添加吧" class="empty-box" />
    </div>

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
import { ArrowRight, StarFilled } from '@element-plus/icons-vue'
import { listFavorites, removeFavorite } from '../../api/favorite'

const router = useRouter()

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(8)

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

const loadList = async () => {
  loading.value = true
  try {
    const { data } = await listFavorites({ page: page.value, page_size: pageSize.value })
    list.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

const handleUnfavorite = async (item) => {
  try {
    await removeFavorite(item.id)
    ElMessage.success('已取消收藏')
    loadList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

const openDetail = (row) => {
  router.push(`/user/browse/${row.id}`)
}

onMounted(() => loadList())
</script>

<style scoped>
.user-favorites { width: 100%; }
.page-title { margin: 0 0 20px; font-size: 20px; color: #1e293b; }
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
.card-accent { width: 4px; flex-shrink: 0; }
.card-accent.positive { background: linear-gradient(180deg, #67c23a 0%, #85ce61 100%); }
.card-accent.negative { background: linear-gradient(180deg, #f56c6c 0%, #f78989 100%); }
.card-accent.neutral, .card-accent { background: linear-gradient(180deg, #909399 0%, #a6a9ad 100%); }
.card-body { flex: 1; padding: 20px 24px; }
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
.unfav-btn { flex-shrink: 0; }
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
.card-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-bottom: 12px; }
.meta-source { font-size: 12px; color: #67b8e3; font-weight: 500; }
.meta-tag { margin-right: 0 !important; }
.meta-time { font-size: 12px; color: #94a3b8; margin-left: auto; }
.card-footer { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #67b8e3; font-weight: 500; }
.empty-box { padding: 60px 0; }
.pagination-wrap { margin-top: 28px; display: flex; justify-content: center; }
.pagination-wrap :deep(.el-pagination.is-background .el-pager li.is-active) { background: #67b8e3; }
</style>

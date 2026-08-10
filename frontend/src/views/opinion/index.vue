<template>
  <div class="opinion-page">
    <el-card class="list-page-card">
      <template #header>
        <span class="card-title">舆情数据列表</span>
        <div style="display: inline-flex; gap: 8px;">
          <el-button type="success" :loading="batchLoading" @click="handleBatchAnalyze">批量分析</el-button>
          <el-button type="warning" :loading="batchRiskLoading" @click="handleBatchRisk">批量评估风险</el-button>
          <el-button type="primary" @click="openDialog()">新增舆情</el-button>
        </div>
      </template>
      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-input v-model="filters.keyword" placeholder="关键词" clearable style="width: 160px" @keyup.enter="loadList" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.sentiment" placeholder="情感" clearable style="width: 110px" @change="loadList">
            <el-option label="正向" value="positive" />
            <el-option label="中性" value="neutral" />
            <el-option label="负向" value="negative" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input v-model="filters.source_platform" placeholder="来源平台" clearable style="width: 120px" @keyup.enter="loadList" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.category" placeholder="主题分类" clearable style="width: 120px" @change="loadList">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">搜索</el-button>
        </el-form-item>
      </el-form>
      <el-table
        :data="list"
        v-loading="loading"
        class="list-table"
        style="width: 100%"
        :header-cell-style="{ textAlign: 'center', background: '#f8f9fa', fontWeight: '700', fontSize: '13px' }"
      >
        <template #empty>
          <el-empty description="暂无数据" />
        </template>
        <el-table-column label="序号" width="60" align="center">
          <template #default="{ $index }">
            {{ (page - 1) * pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column label="标题" min-width="180" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.title || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="110" align="center">
          <template #default="{ row }">
            {{ row.source_platform || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="情感" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.sentiment === 'positive'" type="success">正向</el-tag>
            <el-tag v-else-if="row.sentiment === 'negative'" type="danger">负向</el-tag>
            <el-tag v-else type="info">中性</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="贝叶斯风险" width="100" align="center">
          <template #default="{ row }">
            <el-tooltip v-if="row.risk_level" :content="`风险概率: ${row.risk_score ? (row.risk_score * 100).toFixed(1) + '%' : '-'}`" placement="top">
              <el-tag
                :type="row.risk_level === 'high' ? 'danger' : row.risk_level === 'medium' ? 'warning' : 'success'"
              >{{ riskLabel(row.risk_level) }}</el-tag>
            </el-tooltip>
            <span v-else style="color:#c0c4cc;font-size:12px">未评估</span>
          </template>
        </el-table-column>
        <el-table-column label="主题" width="80" align="center">
          <template #default="{ row }">
            {{ row.category || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="关键词" width="130" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.keywords || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160" align="center">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDetail(row)">详情</el-button>
            <el-button type="success" link :loading="analyzingId === row.id" @click="handleAnalyze(row)">分析</el-button>
            <el-button type="warning" link :loading="riskingId === row.id" @click="handleRisk(row)">评估</el-button>
            <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
      <el-pagination
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        class="pagination"
        @current-change="(val) => { page = val; loadList() }"
        @size-change="(val) => { pageSize = val; page = 1; loadList() }"
      />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑舆情' : '新增舆情'" width="640" @close="resetForm">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="正文内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请输入正文" />
        </el-form-item>
        <el-form-item label="来源平台" prop="source_platform">
          <el-input v-model="form.source_platform" placeholder="如：微博、微信、知乎" />
        </el-form-item>
        <el-form-item label="原始链接" prop="source_url">
          <el-input v-model="form.source_url" placeholder="选填" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="form.author" placeholder="选填" />
        </el-form-item>
        <el-form-item label="发布时间" prop="publish_time">
          <el-date-picker
            v-model="form.publish_time"
            type="datetime"
            placeholder="选填"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="关键词" prop="keywords">
          <el-input v-model="form.keywords" placeholder="多个用英文逗号分隔" />
        </el-form-item>
        <el-form-item label="情感分类" prop="sentiment">
          <el-select v-model="form.sentiment" placeholder="请选择" style="width: 100%">
            <el-option label="正向" value="positive" />
            <el-option label="中性" value="neutral" />
            <el-option label="负向" value="negative" />
          </el-select>
        </el-form-item>
        <el-form-item label="情感得分" prop="sentiment_score">
          <el-input-number v-model="form.sentiment_score" :min="-1" :max="1" :step="0.1" placeholder="选填" style="width: 100%" />
        </el-form-item>
        <el-form-item label="主题分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择" clearable style="width: 100%">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="舆情详情" width="640">
      <el-descriptions :column="1" border v-if="detail">
        <el-descriptions-item label="标题">{{ detail.title || '-' }}</el-descriptions-item>
        <el-descriptions-item label="正文">
          <div class="detail-content">{{ detail.content || '-' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="来源平台">{{ detail.source_platform || '-' }}</el-descriptions-item>
        <el-descriptions-item label="原始链接">
          <a v-if="detail.source_url" :href="detail.source_url" target="_blank" rel="noopener">{{ detail.source_url }}</a>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="作者">{{ detail.author || '-' }}</el-descriptions-item>
        <el-descriptions-item label="发布时间">{{ formatTime(detail.publish_time) }}</el-descriptions-item>
        <el-descriptions-item label="关键词">{{ detail.keywords || '-' }}</el-descriptions-item>
        <el-descriptions-item label="情感">
          <el-tag v-if="detail.sentiment === 'positive'" type="success">正向</el-tag>
          <el-tag v-else-if="detail.sentiment === 'negative'" type="danger">负向</el-tag>
          <el-tag v-else type="info">中性</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="情感得分">{{ detail.sentiment_score ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="主题分类">{{ detail.category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="贝叶斯风险等级">
          <el-tag v-if="detail.risk_level"
            :type="detail.risk_level === 'high' ? 'danger' : detail.risk_level === 'medium' ? 'warning' : 'success'"
          >{{ riskLabel(detail.risk_level) }}</el-tag>
          <span v-else>未评估</span>
          <span v-if="detail.risk_score" style="margin-left:8px;color:#909399;font-size:12px">
            概率 {{ (detail.risk_score * 100).toFixed(1) }}%
          </span>
        </el-descriptions-item>
        <el-descriptions-item v-if="detail.risk_detail" label="风险概率明细">
          <div class="risk-detail-box">
            <div v-for="(v, k) in parsedRiskDetail(detail.risk_detail)?.posterior" :key="k" class="risk-bar-item">
              <span class="risk-bar-label">{{ { low:'低风险', medium:'中风险', high:'高风险' }[k] }}</span>
              <el-progress
                :percentage="+(v * 100).toFixed(1)"
                :color="k === 'high' ? '#f56c6c' : k === 'medium' ? '#e6a23c' : '#67c23a'"
                :stroke-width="10"
                style="flex:1"
              />
              <span class="risk-bar-pct">{{ (v * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listOpinions, getOpinion, createOpinion, updateOpinion, deleteOpinion, analyzeOpinion, batchAnalyze, assessRisk, batchRisk } from '../../api/opinion'

const categories = ['教学', '宿舍', '食堂', '安全', '后勤']

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filters = ref({
  keyword: '',
  sentiment: '',
  source_platform: '',
  category: '',
})

const analyzingId = ref(null)
const batchLoading = ref(false)
const riskingId = ref(null)
const batchRiskLoading = ref(false)

const riskLabel = (level) => ({ low: '低风险', medium: '中风险', high: '高风险' }[level] || level)
const parsedRiskDetail = (str) => { try { return JSON.parse(str) } catch { return null } }

const dialogVisible = ref(false)
const detailVisible = ref(false)
const editId = ref(null)
const detail = ref(null)
const formRef = ref(null)
const submitLoading = ref(false)

const form = ref({
  title: '',
  content: '',
  source_platform: '',
  source_url: '',
  author: '',
  publish_time: '',
  keywords: '',
  sentiment: '',
  sentiment_score: null,
  category: '',
})

function formatTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  return isNaN(d.getTime()) ? val : d.toLocaleString('zh-CN')
}

const loadList = async () => {
  loading.value = true
  try {
    const { data } = await listOpinions({
      page: page.value,
      page_size: pageSize.value,
      keyword: filters.value.keyword || undefined,
      sentiment: filters.value.sentiment || undefined,
      source_platform: filters.value.source_platform || undefined,
      category: filters.value.category || undefined,
    })
    list.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

const openDialog = (row) => {
  editId.value = row?.id || null
  if (row) {
    form.value = {
      title: row.title || '',
      content: row.content || '',
      source_platform: row.source_platform || '',
      source_url: row.source_url || '',
      author: row.author || '',
      publish_time: row.publish_time || '',
      keywords: row.keywords || '',
      sentiment: row.sentiment || '',
      sentiment_score: row.sentiment_score != null ? row.sentiment_score : null,
      category: row.category || '',
    }
  } else {
    form.value = {
      title: '',
      content: '',
      source_platform: '',
      source_url: '',
      author: '',
      publish_time: '',
      keywords: '',
      sentiment: '',
      sentiment_score: null,
      category: '',
    }
  }
  dialogVisible.value = true
}

const resetForm = () => {
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  submitLoading.value = true
  try {
    const payload = {
      ...form.value,
      publish_time: form.value.publish_time || null,
      sentiment_score: form.value.sentiment_score != null ? form.value.sentiment_score : null,
    }
    if (editId.value) {
      await updateOpinion(editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createOpinion(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const openDetail = async (row) => {
  try {
    const { data } = await getOpinion(row.id)
    detail.value = data
    detailVisible.value = true
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '加载失败')
  }
}

const handleAnalyze = async (row) => {
  analyzingId.value = row.id
  try {
    await analyzeOpinion(row.id)
    ElMessage.success('分析完成')
    loadList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '分析失败')
  } finally {
    analyzingId.value = null
  }
}

const handleBatchAnalyze = async () => {
  batchLoading.value = true
  try {
    const { data } = await batchAnalyze()
    ElMessage.success(data.message || '批量分析完成')
    loadList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '批量分析失败')
  } finally {
    batchLoading.value = false
  }
}

const handleRisk = async (row) => {
  riskingId.value = row.id
  try {
    await assessRisk(row.id)
    ElMessage.success('风险评估完成')
    loadList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '评估失败')
  } finally {
    riskingId.value = null
  }
}

const handleBatchRisk = async () => {
  batchRiskLoading.value = true
  try {
    const { data } = await batchRisk()
    ElMessage.success(data.message || '批量评估完成')
    loadList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '批量评估失败')
  } finally {
    batchRiskLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除舆情「${row.title || row.id}」吗？`, '提示', {
    type: 'warning',
  }).then(async () => {
    try {
      await deleteOpinion(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '删除失败')
    }
  }).catch(() => {})
}

onMounted(() => loadList())
</script>

<style scoped>
.opinion-page { width: 100%; }
.detail-content {
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}
.risk-detail-box { width: 100%; }
.risk-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.risk-bar-label { width: 48px; font-size: 12px; color: #606266; }
.risk-bar-pct   { width: 44px; font-size: 12px; color: #909399; text-align: right; }
</style>

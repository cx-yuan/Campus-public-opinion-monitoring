<template>
  <div class="warning-page">
    <el-card class="list-page-card">
      <template #header>
        <span class="card-title">预警记录</span>
      </template>
      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-select v-model="filters.status" placeholder="处理状态" clearable style="width: 120px" @change="loadList">
            <el-option label="未处理" :value="0" />
            <el-option label="已处理" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.warning_level" placeholder="预警等级" clearable style="width: 120px" @change="loadList">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.warning_type" placeholder="预警类型" clearable style="width: 130px" @change="loadList">
            <el-option label="负面情感" value="negative_sentiment" />
            <el-option label="敏感词命中" value="sensitive_word" />
            <el-option label="高频舆情" value="high_frequency" />
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
          <el-empty description="暂无预警数据" />
        </template>
        <el-table-column label="序号" width="60" align="center">
          <template #default="{ $index }">
            {{ (page - 1) * pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column label="预警类型" width="120" align="center">
          <template #default="{ row }">
            {{ row.warning_type_label || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="预警等级" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.warning_level === 'high' ? 'danger' : row.warning_level === 'medium' ? 'warning' : 'info'"
            >
              {{ row.warning_level_label || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预警内容" min-width="200" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.warning_message || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="关联舆情ID" width="100" align="center">
          <template #default="{ row }">
            {{ row.opinion_id || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="处理状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 0 ? 'danger' : 'success'">
              {{ row.status === 0 ? '未处理' : '已处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预警时间" width="160" align="center">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="处理时间" width="160" align="center">
          <template #default="{ row }">
            {{ formatTime(row.handled_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 0"
              type="primary"
              link
              @click="handleProcess(row)"
            >
              标记处理
            </el-button>
            <span v-else class="handled-text">已处理</span>
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
          @current-change="(val) => { page = val; loadList() }"
          @size-change="(val) => { pageSize = val; page = 1; loadList() }"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listWarnings, handleWarning } from '../../api/warning'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filters = ref({ status: null, warning_level: '', warning_type: '' })

function formatTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  return isNaN(d.getTime()) ? val : d.toLocaleString('zh-CN')
}

const loadList = async () => {
  loading.value = true
  try {
    const { data } = await listWarnings({
      page: page.value,
      page_size: pageSize.value,
      status: filters.value.status != null ? filters.value.status : undefined,
      warning_level: filters.value.warning_level || undefined,
      warning_type: filters.value.warning_type || undefined,
    })
    list.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

const handleProcess = (row) => {
  ElMessageBox.confirm(`确定将此预警标记为已处理？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await handleWarning(row.id)
        ElMessage.success('已标记处理')
        loadList()
      } catch (err) {
        ElMessage.error(err.response?.data?.detail || '操作失败')
      }
    }).catch(() => {})
}

onMounted(() => loadList())
</script>

<style scoped>
.warning-page { width: 100%; }
.handled-text { font-size: 13px; color: #67c23a; }
</style>

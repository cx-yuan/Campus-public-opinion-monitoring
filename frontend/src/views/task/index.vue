<template>
  <div class="task-page">
    <el-card class="list-page-card">
      <template #header>
        <span class="card-title">采集任务管理</span>
        <div style="display: inline-flex; gap: 8px;">
          <el-button type="success" :loading="quickLoading" @click="handleQuickCrawl">
            一键采集
          </el-button>
          <el-button type="primary" @click="openDialog()">新增任务</el-button>
        </div>
      </template>

      <el-alert
        title="采集说明"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
        description="「一键采集」将使用所有启用关键词立即从百度新闻抓取舆情，「执行」按钮可手动触发指定任务，采集在后台运行。"
      />

      <el-table
        :data="list"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{ textAlign: 'center', background: '#f8f9fa', fontWeight: '700', fontSize: '13px' }"
      >
        <template #empty>
          <el-empty description="暂无任务" />
        </template>
        <el-table-column label="序号" width="60" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column label="任务名称" min-width="150" align="center" show-overflow-tooltip>
          <template #default="{ row }">{{ row.task_name }}</template>
        </el-table-column>
        <el-table-column label="采集平台" width="110" align="center">
          <template #default="{ row }">{{ row.platform || '-' }}</template>
        </el-table-column>
        <el-table-column label="定时表达式" width="130" align="center">
          <template #default="{ row }">
            <el-tooltip :content="row.cron_expr" placement="top">
              <el-tag type="info" effect="plain">{{ row.cron_expr }}</el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最近执行" width="160" align="center">
          <template #default="{ row }">{{ formatTime(row.last_run_time) }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="160" align="center">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button type="success" link :loading="runningId === row.id" @click="handleRun(row)">执行</el-button>
            <el-button
              :type="row.status === 1 ? 'warning' : 'primary'"
              link
              @click="toggleStatus(row)"
            >{{ row.status === 1 ? '禁用' : '启用' }}</el-button>
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
          layout="total, prev, pager, next"
          @current-change="(val) => { page = val; loadList() }"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑任务' : '新增任务'" width="500" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="任务名称" prop="task_name">
          <el-input v-model="form.task_name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="采集平台" prop="platform">
          <el-select v-model="form.platform" style="width: 100%">
            <el-option label="百度新闻" value="百度新闻" />
            <el-option label="微博" value="微博" />
            <el-option label="知乎" value="知乎" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron 表达式" prop="cron_expr">
          <el-input v-model="form.cron_expr" placeholder="如: 0 */1 * * *（每小时）" />
          <div style="font-size: 12px; color: #999; margin-top: 4px">
            常用：每小时 <code>0 */1 * * *</code>，每天 <code>0 8 * * *</code>
          </div>
        </el-form-item>
        <el-form-item label="关键词ID" prop="keyword_ids">
          <el-input v-model="form.keyword_ids" placeholder="多个ID用英文逗号分隔，留空则用全部关键词" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listTasks, createTask, updateTask, deleteTask, runTask, quickCrawl } from '../../api/task'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const runningId = ref(null)
const quickLoading = ref(false)

const dialogVisible = ref(false)
const editId = ref(null)
const formRef = ref(null)
const submitLoading = ref(false)
const form = ref({ task_name: '', platform: '百度新闻', cron_expr: '0 */1 * * *', keyword_ids: '' })
const rules = {
  task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  cron_expr: [{ required: true, message: '请输入Cron表达式', trigger: 'blur' }],
}

function formatTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  return isNaN(d.getTime()) ? val : d.toLocaleString('zh-CN')
}

const loadList = async () => {
  loading.value = true
  try {
    const { data } = await listTasks({ page: page.value, page_size: pageSize.value })
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
  form.value = row
    ? { task_name: row.task_name, platform: row.platform || '百度新闻', cron_expr: row.cron_expr, keyword_ids: row.keyword_ids || '' }
    : { task_name: '', platform: '百度新闻', cron_expr: '0 */1 * * *', keyword_ids: '' }
  dialogVisible.value = true
}

const resetForm = () => { formRef.value?.resetFields() }

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (editId.value) {
        await updateTask(editId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createTask(form.value)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const toggleStatus = async (row) => {
  try {
    await updateTask(row.id, { status: row.status === 1 ? 0 : 1 })
    ElMessage.success(row.status === 1 ? '已禁用' : '已启用')
    loadList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

const handleRun = async (row) => {
  runningId.value = row.id
  try {
    const { data } = await runTask(row.id)
    ElMessage.success(data.message || '任务已启动')
    setTimeout(loadList, 2000)
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '执行失败')
  } finally {
    runningId.value = null
  }
}

const handleQuickCrawl = async () => {
  quickLoading.value = true
  try {
    const { data } = await quickCrawl()
    ElMessage.success(data.message || '采集已启动')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '采集失败')
  } finally {
    quickLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除任务「${row.task_name}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteTask(row.id)
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
.task-page { width: 100%; }
</style>

<template>
  <div class="sensitive-page">
    <el-card class="list-page-card">
      <template #header>
        <span class="card-title">敏感词管理</span>
        <el-button type="primary" @click="openDialog()">新增敏感词</el-button>
      </template>
      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-input v-model="filters.keyword" placeholder="关键词" clearable style="width: 160px" @keyup.enter="loadList" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.level" placeholder="风险等级" clearable style="width: 110px" @change="loadList">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.status" placeholder="状态" clearable style="width: 100px" @change="loadList">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">搜索</el-button>
        </el-form-item>
      </el-form>

      <el-table
        :data="list"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{ textAlign: 'center', background: '#f8f9fa', fontWeight: '700', fontSize: '13px' }"
      >
        <template #empty>
          <el-empty description="暂无数据" />
        </template>
        <el-table-column label="序号" width="60" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column label="敏感词" width="150" align="center">
          <template #default="{ row }">
            <el-tag type="danger" effect="plain">{{ row.word }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.level === 'high' ? 'danger' : row.level === 'medium' ? 'warning' : 'info'"
            >
              {{ row.level_label || row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="160" align="center" show-overflow-tooltip>
          <template #default="{ row }">{{ row.remark || '-' }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="160" align="center">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button
              :type="row.status === 1 ? 'warning' : 'success'"
              link
              @click="toggleStatus(row)"
            >{{ row.status === 1 ? '禁用' : '启用' }}</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="(val) => { page = val; loadList() }"
          @size-change="(val) => { pageSize = val; page = 1; loadList() }"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑敏感词' : '新增敏感词'" width="440" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="敏感词" prop="word">
          <el-input v-model="form.word" placeholder="请输入敏感词" :disabled="!!editId" />
        </el-form-item>
        <el-form-item label="风险等级" prop="level">
          <el-select v-model="form.level" style="width: 100%">
            <el-option label="高风险" value="high" />
            <el-option label="中风险" value="medium" />
            <el-option label="低风险" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" placeholder="选填" />
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
import { listSensitiveWords, createSensitiveWord, updateSensitiveWord, deleteSensitiveWord } from '../../api/sensitiveWord'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filters = ref({ keyword: '', level: '', status: null })

const dialogVisible = ref(false)
const editId = ref(null)
const formRef = ref(null)
const submitLoading = ref(false)
const form = ref({ word: '', level: 'high', remark: '' })
const rules = {
  word: [{ required: true, message: '请输入敏感词', trigger: 'blur' }],
  level: [{ required: true, message: '请选择风险等级', trigger: 'change' }],
}

function formatTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  return isNaN(d.getTime()) ? val : d.toLocaleString('zh-CN')
}

const loadList = async () => {
  loading.value = true
  try {
    const { data } = await listSensitiveWords({
      page: page.value,
      page_size: pageSize.value,
      keyword: filters.value.keyword || undefined,
      level: filters.value.level || undefined,
      status: filters.value.status != null ? filters.value.status : undefined,
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
  form.value = row
    ? { word: row.word, level: row.level, remark: row.remark || '' }
    : { word: '', level: 'high', remark: '' }
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
        await updateSensitiveWord(editId.value, { level: form.value.level, remark: form.value.remark })
        ElMessage.success('更新成功')
      } else {
        await createSensitiveWord(form.value)
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
    await updateSensitiveWord(row.id, { status: row.status === 1 ? 0 : 1 })
    ElMessage.success(row.status === 1 ? '已禁用' : '已启用')
    loadList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除敏感词「${row.word}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteSensitiveWord(row.id)
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
.sensitive-page { width: 100%; }
</style>

<template>
  <div class="setting-page">
    <el-card class="list-page-card">
      <template #header>
        <span class="card-title">系统配置</span>
        <el-button type="primary" :loading="loading" @click="loadList">刷新</el-button>
      </template>

      <el-alert
        title="配置说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
        description="修改配置后，部分功能（如预警阈值）将在下次执行分析或采集时生效。"
      />

      <el-table
        :data="list"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{ textAlign: 'center', background: '#f8f9fa', fontWeight: '700', fontSize: '13px' }"
      >
        <el-table-column label="配置名称" width="160" align="center">
          <template #default="{ row }">{{ row.setting_name || row.setting_key }}</template>
        </el-table-column>
        <el-table-column label="配置键" width="180" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.setting_key }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="配置值" min-width="200" align="center">
          <template #default="{ row }">
            <template v-if="editingKey === row.setting_key">
              <el-select
                v-if="row.setting_key === 'warning_enabled' || row.setting_key === 'sensitive_word_enabled'"
                v-model="editingValue"
                size="small"
                style="width: 120px; margin-right: 8px"
              >
                <el-option label="开启" value="1" />
                <el-option label="关闭" value="0" />
              </el-select>
              <el-input
                v-else
                v-model="editingValue"
                size="small"
                style="width: 160px; margin-right: 8px"
                placeholder="请输入"
              />
              <el-button type="primary" size="small" @click="handleSave(row)">保存</el-button>
              <el-button size="small" @click="cancelEdit">取消</el-button>
            </template>
            <span v-else>
              {{ formatValue(row) }}
              <el-button type="primary" link size="small" @click="startEdit(row)">修改</el-button>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="220" align="center" show-overflow-tooltip>
          <template #default="{ row }">{{ row.remark || '-' }}</template>
        </el-table-column>
      </el-table>

      <template #empty>
        <el-empty description="暂无配置项" />
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listSettings, updateSetting } from '../../api/setting'

const loading = ref(false)
const list = ref([])
const editingKey = ref('')
const editingValue = ref('')

const formatValue = (row) => {
  if (row.setting_key === 'warning_enabled' || row.setting_key === 'sensitive_word_enabled') {
    return row.setting_value === '1' ? '开启' : '关闭'
  }
  return row.setting_value ?? '-'
}

const loadList = async () => {
  loading.value = true
  try {
    const { data } = await listSettings()
    list.value = data.items || []
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

const startEdit = (row) => {
  editingKey.value = row.setting_key
  editingValue.value = row.setting_value ?? ''
}

const cancelEdit = () => {
  editingKey.value = ''
  editingValue.value = ''
}

const handleSave = async (row) => {
  try {
    await updateSetting(row.setting_key, editingValue.value)
    ElMessage.success('保存成功')
    editingKey.value = ''
    editingValue.value = ''
    loadList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '保存失败')
  }
}

onMounted(() => loadList())
</script>

<style scoped>
.setting-page { width: 100%; }
</style>

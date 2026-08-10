<template>
  <div class="user-page">
    <el-card class="list-page-card">
      <template #header>
        <span class="card-title">用户列表</span>
        <el-button type="primary" @click="openDialog()">新增用户</el-button>
      </template>
      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-input v-model="keyword" placeholder="用户名/姓名" clearable @clear="loadList" @keyup.enter="loadList" />
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
        <el-table-column label="用户名" width="120" align="center">
          <template #default="{ row }">
            {{ row.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="姓名" width="100" align="center">
          <template #default="{ row }">
            {{ row.real_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="角色" width="110" align="center">
          <template #default="{ row }">
            {{ row.role_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="邮箱" min-width="160" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.email || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="电话" width="130" align="center">
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">{{ row.status === 1 ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)" :disabled="row.id === currentUserId">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑用户' : '新增用户'" width="480" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="!!editId" />
        </el-form-item>
        <el-form-item v-if="!editId" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item v-if="editId" label="新密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="不修改请留空" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="form.role_id" placeholder="请选择角色" style="width: 100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.role_name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item v-if="editId" label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">正常</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listUsers, getRoles, createUser, updateUser, deleteUser } from '../../api/user'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')

const roles = ref([])
const dialogVisible = ref(false)
const editId = ref(null)
const formRef = ref(null)
const submitLoading = ref(false)

const form = ref({
  username: '',
  password: '',
  real_name: '',
  role_id: null,
  email: '',
  phone: '',
  status: 1,
})

const currentUserId = computed(() => {
  try {
    const u = localStorage.getItem('user')
    return u ? JSON.parse(u).user_id : null
  } catch {
    return null
  }
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur', when: () => !editId.value },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const loadList = async () => {
  loading.value = true
  try {
    const { data } = await listUsers({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
    })
    list.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    const { data } = await getRoles()
    roles.value = data || []
    if (roles.value.length && !form.value.role_id) {
      form.value.role_id = roles.value.find(r => r.role_code === 'user')?.id || roles.value[0].id
    }
  } catch (_) {}
}

const openDialog = (row) => {
  editId.value = row?.id || null
  if (row) {
    form.value = {
      username: row.username,
      password: '',
      real_name: row.real_name || '',
      role_id: row.role_id,
      email: row.email || '',
      phone: row.phone || '',
      status: row.status,
    }
  } else {
    form.value = {
      username: '',
      password: '',
      real_name: '',
      role_id: roles.value.find(r => r.role_code === 'user')?.id || null,
      email: '',
      phone: '',
      status: 1,
    }
  }
  dialogVisible.value = true
}

const resetForm = () => {
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      const payload = {
        real_name: form.value.real_name,
        role_id: form.value.role_id,
        email: form.value.email,
        phone: form.value.phone,
      }
      if (editId.value) {
        if (form.value.password) payload.password = form.value.password
        payload.status = form.value.status
        await updateUser(editId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createUser({
          username: form.value.username,
          password: form.value.password,
          ...payload,
          status: 1,
        })
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

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除用户「${row.username}」吗？`, '提示', {
    type: 'warning',
  }).then(async () => {
    try {
      await deleteUser(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadRoles()
  loadList()
})
</script>

<style scoped>
.user-page {
  width: 100%;
}
</style>

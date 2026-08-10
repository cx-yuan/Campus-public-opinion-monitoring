<template>
  <div class="user-profile">
    <el-card>
      <template #header>
        <span>个人中心</span>
      </template>
      <el-descriptions v-loading="loading" :column="1" border>
        <el-descriptions-item label="用户名">{{ userInfo?.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ roleLabel }}</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <div class="profile-section">
        <div class="section-title">主题订阅</div>
        <p class="section-desc">选择您关心的主题，首页和舆情列表将优先展示相关内容</p>
        <el-checkbox-group v-model="subscribedTopics" @change="saveTopics">
          <el-checkbox v-for="c in categoryOptions" :key="c" :value="c" border class="topic-checkbox">{{ c }}</el-checkbox>
        </el-checkbox-group>
      </div>

      <el-divider />

      <div class="profile-actions">
        <el-button type="primary" @click="showPasswordDialog = true">
          <el-icon><Lock /></el-icon>
          修改密码
        </el-button>
      </div>

      <el-divider />

      <div class="profile-tip">
        <el-icon><InfoFilled /></el-icon>
        <span>普通用户仅可浏览公开舆情数据。如需更多权限，请联系系统管理员。</span>
      </div>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400" @close="resetPasswordForm">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="90px">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="pwdLoading" @click="handleChangePassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { InfoFilled, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getMe, changePassword } from '../../api/auth'
import { getMyTopics, getCategoryOptions, updateMyTopics } from '../../api/topicPreference'

const userInfo = ref(null)
const categoryOptions = ref(['教学', '宿舍', '食堂', '安全', '后勤', '图书馆', '其他'])
const subscribedTopics = ref([])
const loading = ref(true)
const showPasswordDialog = ref(false)
const pwdFormRef = ref(null)
const pwdLoading = ref(false)
const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })

const validateConfirm = (rule, value, callback) => {
  if (value !== pwdForm.value.new_password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

const roleLabel = computed(() => {
  const code = userInfo.value?.role_code
  return code === 'user' ? '普通用户' : code === 'analyst' ? '舆情分析员' : code === 'admin' ? '系统管理员' : '-'
})

const resetPasswordForm = () => {
  pwdForm.value = { old_password: '', new_password: '', confirm_password: '' }
  pwdFormRef.value?.clearValidate()
}

const handleChangePassword = async () => {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    pwdLoading.value = true
    try {
      await changePassword({
        old_password: pwdForm.value.old_password,
        new_password: pwdForm.value.new_password,
      })
      ElMessage.success('密码修改成功，请重新登录')
      showPasswordDialog.value = false
      resetPasswordForm()
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '修改失败')
    } finally {
      pwdLoading.value = false
    }
  })
}

const saveTopics = async () => {
  try {
    await updateMyTopics(subscribedTopics.value)
    ElMessage.success('主题订阅已更新')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '保存失败')
  }
}

onMounted(async () => {
  try {
    const [meRes, topicsRes] = await Promise.all([
      getMe(),
      getMyTopics().catch(() => ({ data: { categories: [] } })),
    ])
    userInfo.value = meRes.data
    subscribedTopics.value = topicsRes.data?.categories || []
  } catch (_) {
    userInfo.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.user-profile { width: 100%; }
.profile-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: #f0f9ff;
  border-radius: 8px;
  color: #64748b;
  font-size: 14px;
}
.profile-section { margin-bottom: 16px; }
.section-title { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 8px; }
.section-desc { font-size: 13px; color: #64748b; margin: 0 0 12px; }
.topic-checkbox { margin-right: 12px; margin-bottom: 8px; }
.profile-actions { margin-bottom: 8px; }
.profile-tip .el-icon { color: #67b8e3; flex-shrink: 0; margin-top: 2px; }
</style>

<template>
  <div class="login-page">
    <div class="login-box">
      <h1 class="title">校园舆情监测系统</h1>
      <p class="subtitle">基于贝叶斯网络的校园舆情监测系统设计与实现</p>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            maxlength="50"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
            maxlength="50"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            style="width: 100%"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
        <el-form-item>
          <span class="tip">没有账号？</span>
          <el-button type="primary" link @click="showRegister = true">注册</el-button>
        </el-form-item>
      </el-form>

      <el-dialog v-model="showRegister" title="用户注册" width="400" @close="resetRegisterForm" @open="loadRegisterRoles">
        <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-width="70px">
          <el-form-item prop="username" label="用户名">
            <el-input v-model="registerForm.username" placeholder="请输入用户名" maxlength="50" />
          </el-form-item>
          <el-form-item prop="password" label="密码">
            <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password maxlength="50" />
          </el-form-item>
          <el-form-item prop="email" label="邮箱">
            <el-input v-model="registerForm.email" placeholder="选填" maxlength="100" />
          </el-form-item>
          <el-form-item prop="phone" label="电话">
            <el-input v-model="registerForm.phone" placeholder="选填" maxlength="20" />
          </el-form-item>
          <el-form-item prop="role_id" label="身份">
            <el-select v-model="registerForm.role_id" placeholder="请选择身份" style="width: 100%">
              <el-option v-for="r in registerRoles" :key="r.id" :label="r.role_name" :value="r.id" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showRegister = false">取消</el-button>
          <el-button type="primary" :loading="registerLoading" @click="handleRegister">注册</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../../api/request'
import { getRegisterRoles as fetchRegisterRoles } from '../../api/auth'

const router = useRouter()
const formRef = ref(null)
const registerFormRef = ref(null)
const loading = ref(false)
const registerLoading = ref(false)
const showRegister = ref(false)
const form = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', password: '', email: '', phone: '', role_id: null })
const registerRoles = ref([])
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  role_id: [{ required: true, message: '请选择身份', trigger: 'change' }],
}

const loadRegisterRoles = async () => {
  try {
    const { data } = await fetchRegisterRoles()
    registerRoles.value = data || []
    const userRole = registerRoles.value.find(r => r.role_code === 'user')
    registerForm.role_id = userRole?.id ?? registerRoles.value[0]?.id ?? null
  } catch (_) {
    registerRoles.value = []
    registerForm.role_id = null
  }
}

const resetRegisterForm = () => {
  registerForm.username = ''
  registerForm.password = ''
  registerForm.email = ''
  registerForm.phone = ''
  const userRole = registerRoles.value.find(r => r.role_code === 'user')
  registerForm.role_id = userRole?.id ?? registerRoles.value[0]?.id ?? null
  registerFormRef.value?.clearValidate()
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return
    registerLoading.value = true
    try {
      await request.post('/auth/register', {
        username: registerForm.username,
        password: registerForm.password,
        role_id: registerForm.role_id,
        email: registerForm.email || undefined,
        phone: registerForm.phone || undefined,
      })
      ElMessage.success('注册成功，请登录')
      showRegister.value = false
      form.username = registerForm.username
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '注册失败')
    } finally {
      registerLoading.value = false
    }
  })
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const { data } = await request.post('/auth/login', {
        username: form.username,
        password: form.password,
      })
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify({
        user_id: data.user_id,
        username: data.username,
        role_code: data.role_code,
      }))
      ElMessage.success('登录成功')
      const role = data.role_code
      router.push(role === 'user' ? '/user/home' : '/admin/dashboard')
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('../../assets/login-bg.svg') no-repeat center center / cover;
}
.login-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
.title {
  margin: 0 0 8px;
  font-size: 24px;
  color: #333;
  text-align: center;
}
.subtitle {
  margin: 0 0 32px;
  font-size: 14px;
  color: #666;
  text-align: center;
}
.login-form {
  margin-top: 24px;
}
.tip {
  font-size: 14px;
  color: #666;
}
.login-btn {
  background-color: #67b8e3 !important;
  border-color: #67b8e3 !important;
}
.login-btn:hover {
  background-color: #5aabd9 !important;
  border-color: #5aabd9 !important;
}
</style>

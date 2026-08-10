<template>
  <div class="home-page">
    <div class="header">
      <span class="title">校园舆情监测系统首页</span>
      <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
    </div>
    <div class="content">
      <h1>校园舆情监测系统首页</h1>
      <p>欢迎使用基于贝叶斯网络的校园舆情监测系统</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f7fa;
}
.header {
  padding: 16px 24px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}
.content {
  padding: 48px 24px;
  text-align: center;
}
.content h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 16px;
}
.content p {
  font-size: 16px;
  color: #666;
}
</style>

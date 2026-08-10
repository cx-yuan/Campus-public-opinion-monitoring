<template>
  <el-container class="main-layout">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon class="logo-icon"><Monitor /></el-icon>
        <span>管理后台</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="aside-menu"
        background-color="#f8fafc"
        text-color="#4a5568"
        active-text-color="#67b8e3"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/admin/opinion">
          <el-icon><Document /></el-icon>
          <span>舆情管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/keyword">
          <el-icon><Collection /></el-icon>
          <span>关键词管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/warning">
          <el-icon><Bell /></el-icon>
          <span>预警记录</span>
        </el-menu-item>
        <el-menu-item index="/admin/task">
          <el-icon><Cpu /></el-icon>
          <span>采集任务</span>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/admin/sensitive">
          <el-icon><Warning /></el-icon>
          <span>敏感词管理</span>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/admin/setting">
          <el-icon><Setting /></el-icon>
          <span>系统配置</span>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/admin/user">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container direction="vertical">
      <el-header class="header">
        <span class="header-title">{{ pageTitle }}</span>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleUserCommand">
            <span class="user-trigger">
              <el-icon><UserFilled /></el-icon>
              {{ userInfo?.username }}
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <el-dialog v-model="profileVisible" title="个人信息" width="400" align-center>
          <el-descriptions :column="1" border v-if="userInfo">
            <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              {{ userInfo.role_code === 'admin' ? '系统管理员' : userInfo.role_code === 'analyst' ? '舆情分析员' : '普通用户' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-dialog>
      </el-header>
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { House, User, Document, Monitor, Collection, Bell, Warning, Cpu, Setting, UserFilled, ArrowDown, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const userInfo = ref(null)
const profileVisible = ref(false)
const isAdmin = computed(() => userInfo.value?.role_code === 'admin')

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => {
  const map = {
    '/admin/dashboard': '首页',
    '/admin/opinion': '舆情管理',
    '/admin/keyword': '关键词管理',
    '/admin/warning': '预警记录',
    '/admin/task': '采集任务',
    '/admin/sensitive': '敏感词管理',
    '/admin/setting': '系统配置',
    '/admin/user': '用户管理',
  }
  return map[route.path] || '校园舆情监测系统'
})

const handleUserCommand = (cmd) => {
  if (cmd === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (cmd === 'profile') {
    profileVisible.value = true
  }
}

onMounted(() => {
  try {
    const u = localStorage.getItem('user')
    if (u) userInfo.value = JSON.parse(u)
  } catch (_) {}
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
}
.aside {
  background-color: #f8fafc;
  overflow-x: hidden;
  border-right: 1px solid #e2e8f0;
}
.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #334155;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #e2e8f0;
}
.logo-icon {
  font-size: 22px;
  color: #67b8e3;
}
.aside-menu {
  border-right: none;
}
.aside-menu :deep(.el-menu-item.is-active) {
  background-color: #e8f4fc !important;
  color: #67b8e3 !important;
  border-radius: 8px;
  margin: 4px 12px;
  width: calc(100% - 24px);
}
.aside-menu :deep(.el-menu-item) {
  margin: 4px 12px;
  border-radius: 8px;
  width: calc(100% - 24px);
}
.header {
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}
.header-title {
  font-size: 16px;
  font-weight: 500;
  color: #334155;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  color: #475569;
  cursor: pointer;
  transition: background 0.2s;
}
.user-trigger:hover {
  background: #f1f5f9;
  color: #67b8e3;
}
.user-trigger .arrow {
  font-size: 12px;
  margin-left: 2px;
}
.main {
  background: #f1f5f9;
  padding: 20px;
  overflow-y: auto;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

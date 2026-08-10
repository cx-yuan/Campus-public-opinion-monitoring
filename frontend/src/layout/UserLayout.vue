<template>
  <div class="user-layout">
    <el-header class="header">
      <div class="header-left">
        <el-icon class="logo-icon"><Monitor /></el-icon>
        <span class="site-name">校园舆情监测系统</span>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          :ellipsis="false"
          router
          class="nav-menu"
          background-color="transparent"
          text-color="#475569"
          active-text-color="#67b8e3"
        >
          <el-menu-item index="/user/home">首页</el-menu-item>
          <el-menu-item index="/user/browse">舆情浏览</el-menu-item>
          <el-menu-item index="/user/favorites">我的收藏</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <el-dropdown trigger="click" @command="handleUserCommand">
          <span class="user-trigger">
            <el-icon><User /></el-icon>
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
    </el-header>
    <el-main class="main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Monitor, User, ArrowDown, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const userInfo = ref(null)
const activeMenu = computed(() => route.path)

const handleUserCommand = (cmd) => {
  if (cmd === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (cmd === 'profile') {
    router.push('/user/profile')
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
.user-layout {
  min-height: 100vh;
  background: #f8fafc;
}
.header {
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 56px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}
.logo-icon {
  font-size: 24px;
  color: #67b8e3;
}
.site-name {
  font-size: 18px;
  font-weight: 600;
  color: #334155;
}
.nav-menu {
  border: none;
}
.nav-menu :deep(.el-menu-item) {
  border-bottom: none !important;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
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
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
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

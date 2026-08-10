import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'
import UserLayout from '../layout/UserLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue'),
    meta: { public: true },
  },
  {
    path: '/admin',
    component: MainLayout,
    meta: { role: ['admin', 'analyst'] },
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('../views/dashboard/index.vue') },
      { path: 'user', name: 'User', component: () => import('../views/user/index.vue') },
      { path: 'opinion', name: 'Opinion', component: () => import('../views/opinion/index.vue') },
      { path: 'keyword', name: 'Keyword', component: () => import('../views/keyword/index.vue') },
      { path: 'warning', name: 'Warning', component: () => import('../views/warning/index.vue') },
      { path: 'task', name: 'Task', component: () => import('../views/task/index.vue') },
      { path: 'sensitive', name: 'Sensitive', component: () => import('../views/sensitive/index.vue') },
      { path: 'setting', name: 'Setting', component: () => import('../views/setting/index.vue') },
    ],
  },
  {
    path: '/user',
    component: UserLayout,
    meta: { role: ['user'] },
    redirect: '/user/home',
    children: [
      { path: 'home', name: 'UserHome', component: () => import('../views/user-front/Home.vue') },
      { path: 'browse', name: 'UserBrowse', component: () => import('../views/user-front/Browse.vue') },
      { path: 'browse/:id', name: 'UserOpinionDetail', component: () => import('../views/user-front/Detail.vue') },
      { path: 'favorites', name: 'UserFavorites', component: () => import('../views/user-front/Favorites.vue') },
      { path: 'profile', name: 'UserProfile', component: () => import('../views/user-front/Profile.vue') },
    ],
  },
  {
    path: '/',
    redirect: () => {
      const u = localStorage.getItem('user')
      if (!u) return '/login'
      try {
        const { role_code } = JSON.parse(u)
        if (role_code === 'user') return '/user/home'
        return '/admin/dashboard'
      } catch {
        return '/login'
      }
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.public) {
    next()
    return
  }

  if (!token) {
    next('/login')
    return
  }

  let roleCode = ''
  try {
    const u = localStorage.getItem('user')
    if (u) roleCode = JSON.parse(u).role_code || ''
  } catch (_) {}

  if (roleCode === 'user') {
    if (to.path.startsWith('/admin')) {
      next('/user/home')
      return
    }
    if (to.path === '/' || to.path === '/user') {
      next('/user/home')
      return
    }
  } else if (roleCode === 'admin' || roleCode === 'analyst') {
    if (to.path.startsWith('/user/')) {
      next('/admin/dashboard')
      return
    }
    if (to.path === '/' || to.path === '/user') {
      next('/admin/dashboard')
      return
    }
  }

  next()
})

export default router

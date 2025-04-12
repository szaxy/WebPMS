import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

// 路由懒加载
const Dashboard = () => import('../views/dashboard/Index.vue')
const Login = () => import('../views/Login.vue')
const UserManagement = () => import('../views/settings/UserManagement.vue')
const ShotTest = () => import('../components/ShotTest.vue')
const ShotManagement = () => import('../views/shots/ShotManagement.vue')

// 定义路由
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/settings/users',
    name: 'user-management',
    component: UserManagement,
    meta: {
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/shot-test',
    name: 'shot-test',
    component: ShotTest,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/shots',
    name: 'shots',
    component: ShotManagement,
    meta: {
      requiresAuth: true
    }
  }
  // 更多路由会在后续添加
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果存在token但用户信息为空，尝试获取用户信息
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchCurrentUser()
    } catch (error) {
      console.error('获取用户信息失败，可能需要重新登录:', error)
    }
  }
  
  const isAuthenticated = authStore.isAuthenticated
  
  // 需要认证但未登录
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }
  
  // 需要管理员权限
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router 
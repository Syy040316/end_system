import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue')
        },
        {
          path: 'monitoring-rules',
          name: 'MonitoringRules',
          component: () => import('@/views/MonitoringRules.vue')
        },
        {
          path: 'scan-results',
          name: 'ScanResults',
          component: () => import('@/views/ScanResults.vue')
        },
        {
          path: 'jobs',
          name: 'Jobs',
          component: () => import('@/views/Jobs.vue')
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
  } else if (!to.meta.requiresAuth && authStore.isAuthenticated && to.name !== 'Login') {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router


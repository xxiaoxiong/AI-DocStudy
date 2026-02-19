import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/documents'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/modules/auth/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/modules/auth/views/Register.vue')
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'documents',
        name: 'DocumentList',
        component: () => import('@/modules/document/views/DocumentList.vue')
      },
      {
        path: 'document/:id',
        name: 'DocumentDetail',
        component: () => import('@/modules/document/views/DocumentDetail.vue')
      },
      {
        path: 'qa/:documentId',
        name: 'QAChat',
        component: () => import('@/modules/qa/views/QAChat.vue')
      },
      {
        path: 'qa-history',
        name: 'QAHistory',
        component: () => import('@/modules/qa/views/QAHistory.vue')
      },
      {
        path: 'exam',
        name: 'Exam',
        component: () => import('@/modules/exam/views/ExamList.vue')
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/modules/document/views/Statistics.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/documents')
  } else {
    next()
  }
})

export default router


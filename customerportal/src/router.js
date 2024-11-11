import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/ServiceReport/ServiceReportList.vue'),
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    name: 'ServiceReportList',
    path: '/service-report',
    component: () => import('@/pages/ServiceReport/ServiceReportList.vue'),
  }
]

let router = createRouter({
  history: createWebHistory('/customerportal'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('customer_token')
  
  if (!token && to.name !== 'Login') {
    next({ name: 'Login' })
    return
  }
  
  if (token && to.name === 'Login') {
    next({ name: 'ServiceReportList' })
    return
  }
  
  next()
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    name: 'TaskList',
    path: '/tasks/',
    component: () => import('@/pages/task/TaskList.vue'),
  },
  {
    name: 'TaskDetail',
    path: '/tasks/:id',
    component: () => import('@/pages/task/TaskDetail.vue'),
  },
  {
    name: 'ExpenseEntryList',
    path: '/expense-entry',
    component: () => import('@/pages/ExpenseEntry/ExpenseEntryList.vue'),
  },
  {
    name: 'ServiceReportList',
    path: '/service-report',
    component: () => import('@/pages/ServiceReport/ServiceReportList.vue'),
  },
  {
    name: 'ExpenseRequestList',
    path: '/expense-request',
    component: () => import('@/pages/ExpenseRequest/ExpenseRequestList.vue'),
  },
  {
    name: 'AdvanceRequestList',
    path: '/advance-request',
    component: () => import('@/pages/AdvanceRequest/AdvanceRequestList.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/intranet'),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router

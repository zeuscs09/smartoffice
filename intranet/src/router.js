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
    component: () => import('@/pages/Task/TaskList.vue'),//update git
  },
  {
    name: 'TaskDetail',
    path: '/tasks/:id',
    component: () => import('@/pages/Task/TaskDetail.vue'),
  },
  {
    name: 'ExpenseEntryList',
    path: '/expense-entry',
    component: () => import('@/pages/ExpenseEntry/ExpenseEntryList.vue'),
  },
  {
    name: 'ExpenseEntryDetail',
    path: '/expense-entry/:id',
    component: () => import('@/pages/ExpenseEntry/ExpenseEntryDetail.vue'),
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
    name: 'ExpenseRequestDetail',
    path: '/expense-request/:id',
    component: () => import('@/pages/ExpenseRequest/ExpenseRequestDetail.vue'),
  },
  {
    name: 'AdvanceRequestList',
    path: '/advance-entry',
    component: () => import('@/pages/AdvanceEntry/AdvanceEntryList.vue'),
  },
  {
    name: 'AdvanceEntryDetail',
    path: '/advance-entry/:id',
    component: () => import('@/pages/AdvanceEntry/AdvanceEntryDetail.vue'),
  },
  {
    name: 'MailBoxList',
    path: '/mailbox',
    component: () => import('@/pages/MailBox/MailBoxList.vue'),//update git 
  },
  {
    name:'WorkLoad',
    path:'/workload',
    component:()=>import('@/pages/Team/WorkLoad.vue')
  },
  {
    path: '/customer',
    redirect: '/customer/login',
    children: [
      {
        name: 'CustomerLogin',
        path: 'login',
        component: () => import('@/pages/CustomerPortal/Login.vue'),
      },
      {
        name: 'CustomerServiceList',
        path: 'services',
        component: () => import('@/pages/CustomerPortal/ServiceList.vue'),
        meta: { requiresCustomerAuth: true }
      }
    ]
  },
  {
    name: 'ServiceReportDetail',
    path: '/service-report/:id',
    component: () => import('@/pages/ServiceReport/ServiceReportDetail.vue'),
  }
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

const isCustomerAuthenticated = () => {
  const token = localStorage.getItem('customerToken')
  return !!token // returns true if token exists
}

router.beforeEach(async (to, from, next) => {
  if (to.matched.some(record => record.meta.requiresCustomerAuth)) {
    if (!isCustomerAuthenticated()) {
      next({ name: 'CustomerLogin' })
      return
    }
  }

  if (to.name === 'CustomerLogin' && isCustomerAuthenticated()) {
    next({ name: 'CustomerServiceList' })
    return
  }

  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn && !to.path.startsWith('/customer')) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router

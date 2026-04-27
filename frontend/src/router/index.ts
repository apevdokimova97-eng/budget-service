import { createRouter, createWebHistory } from '@ionic/vue-router'
import type { RouteRecordRaw } from 'vue-router'

import HomePage from '../views/HomePage.vue'
import AddTransactionPage from '../views/AddTransactionPage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import CategoriesPage from '../views/CategoriesPage.vue'
import StatisticsPage from '../views/StatisticsPage.vue'
import GoalsPage from '../views/GoalsPage.vue'
import AssistantPage from '../views/AssistantPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import RecurringPaymentsPage from '../views/RecurringPaymentsPage.vue'
import GoalDetailsPage from '../views/GoalDetailsPage.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
  },
  {
    path: '/home',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/add',
    name: 'Add',
    component: AddTransactionPage,
  },
  {
    path: '/categories',
    name: 'Categories',
    component: CategoriesPage,
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: StatisticsPage,
  },
  {
    path: '/goals/:id',
    name: 'GoalDetails',
    component: GoalDetailsPage,
  },
  {
    path: '/goals',
    name: 'Goals',
    component: GoalsPage,
  },
  {
    path: '/assistant',
    name: 'Assistant',
    component: AssistantPage,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage,
  },
  {
    path: '/recurring-payments',
    name: 'RecurringPayments',
    component: RecurringPaymentsPage,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (!token && to.path !== '/login' && to.path !== '/register') {
    next('/login')
    return
  }

  if (token && (to.path === '/login' || to.path === '/register')) {
    next('/home')
    return
  }

  next()
})

export default router
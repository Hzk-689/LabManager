import { createRouter, createWebHistory } from 'vue-router'

// 路由组件懒加载
const Login = () => import('@/views/Login.vue')
const Dashboard = () => import('@/views/Dashboard.vue')
const Devices = () => import('@/views/Devices.vue')
const Reservations = () => import('@/views/Reservations.vue')
const Layout = () => import('@/views/layout/Layout.vue')

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    name: 'MainLayout',
    component: Layout,
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'devices',
        name: 'Devices',
        component: Devices
      },
      {
        path: 'reservations',
        name: 'Reservations',
        component: Reservations
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
  const isAuthenticated = !!token

  if (to.path === '/login' && isAuthenticated) {
    next('/dashboard')
  } else if (to.path !== '/login' && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
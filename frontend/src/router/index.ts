import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/AppShell.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', component: () => import('@/pages/dashboard/DashboardPage.vue') },
        { path: 'historico', component: () => import('@/pages/historico/HistoryPage.vue') },
        { path: 'lancar', component: () => import('@/pages/lancamentos/LaunchSelectPage.vue') },
        { path: 'lancar/ganho', component: () => import('@/pages/lancamentos/IncomeLaunchPage.vue') },
        { path: 'lancar/despesa', component: () => import('@/pages/lancamentos/ExpenseHubPage.vue') },
        { path: 'abastecimento', component: () => import('@/pages/abastecimento/FuelPage.vue') },
        { path: 'manutencao', component: () => import('@/pages/manutencao/MaintenancePage.vue') },
        { path: 'monitor', component: () => import('@/pages/monitor/TacticalMonitorPage.vue') },
        { path: 'moto', component: () => import('@/pages/moto/MyBikePage.vue') },
      ],
    },
    {
      path: '/auth',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        { path: 'login', component: () => import('@/pages/auth/LoginPage.vue'), meta: { guestOnly: true } },
        { path: 'criar-conta', component: () => import('@/pages/auth/RegisterPage.vue'), meta: { guestOnly: true } },
      ],
    },
    {
      path: '/onboarding',
      component: () => import('@/layouts/AuthLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: 'placa', component: () => import('@/pages/onboarding/PlateLookupPage.vue') },
        { path: 'cadastro-manual', component: () => import('@/pages/onboarding/ManualVehiclePage.vue') },
        { path: 'km-inicial', component: () => import('@/pages/onboarding/InitialKmPage.vue') },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (!auth.initialized) {
    await auth.initialize()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: '/auth/login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { path: '/dashboard' }
  }

  return true
})

export default router

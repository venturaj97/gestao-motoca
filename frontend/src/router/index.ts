import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // === Rotas públicas ===
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { publica: true },
    },
    {
      path: '/cadastro',
      name: 'cadastro',
      component: () => import('@/views/CadastroView.vue'),
      meta: { publica: true },
    },

    // === Rotas autenticadas ===
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
    },
    {
      path: '/historico',
      name: 'historico',
      component: () => import('@/views/HistoricoView.vue'),
    },
    {
      path: '/lancar',
      name: 'lancar',
      component: () => import('@/views/LancarView.vue'),
    },
    {
      path: '/abastecer',
      name: 'abastecer',
      component: () => import('@/views/AbastecerView.vue'),
    },
    {
      path: '/manutencao',
      name: 'manutencao',
      component: () => import('@/views/ManutencaoView.vue'),
    },
    {
      path: '/moto',
      name: 'moto',
      component: () => import('@/views/MinhaMotaView.vue'),
    },
    {
      path: '/moto/cadastrar',
      name: 'cadastrar-moto',
      component: () => import('@/views/CadastrarMotoView.vue'),
    },

    // Redireciona qualquer rota desconhecida para home
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

// Guard de navegação: redireciona não-autenticados para login
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.publica && !auth.estaLogado) {
    return { name: 'login' }
  }
  // Se já está logado e tenta acessar login/cadastro, vai para home
  if (to.meta.publica && auth.estaLogado) {
    return { name: 'dashboard' }
  }
})

export default router

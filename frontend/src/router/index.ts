import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMotoStore } from '@/stores/moto'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // === Rotas públicas ===
    {
      path: '/inicio',
      name: 'inicio',
      component: () => import('@/views/InicioView.vue'),
      meta: { publica: true },
    },
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

    // === Rota de vínculo de moto (autenticada, mas pré-dashboard) ===
    {
      path: '/vincular-moto',
      name: 'vincular-moto',
      component: () => import('@/views/VincularMotoView.vue'),
      meta: { semMoto: true }, // só acessa sem moto
    },

    // === Rotas autenticadas principais ===
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
      path: '/metas',
      name: 'metas',
      component: () => import('@/views/MetasView.vue'),
    },
    {
      path: '/manutencao',
      name: 'manutencao',
      component: () => import('@/views/ManutencaoView.vue'),
    },
    {
      path: '/configuracoes',
      alias: ['/moto'],
      name: 'configuracoes',
      component: () => import('@/views/ConfiguracoesView.vue'),
    },
    {
      path: '/moto/cadastrar',
      name: 'cadastrar-moto',
      component: () => import('@/views/CadastrarMotoView.vue'),
      meta: { semMoto: true }, // pode acessar sem ter moto
    },

    // === Rotas de Erro ===
    {
      path: '/404',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { isError: true },
    },
    {
      path: '/erro',
      name: 'erro',
      component: () => import('@/views/ErrorView.vue'),
      meta: { isError: true },
    },

    // Redireciona qualquer rota desconhecida para 404
    {
      path: '/:pathMatch(.*)*',
      redirect: { name: 'not-found' },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const motoStore = useMotoStore()

  // 0. Rotas de erro: permite acesso livre para usuários logados ou visitantes
  if (to.meta.isError) return

  // 1. Rotas públicas: redireciona logados para home
  if (to.meta.publica) {
    if (auth.estaLogado) return { name: 'dashboard' }
    return // deixa passar
  }

  // 2. Não autenticado: vai para a entrada pública
  if (!auth.estaLogado) return { name: 'inicio' }

  // 3. Autenticado: carrega dados se ainda não carregou
  if (!auth.usuario) await auth.carregarUsuario()
  if (!motoStore.carregado) await motoStore.carregarMotos()

  // 4. Sem moto: bloqueia rotas que precisam de moto, redireciona para vincular
  //    Exceção: rotas marcadas com semMoto (vincular-moto, cadastrar-moto)
  //    ou rotas de auth (login, cadastro)
  const semMotoPermitida = to.meta.semMoto || to.name === 'login' || to.name === 'cadastro'
  if (!motoStore.temMoto && !semMotoPermitida) {
    return { name: 'vincular-moto' }
  }

  // 5. Com moto: bloqueia o acesso à tela de vínculo
  if (motoStore.temMoto && to.meta.semMoto) {
    return { name: 'dashboard' }
  }
})

export default router

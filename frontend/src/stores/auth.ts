import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UsuarioLogadoResposta, AssinaturaStatusResposta } from '@/types'
import { me } from '@/api/auth'
import { obterStatusAssinatura } from '@/api/assinaturas'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const usuario = ref<UsuarioLogadoResposta | null>(null)
  const statusAssinatura = ref<AssinaturaStatusResposta | null>(null)
  const carregando = ref(false)

  const estaLogado = computed(() => !!token.value)

  const ehPro = computed(() => {
    if (usuario.value?.plano === 'PRO') return true
    if (statusAssinatura.value?.em_trial) return true
    return false
  })

  function salvarToken(novoToken: string, novoRefreshToken?: string) {
    token.value = novoToken
    localStorage.setItem('access_token', novoToken)
    if (novoRefreshToken) {
      refreshToken.value = novoRefreshToken
      localStorage.setItem('refresh_token', novoRefreshToken)
    }
  }

  function logout() {
    token.value = null
    refreshToken.value = null
    usuario.value = null
    statusAssinatura.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function carregarUsuario() {
    if (!token.value) return
    try {
      carregando.value = true
      usuario.value = await me()
      await carregarStatusAssinatura()
    } catch {
      logout()
    } finally {
      carregando.value = false
    }
  }

  async function carregarStatusAssinatura() {
    if (!token.value) return
    try {
      statusAssinatura.value = await obterStatusAssinatura()
      if (usuario.value && statusAssinatura.value) {
        usuario.value.plano = statusAssinatura.value.plano
      }
    } catch {
      // Falha silenciosa
    }
  }

  return {
    token,
    refreshToken,
    usuario,
    statusAssinatura,
    carregando,
    estaLogado,
    ehPro,
    salvarToken,
    logout,
    carregarUsuario,
    carregarStatusAssinatura,
  }
})


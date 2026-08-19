import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UsuarioLogadoResposta } from '@/types'
import { me } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const usuario = ref<UsuarioLogadoResposta | null>(null)
  const carregando = ref(false)

  const estaLogado = computed(() => !!token.value)

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
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function carregarUsuario() {
    if (!token.value) return
    try {
      carregando.value = true
      usuario.value = await me()
    } catch {
      logout()
    } finally {
      carregando.value = false
    }
  }

  return {
    token,
    refreshToken,
    usuario,
    carregando,
    estaLogado,
    salvarToken,
    logout,
    carregarUsuario,
  }
})

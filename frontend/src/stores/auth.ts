import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UsuarioLogadoResposta } from '@/types'
import { me } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const usuario = ref<UsuarioLogadoResposta | null>(null)
  const carregando = ref(false)

  const estaLogado = computed(() => !!token.value)

  function salvarToken(novoToken: string) {
    token.value = novoToken
    localStorage.setItem('access_token', novoToken)
  }

  function logout() {
    token.value = null
    usuario.value = null
    localStorage.removeItem('access_token')
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
    usuario,
    carregando,
    estaLogado,
    salvarToken,
    logout,
    carregarUsuario,
  }
})

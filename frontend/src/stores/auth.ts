import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchCurrentUser, loginRequest, registerRequest } from '@/modules/auth/api'
import { setAuthToken } from '@/shared/api/http'
import { getApiErrorMessage } from '@/shared/api/errors'
import type { CurrentUser, LoginPayload, RegisterPayload } from '@/shared/types/auth'

const TOKEN_STORAGE_KEY = 'gestao-motoca.token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY))
  const user = ref<CurrentUser | null>(null)
  const initialized = ref(false)
  const loading = ref(false)
  const errorMessage = ref('')

  const isAuthenticated = computed(() => Boolean(token.value && user.value))

  const applyToken = (nextToken: string | null) => {
    token.value = nextToken
    setAuthToken(nextToken)

    if (nextToken) {
      localStorage.setItem(TOKEN_STORAGE_KEY, nextToken)
      return
    }

    localStorage.removeItem(TOKEN_STORAGE_KEY)
  }

  const clearSession = () => {
    applyToken(null)
    user.value = null
  }

  const initialize = async () => {
    if (initialized.value) return

    if (!token.value) {
      initialized.value = true
      return
    }

    setAuthToken(token.value)

    try {
      user.value = await fetchCurrentUser()
    } catch {
      clearSession()
    } finally {
      initialized.value = true
    }
  }

  const login = async (payload: LoginPayload) => {
    loading.value = true
    errorMessage.value = ''

    try {
      const response = await loginRequest(payload)
      applyToken(response.access_token)
      user.value = await fetchCurrentUser()
      return true
    } catch (error) {
      clearSession()
      errorMessage.value = getApiErrorMessage(error, 'Não foi possível entrar.')
      return false
    } finally {
      loading.value = false
    }
  }

  const register = async (payload: RegisterPayload) => {
    loading.value = true
    errorMessage.value = ''

    try {
      await registerRequest(payload)
      return await login({ email: payload.email, senha: payload.senha })
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error, 'Não foi possível criar a conta.')
      loading.value = false
      return false
    }
  }

  const logout = () => {
    clearSession()
    errorMessage.value = ''
  }

  return {
    token,
    user,
    initialized,
    loading,
    errorMessage,
    isAuthenticated,
    initialize,
    login,
    register,
    logout,
  }
})

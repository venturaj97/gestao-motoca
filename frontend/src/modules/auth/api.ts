import { http } from '@/shared/api/http'
import type { CurrentUser, LoginPayload, RegisterPayload, TokenResponse } from '@/shared/types/auth'

export const loginRequest = async (payload: LoginPayload) => {
  const { data } = await http.post<TokenResponse>('/auth/login', payload)
  return data
}

export const fetchCurrentUser = async () => {
  const { data } = await http.get<CurrentUser>('/auth/me')
  return data
}

export const registerRequest = async (payload: RegisterPayload) => {
  const { data } = await http.post<CurrentUser>('/usuarios', payload)
  return data
}

import api from './client'
import type { LoginEntrada, TokenResposta, UsuarioCriar, UsuarioResposta, UsuarioLogadoResposta } from '@/types'

export async function login(dados: LoginEntrada): Promise<TokenResposta> {
  const res = await api.post<TokenResposta>('/auth/login', dados)
  return res.data
}

export async function me(): Promise<UsuarioLogadoResposta> {
  const res = await api.get<UsuarioLogadoResposta>('/auth/me')
  return res.data
}

export async function criarUsuario(dados: UsuarioCriar): Promise<UsuarioResposta> {
  const res = await api.post<UsuarioResposta>('/usuarios', dados)
  return res.data
}

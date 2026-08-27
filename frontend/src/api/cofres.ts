import client from './client'
import type { CofreResposta, CofreCriar, CofreAtualizar, CofreAporte } from '@/types'

export async function listarCofres(): Promise<CofreResposta[]> {
  const { data } = await client.get<CofreResposta[]>('/cofres')
  return data
}

export async function criarCofre(dados: CofreCriar): Promise<CofreResposta> {
  const { data } = await client.post<CofreResposta>('/cofres', dados)
  return data
}

export async function atualizarCofre(id: number, dados: CofreAtualizar): Promise<CofreResposta> {
  const { data } = await client.put<CofreResposta>(`/cofres/${id}`, dados)
  return data
}

export async function aportarCofre(id: number, dados: CofreAporte): Promise<CofreResposta> {
  const { data } = await client.post<CofreResposta>(`/cofres/${id}/aporte`, dados)
  return data
}

export async function excluirCofre(id: number): Promise<void> {
  await client.delete(`/cofres/${id}`)
}

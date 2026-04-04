import api from './client'
import type {
  AbastecimentoCriar,
  AbastecimentoResposta,
} from '@/types'

export interface FiltrosAbastecimento {
  data_inicio?: string   // formato: YYYY-MM-DD
  data_fim?: string
  moto_usuario_id?: number
}

// POST /abastecimentos
export async function criarAbastecimento(dados: AbastecimentoCriar): Promise<AbastecimentoResposta> {
  const res = await api.post<AbastecimentoResposta>('/abastecimentos', dados)
  return res.data
}

// GET /abastecimentos
export async function listarAbastecimentos(filtros?: FiltrosAbastecimento): Promise<AbastecimentoResposta[]> {
  const res = await api.get<AbastecimentoResposta[]>('/abastecimentos', { params: filtros })
  return res.data
}

// PUT /abastecimentos/:id
export async function atualizarAbastecimento(id: number, dados: AbastecimentoCriar): Promise<AbastecimentoResposta> {
  const res = await api.put<AbastecimentoResposta>(`/abastecimentos/${id}`, dados)
  return res.data
}

// DELETE /abastecimentos/:id  → 204 sem body
export async function excluirAbastecimento(id: number): Promise<void> {
  await api.delete(`/abastecimentos/${id}`)
}

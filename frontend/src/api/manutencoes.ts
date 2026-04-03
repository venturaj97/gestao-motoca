import api from './client'
import type {
  ManutencaoCriar,
  ManutencaoResposta,
} from '@/types'

export interface FiltrosManutencao {
  data_inicio?: string   // formato: YYYY-MM-DD
  data_fim?: string
  moto_usuario_id?: number
}

// POST /manutencoes
export async function criarManutencao(dados: ManutencaoCriar): Promise<ManutencaoResposta> {
  const res = await api.post<ManutencaoResposta>('/manutencoes', dados)
  return res.data
}

// GET /manutencoes
export async function listarManutencoes(filtros?: FiltrosManutencao): Promise<ManutencaoResposta[]> {
  const res = await api.get<ManutencaoResposta[]>('/manutencoes', { params: filtros })
  return res.data
}

// PUT /manutencoes/:id
export async function atualizarManutencao(id: number, dados: ManutencaoCriar): Promise<ManutencaoResposta> {
  const res = await api.put<ManutencaoResposta>(`/manutencoes/${id}`, dados)
  return res.data
}

// DELETE /manutencoes/:id  → 204 sem body
export async function excluirManutencao(id: number): Promise<void> {
  await api.delete(`/manutencoes/${id}`)
}

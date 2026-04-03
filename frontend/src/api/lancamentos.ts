import api from './client'
import type {
  LancamentoCriar,
  LancamentoResposta,
} from '@/types'

export interface FiltrosLancamento {
  tipo?: 'GANHO' | 'DESPESA'
  data_inicio?: string   // formato: YYYY-MM-DD
  data_fim?: string
}

// POST /lancamentos
export async function criarLancamento(dados: LancamentoCriar): Promise<LancamentoResposta> {
  const res = await api.post<LancamentoResposta>('/lancamentos', dados)
  return res.data
}

// GET /lancamentos
export async function listarLancamentos(filtros?: FiltrosLancamento): Promise<LancamentoResposta[]> {
  const res = await api.get<LancamentoResposta[]>('/lancamentos', { params: filtros })
  return res.data
}

// PUT /lancamentos/:id
export async function atualizarLancamento(id: number, dados: LancamentoCriar): Promise<LancamentoResposta> {
  const res = await api.put<LancamentoResposta>(`/lancamentos/${id}`, dados)
  return res.data
}

// DELETE /lancamentos/:id  → 204 sem body
export async function excluirLancamento(id: number): Promise<void> {
  await api.delete(`/lancamentos/${id}`)
}

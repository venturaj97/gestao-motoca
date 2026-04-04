import api from './client'
import type {
  LancamentoCriar,
  LancamentoListaPaginadaResposta,
  LancamentoResposta,
} from '@/types'

export interface FiltrosLancamento {
  tipo?: 'GANHO' | 'DESPESA'
  data_inicio?: string   // formato: YYYY-MM-DD
  data_fim?: string
  pagina?: number
  limite?: number
}

export interface LancamentoLoteResposta {
  quantidade: number
  tipo: 'GANHO' | 'DESPESA'
  data_lancamento: string
  total_valor: string
  mensagem: string
  itens_resumo: Array<{
    categoria_id: number
    categoria_nome: string
    valor: string
  }>
  lancamentos: LancamentoResposta[]
}

// POST /lancamentos
export async function criarLancamento(dados: LancamentoCriar): Promise<LancamentoResposta> {
  const res = await api.post<LancamentoResposta>('/lancamentos', dados)
  return res.data
}

export async function criarLancamentosLote(itens: LancamentoCriar[]): Promise<LancamentoLoteResposta> {
  const res = await api.post<LancamentoLoteResposta>('/lancamentos/lote', { itens })
  return res.data
}

// GET /lancamentos
export async function listarLancamentos(filtros?: FiltrosLancamento): Promise<LancamentoListaPaginadaResposta> {
  const res = await api.get<LancamentoListaPaginadaResposta>('/lancamentos', { params: filtros })
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

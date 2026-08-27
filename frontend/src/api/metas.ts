import api from './client'
import type {
  MetaCriar,
  MetaAtualizar,
  MetaResposta,
  MetaAlertaResposta,
} from '@/types'

// POST /metas
export async function criarMeta(dados: MetaCriar): Promise<MetaResposta> {
  const res = await api.post<MetaResposta>('/metas', dados)
  return res.data
}

// GET /metas
export async function listarMetas(apenasAtivas?: boolean | null): Promise<MetaResposta[]> {
  const res = await api.get<MetaResposta[]>('/metas', {
    params: apenasAtivas != null ? { apenas_ativas: apenasAtivas } : undefined,
  })
  return res.data
}

// PUT /metas/:id
export async function atualizarMeta(id: number, dados: MetaAtualizar): Promise<MetaResposta> {
  const res = await api.put<MetaResposta>(`/metas/${id}`, dados)
  return res.data
}

// DELETE /metas/:id → 204 sem body
export async function excluirMeta(id: number): Promise<void> {
  await api.delete(`/metas/${id}`)
}

// GET /metas/alertas
export async function listarAlertasMetas(): Promise<MetaAlertaResposta[]> {
  const res = await api.get<MetaAlertaResposta[]>('/metas/alertas')
  return res.data
}

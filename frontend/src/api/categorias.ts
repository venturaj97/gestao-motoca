import api from './client'
import type { CategoriaAtualizar, CategoriaCriar, CategoriaResposta } from '@/types'

// GET /categorias
export async function listarCategorias(): Promise<CategoriaResposta[]> {
  const res = await api.get<CategoriaResposta[]>('/categorias')
  return res.data
}

export async function criarCategoria(dados: CategoriaCriar): Promise<CategoriaResposta> {
  const res = await api.post<CategoriaResposta>('/categorias', dados)
  return res.data
}

export async function atualizarCategoria(id: number, dados: CategoriaAtualizar): Promise<CategoriaResposta> {
  const res = await api.put<CategoriaResposta>(`/categorias/${id}`, dados)
  return res.data
}

export async function excluirCategoria(id: number): Promise<void> {
  await api.delete(`/categorias/${id}`)
}

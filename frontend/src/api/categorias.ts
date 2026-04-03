import api from './client'
import type { CategoriaResposta } from '@/types'

// GET /categorias
export async function listarCategorias(): Promise<CategoriaResposta[]> {
  const res = await api.get<CategoriaResposta[]>('/categorias')
  return res.data
}

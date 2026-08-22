import api from './client'
import type { InteligenciaResumo } from '@/types'

export async function obterInteligenciaResumo(ano?: number, mes?: number): Promise<InteligenciaResumo> {
  const res = await api.get<InteligenciaResumo>('/inteligencia/resumo', {
    params: { ano, mes },
  })
  return res.data
}

import api from './client'
import type { VisaoMesResposta } from '@/types'

export interface FiltrosVisaoMes {
  ano?: number
  mes?: number
  dataInicio?: string
  dataFim?: string
  motoUsuarioId?: number
}

export async function obterVisaoMes(
  filtros: FiltrosVisaoMes = {}
): Promise<VisaoMesResposta> {
  const { ano, mes, dataInicio, dataFim, motoUsuarioId } = filtros
  const res = await api.get<VisaoMesResposta>('/visao-mes', {
    params: {
      ano,
      mes,
      data_inicio: dataInicio,
      data_fim: dataFim,
      moto_usuario_id: motoUsuarioId,
    },
  })
  return res.data
}

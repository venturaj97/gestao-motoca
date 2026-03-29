import api from './client'
import type { VisaoMesResposta } from '@/types'

export async function obterVisaoMes(
  ano?: number,
  mes?: number,
  motoUsuarioId?: number
): Promise<VisaoMesResposta> {
  const res = await api.get<VisaoMesResposta>('/visao-mes', {
    params: { ano, mes, moto_usuario_id: motoUsuarioId },
  })
  return res.data
}

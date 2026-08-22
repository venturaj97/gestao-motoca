import api from './client'
import type {
  MotoUsuarioResposta,
  MotoUsuarioCriar,
  MotoUsuarioCriarPorPlaca,
  MotoUsuarioAtualizar,
  MotoAtualizarKmEntrada,
  MotoHistoricoKmResumo,
  ConsultaPlacaResposta,
} from '@/types'

export interface ListaMotosResposta {
  usuario_id: number
  motos: MotoUsuarioResposta[]
}

export async function listarMinhasMotos(): Promise<ListaMotosResposta> {
  const res = await api.get<ListaMotosResposta>('/motos/minha')
  return res.data
}

export async function consultarPlaca(placa: string): Promise<ConsultaPlacaResposta> {
  const res = await api.get<ConsultaPlacaResposta>(`/motos/consulta-placa/${placa}`)
  return res.data
}

export async function cadastrarMotoPorPlaca(dados: MotoUsuarioCriarPorPlaca): Promise<MotoUsuarioResposta> {
  const res = await api.post<MotoUsuarioResposta>('/motos/minha/placa', dados)
  return res.data
}

export async function cadastrarMotoManual(dados: MotoUsuarioCriar): Promise<MotoUsuarioResposta> {
  const res = await api.post<MotoUsuarioResposta>('/motos/minha', dados)
  return res.data
}

export async function atualizarMoto(id: number, dados: MotoUsuarioAtualizar): Promise<MotoUsuarioResposta> {
  const res = await api.put<MotoUsuarioResposta>(`/motos/minha/${id}`, dados)
  return res.data
}

export async function atualizarKmMinhaMoto(dados: MotoAtualizarKmEntrada): Promise<MotoUsuarioResposta> {
  const res = await api.patch<MotoUsuarioResposta>('/motos/minha/km', dados)
  return res.data
}

export async function listarMarcas(): Promise<{ marcas: string[] }> {
  const res = await api.get<{ marcas: string[] }>('/motos/marcas')
  return res.data
}

export async function listarModelos(marca: string): Promise<{ modelos: { id: number; nome: string }[] }> {
  const res = await api.get('/motos/modelos', { params: { marca } })
  return res.data
}

export async function listarAnos(modeloId: number): Promise<{ anos: { id: number; ano: number }[] }> {
  const res = await api.get('/motos/anos', { params: { modelo_id: modeloId } })
  return res.data
}

// === Histórico de KM ===

export async function obterHistoricoKm(motoUsuarioId: number): Promise<MotoHistoricoKmResumo> {
  const res = await api.get<MotoHistoricoKmResumo>('/motos/minha/historico-km', {
    params: { moto_usuario_id: motoUsuarioId },
  })
  return res.data
}

export async function registrarHistoricoKm(motoUsuarioId: number, km: number): Promise<{ id: number }> {
  const res = await api.post('/motos/minha/historico-km', { km, origem: 'MANUAL' }, {
    params: { moto_usuario_id: motoUsuarioId },
  })
  return res.data
}

export async function excluirHistoricoKm(registroId: number): Promise<void> {
  await api.delete(`/motos/minha/historico-km/${registroId}`)
}


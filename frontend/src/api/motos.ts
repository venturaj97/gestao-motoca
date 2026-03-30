import api from './client'
import type {
  MotoUsuarioResposta,
  MotoUsuarioCriar,
  MotoUsuarioCriarPorPlaca,
  MotoUsuarioAtualizar,
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

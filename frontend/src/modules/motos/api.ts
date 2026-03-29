import { http } from '@/shared/api/http'
import type {
  Moto,
  MotoManualPayload,
  MotoPlacaPayload,
  MotosResponse,
  MotoUpdatePayload,
  PlateLookupResponse,
} from '@/shared/types/motos'

export const fetchMotos = async () => {
  const { data } = await http.get<MotosResponse>('/motos/minha')
  return data
}

export const createMotoManual = async (payload: MotoManualPayload) => {
  const { data } = await http.post<Moto>('/motos/minha', payload)
  return data
}

export const createMotoByPlate = async (payload: MotoPlacaPayload) => {
  const { data } = await http.post<Moto>('/motos/minha/placa', payload)
  return data
}

export const updateMoto = async (motoId: number, payload: MotoUpdatePayload) => {
  const { data } = await http.put<Moto>(`/motos/minha/${motoId}`, payload)
  return data
}

export const deleteMoto = async (motoId: number) => {
  await http.delete(`/motos/minha/${motoId}`)
}

export const setMotoActive = async (motoId: number, ativa: boolean) => {
  const { data } = await http.patch<Moto>('/motos/minha/ativa', {
    moto_usuario_id: motoId,
    ativa,
  })
  return data
}

export const lookupPlate = async (placa: string) => {
  const { data } = await http.get<PlateLookupResponse>(`/motos/consulta-placa/${placa}`)
  return data
}

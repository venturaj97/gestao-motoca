import api from './client'
import type { AssinaturaStatusResposta, PrecosAssinaturaResposta } from '@/types'

export async function obterStatusAssinatura(): Promise<AssinaturaStatusResposta> {
  const res = await api.get<AssinaturaStatusResposta>('/assinaturas/status')
  return res.data
}

export async function obterPrecosAssinatura(): Promise<PrecosAssinaturaResposta> {
  const res = await api.get<PrecosAssinaturaResposta>('/assinaturas/precos')
  return res.data
}

export async function criarCheckoutStripe(priceId: string): Promise<{ client_secret: string; checkout_url?: string }> {
  const res = await api.post<{ client_secret: string; checkout_url?: string }>('/assinaturas/checkout', {
    price_id: priceId,
  })
  return res.data
}

export async function cancelarAssinaturaStripe(): Promise<{ mensagem: string }> {
  const res = await api.post<{ mensagem: string }>('/assinaturas/cancelar')
  return res.data
}

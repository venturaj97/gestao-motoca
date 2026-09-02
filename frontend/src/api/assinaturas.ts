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

export async function criarCheckoutInfinitePay(plano: string = 'pix_avulso'): Promise<{ checkout_url: string; order_nsu?: string }> {
  const res = await api.post<{ checkout_url: string; order_nsu?: string }>('/assinaturas/checkout/infinitepay', {
    plano,
  })
  return res.data
}

export interface PixDiretoResposta {
  qr_code_text: string
  qr_code_url: string
  order_nsu: string
  valor_formatado: string
  expires_at?: string
  checkout_url_fallback?: string
}


export async function gerarPixDireto(plano: string = 'pix_avulso'): Promise<PixDiretoResposta> {
  const res = await api.post<PixDiretoResposta>('/assinaturas/pix/gerar', {
    plano,
  })
  return res.data
}

export async function checarStatusPix(orderNsu: string): Promise<{ pago: boolean; plano: string }> {
  const res = await api.post<{ pago: boolean; plano: string }>('/assinaturas/pix/checar', {
    order_nsu: orderNsu,
  })
  return res.data
}

export async function confirmarRetornoAssinatura(params?: { order_nsu?: string; transaction_nsu?: string }): Promise<{ sucesso: boolean; plano: string }> {
  const res = await api.post<{ sucesso: boolean; plano: string }>('/assinaturas/confirmar-retorno', null, {
    params,
  })
  return res.data
}




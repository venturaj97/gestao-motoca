export type Moto = {
  id: number
  usuario_id: number
  origem: string
  origem_dados: string
  marca: string | null
  modelo: string | null
  ano: number | null
  moto_versao_id: number | null
  placa: string | null
  km_atual: number
  cor: string | null
  ativa: boolean
}

export type MotosResponse = {
  usuario_id: number
  motos: Moto[]
}

export type MotoManualPayload = {
  marca_manual?: string | null
  modelo_manual?: string | null
  ano_manual?: number | null
  km_atual: number
  cor?: string | null
}

export type MotoPlacaPayload = {
  placa: string
  km_atual: number
  cor?: string | null
}

export type MotoUpdatePayload = {
  km_atual?: number
  cor?: string | null
  ativa?: boolean
  marca_manual?: string | null
  modelo_manual?: string | null
  ano_manual?: number | null
}

export type PlateLookupResponse = {
  placa_consultada: string
  extra_disponivel: boolean
  fipe_disponivel: boolean
  fipe_melhor_correspondencia: Record<string, unknown> | null
  dados: Record<string, unknown>
}

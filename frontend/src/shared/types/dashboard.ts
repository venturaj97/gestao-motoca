export type IndicatorDay = {
  dia_semana: string
  total: string
  quantidade: number
}

export type IndicatorSummary = {
  tipo: string
  data_inicio: string | null
  data_fim: string | null
  moto_usuario_id: number | null
  total_periodo: string
  quantidade_lancamentos: number
  ticket_medio: string
  melhor_dia_semana: IndicatorDay | null
  pior_dia_semana: IndicatorDay | null
  resumo_dia_semana: IndicatorDay[]
  calendario_periodo: Array<{ data: string; total: string; quantidade: number }>
  ganhos_por_periodo: Array<{ periodo: string; total: string; quantidade: number }>
  despesas_por_categoria: Array<{ categoria_id: number; categoria_nome: string; total: string; quantidade: number }>
}

export type MetaAlert = {
  meta_id: number
  nome: string
  tipo: string
  periodo: string
  valor_meta: string
  periodo_inicio: string
  periodo_fim: string
  realizado: string
  progresso_periodo_percentual: string
  percentual_meta: string
  status: string
  recomendacao: string
}

export type MonthlyView = {
  ano: number
  mes: number
  periodo_inicio: string
  periodo_fim: string
  moto_usuario_id: number | null
  ganho: IndicatorSummary
  despesa: IndicatorSummary
  saldo_mes: string
  resumo_executivo: string[]
  metas_ativas: Array<{ id: number; nome: string; tipo: string; periodo: string; valor_meta: string; ativa: boolean }>
  alertas_mensais: MetaAlert[]
}

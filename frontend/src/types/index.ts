// === AUTH ===
export interface LoginEntrada {
  email: string
  senha: string
}

export interface UsuarioCriar {
  nome: string
  email: string
  senha: string
}

export interface TokenResposta {
  access_token: string
  token_type: string
}

export interface UsuarioLogadoResposta {
  id: number
  nome: string
  email: string
}

export interface UsuarioResposta {
  id: number
  nome: string
  email: string
}

// === MOTO ===
export interface MotoUsuarioResposta {
  id: number
  usuario_id: number
  moto_versao_id: number | null
  marca_manual: string | null
  modelo_manual: string | null
  ano_manual: number | null
  placa: string | null
  origem_dados: string
  km_atual: number
  cor: string | null
  ativa: boolean
}

export interface MotoUsuarioCriar {
  moto_versao_id?: number
  marca_manual?: string
  modelo_manual?: string
  ano_manual?: number
  km_atual: number
  cor?: string
}

export interface MotoUsuarioCriarPorPlaca {
  placa: string
  km_atual: number
  cor?: string
}

export interface MotoUsuarioAtivaAlterar {
  moto_usuario_id: number
  ativa: boolean
}

export interface MotoUsuarioAtualizar {
  km_atual?: number
  cor?: string
  ativa?: boolean
  marca_manual?: string
  modelo_manual?: string
  ano_manual?: number
}

export interface ConsultaPlacaResposta {
  placa_consultada: string
  extra_disponivel: boolean
  fipe_disponivel: boolean
  fipe_melhor_correspondencia?: Record<string, unknown>
  dados: Record<string, unknown>
}

// === CATEGORIA ===
export type TipoLancamento = 'GANHO' | 'DESPESA'
export type PeriodoLancamento = 'DIARIO' | 'SEMANAL' | 'CORRIDA'
export type PeriodoMeta = 'SEMANAL' | 'MENSAL'
export type StatusMeta = 'EM_DIA' | 'ATENCAO' | 'CRITICO'

export interface CategoriaResposta {
  id: number
  nome: string
  tipo: TipoLancamento
  ativa: boolean
}

// === LANÇAMENTO ===
export interface LancamentoCriar {
  categoria_id: number
  tipo: TipoLancamento
  valor: number
  descricao?: string
  periodo?: PeriodoLancamento
  minutos_corrida?: number
  km_corrida?: number
  data_lancamento?: string
  moto_usuario_id?: number
}

export interface LancamentoResposta {
  id: number
  usuario_id: number
  categoria_id: number
  moto_usuario_id: number | null
  tipo: TipoLancamento
  valor: string
  dia_semana: string | null
  periodo: PeriodoLancamento | null
  minutos_corrida: number | null
  km_corrida: string | null
  data_lancamento: string
  data_criacao: string
}

// === ABASTECIMENTO ===
export interface AbastecimentoCriar {
  categoria_id: number
  valor_total: number
  litros: number
  km_atual?: number
  data_abastecimento?: string
  descricao?: string
  posto?: string
  tipo_combustivel?: string
  moto_usuario_id?: number
}

export interface AbastecimentoResposta {
  id: number
  usuario_id: number
  moto_usuario_id: number | null
  lancamento_id: number
  litros: string
  valor_total: string
  valor_litro: string
  km_atual: number | null
  data_abastecimento: string
  data_criacao: string
  posto: string | null
  tipo_combustivel: string | null
}

// === MANUTENÇÃO ===
export interface ManutencaoCriar {
  categoria_id: number
  valor_total: number
  km_atual?: number
  data_manutencao?: string
  descricao?: string
  descricao_servico?: string
  oficina?: string
  tipo_servico?: string
  moto_usuario_id?: number
}

export interface ManutencaoResposta {
  id: number
  usuario_id: number
  moto_usuario_id: number | null
  lancamento_id: number
  valor_total: string
  km_atual: number | null
  data_manutencao: string
  data_criacao: string
  descricao_servico: string | null
  oficina: string | null
  tipo_servico: string | null
}

// === INDICADORES ===
export interface IndicadorDiaSemanaItem {
  dia_semana: string
  total: string
  quantidade: number
}

export interface IndicadorCalendarioItem {
  data: string
  total: string
  quantidade: number
}

export interface IndicadorPeriodoGanhoItem {
  periodo: string
  total: string
  quantidade: number
}

export interface IndicadorCategoriaItem {
  categoria_id: number
  categoria_nome: string
  total: string
  quantidade: number
}

export interface IndicadorResumoResposta {
  tipo: TipoLancamento
  data_inicio: string | null
  data_fim: string | null
  moto_usuario_id: number | null
  total_periodo: string
  quantidade_lancamentos: number
  ticket_medio: string
  melhor_dia_semana: IndicadorDiaSemanaItem | null
  pior_dia_semana: IndicadorDiaSemanaItem | null
  resumo_dia_semana: IndicadorDiaSemanaItem[]
  calendario_periodo: IndicadorCalendarioItem[]
  ganhos_por_periodo: IndicadorPeriodoGanhoItem[]
  despesas_por_categoria: IndicadorCategoriaItem[]
}

// === META ===
export interface MetaCriar {
  nome: string
  tipo: TipoLancamento
  periodo: PeriodoMeta
  valor_meta: number
  ativa: boolean
}

export interface MetaAtualizar {
  nome?: string
  tipo?: TipoLancamento
  periodo?: PeriodoMeta
  valor_meta?: number
  ativa?: boolean
}

export interface MetaResposta {
  id: number
  usuario_id: number
  nome: string
  tipo: TipoLancamento
  periodo: PeriodoMeta
  valor_meta: string
  ativa: boolean
  data_criacao: string
}

export interface MetaAlertaResposta {
  meta_id: number
  nome: string
  tipo: TipoLancamento
  periodo: PeriodoMeta
  valor_meta: string
  periodo_inicio: string
  periodo_fim: string
  realizado: string
  progresso_periodo_percentual: string
  percentual_meta: string
  status: StatusMeta
  recomendacao: string
}

// === VISÃO DO MÊS (DASHBOARD) ===
export interface VisaoMesResposta {
  ano: number
  mes: number
  periodo_inicio: string
  periodo_fim: string
  moto_usuario_id: number | null
  ganho: IndicadorResumoResposta
  despesa: IndicadorResumoResposta
  saldo_mes: string
  resumo_executivo: string[]
  metas_ativas: MetaResposta[]
  alertas_mensais: MetaAlertaResposta[]
}

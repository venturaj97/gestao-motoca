<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { listarAlertasMetas, listarMetas, criarMeta, atualizarMeta, excluirMeta } from '@/api/metas'
import { listarCofres, criarCofre, atualizarCofre, aportarCofre, excluirCofre } from '@/api/cofres'
import type { MetaAlertaResposta, MetaResposta, MetaCriar, MetaAtualizar, CofreResposta, CofreCriar, CofreAtualizar } from '@/types'

// ── Estado ───────────────────────────────────────────────────
const alertas      = ref<MetaAlertaResposta[]>([])
const metas        = ref<MetaResposta[]>([])
const cofres       = ref<CofreResposta[]>([])
const carregando   = ref(true)
const erroCarregar = ref('')

// ── Modal: META ──────────────────────────────────────────────
const modalMetaVisivel    = ref(false)
const modalMetaModoEdicao = ref(false)
const modalMetaId         = ref<number | null>(null)
const modalMetaNome       = ref('')
const modalMetaTipo       = ref<'GANHO' | 'DESPESA'>('GANHO')
const modalMetaPeriodo    = ref<'DIARIO' | 'SEMANAL' | 'MENSAL'>('SEMANAL')
const modalMetaValor      = ref('')
const modalMetaDias       = ref(6)
const modalMetaEnviando   = ref(false)
const modalMetaErro       = ref('')

// ── Modal: COFRE ─────────────────────────────────────────────
const modalCofreVisivel     = ref(false)
const modalCofreModoEdicao  = ref(false)
const modalCofreId          = ref<number | null>(null)
const modalCofreNome        = ref('')
const modalCofreCategoria   = ref<string>('PNEU')
const modalCofreMetaValor   = ref('')
const modalCofreSaldoAtual  = ref('')
const modalCofreAutoguarda  = ref('')
const modalCofreEnviando    = ref(false)
const modalCofreErro        = ref('')

// ── Modal: APORTE NO COFRE ───────────────────────────────────
const modalAporteVisivel  = ref(false)
const aporteCofreId       = ref<number | null>(null)
const aporteCofreNome     = ref('')
const aporteTipoOperacao  = ref<'DEPOSITO' | 'SAQUE'>('DEPOSITO')
const aporteValor         = ref('')
const aporteEnviando      = ref(false)
const aporteErro          = ref('')

// ── Modal: Exclusão ──────────────────────────────────────────
const confirmarExcluir     = ref(false)
const confirmarExcluirTipo = ref<'META' | 'COFRE'>('META')
const confirmarExcluirId   = ref<number | null>(null)
const confirmarExcluirNome = ref('')
const excluindo            = ref(false)

// ── Categorias de cofre ──────────────────────────────────────
const categoriasCofre: { valor: string; label: string; icone: string }[] = [
  { valor: 'PNEU',    label: 'Pneu & Relação', icone: 'tire_repair' },
  { valor: 'SEGURO',  label: 'Seguro',         icone: 'shield' },
  { valor: 'IPVA',    label: 'IPVA',            icone: 'receipt_long' },
  { valor: 'REVISAO', label: 'Revisão',         icone: 'build' },
  { valor: 'RESERVA', label: 'Reserva',         icone: 'savings' },
  { valor: 'OUTROS',  label: 'Outros',          icone: 'more_horiz' },
]

// ── Dados derivados ──────────────────────────────────────────
const alertasGanho = computed(() => alertas.value.filter(a => a.tipo === 'GANHO'))
const alertasDespesa = computed(() => alertas.value.filter(a => a.tipo === 'DESPESA'))

// ── Helpers ──────────────────────────────────────────────────
function formatarReais(valor: string | number): string {
  const n = typeof valor === 'string' ? parseFloat(valor) : valor
  if (isNaN(n)) return 'R$ 0,00'
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function periodoLabel(periodo: string): string {
  const map: Record<string, string> = {
    DIARIO: 'DIÁRIO',
    SEMANAL: 'SEMANAL',
    MENSAL: 'MENSAL',
  }
  return map[periodo] ?? periodo
}

function statusConfig(status: string): { cor: string; badge: string; icone: string } {
  const map: Record<string, { cor: string; badge: string; icone: string }> = {
    atingida:     { cor: 'status-atingida',     badge: 'Meta Atingida',   icone: 'check_circle' },
    em_andamento: { cor: 'status-em-andamento', badge: 'Em Andamento',    icone: 'schedule' },
    estourada:    { cor: 'status-estourada',     badge: 'Teto Excedido',  icone: 'error' },
    atencao:      { cor: 'status-atencao',       badge: 'Atenção',        icone: 'warning' },
    dentro_meta:  { cor: 'status-dentro-meta',   badge: 'Sob Controle',   icone: 'verified' },
  }
  return map[status] ?? { cor: 'status-em-andamento', badge: status, icone: 'info' }
}

function iconeCofre(categoria: string): string {
  const item = categoriasCofre.find(c => c.valor === categoria)
  return item?.icone ?? 'savings'
}

function labelCofre(categoria: string): string {
  const item = categoriasCofre.find(c => c.valor === categoria)
  return item?.label ?? 'Cofre'
}

function formatarInputMoeda(val: string): string {
  val = val.replace(/[^0-9.,]/g, '')
  let separadorEncontrado = false
  let resultado = ''
  for (let i = 0; i < val.length; i++) {
    const char = val[i]
    if (char === ',' || char === '.') {
      if (!separadorEncontrado) {
        resultado += ','
        separadorEncontrado = true
      }
    } else {
      resultado += char
    }
  }
  if (separadorEncontrado) {
    const partes = resultado.split(',')
    if (partes[1] && partes[1].length > 2) {
      resultado = partes[0] + ',' + partes[1].slice(0, 2)
    }
  }
  return resultado
}

// ── Carregar dados ───────────────────────────────────────────
async function carregar() {
  carregando.value = true
  erroCarregar.value = ''
  try {
    const [alertasRes, metasRes, cofresRes] = await Promise.all([
      listarAlertasMetas(),
      listarMetas(),
      listarCofres(),
    ])
    alertas.value = alertasRes
    metas.value = metasRes.filter(m => m.periodo !== 'OBJETIVO')
    cofres.value = cofresRes
  } catch {
    erroCarregar.value = 'Erro ao carregar planejamento.'
  } finally {
    carregando.value = false
  }
}

// ── Handlers: META ───────────────────────────────────────────
function abrirCriarMeta() {
  modalMetaModoEdicao.value = false
  modalMetaId.value = null
  modalMetaNome.value = ''
  modalMetaTipo.value = 'GANHO'
  modalMetaPeriodo.value = 'SEMANAL'
  modalMetaValor.value = ''
  modalMetaDias.value = 6
  modalMetaErro.value = ''
  modalMetaVisivel.value = true
}

function abrirEditarMeta(meta: MetaResposta) {
  modalMetaModoEdicao.value = true
  modalMetaId.value = meta.id
  modalMetaNome.value = meta.nome
  modalMetaTipo.value = meta.tipo as 'GANHO' | 'DESPESA'
  modalMetaPeriodo.value = meta.periodo as 'DIARIO' | 'SEMANAL' | 'MENSAL'
  modalMetaValor.value = meta.valor_meta ? parseFloat(meta.valor_meta).toString().replace('.', ',') : ''
  modalMetaDias.value = meta.dias_trabalho_semana ?? 6
  modalMetaErro.value = ''
  modalMetaVisivel.value = true
}

async function salvarMeta() {
  modalMetaErro.value = ''
  const valor = parseFloat(modalMetaValor.value.replace(',', '.'))
  if (!modalMetaNome.value.trim()) { modalMetaErro.value = 'Informe o nome da meta.'; return }
  if (isNaN(valor) || valor <= 0) { modalMetaErro.value = 'Informe um valor válido.'; return }

  modalMetaEnviando.value = true
  try {
    if (modalMetaModoEdicao.value && modalMetaId.value) {
      const dados: MetaAtualizar = {
        nome: modalMetaNome.value.trim(),
        tipo: modalMetaTipo.value,
        periodo: modalMetaPeriodo.value,
        valor_meta: valor,
        dias_trabalho_semana: modalMetaDias.value,
      }
      await atualizarMeta(modalMetaId.value, dados)
    } else {
      const dados: MetaCriar = {
        nome: modalMetaNome.value.trim(),
        tipo: modalMetaTipo.value,
        periodo: modalMetaPeriodo.value,
        valor_meta: valor,
        dias_trabalho_semana: modalMetaDias.value,
        ativa: true,
      }
      await criarMeta(dados)
    }
    modalMetaVisivel.value = false
    await carregar()
  } catch {
    modalMetaErro.value = 'Erro ao salvar meta. Tente novamente.'
  } finally {
    modalMetaEnviando.value = false
  }
}

// ── Handlers: COFRE ──────────────────────────────────────────
function abrirCriarCofre() {
  modalCofreModoEdicao.value = false
  modalCofreId.value = null
  modalCofreNome.value = ''
  modalCofreCategoria.value = 'PNEU'
  modalCofreMetaValor.value = ''
  modalCofreSaldoAtual.value = '0,00'
  modalCofreAutoguarda.value = '0'
  modalCofreErro.value = ''
  modalCofreVisivel.value = true
}

function abrirEditarCofre(cofre: CofreResposta) {
  modalCofreModoEdicao.value = true
  modalCofreId.value = cofre.id
  modalCofreNome.value = cofre.nome
  modalCofreCategoria.value = cofre.categoria
  modalCofreMetaValor.value = parseFloat(cofre.valor_meta).toString().replace('.', ',')
  modalCofreSaldoAtual.value = parseFloat(cofre.saldo_atual).toString().replace('.', ',')
  modalCofreAutoguarda.value = parseFloat(cofre.porcentagem_autoguarda).toString()
  modalCofreErro.value = ''
  modalCofreVisivel.value = true
}

async function salvarCofre() {
  modalCofreErro.value = ''
  const metaVal = parseFloat(modalCofreMetaValor.value.replace(',', '.'))
  const saldoVal = parseFloat(modalCofreSaldoAtual.value.replace(',', '.')) || 0
  const autoVal = parseFloat(modalCofreAutoguarda.value.replace(',', '.')) || 0

  if (!modalCofreNome.value.trim()) { modalCofreErro.value = 'Informe o nome do cofre.'; return }
  if (isNaN(metaVal) || metaVal <= 0) { modalCofreErro.value = 'Informe um valor de meta válido.'; return }
  if (autoVal < 0 || autoVal > 100) { modalCofreErro.value = 'Porcentagem de autoguarda deve ser entre 0 e 100%.'; return }

  modalCofreEnviando.value = true
  try {
    if (modalCofreModoEdicao.value && modalCofreId.value) {
      const dados: CofreAtualizar = {
        nome: modalCofreNome.value.trim(),
        categoria: modalCofreCategoria.value,
        valor_meta: metaVal,
        saldo_atual: saldoVal,
        porcentagem_autoguarda: autoVal,
      }
      await atualizarCofre(modalCofreId.value, dados)
    } else {
      const dados: CofreCriar = {
        nome: modalCofreNome.value.trim(),
        categoria: modalCofreCategoria.value,
        valor_meta: metaVal,
        saldo_atual: saldoVal,
        porcentagem_autoguarda: autoVal,
        ativa: true,
      }
      await criarCofre(dados)
    }
    modalCofreVisivel.value = false
    await carregar()
  } catch {
    modalCofreErro.value = 'Erro ao salvar cofre. Tente novamente.'
  } finally {
    modalCofreEnviando.value = false
  }
}

// ── Handlers: APORTE NO COFRE ────────────────────────────────
function abrirAporteCofre(cofre: CofreResposta) {
  aporteCofreId.value = cofre.id
  aporteCofreNome.value = cofre.nome
  aporteTipoOperacao.value = 'DEPOSITO'
  aporteValor.value = ''
  aporteErro.value = ''
  modalAporteVisivel.value = true
}

async function confirmarAporte() {
  aporteErro.value = ''
  const val = parseFloat(aporteValor.value.replace(',', '.'))
  if (isNaN(val) || val <= 0) { aporteErro.value = 'Informe um valor válido.'; return }
  if (!aporteCofreId.value) return

  aporteEnviando.value = true
  try {
    await aportarCofre(aporteCofreId.value, {
      valor: val,
      tipo_operacao: aporteTipoOperacao.value,
    })
    modalAporteVisivel.value = false
    await carregar()
  } catch (err: unknown) {
    const errorObj = err as { response?: { data?: { detail?: string } } }
    if (errorObj.response?.data?.detail === 'saldo_insuficiente') {
      aporteErro.value = 'Saldo insuficiente no cofre para este saque.'
    } else {
      aporteErro.value = 'Erro ao realizar operação no cofre.'
    }
  } finally {
    aporteEnviando.value = false
  }
}

// ── Exclusão ─────────────────────────────────────────────────
function pedirExclusaoMeta(meta: MetaResposta) {
  confirmarExcluirTipo.value = 'META'
  confirmarExcluirId.value = meta.id
  confirmarExcluirNome.value = meta.nome
  confirmarExcluir.value = true
}

function pedirExclusaoCofre(cofre: CofreResposta) {
  confirmarExcluirTipo.value = 'COFRE'
  confirmarExcluirId.value = cofre.id
  confirmarExcluirNome.value = cofre.nome
  confirmarExcluir.value = true
}

async function confirmarExclusao() {
  if (!confirmarExcluirId.value) return
  excluindo.value = true
  try {
    if (confirmarExcluirTipo.value === 'META') {
      await excluirMeta(confirmarExcluirId.value)
    } else {
      await excluirCofre(confirmarExcluirId.value)
    }
    confirmarExcluir.value = false
    await carregar()
  } catch {
    // silently fail
  } finally {
    excluindo.value = false
  }
}

// ── Toggle ativa ─────────────────────────────────────────────
async function toggleAtivaMeta(meta: MetaResposta) {
  try {
    await atualizarMeta(meta.id, { ativa: !meta.ativa })
    await carregar()
  } catch {
    // silently fail
  }
}

onMounted(carregar)
</script>

<template>
  <AppLayout>
    <div class="bg-background text-on-surface font-body min-h-screen">
      <main class="px-5 py-5 lg:px-8 lg:py-6 space-y-5 max-w-4xl mx-auto pb-28 lg:pb-8">

      <!-- ══ Cabeçalho ══════════════════════════════════════════ -->
      <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">PLANEJAMENTO</p>
          <h2 class="font-headline font-extrabold text-4xl tracking-tighter uppercase leading-none">METAS & COFRES</h2>
          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mt-1">Controle de ritmo e reservas da moto</p>
        </div>
        <div class="grid grid-cols-2 gap-2 w-full sm:w-auto sm:flex">
          <button
            class="h-11 px-3 sm:px-5 bg-surface-container-high border border-outline font-label text-[10px] font-bold tracking-widest uppercase flex items-center justify-center gap-1.5 hover:bg-surface-bright transition-all text-on-surface w-full sm:w-auto"
            @click="abrirCriarCofre"
          >
            <span class="material-symbols-outlined text-sm">savings</span>
            NOVO COFRE
          </button>
          <button
            class="h-11 px-3 sm:px-5 bg-primary-container text-on-primary-fixed font-label text-[10px] font-bold tracking-widest uppercase flex items-center justify-center gap-1.5 hover:brightness-110 transition-all w-full sm:w-auto"
            @click="abrirCriarMeta"
          >
            <span class="material-symbols-outlined text-sm">add</span>
            NOVA META
          </button>
        </div>
      </div>

      <!-- Erro -->
      <div v-if="erroCarregar" class="error-banner">
        <span class="material-symbols-outlined text-sm">warning</span>
        {{ erroCarregar }}
      </div>

      <!-- Skeleton -->
      <template v-if="carregando && alertas.length === 0 && cofres.length === 0">
        <div class="space-y-4 animate-pulse px-5 lg:px-8 mt-4">
          <div class="h-28 bg-surface-container-low" />
          <div class="h-28 bg-surface-container-low" />
          <div class="grid grid-cols-2 gap-3">
            <div class="h-24 bg-surface-container-low" />
            <div class="h-24 bg-surface-container-low" />
          </div>
        </div>
      </template>

      <!-- ══ Conteúdo principal ═══════════════════════════════ -->
      <template v-else>
        <div class="space-y-6">

          <section v-if="alertasGanho.length > 0" class="flex flex-col gap-3">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined w-8 h-8 flex items-center justify-center text-lg bg-primary-container/15 text-primary-container">trending_up</span>
              <h3 class="font-headline font-black text-[11px] tracking-[0.15em] uppercase text-on-surface">METAS DE GANHO</h3>
              <div class="tooltip-trigger ml-auto lg:ml-0">
                <span class="material-symbols-outlined text-on-surface-variant text-base">info</span>
                <div class="tooltip-box">Meta de faturamento mínimo esperado para o período.</div>
              </div>
            </div>

            <div class="metas-cards-grid">
              <div v-for="alerta in alertasGanho" :key="alerta.meta_id" class="meta-card">
                <!-- Header do card -->
                <div class="meta-card__header">
                  <div class="meta-card__info">
                    <span class="meta-card__periodo">{{ periodoLabel(alerta.periodo) }}</span>
                    <h4 class="meta-card__nome">{{ alerta.nome }}</h4>
                  </div>
                  <div class="meta-card__actions">
                    <button
                      class="meta-card__btn"
                      title="Editar"
                      @click="abrirEditarMeta(metas.find(m => m.id === alerta.meta_id)!)"
                    >
                      <span class="material-symbols-outlined text-sm">edit</span>
                    </button>
                    <button
                      class="meta-card__btn meta-card__btn--danger"
                      title="Excluir"
                      @click="pedirExclusaoMeta(metas.find(m => m.id === alerta.meta_id)!)"
                    >
                      <span class="material-symbols-outlined text-sm">delete</span>
                    </button>
                  </div>
                </div>

                <!-- Valores -->
                <div class="meta-card__valores">
                  <div>
                    <span class="meta-card__label">REALIZADO</span>
                    <span class="meta-card__valor meta-card__valor--ganho">{{ formatarReais(alerta.realizado) }}</span>
                  </div>
                  <div class="text-right">
                    <span class="meta-card__label">META</span>
                    <span class="meta-card__valor">{{ formatarReais(alerta.valor_meta) }}</span>
                  </div>
                </div>

                <!-- Barra de progresso -->
                <div class="progress-bar">
                  <div
                    class="progress-bar__fill progress-bar__fill--ganho"
                    :style="{ width: Math.min(parseFloat(alerta.percentual_meta), 100) + '%' }"
                  />
                </div>
                <div class="meta-card__progress-info">
                  <span>{{ parseFloat(alerta.percentual_meta).toFixed(0) }}%</span>
                  <span>{{ formatarReais(alerta.valor_restante) }} restante</span>
                </div>

                <!-- Status badge + recomendação -->
                <div class="meta-card__status" :class="statusConfig(alerta.status).cor">
                  <span class="material-symbols-outlined text-sm">{{ statusConfig(alerta.status).icone }}</span>
                  <span class="meta-card__status-text">{{ alerta.recomendacao }}</span>
                </div>

                <!-- Meta diária necessária -->
                <div v-if="alerta.dias_trabalho_restantes > 0 && parseFloat(alerta.valor_restante) > 0" class="meta-card__ritmo tooltip-trigger">
                  <span class="material-symbols-outlined text-xs">pace</span>
                  <span>{{ formatarReais(alerta.meta_diaria_necessaria) }}/dia · {{ alerta.dias_trabalho_restantes }} dias restantes</span>
                  <div class="tooltip-box">Valor diário necessário nos dias de trabalho restantes para bater a meta.</div>
                </div>
              </div>
            </div>
          </section>

          <section v-if="alertasDespesa.length > 0" class="flex flex-col gap-3">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined w-8 h-8 flex items-center justify-center text-lg bg-secondary/15 text-secondary">money_off</span>
              <h3 class="font-headline font-black text-[11px] tracking-[0.15em] uppercase text-on-surface">TETO DE DESPESAS</h3>
              <div class="tooltip-trigger ml-auto lg:ml-0">
                <span class="material-symbols-outlined text-on-surface-variant text-base">info</span>
                <div class="tooltip-box">Limite máximo de gastos para manter os custos sob controle.</div>
              </div>
            </div>

            <div class="metas-cards-grid">
              <div v-for="alerta in alertasDespesa" :key="alerta.meta_id" class="meta-card">
                <div class="meta-card__header">
                  <div class="meta-card__info">
                    <span class="meta-card__periodo">{{ periodoLabel(alerta.periodo) }}</span>
                    <h4 class="meta-card__nome">{{ alerta.nome }}</h4>
                  </div>
                  <div class="meta-card__actions">
                    <button
                      class="meta-card__btn"
                      title="Editar"
                      @click="abrirEditarMeta(metas.find(m => m.id === alerta.meta_id)!)"
                    >
                      <span class="material-symbols-outlined text-sm">edit</span>
                    </button>
                    <button
                      class="meta-card__btn meta-card__btn--danger"
                      title="Excluir"
                      @click="pedirExclusaoMeta(metas.find(m => m.id === alerta.meta_id)!)"
                    >
                      <span class="material-symbols-outlined text-sm">delete</span>
                    </button>
                  </div>
                </div>

                <!-- Indicador de consumo -->
                <div class="meta-card__valores">
                  <div>
                    <span class="meta-card__label">GASTO</span>
                    <span class="meta-card__valor meta-card__valor--despesa">{{ formatarReais(alerta.realizado) }}</span>
                  </div>
                  <div class="text-right">
                    <span class="meta-card__label">LIMITE</span>
                    <span class="meta-card__valor">{{ formatarReais(alerta.valor_meta) }}</span>
                  </div>
                </div>

                <div class="progress-bar">
                  <div
                    class="progress-bar__fill progress-bar__fill--despesa"
                    :style="{ width: Math.min(parseFloat(alerta.percentual_meta), 100) + '%' }"
                  />
                </div>
                <div class="meta-card__progress-info">
                  <span>{{ parseFloat(alerta.percentual_meta).toFixed(0) }}% consumido</span>
                  <span>{{ formatarReais(alerta.valor_restante) }} disponível</span>
                </div>

                <div class="meta-card__status" :class="statusConfig(alerta.status).cor">
                  <span class="material-symbols-outlined text-sm">{{ statusConfig(alerta.status).icone }}</span>
                  <span class="meta-card__status-text">{{ alerta.recomendacao }}</span>
                </div>
              </div>
            </div>
          </section>

          <section class="flex flex-col gap-3">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined w-8 h-8 flex items-center justify-center text-lg bg-tertiary/15 text-tertiary">savings</span>
              <h3 class="font-headline font-black text-[11px] tracking-[0.15em] uppercase text-on-surface">COFRES TÁTICOS (RESERVAS)</h3>
              <div class="tooltip-trigger ml-auto lg:ml-0">
                <span class="material-symbols-outlined text-on-surface-variant text-base">info</span>
                <div class="tooltip-box">Reservas financeiras acumulativas para despesas futuras da moto.</div>
              </div>
            </div>

            <!-- Grid de cofres -->
            <div v-if="cofres.length > 0" class="cofres-grid">
              <div v-for="cofre in cofres" :key="cofre.id" class="cofre-card">
                <div class="cofre-card__header">
                  <div class="cofre-card__icon">
                    <span class="material-symbols-outlined">{{ iconeCofre(cofre.categoria) }}</span>
                  </div>
                  <div class="cofre-card__info">
                    <span class="cofre-card__categoria">{{ labelCofre(cofre.categoria) }}</span>
                    <h4 class="cofre-card__nome">{{ cofre.nome }}</h4>
                  </div>
                  <div class="meta-card__actions">
                    <button
                      class="meta-card__btn"
                      title="Editar"
                      @click="abrirEditarCofre(cofre)"
                    >
                      <span class="material-symbols-outlined text-sm">edit</span>
                    </button>
                    <button
                      class="meta-card__btn meta-card__btn--danger"
                      title="Excluir"
                      @click="pedirExclusaoCofre(cofre)"
                    >
                      <span class="material-symbols-outlined text-sm">delete</span>
                    </button>
                  </div>
                </div>

                <!-- Autoguarda Badge -->
                <div v-if="parseFloat(cofre.porcentagem_autoguarda) > 0" class="cofre-badge-autoguarda">
                  <span class="material-symbols-outlined text-xs">bolt</span>
                  <span>Guarda {{ cofre.porcentagem_autoguarda }}% de cada ganho</span>
                </div>

                <!-- Valores acumulados -->
                <div class="cofre-card__valores">
                  <div>
                    <span class="cofre-card__label">GUARDADO</span>
                    <span class="cofre-card__realizado">{{ formatarReais(cofre.saldo_atual) }}</span>
                  </div>
                  <div class="text-right">
                    <span class="cofre-card__label">META</span>
                    <span class="cofre-card__meta">{{ formatarReais(cofre.valor_meta) }}</span>
                  </div>
                </div>

                <!-- Barra de progresso do cofre -->
                <div class="progress-bar progress-bar--cofre">
                  <div
                    class="progress-bar__fill progress-bar__fill--cofre"
                    :style="{ width: Math.min(cofre.percentual_meta, 100) + '%' }"
                  />
                </div>
                <div class="cofre-card__progress-info">
                  <span>{{ cofre.percentual_meta.toFixed(0) }}% alcançado</span>
                  <span>Faltam {{ formatarReais(cofre.valor_restante) }}</span>
                </div>

                <!-- Botão de Aporte Rápido -->
                <button class="btn-aporte-cofre mt-1" @click="abrirAporteCofre(cofre)">
                  <span class="material-symbols-outlined text-sm">account_balance_wallet</span>
                  GUARDAR / SACAR
                </button>
              </div>
            </div>

            <!-- Estado Vazio de Cofres -->
            <div v-else class="empty-state-cofre">
              <p class="empty-state__desc">Nenhum cofre criado. Crie cofres para guardar reservas de pneu, seguro e revisão.</p>
              <button class="btn-novo-cofre mx-auto mt-2" @click="abrirCriarCofre">
                <span class="material-symbols-outlined text-sm">savings</span>
                CRIAR PRIMEIRO COFRE
              </button>
            </div>
          </section>

          <!-- Estado vazio geral se nada existir -->
          <div v-if="alertas.length === 0 && cofres.length === 0 && !carregando" class="empty-state">
            <span class="material-symbols-outlined empty-state__icon">flag</span>
            <p class="empty-state__title">Sem metas ou cofres</p>
            <p class="empty-state__desc">Comece planejando suas metas de faturamento e cofres de emergência.</p>
          </div>

          <section v-if="metas.length > 0" class="flex flex-col gap-3 pt-4 border-t border-outline-variant">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined w-8 h-8 flex items-center justify-center text-lg bg-on-surface-variant/10 text-on-surface-variant">list_alt</span>
              <h3 class="font-headline font-black text-[11px] tracking-[0.15em] uppercase text-on-surface">TODAS AS METAS ({{ metas.length }})</h3>
            </div>

            <div class="metas-lista">
              <div v-for="meta in metas" :key="meta.id" class="meta-lista-item" :class="{ 'meta-lista-item--inativa': !meta.ativa }">
                <div class="meta-lista-item__info">
                  <span class="meta-lista-item__tipo" :class="meta.tipo === 'GANHO' ? 'text-primary-container' : 'text-secondary'">
                    {{ meta.tipo }}
                  </span>
                  <span class="meta-lista-item__nome">{{ meta.nome }}</span>
                  <span class="meta-lista-item__valor">{{ formatarReais(meta.valor_meta) }} · {{ periodoLabel(meta.periodo) }}</span>
                </div>
                <div class="meta-lista-item__actions">
                  <button
                    class="meta-card__btn"
                    :title="meta.ativa ? 'Desativar' : 'Ativar'"
                    @click="toggleAtivaMeta(meta)"
                  >
                    <span class="material-symbols-outlined text-sm">
                      {{ meta.ativa ? 'toggle_on' : 'toggle_off' }}
                    </span>
                  </button>
                  <button class="meta-card__btn" title="Editar" @click="abrirEditarMeta(meta)">
                    <span class="material-symbols-outlined text-sm">edit</span>
                  </button>
                  <button class="meta-card__btn meta-card__btn--danger" title="Excluir" @click="pedirExclusaoMeta(meta)">
                    <span class="material-symbols-outlined text-sm">delete</span>
                  </button>
                </div>
              </div>
            </div>
          </section>

        </div>
      </template>
      </main>

      <!-- ══ Modal: Nova / Editar Meta ═════════════════════════ -->
      <div v-if="modalMetaVisivel" class="modal-overlay" @click.self="modalMetaVisivel = false">
        <div class="modal-box">
          <div class="modal-header">
            <span class="material-symbols-outlined text-primary-container">{{ modalMetaModoEdicao ? 'edit' : 'add_circle' }}</span>
            <h3 class="modal-titulo">{{ modalMetaModoEdicao ? 'EDITAR META' : 'NOVA META' }}</h3>
          </div>

          <form class="modal-form" @submit.prevent="salvarMeta">
            <!-- Tipo -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">TIPO DE META</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Ganho = faturamento mínimo desejado | Despesa = limite máximo de gastos.</div>
                </div>
              </div>
              <div class="campo-toggle-group">
                <button type="button"
                  class="campo-toggle" :class="{ 'campo-toggle--active-ganho': modalMetaTipo === 'GANHO' }"
                  @click="modalMetaTipo = 'GANHO'">GANHO</button>
                <button type="button"
                  class="campo-toggle" :class="{ 'campo-toggle--active-despesa': modalMetaTipo === 'DESPESA' }"
                  @click="modalMetaTipo = 'DESPESA'">DESPESA</button>
              </div>
              <p class="campo-dica">
                {{ modalMetaTipo === 'GANHO' ? 'Meta de faturamento (quanto mais, melhor)' : 'Teto limite de gastos (quanto menos, melhor)' }}
              </p>
            </div>

            <!-- Período -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">PERÍODO</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Frequência da meta (Diário, Semanal ou Mensal).</div>
                </div>
              </div>
              <div class="campo-toggle-group">
                <button type="button" v-for="p in (['DIARIO', 'SEMANAL', 'MENSAL'] as const)" :key="p"
                  class="campo-toggle" :class="{ 'campo-toggle--active': modalMetaPeriodo === p }"
                  @click="modalMetaPeriodo = p">{{ periodoLabel(p) }}</button>
              </div>
              <p class="campo-dica">Acompanha o ritmo {{ modalMetaPeriodo.toLowerCase() }} de trabalho</p>
            </div>

            <!-- Nome -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">NOME DA META</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Nome de identificação (ex: Meta Semanal de Faturamento).</div>
                </div>
              </div>
              <input v-model="modalMetaNome" type="text" class="tactical-input py-3"
                placeholder="Ex: Meta semanal de ganho" />
            </div>

            <!-- Valor -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">VALOR (R$)</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Valor alvo a ser atingido ou limite máximo a não ultrapassar.</div>
                </div>
              </div>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 font-headline font-bold text-on-surface-variant">R$</span>
                <input :value="modalMetaValor" type="text" inputmode="numeric" placeholder="0,00"
                  class="tactical-input pl-10 py-3 text-xl font-bold"
                  @input="e => {
                    const t = e.target as HTMLInputElement;
                    const v = formatarInputMoeda(t.value);
                    modalMetaValor = v;
                    t.value = v;
                  }" />
              </div>
            </div>

            <!-- Dias de trabalho -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">DIAS DE TRABALHO POR SEMANA</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Quantos dias na semana você costuma rodar na pista.</div>
                </div>
              </div>
              <div class="dias-trabalho-grid">
                <button type="button" v-for="d in 7" :key="d"
                  class="dia-btn" :class="{ 'dia-btn--active': modalMetaDias === d }"
                  @click="modalMetaDias = d">{{ d }}</button>
              </div>
              <p class="campo-dica">Usado para calcular a meta diária necessária nos dias restantes.</p>
            </div>

            <!-- Erro -->
            <div v-if="modalMetaErro" class="error-banner">
              <span class="material-symbols-outlined text-sm">error</span>
              {{ modalMetaErro }}
            </div>

            <!-- Botões -->
            <div class="modal-actions">
              <button type="button" class="btn-secondary h-12" @click="modalMetaVisivel = false">CANCELAR</button>
              <button type="submit" class="btn-primary h-12" :disabled="modalMetaEnviando">
                <span v-if="modalMetaEnviando" class="material-symbols-outlined animate-spin">refresh</span>
                <template v-else>
                  <span class="material-symbols-outlined">{{ modalMetaModoEdicao ? 'save' : 'add' }}</span>
                  {{ modalMetaModoEdicao ? 'SALVAR' : 'CRIAR META' }}
                </template>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- ══ Modal: Novo / Editar Cofre ════════════════════════ -->
      <div v-if="modalCofreVisivel" class="modal-overlay" @click.self="modalCofreVisivel = false">
        <div class="modal-box">
          <div class="modal-header">
            <span class="material-symbols-outlined text-tertiary">{{ modalCofreModoEdicao ? 'edit' : 'savings' }}</span>
            <h3 class="modal-titulo">{{ modalCofreModoEdicao ? 'EDITAR COFRE' : 'NOVO COFRE TÁTICO' }}</h3>
          </div>

          <form class="modal-form" @submit.prevent="salvarCofre">
            <!-- Categoria -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">CATEGORIA DO COFRE</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Finalidade da reserva (Pneu, Seguro, IPVA, Revisão, etc).</div>
                </div>
              </div>
              <div class="cofre-select-grid">
                <button type="button" v-for="cat in categoriasCofre" :key="cat.valor"
                  class="cofre-select-btn" :class="{ 'cofre-select-btn--active': modalCofreCategoria === cat.valor }"
                  @click="modalCofreCategoria = cat.valor">
                  <span class="material-symbols-outlined text-base">{{ cat.icone }}</span>
                  <span>{{ cat.label }}</span>
                </button>
              </div>
            </div>

            <!-- Nome -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">NOME DO COFRE</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Nome do seu objetivo (ex: Troca de Pneu Traseiro).</div>
                </div>
              </div>
              <input v-model="modalCofreNome" type="text" class="tactical-input py-3"
                placeholder="Ex: Reserva para Pneu Traseiro" />
            </div>

            <!-- Meta do Cofre -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">VALOR ALVO DA RESERVA (R$)</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Valor total que você precisa acumular para esse objetivo.</div>
                </div>
              </div>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 font-headline font-bold text-on-surface-variant">R$</span>
                <input :value="modalCofreMetaValor" type="text" inputmode="numeric" placeholder="0,00"
                  class="tactical-input pl-10 py-3 text-xl font-bold"
                  @input="e => {
                    const t = e.target as HTMLInputElement;
                    const v = formatarInputMoeda(t.value);
                    modalCofreMetaValor = v;
                    t.value = v;
                  }" />
              </div>
            </div>

            <!-- Saldo Inicial -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">SALDO ATUAL GUARDADO (R$)</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Quanto você já possui guardado neste cofre no momento.</div>
                </div>
              </div>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 font-headline font-bold text-on-surface-variant">R$</span>
                <input :value="modalCofreSaldoAtual" type="text" inputmode="numeric" placeholder="0,00"
                  class="tactical-input pl-10 py-3 text-xl font-bold"
                  @input="e => {
                    const t = e.target as HTMLInputElement;
                    const v = formatarInputMoeda(t.value);
                    modalCofreSaldoAtual = v;
                    t.value = v;
                  }" />
              </div>
            </div>

            <!-- Autoguarda por Porcentagem -->
            <div>
              <div class="campo-label-box">
                <label class="campo-label mb-0">GUARDAR % AUTOMÁTICA DO GANHO</label>
                <div class="tooltip-trigger">
                  <span class="material-symbols-outlined tooltip-icon">info</span>
                  <div class="tooltip-box">Porcentagem de cada ganho lançado que irá AUTOMATICAMENTE para este cofre (ex: 5%).</div>
                </div>
              </div>
              <div class="relative">
                <span class="absolute right-4 top-1/2 -translate-y-1/2 font-headline font-bold text-on-surface-variant">%</span>
                <input :value="modalCofreAutoguarda" type="text" inputmode="numeric" placeholder="0"
                  class="tactical-input pr-10 py-3 text-xl font-bold"
                  @input="e => {
                    const t = e.target as HTMLInputElement;
                    const v = t.value.replace(/[^0-9.,]/g, '');
                    modalCofreAutoguarda = v;
                    t.value = v;
                  }" />
              </div>
              <div class="flex gap-2 mt-2">
                <button type="button" class="btn-preset-pct" @click="modalCofreAutoguarda = '0'">0% (Manual)</button>
                <button type="button" class="btn-preset-pct" @click="modalCofreAutoguarda = '3'">3%</button>
                <button type="button" class="btn-preset-pct" @click="modalCofreAutoguarda = '5'">5%</button>
                <button type="button" class="btn-preset-pct" @click="modalCofreAutoguarda = '10'">10%</button>
              </div>
              <p class="campo-dica">Se colocar 5%, de cada R$ 100 faturados, R$ 5,00 sobem pro cofre automaticamente.</p>
            </div>

            <!-- Erro -->
            <div v-if="modalCofreErro" class="error-banner">
              <span class="material-symbols-outlined text-sm">error</span>
              {{ modalCofreErro }}
            </div>

            <!-- Botões -->
            <div class="modal-actions">
              <button type="button" class="btn-secondary h-12" @click="modalCofreVisivel = false">CANCELAR</button>
              <button type="submit" class="btn-primary h-12" :disabled="modalCofreEnviando">
                <span v-if="modalCofreEnviando" class="material-symbols-outlined animate-spin">refresh</span>
                <template v-else>
                  <span class="material-symbols-outlined">{{ modalCofreModoEdicao ? 'save' : 'savings' }}</span>
                  {{ modalCofreModoEdicao ? 'SALVAR' : 'CRIAR COFRE' }}
                </template>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- ══ Modal: Aporte / Saque Rápido no Cofre ────────────── -->
      <div v-if="modalAporteVisivel" class="modal-overlay" @click.self="modalAporteVisivel = false">
        <div class="modal-box modal-box--sm">
          <div class="modal-header">
            <span class="material-symbols-outlined text-primary-container">account_balance_wallet</span>
            <h3 class="modal-titulo">AJUSTAR SALDO: {{ aporteCofreNome }}</h3>
          </div>

          <form class="modal-form" @submit.prevent="confirmarAporte">
            <!-- Operação -->
            <div>
              <label class="campo-label">OPERACÃO</label>
              <div class="campo-toggle-group">
                <button type="button"
                  class="campo-toggle" :class="{ 'campo-toggle--active-ganho': aporteTipoOperacao === 'DEPOSITO' }"
                  @click="aporteTipoOperacao = 'DEPOSITO'">+ DEPOSITAR (GUARDAR)</button>
                <button type="button"
                  class="campo-toggle" :class="{ 'campo-toggle--active-despesa': aporteTipoOperacao === 'SAQUE' }"
                  @click="aporteTipoOperacao = 'SAQUE'">- SACAR (RETIRAR)</button>
              </div>
            </div>

            <!-- Valor -->
            <div>
              <label class="campo-label">VALOR DA OPERAÇÃO (R$)</label>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 font-headline font-bold text-on-surface-variant">R$</span>
                <input :value="aporteValor" type="text" inputmode="numeric" placeholder="0,00"
                  class="tactical-input pl-10 py-3 text-xl font-bold"
                  @input="e => {
                    const t = e.target as HTMLInputElement;
                    const v = formatarInputMoeda(t.value);
                    aporteValor = v;
                    t.value = v;
                  }" />
              </div>
            </div>

            <!-- Erro -->
            <div v-if="aporteErro" class="error-banner">
              <span class="material-symbols-outlined text-sm">error</span>
              {{ aporteErro }}
            </div>

            <!-- Ações -->
            <div class="modal-actions">
              <button type="button" class="btn-secondary h-11" @click="modalAporteVisivel = false">CANCELAR</button>
              <button type="submit" class="btn-primary h-11" :disabled="aporteEnviando">
                <span v-if="aporteEnviando" class="material-symbols-outlined animate-spin">refresh</span>
                <template v-else>
                  <span class="material-symbols-outlined">check</span>
                  CONFIRMAR
                </template>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- ══ Modal: Confirmar Exclusão ═════════════════════════ -->
      <div v-if="confirmarExcluir" class="modal-overlay" @click.self="confirmarExcluir = false">
        <div class="modal-box modal-box--sm">
          <div class="modal-header">
            <span class="material-symbols-outlined text-secondary">delete_forever</span>
            <h3 class="modal-titulo">EXCLUIR {{ confirmarExcluirTipo }}</h3>
          </div>
          <p class="font-body text-sm text-on-surface px-1 py-2">
            Tem certeza que deseja excluir <strong>{{ confirmarExcluirNome }}</strong>?
          </p>
          <div class="modal-actions">
            <button type="button" class="btn-secondary h-11" @click="confirmarExcluir = false">CANCELAR</button>
            <button type="button"
              class="h-11 w-full bg-secondary text-on-secondary font-headline font-black tracking-widest uppercase flex items-center justify-center gap-3 transition-all active:scale-[0.98]"
              :disabled="excluindo"
              @click="confirmarExclusao">
              <span v-if="excluindo" class="material-symbols-outlined animate-spin">refresh</span>
              <template v-else>
                <span class="material-symbols-outlined">delete</span>
                EXCLUIR
              </template>
            </button>
          </div>
        </div>
      </div>

    </div>
  </AppLayout>
</template>

<style scoped>
/* ─── Page layout ────────────────────────────────────────────── */
.metas-page {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

/* ─── Page header ────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.header-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.label-overline {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface-variant));
}

.page-title {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 900;
  font-size: 2rem;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  line-height: 1;
  color: rgb(var(--color-on-surface));
}

.btn-nova-meta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.625rem 0.875rem;
  background: rgb(var(--color-primary-container));
  color: rgb(var(--color-on-primary-fixed));
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
  border: none;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-novo-cofre {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.625rem 0.875rem;
  background: rgb(var(--color-surface-container-high));
  color: rgb(var(--color-on-surface));
  border: 1px solid rgb(var(--color-outline));
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-nova-meta:hover, .btn-novo-cofre:hover {
  filter: brightness(1.1);
}

.btn-nova-meta:active, .btn-novo-cofre:active {
  transform: scale(0.97);
}

/* ─── Error banner ───────────────────────────────────────────── */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgb(var(--color-error-container));
  color: rgb(var(--color-on-error-container));
  padding: 0.75rem 1rem;
  margin: 0.75rem 1.25rem 0;
  font-size: 12px;
}

/* ─── Content area ───────────────────────────────────────────── */
.metas-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ─── Section ────────────────────────────────────────────────── */
.metas-secao {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.secao-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.secao-icone {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.secao-icone--ganho {
  background: rgb(var(--color-primary-container) / 0.15);
  color: rgb(var(--color-primary-container));
}

.secao-icone--despesa {
  background: rgb(var(--color-secondary) / 0.15);
  color: rgb(var(--color-secondary));
}

.secao-icone--cofre {
  background: rgb(var(--color-tertiary) / 0.15);
  color: rgb(var(--color-tertiary));
}

.secao-icone--lista {
  background: rgb(var(--color-on-surface-variant) / 0.1);
  color: rgb(var(--color-on-surface-variant));
}

.secao-titulo {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 900;
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface));
}

/* ─── Meta cards grid ────────────────────────────────────────── */
.metas-cards-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .metas-cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  }
}

/* ─── Meta card ──────────────────────────────────────────────── */
.meta-card {
  background: rgb(var(--color-surface-container));
  padding: 1.125rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: transform 0.15s;
  overflow: hidden;
  word-break: break-word;
}

.meta-card:hover {
  transform: translateY(-1px);
}

.meta-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.meta-card__info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
  flex: 1;
}

.meta-card__periodo {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface-variant));
}

.meta-card__nome {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 800;
  font-size: 14px;
  letter-spacing: 0.02em;
  color: rgb(var(--color-on-surface));
  text-transform: uppercase;
  word-break: break-word;
}

.meta-card__actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.meta-card__btn {
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  color: rgb(var(--color-on-surface-variant));
  transition: all 0.15s;
}

.meta-card__btn:hover {
  color: rgb(var(--color-primary-container));
  background: rgb(var(--color-primary-container) / 0.1);
}

.meta-card__btn--danger:hover {
  color: rgb(var(--color-secondary));
  background: rgb(var(--color-secondary) / 0.1);
}

/* ─── Valores ────────────────────────────────────────────────── */
.meta-card__valores {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 0.5rem;
}

.meta-card__label {
  display: block;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface-variant));
  margin-bottom: 0.125rem;
}

.meta-card__valor {
  display: block;
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 800;
  font-size: 16px;
  color: rgb(var(--color-on-surface));
}

.meta-card__valor--ganho {
  color: rgb(var(--color-primary-container));
}

.meta-card__valor--despesa {
  color: rgb(var(--color-secondary));
}

/* ─── Progress bar ───────────────────────────────────────────── */
.progress-bar {
  width: 100%;
  height: 6px;
  background: rgb(var(--color-surface-container-highest));
  overflow: hidden;
}

.progress-bar--cofre {
  height: 8px;
}

.progress-bar__fill {
  height: 100%;
  transition: width 0.6s ease;
}

.progress-bar__fill--ganho {
  background: rgb(var(--color-primary-container));
}

.progress-bar__fill--despesa {
  background: rgb(var(--color-secondary));
}

.progress-bar__fill--cofre {
  background: linear-gradient(90deg, rgb(var(--color-tertiary)), rgb(var(--color-primary-container)));
}

.meta-card__progress-info, .cofre-card__progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  font-weight: 600;
  color: rgb(var(--color-on-surface-variant));
}

/* ─── Status badge ───────────────────────────────────────────── */
.meta-card__status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 11px;
  font-weight: 600;
}

.meta-card__status-text {
  flex: 1;
  min-width: 0;
}

.status-atingida {
  background: rgb(var(--color-primary-container) / 0.12);
  color: rgb(var(--color-primary-container));
  border-left: 3px solid rgb(var(--color-primary-container));
}

.status-em-andamento {
  background: rgb(var(--color-surface-container-high) / 0.5);
  color: rgb(var(--color-on-surface-variant));
  border-left: 3px solid rgb(var(--color-on-surface-variant));
}

.status-estourada {
  background: rgb(var(--color-error-container));
  color: rgb(var(--color-on-error-container));
  border-left: 3px solid rgb(var(--color-error));
}

.status-atencao {
  background: rgb(var(--color-secondary) / 0.1);
  color: rgb(var(--color-secondary));
  border-left: 3px solid rgb(var(--color-secondary));
}

.status-dentro-meta {
  background: rgb(var(--color-primary-container) / 0.08);
  color: rgb(var(--color-primary-container));
  border-left: 3px solid rgb(var(--color-primary-container) / 0.5);
}

/* ─── Ritmo diário ───────────────────────────────────────────── */
.meta-card__ritmo {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  background: rgb(var(--color-primary-container) / 0.06);
  color: rgb(var(--color-primary-container));
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
  flex-wrap: wrap;
}

/* ─── Cofres grid & card ─────────────────────────────────────── */
.cofres-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .cofres-grid {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  }
}

.cofre-card {
  background: rgb(var(--color-surface-container));
  padding: 1.125rem;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  transition: transform 0.15s;
  overflow: hidden;
}

.cofre-card:hover {
  transform: translateY(-1px);
}

.cofre-card__header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.cofre-card__icon {
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgb(var(--color-tertiary) / 0.15);
  color: rgb(var(--color-tertiary));
  flex-shrink: 0;
}

.cofre-card__info {
  flex: 1;
  min-width: 0;
}

.cofre-card__categoria {
  display: block;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgb(var(--color-tertiary));
}

.cofre-card__nome {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 800;
  font-size: 13px;
  color: rgb(var(--color-on-surface));
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cofre-badge-autoguarda {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: rgb(var(--color-primary-container) / 0.12);
  color: rgb(var(--color-primary-container));
  font-size: 10px;
  font-weight: 700;
  width: fit-content;
}

.cofre-card__valores {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.cofre-card__label {
  display: block;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface-variant));
  margin-bottom: 0.125rem;
}

.cofre-card__realizado {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 900;
  font-size: 17px;
  color: rgb(var(--color-primary-container));
}

.cofre-card__meta {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 700;
  font-size: 15px;
  color: rgb(var(--color-on-surface-variant));
}

.btn-aporte-cofre {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.625rem 0.5rem;
  min-height: 40px;
  background: rgb(var(--color-surface-container-high));
  color: rgb(var(--color-on-surface));
  border: 1px solid rgb(var(--color-outline-variant));
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-aporte-cofre:hover {
  background: rgb(var(--color-surface-bright));
  border-color: rgb(var(--color-outline));
}

.empty-state-cofre {
  background: rgb(var(--color-surface-container-low));
  padding: 1.25rem;
  text-align: center;
  border: 1px dashed rgb(var(--color-outline-variant));
}

/* ─── Empty state ────────────────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 3rem 1.5rem;
}

.empty-state__icon {
  font-size: 48px;
  color: rgb(var(--color-on-surface-variant) / 0.3);
  margin-bottom: 1rem;
}

.empty-state__title {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 800;
  font-size: 16px;
  color: rgb(var(--color-on-surface));
  text-transform: uppercase;
}

.empty-state__desc {
  font-size: 12px;
  color: rgb(var(--color-on-surface-variant));
  margin-top: 0.25rem;
}

/* ─── Lista completa ─────────────────────────────────────────── */
.metas-lista-secao {
  border-top: 1px solid rgb(var(--color-outline-variant));
  padding-top: 1rem;
}

.metas-lista {
  display: flex;
  flex-direction: column;
}

.meta-lista-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid rgb(var(--color-outline-variant) / 0.5);
  transition: background 0.1s;
  gap: 0.5rem;
}

.meta-lista-item:hover {
  background: rgb(var(--color-surface-container) / 0.5);
}

.meta-lista-item--inativa {
  opacity: 0.45;
}

.meta-lista-item__info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
  flex: 1;
}

.meta-lista-item__tipo {
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.meta-lista-item__nome {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 700;
  font-size: 13px;
  color: rgb(var(--color-on-surface));
  text-transform: uppercase;
  word-break: break-word;
}

.meta-lista-item__valor {
  font-size: 11px;
  color: rgb(var(--color-on-surface-variant));
}

.meta-lista-item__actions {
  display: flex;
  gap: 0.125rem;
  flex-shrink: 0;
}

/* ─── Modal ──────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 80;
  background: rgb(0 0 0 / 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
}

.modal-box {
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  background: rgb(var(--color-surface-container-high));
  border: 1px solid rgb(var(--color-outline-variant));
  padding: 1.25rem;
}

.modal-box--sm {
  max-width: 380px;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.modal-titulo {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 900;
  font-size: 14px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface));
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

.modal-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

/* ─── Campo label ────────────────────────────────────────────── */
.campo-label {
  display: block;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface-variant));
  margin-bottom: 0.5rem;
}

.campo-label-box {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-bottom: 0.5rem;
}

.campo-dica {
  font-size: 10px;
  color: rgb(var(--color-on-surface-variant));
  margin-top: 0.375rem;
  font-weight: 500;
}

/* ─── Toggle group ───────────────────────────────────────────── */
.campo-toggle-group {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.campo-toggle {
  padding: 0.5rem 0.875rem;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-on-surface-variant));
  border: 1px solid rgb(var(--color-outline-variant));
  cursor: pointer;
  transition: all 0.15s;
}

.campo-toggle:hover {
  background: rgb(var(--color-surface-variant));
}

.campo-toggle--active {
  background: rgb(var(--color-on-surface));
  color: rgb(var(--color-background));
  border-color: rgb(var(--color-on-surface));
  font-weight: 900;
}

.campo-toggle--active-ganho {
  background: rgb(var(--color-primary-container));
  color: rgb(var(--color-on-primary-fixed));
  border-color: rgb(var(--color-primary-container));
  font-weight: 900;
}

.campo-toggle--active-despesa {
  background: rgb(var(--color-secondary));
  color: rgb(var(--color-on-secondary));
  border-color: rgb(var(--color-secondary));
  font-weight: 900;
}

/* ─── Dias de trabalho ───────────────────────────────────────── */
.dias-trabalho-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
}

.dia-btn {
  height: 2.25rem;
  min-width: 0;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 700;
  font-size: 12px;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-on-surface-variant));
  border: 1px solid rgb(var(--color-outline-variant));
  cursor: pointer;
  transition: all 0.15s;
}

.dia-btn:hover {
  background: rgb(var(--color-surface-variant));
}

.dia-btn--active {
  background: rgb(var(--color-on-surface));
  color: rgb(var(--color-background));
  border-color: rgb(var(--color-on-surface));
  font-weight: 900;
}

/* ─── Cofre select ───────────────────────────────────────────── */
.cofre-select-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.375rem;
}

@media (min-width: 400px) {
  .cofre-select-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.cofre-select-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.625rem;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-on-surface-variant));
  border: 1px solid rgb(var(--color-outline-variant));
  cursor: pointer;
  transition: all 0.15s;
}

.cofre-select-btn:hover {
  background: rgb(var(--color-surface-variant));
}

.cofre-select-btn--active {
  background: rgb(var(--color-tertiary) / 0.15);
  color: rgb(var(--color-tertiary));
  border-color: rgb(var(--color-tertiary));
  font-weight: 900;
}

.btn-preset-pct {
  padding: 0.25rem 0.5rem;
  font-size: 10px;
  font-weight: 700;
  background: rgb(var(--color-surface-container));
  border: 1px solid rgb(var(--color-outline-variant));
  color: rgb(var(--color-on-surface));
  cursor: pointer;
}

.btn-preset-pct:hover {
  background: rgb(var(--color-surface-bright));
}

/* ─── Tooltip & Dicas de ajuda ───────────────────────────────── */
.tooltip-trigger {
  position: relative;
  display: inline-flex;
  align-items: center;
  cursor: help;
}

.tooltip-icon {
  font-size: 14px;
  color: rgb(var(--color-on-surface-variant));
  opacity: 0.7;
  transition: opacity 0.15s;
}

.tooltip-trigger:hover .tooltip-icon {
  opacity: 1;
  color: rgb(var(--color-primary-container));
}

.tooltip-box {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-4px);
  background: rgb(var(--color-surface-bright));
  color: rgb(var(--color-on-surface));
  border: 1px solid rgb(var(--color-outline-variant));
  padding: 0.375rem 0.625rem;
  font-size: 10px;
  font-weight: 600;
  line-height: 1.35;
  white-space: normal;
  width: max-content;
  max-width: min(220px, 80vw);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  z-index: 99;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease, transform 0.15s ease;
  text-transform: none;
  letter-spacing: normal;
}

.tooltip-trigger:hover .tooltip-box,
.tooltip-trigger:focus .tooltip-box,
.tooltip-trigger:active .tooltip-box {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(-50%) translateY(-8px);
}
</style>

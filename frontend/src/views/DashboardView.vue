<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMotoStore } from '@/stores/moto'
import { obterVisaoMes } from '@/api/visaoMes'
import type { VisaoMesResposta } from '@/types'
import AppDateInput from '@/components/AppDateInput.vue'
import ConfirmarEmailBanner from '@/components/ConfirmarEmailBanner.vue'
import NotificacaoUsuarioFreeBanner from '@/components/NotificacaoUsuarioFreeBanner.vue'
import AtualizarKmModal from '@/components/AtualizarKmModal.vue'
import AppLayout from '@/components/AppLayout.vue'

const router    = useRouter()
const auth      = useAuthStore()
const motoStore = useMotoStore()

// ── Estado ───────────────────────────────────────────────────
const visao          = ref<VisaoMesResposta | null>(null)
const carregando     = ref(true)
const erroCarregar   = ref('')
const modalKmVisivel = ref(false)

type ModoPeriodo = 'HOJE' | 'SEMANA' | 'MES' | 'PERSONALIZADO'

const modoPeriodo = ref<ModoPeriodo>('HOJE')
const dataInicio  = ref('')
const dataFim     = ref('')

// ── Dados derivados ───────────────────────────────────────────
const primeiroNome = computed(() => {
  const nome = auth.usuario?.nome ?? ''
  return nome.split(' ')[0].toUpperCase()
})

const motoAtiva = computed(() => motoStore.motoAtiva)

const nomeMoto = computed(() => {
  const m = motoAtiva.value
  if (!m) return '—'
  const marca  = m.marca_manual  ?? ''
  const modelo = m.modelo_manual ?? ''
  return [marca, modelo].filter(Boolean).join(' ') || '—'
})

// ── Dados financeiros ────────────────────────────────────────
const ganho   = computed(() => visao.value?.ganho?.total_periodo   ?? '0.00')
const despesa = computed(() => visao.value?.despesa?.total_periodo ?? '0.00')
const saldo   = computed(() => visao.value?.saldo_mes              ?? '0.00')

// ── Formatações ───────────────────────────────────────────────
function formatarReais(valor: string | number): string {
  const n = typeof valor === 'string' ? parseFloat(valor) : valor
  if (isNaN(n)) return 'R$ 0,00'
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

const hojeFormatado = computed(() =>
  new Date().toLocaleDateString('pt-BR', {
    weekday: 'long', day: '2-digit', month: 'long',
  }).toUpperCase()
)

const saldoPositivo = computed(() => {
  const n = parseFloat(saldo.value)
  return isNaN(n) || n >= 0
})

const alertas = computed(() => visao.value?.resumo_executivo ?? [])

const tituloSaldo = computed(() => {
  if (modoPeriodo.value === 'HOJE') return 'SALDO DE HOJE'
  if (modoPeriodo.value === 'SEMANA') return 'SALDO DA SEMANA'
  if (modoPeriodo.value === 'PERSONALIZADO') return 'SALDO DO PERÍODO'
  return 'SALDO DO MÊS'
})

const faixaPeriodo = computed(() => {
  if (!dataInicio.value || !dataFim.value) return ''
  const inicio = formatarIsoParaBr(dataInicio.value)
  const fim    = formatarIsoParaBr(dataFim.value)
  return inicio === fim ? inicio : `${inicio} até ${fim}`
})

function formatarDataIso(data: Date): string {
  const ano = data.getFullYear()
  const mes = String(data.getMonth() + 1).padStart(2, '0')
  const dia = String(data.getDate()).padStart(2, '0')
  return `${ano}-${mes}-${dia}`
}

function formatarIsoParaBr(iso: string): string {
  const [ano, mes, dia] = iso.split('-')
  if (!ano || !mes || !dia) return iso
  return `${dia}/${mes}/${ano}`
}

function obterInicioSemanaAtual(): Date {
  const hoje    = new Date()
  const inicio  = new Date(hoje)
  const diaSemana   = inicio.getDay()
  const deslocamento = diaSemana === 0 ? 6 : diaSemana - 1
  inicio.setDate(inicio.getDate() - deslocamento)
  return inicio
}

function obterFimSemanaAtual(): Date {
  const inicio = obterInicioSemanaAtual()
  const fim    = new Date(inicio)
  fim.setDate(inicio.getDate() + 6)
  return fim
}

function obterInicioMesAtual(): Date {
  const hoje = new Date()
  return new Date(hoje.getFullYear(), hoje.getMonth(), 1)
}

function obterFimMesAtual(): Date {
  const hoje = new Date()
  return new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0)
}

function aplicarPeriodoRapido(modo: Exclude<ModoPeriodo, 'PERSONALIZADO'>): void {
  modoPeriodo.value = modo
  const hoje = new Date()

  if (modo === 'HOJE') {
    const isoHoje = formatarDataIso(hoje)
    dataInicio.value = isoHoje
    dataFim.value    = isoHoje
    carregar()
    return
  }

  if (modo === 'SEMANA') {
    dataInicio.value = formatarDataIso(obterInicioSemanaAtual())
    dataFim.value    = formatarDataIso(obterFimSemanaAtual())
    carregar()
    return
  }

  dataInicio.value = formatarDataIso(obterInicioMesAtual())
  dataFim.value    = formatarDataIso(obterFimMesAtual())
  carregar()
}

function aplicarPeriodoPersonalizado(): void {
  if (!dataInicio.value || !dataFim.value) {
    erroCarregar.value = 'Selecione data de início e fim.'
    return
  }
  if (dataInicio.value > dataFim.value) {
    erroCarregar.value = 'Data inicial não pode ser maior que a data final.'
    return
  }
  modoPeriodo.value = 'PERSONALIZADO'
  carregar()
}

// ── Carregar dados ────────────────────────────────────────────
async function carregar() {
  carregando.value   = true
  erroCarregar.value = ''
  try {
    const motoId = motoAtiva.value?.id
    if (modoPeriodo.value === 'MES') {
      const inicioMes = obterInicioMesAtual()
      visao.value = await obterVisaoMes({
        ano: inicioMes.getFullYear(),
        mes: inicioMes.getMonth() + 1,
        motoUsuarioId: motoId,
      })
    } else {
      visao.value = await obterVisaoMes({
        dataInicio: dataInicio.value,
        dataFim:    dataFim.value,
        motoUsuarioId: motoId,
      })
    }
  } catch {
    erroCarregar.value = 'Não foi possível carregar os dados do período.'
  } finally {
    carregando.value = false
  }
}

onMounted(() => {
  aplicarPeriodoRapido('HOJE')
})
</script>

<template>
  <AppLayout>
    <div class="dashboard-page">

      <!-- Banner de Confirmação de E-mail -->
      <ConfirmarEmailBanner />

      <!-- ══ Cabeçalho da página ═════════════════════════════ -->
      <section class="page-header">
        <div>
          <p class="label-overline">{{ hojeFormatado }}</p>
          <h2 class="page-title">OLÁ, {{ primeiroNome }}</h2>
          <p v-if="nomeMoto !== '—'" class="moto-label">
            <span class="material-symbols-outlined text-xs align-middle">two_wheeler</span>
            {{ nomeMoto }}
          </p>
        </div>

        <!-- Card Odômetro (apenas se tiver moto) -->
        <div v-if="motoAtiva" class="odometer-card">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 bg-primary-container/10 flex items-center justify-center text-primary-container">
              <span class="material-symbols-outlined text-lg">speed</span>
            </div>
            <div>
              <p class="label-overline">ODÔMETRO ATUAL</p>
              <p class="font-headline font-black text-sm text-on-surface tracking-wide">
                {{ motoAtiva.km_atual.toLocaleString('pt-BR') }} KM
              </p>
            </div>
          </div>
          <button class="btn-km" @click="modalKmVisivel = true">
            <span class="material-symbols-outlined text-xs">edit</span>
            ATUALIZAR KM
          </button>
        </div>
      </section>

      <!-- Modal atualizar KM -->
      <AtualizarKmModal
        :show="modalKmVisivel"
        :km-atual="motoAtiva?.km_atual ?? 0"
        @close="modalKmVisivel = false"
        @salvo="carregar"
      />

      <!-- ══ Grid Principal Desktop ══════════════════════════ -->
      <div class="dashboard-grid">

        <!-- ── Coluna Esquerda / Coluna única em mobile ─────── -->
        <div class="dashboard-col-main">

          <!-- Filtro de período -->
          <section class="card-section">
            <p class="label-overline">PERÍODO DA VISÃO</p>

            <div class="period-tabs">
              <button
                class="period-tab"
                :class="{ 'period-tab--active': modoPeriodo === 'HOJE' }"
                @click="aplicarPeriodoRapido('HOJE')"
              >HOJE</button>
              <button
                class="period-tab"
                :class="{ 'period-tab--active': modoPeriodo === 'SEMANA' }"
                @click="aplicarPeriodoRapido('SEMANA')"
              >SEMANA</button>
              <button
                class="period-tab"
                :class="{ 'period-tab--active': modoPeriodo === 'MES' }"
                @click="aplicarPeriodoRapido('MES')"
              >MÊS</button>
            </div>

            <div class="custom-period">
              <p class="label-overline">PERSONALIZADO</p>
              <div class="grid grid-cols-2 gap-2">
                <AppDateInput v-model="dataInicio" tone="system" :max="dataFim || undefined" />
                <AppDateInput v-model="dataFim" tone="system" :min="dataInicio || undefined" />
              </div>
              <button class="btn-apply" @click="aplicarPeriodoPersonalizado">
                <span class="material-symbols-outlined text-sm">check_circle</span>
                APLICAR PERÍODO
              </button>
            </div>
          </section>

          <!-- Erro de carregamento -->
          <div v-if="erroCarregar" class="error-banner">
            <span class="material-symbols-outlined text-sm">warning</span>
            {{ erroCarregar }}
          </div>

          <!-- Skeleton -->
          <template v-if="carregando && !visao">
            <div class="space-y-4 animate-pulse">
              <div class="h-32 bg-surface-container-low" />
              <div class="grid grid-cols-2 gap-3">
                <div class="h-20 bg-surface-container-low" />
                <div class="h-20 bg-surface-container-low" />
              </div>
            </div>
          </template>

          <template v-else>
            <!-- ── Card principal: Saldo ──────────────────── -->
            <div class="saldo-card">
              <div class="saldo-card__glow" />
              <p class="label-overline">{{ tituloSaldo }}</p>
              <p v-if="faixaPeriodo" class="label-overline">{{ faixaPeriodo }}</p>
              <div class="flex items-baseline gap-2 mt-1">
                <span
                  class="font-headline font-black text-5xl leading-none"
                  :class="saldoPositivo ? 'text-primary-container' : 'text-secondary'"
                >
                  {{ formatarReais(saldo) }}
                </span>
              </div>
              <div
                class="mt-3 flex items-center gap-1.5 text-[9px] font-label font-bold"
                :class="saldoPositivo ? 'text-primary-container' : 'text-secondary'"
              >
                <span class="material-symbols-outlined text-sm">
                  {{ saldoPositivo ? 'trending_up' : 'trending_down' }}
                </span>
                <span>{{ saldoPositivo ? 'SALDO POSITIVO' : 'SALDO NEGATIVO' }}</span>
              </div>
            </div>

            <!-- ── Link histórico ────────────────────────── -->
            <button class="historico-link" @click="router.push({ name: 'historico' })">
              <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary-container">analytics</span>
                <span class="font-label text-xs font-bold tracking-[0.2em] uppercase">HISTÓRICO DETALHADO</span>
              </div>
              <span class="material-symbols-outlined text-on-surface-variant text-sm">chevron_right</span>
            </button>

            <!-- ── Métricas: Ganhos / Despesas ───────────── -->
            <div class="metrics-grid">
              <div class="metric-card">
                <p class="label-overline">GANHOS</p>
                <p class="font-headline font-bold text-lg text-on-surface">{{ formatarReais(ganho) }}</p>
              </div>
              <div class="metric-card">
                <p class="label-overline">DESPESAS</p>
                <p class="font-headline font-bold text-lg text-secondary">{{ formatarReais(despesa) }}</p>
              </div>
            </div>
          </template>
        </div>

        <!-- ── Coluna Direita: Ações + Alertas (desktop) ─── -->
        <div class="dashboard-col-side">

          <!-- Ações rápidas -->
          <section class="card-section">
            <p class="label-overline">AÇÕES RÁPIDAS</p>
            <div class="actions-grid">
              <!-- Lançar Ganho -->
              <button class="action-card action-card--ganho" @click="router.push({ name: 'lancar' })">
                <div class="action-card__icon action-card__icon--ganho">
                  <span class="material-symbols-outlined text-2xl">add_circle</span>
                </div>
                <div class="action-card__text">
                  <span class="action-card__title">LANÇAR GANHO</span>
                  <span class="action-card__sub">Corrida, entrega...</span>
                </div>
              </button>

              <!-- Lançar Despesa -->
              <button
                class="action-card action-card--despesa"
                @click="router.push({ name: 'lancar', query: { tipo: 'DESPESA' } })"
              >
                <div class="action-card__icon action-card__icon--despesa">
                  <span class="material-symbols-outlined text-2xl">remove_circle</span>
                </div>
                <div class="action-card__text">
                  <span class="action-card__title">LANÇAR DESPESA</span>
                  <span class="action-card__sub">Gasolina, manutenção...</span>
                </div>
              </button>
            </div>
          </section>

          <!-- Alertas -->
          <div v-if="alertas.length" class="alerts-card">
            <p class="label-overline text-secondary">ALERTAS DO PERÍODO</p>
            <ul class="space-y-1.5 mt-2">
              <li
                v-for="(alerta, i) in alertas"
                :key="i"
                class="flex items-start gap-2 text-xs text-on-surface-variant font-body"
              >
                <span class="material-symbols-outlined text-secondary text-sm mt-0.5 flex-shrink-0">warning</span>
                {{ alerta }}
              </li>
            </ul>
          </div>
        </div>

      </div>

      <!-- Notificação de Vantagens para Usuário Free (No final da página de início) -->
      <NotificacaoUsuarioFreeBanner />
    </div>
  </AppLayout>
</template>

<style scoped>
/* ─── Page wrapper ───────────────────────────────────────── */
.dashboard-page {
  padding: 1.5rem 1.25rem;
  padding-bottom: 7rem; /* espaço para bottom nav mobile */
  max-width: 100%;
}

@media (min-width: 1024px) {
  .dashboard-page {
    padding: 2rem 2.5rem;
    padding-bottom: 2rem; /* sem bottom nav */
  }
}

/* ─── Cabeçalho da página ────────────────────────────────── */
.page-header {
  margin-bottom: 1.5rem;
}

@media (min-width: 640px) {
  .page-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
  }
}

.page-title {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 900;
  font-size: 1.875rem;
  line-height: 1.1;
  text-transform: uppercase;
  letter-spacing: -0.02em;
  color: rgb(var(--color-on-surface));
}

.moto-label {
  font-size: 10px;
  color: rgb(var(--color-primary-container));
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-weight: 700;
  margin-top: 0.25rem;
}

.label-overline {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface-variant));
  margin-bottom: 0.25rem;
}

/* ─── Odômetro card ──────────────────────────────────────── */
.odometer-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgb(var(--color-surface-container));
  padding: 0.75rem 1rem;
  border-left: 4px solid rgb(var(--color-primary-container));
  margin-top: 0.75rem;
  gap: 1rem;
}

@media (min-width: 640px) {
  .odometer-card {
    margin-top: 0;
    min-width: 280px;
  }
}

.btn-km {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: rgb(var(--color-primary-container) / 0.1);
  border: 1px solid rgb(var(--color-primary-container) / 0.3);
  color: rgb(var(--color-primary-container));
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-km:hover {
  background: rgb(var(--color-primary-container));
  color: rgb(var(--color-on-primary-fixed));
}

/* ─── Dashboard grid (2 colunas em desktop) ──────────────── */
.dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 2rem;
    align-items: start;
  }
}

.dashboard-col-main,
.dashboard-col-side {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* ─── Card section genérico ──────────────────────────────── */
.card-section {
  background: rgb(var(--color-surface-container));
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* ─── Period tabs ────────────────────────────────────────── */
.period-tabs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.period-tab {
  padding: 0.625rem;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  border: 1px solid rgb(var(--color-outline-variant));
  cursor: pointer;
  transition: all 0.15s;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-on-surface-variant));
}

.period-tab:hover {
  background: rgb(var(--color-surface-variant));
  color: rgb(var(--color-on-surface));
}

.period-tab--active {
  background: rgb(var(--color-primary-container));
  color: rgb(var(--color-on-primary-fixed));
  border-color: rgb(var(--color-primary-container));
  font-weight: 900;
}

.custom-period {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-apply {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  width: 100%;
  padding: 0.625rem;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-outline));
  color: rgb(var(--color-on-surface));
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-apply:hover {
  background: rgb(var(--color-surface-variant));
}

/* ─── Erro ───────────────────────────────────────────────── */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgb(var(--color-error-container));
  color: rgb(var(--color-on-error-container));
  padding: 0.75rem 1rem;
  font-size: 12px;
}

/* ─── Card de Saldo ──────────────────────────────────────── */
.saldo-card {
  background: rgb(var(--color-surface-container-low));
  padding: 1.25rem;
  position: relative;
  overflow: hidden;
}

.saldo-card__glow {
  position: absolute;
  top: -5rem;
  right: -5rem;
  width: 10rem;
  height: 10rem;
  background: rgb(var(--color-primary-container) / 0.1);
  border-radius: 50%;
  filter: blur(2rem);
  pointer-events: none;
}

/* ─── Link histórico ─────────────────────────────────────── */
.historico-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 1rem;
  background: rgb(var(--color-surface-container));
  border: 1px solid rgb(var(--color-outline-variant));
  cursor: pointer;
  transition: all 0.15s;
}

.historico-link:hover {
  background: rgb(var(--color-surface-container-high));
}

/* ─── Métricas ───────────────────────────────────────────── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.metric-card {
  background: rgb(var(--color-surface-container));
  padding: 1rem;
}

/* ─── Ações rápidas ──────────────────────────────────────── */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgb(var(--color-surface));
  border: 2px solid rgb(var(--color-outline-variant));
  padding: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  min-width: 0;
  width: 100%;
}

.action-card--ganho:hover {
  border-color: rgb(var(--color-primary-container));
}

.action-card--despesa:hover {
  border-color: rgb(var(--color-secondary));
}

.action-card--manutencao:hover {
  border-color: rgb(var(--color-tertiary));
}

.action-card:active {
  transform: scale(0.97);
}

.action-card__icon {
  width: 2.75rem;
  height: 2.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.action-card:hover .action-card__icon {
  transform: scale(1.05);
}

.action-card__icon--ganho {
  background: rgb(var(--color-primary-container));
  color: rgb(var(--color-on-primary-fixed));
}

.action-card__icon--despesa {
  background: rgb(var(--color-secondary));
  color: rgb(var(--color-on-secondary));
}

.action-card__icon--manutencao {
  background: rgb(var(--color-tertiary));
  color: rgb(var(--color-on-tertiary));
}

.action-card__text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  flex: 1;
}

.action-card__title {
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface));
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-card__sub {
  font-size: 9px;
  color: rgb(var(--color-on-surface-variant));
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ─── Alertas ────────────────────────────────────────────── */
.alerts-card {
  background: rgb(var(--color-surface-container-lowest));
  padding: 1.25rem;
  border-left: 4px solid rgb(var(--color-secondary));
}
</style>

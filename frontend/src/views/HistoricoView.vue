<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { listarLancamentos, excluirLancamentosLote } from '@/api/lancamentos'
import { obterHistoricoKm, excluirHistoricoKm } from '@/api/motos'
import { obterInteligenciaResumo } from '@/api/inteligencia'
import { useMotoStore } from '@/stores/moto'
import type {
  LancamentoResposta, TipoLancamento,
  MotoHistoricoKmResumo,
  InteligenciaResumo,
} from '@/types'
import AppDateInput from '@/components/AppDateInput.vue'
import EditarLancamentoModal from '@/components/EditarLancamentoModal.vue'
import AppLayout from '@/components/AppLayout.vue'

const router   = useRouter()
const motoStore = useMotoStore()

// ── 2 Abas Táticas: Transações vs Relatórios ─────────────────────
type AbaId = 'transacoes' | 'relatorios'
const abaAtiva = ref<AbaId>('transacoes')
const abas: { id: AbaId; label: string; icon: string }[] = [
  { id: 'transacoes', label: 'TRANSAÇÕES', icon: 'receipt_long' },
  { id: 'relatorios', label: 'RELATÓRIOS', icon: 'insights' },
]

// ── Estado Transações ───────────────────────────────────────────
const lancamentos  = ref<LancamentoResposta[]>([])
const carregando   = ref(false)
const erro         = ref('')
const filtroTipo   = ref<TipoLancamento | 'TODOS'>('TODOS')
const dataInicio   = ref('')
const dataFim      = ref('')
const paginaAtual  = ref(1)
const totalRegistros = ref(0)
const totalPaginas = ref(1)
const mostrarFiltros = ref(false)
const filtroCategoriaNome = ref('')
const filtroBusca = ref('')
const filtroValorMin = ref('')
const filtroValorMax = ref('')
type ModoPeriodo = 'HOJE' | 'SEMANA' | 'MES' | 'PERSONALIZADO'
const modoPeriodo = ref<ModoPeriodo>('HOJE')

// ── Estado Seleção & Edição ─────────────────────────────────────
const modoSelecao = ref(false)
const idsSelecionados = ref<number[]>([])
const executandoExclusaoLote = ref(false)

const modalEdicaoVisivel = ref(false)
const lancamentoParaEditar = ref<LancamentoResposta | null>(null)

// ── Estado Relatórios (KM + Inteligência) ───────────────────────
const historicoKm = ref<MotoHistoricoKmResumo | null>(null)
const inteligencia = ref<InteligenciaResumo | null>(null)
const carregandoRelatorios = ref(false)

// ── Computed ────────────────────────────────────────────────────
const lancamentosFiltrados = computed(() => lancamentos.value)

const tipoFiltroApi = computed(() =>
  filtroTipo.value === 'TODOS' ? undefined : filtroTipo.value
)


const faixaPeriodo = computed(() => {
  if (!dataInicio.value || !dataFim.value) return ''
  const inicio = formatarIsoParaBr(dataInicio.value)
  const fim = formatarIsoParaBr(dataFim.value)
  return inicio === fim ? inicio : `${inicio} até ${fim}`
})

const filtrosAtivos = computed(() => {
  const chips: Array<{ chave: 'categoria' | 'busca' | 'min' | 'max'; texto: string }> = []
  if (filtroCategoriaNome.value.trim()) {
    chips.push({ chave: 'categoria', texto: `Categoria: ${filtroCategoriaNome.value.trim()}` })
  }
  if (filtroBusca.value.trim()) {
    chips.push({ chave: 'busca', texto: `Busca: "${filtroBusca.value.trim()}"` })
  }
  if (filtroValorMin.value.trim()) {
    chips.push({ chave: 'min', texto: `Min: R$ ${filtroValorMin.value.trim()}` })
  }
  if (filtroValorMax.value.trim()) {
    chips.push({ chave: 'max', texto: `Max: R$ ${filtroValorMax.value.trim()}` })
  }
  return chips
})

const motoAtiva = computed(() => motoStore.motoAtiva)

const registrosParaGrafico = computed(() => {
  if (!historicoKm.value || !historicoKm.value.registros.length) return []
  const ordenados = historicoKm.value.registros.slice().reverse()
  if (ordenados.length <= 15) return ordenados

  const passo = (ordenados.length - 1) / 14
  const pontos = []
  for (let i = 0; i < 15; i++) {
    const idx = Math.round(i * passo)
    if (ordenados[idx]) pontos.push(ordenados[idx])
  }
  return pontos
})

function paraNumeroFiltro(valor: string): number | undefined {
  const txt = valor.trim()
  if (!txt) return undefined
  const n = Number(txt.replace(',', '.'))
  if (Number.isNaN(n) || n < 0) return undefined
  return n
}

// ── Carregar Transações ─────────────────────────────────────────
async function carregarTransacoes(pagina = paginaAtual.value) {
  carregando.value = true
  erro.value = ''
  try {
    const resposta = await listarLancamentos({
      tipo: tipoFiltroApi.value,
      data_inicio: dataInicio.value || undefined,
      data_fim: dataFim.value || undefined,
      categoria_nome: filtroCategoriaNome.value.trim() || undefined,
      busca: filtroBusca.value.trim() || undefined,
      valor_min: paraNumeroFiltro(filtroValorMin.value),
      valor_max: paraNumeroFiltro(filtroValorMax.value),
      pagina,
      limite: 10,
    })
    lancamentos.value = resposta.itens
    totalRegistros.value = resposta.total
    paginaAtual.value = resposta.pagina
    totalPaginas.value = resposta.total_paginas
  } catch {
    erro.value = 'Erro ao carregar histórico.'
  } finally {
    carregando.value = false
  }
}

// ── Carregar Relatórios ─────────────────────────────────────────
async function carregarRelatorios() {
  carregandoRelatorios.value = true
  try {
    const promessas: [Promise<InteligenciaResumo>, Promise<MotoHistoricoKmResumo | null>] = [
      obterInteligenciaResumo(),
      motoAtiva.value ? obterHistoricoKm(motoAtiva.value.id) : Promise.resolve(null),
    ]
    const [intelRes, kmRes] = await Promise.all(promessas)
    inteligencia.value = intelRes
    historicoKm.value = kmRes
  } catch {
    /* falha silenciosa se houver erro ao carregar relatórios */
  } finally {
    carregandoRelatorios.value = false
  }
}

async function removerRegistroKm(id: number) {
  try {
    await excluirHistoricoKm(id)
    await carregarRelatorios()
  } catch { /* silencioso */ }
}

// ── Watch da Aba ────────────────────────────────────────────────
watch(abaAtiva, (novaAba) => {
  if (novaAba === 'relatorios' && (!inteligencia.value || !historicoKm.value)) {
    carregarRelatorios()
  }
})

// ── Formatações ─────────────────────────────────────────────────
function formatarReais(valor: string | number): string {
  const n = typeof valor === 'string' ? parseFloat(valor) : valor
  if (isNaN(n)) return 'R$ 0,00'
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatarData(iso: string): string {
  return new Date(iso + 'T12:00:00').toLocaleDateString('pt-BR', {
    day: '2-digit', month: 'short'
  }).toUpperCase()
}

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

function formatarDataCriacao(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  } catch { return iso }
}

function obterInicioSemanaAtual(): Date {
  const hoje = new Date()
  const inicio = new Date(hoje)
  const diaSemana = inicio.getDay()
  const deslocamento = diaSemana === 0 ? 6 : diaSemana - 1
  inicio.setDate(inicio.getDate() - deslocamento)
  return inicio
}

function obterFimSemanaAtual(): Date {
  const inicio = obterInicioSemanaAtual()
  const fim = new Date(inicio)
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
    dataFim.value = isoHoje
    carregarTransacoes(1)
    return
  }
  if (modo === 'SEMANA') {
    dataInicio.value = formatarDataIso(obterInicioSemanaAtual())
    dataFim.value = formatarDataIso(obterFimSemanaAtual())
    carregarTransacoes(1)
    return
  }
  dataInicio.value = formatarDataIso(obterInicioMesAtual())
  dataFim.value = formatarDataIso(obterFimMesAtual())
  carregarTransacoes(1)
}

function aplicarPeriodoPersonalizado(): void {
  if (!dataInicio.value || !dataFim.value) {
    erro.value = 'Selecione data de início e fim.'
    return
  }
  if (dataInicio.value > dataFim.value) {
    erro.value = 'Data inicial não pode ser maior que a data final.'
    return
  }
  modoPeriodo.value = 'PERSONALIZADO'
  carregarTransacoes(1)
}

function mudarTipoFiltro(tipo: TipoLancamento | 'TODOS') {
  filtroTipo.value = tipo
  carregarTransacoes(1)
}

function aplicarFiltrosAvancados() {
  const min = paraNumeroFiltro(filtroValorMin.value)
  const max = paraNumeroFiltro(filtroValorMax.value)
  if (min !== undefined && max !== undefined && min > max) {
    erro.value = 'Valor mínimo não pode ser maior que o valor máximo.'
    return
  }
  carregarTransacoes(1)
}

function limparFiltrosAvancados() {
  filtroCategoriaNome.value = ''
  filtroBusca.value = ''
  filtroValorMin.value = ''
  filtroValorMax.value = ''
  carregarTransacoes(1)
}

function removerFiltro(chave: 'categoria' | 'busca' | 'min' | 'max') {
  if (chave === 'categoria') filtroCategoriaNome.value = ''
  if (chave === 'busca') filtroBusca.value = ''
  if (chave === 'min') filtroValorMin.value = ''
  if (chave === 'max') filtroValorMax.value = ''
  carregarTransacoes(1)
}

// ── Ações de Seleção e Edição ────────────────────────────────────
function abrirEdicao(lanc: LancamentoResposta) {
  lancamentoParaEditar.value = lanc
  modalEdicaoVisivel.value = true
}

function clicarNaLinha(lanc: LancamentoResposta) {
  if (modoSelecao.value) {
    toggleItemSelecao(lanc.id)
  } else {
    abrirEdicao(lanc)
  }
}

function toggleModoSelecao() {
  modoSelecao.value = !modoSelecao.value
  idsSelecionados.value = []
}

function cancelarSelecao() {
  modoSelecao.value = false
  idsSelecionados.value = []
}

function toggleItemSelecao(id: number) {
  const idx = idsSelecionados.value.indexOf(id)
  if (idx > -1) {
    idsSelecionados.value.splice(idx, 1)
  } else {
    idsSelecionados.value.push(id)
  }
}

function ehSelecionado(id: number): boolean {
  return idsSelecionados.value.includes(id)
}

async function executarExclusaoLote() {
  if (!idsSelecionados.value.length) return
  const qtd = idsSelecionados.value.length
  if (!confirm(`Tem certeza que deseja excluir ${qtd} lançamento(s)?`)) return

  executandoExclusaoLote.value = true
  try {
    await excluirLancamentosLote(idsSelecionados.value)
    await motoStore.carregarMotos()
    idsSelecionados.value = []
    modoSelecao.value = false
    await carregarTransacoes()
  } catch {
    erro.value = 'Erro ao excluir lançamentos.'
  } finally {
    executandoExclusaoLote.value = false
  }
}

function paginaAnterior() {
  if (paginaAtual.value <= 1) return
  carregarTransacoes(paginaAtual.value - 1)
}

function proximaPagina() {
  if (paginaAtual.value >= totalPaginas.value) return
  carregarTransacoes(paginaAtual.value + 1)
}

function formatarDiaSemana(ds: string | null): string {
  if (!ds) return ''
  const map: Record<string, string> = {
    'SEGUNDA': 'SEG', 'TERCA': 'TER', 'QUARTA': 'QUA',
    'QUINTA': 'QUI', 'SEXTA': 'SEX', 'SABADO': 'SAB', 'DOMINGO': 'DOM'
  }
  return map[ds] ?? ds.slice(0, 3)
}

function diaSemanaCompleto(ds: string): string {
  const map: Record<string, string> = {
    'SEGUNDA': 'Segunda', 'TERCA': 'Terça', 'QUARTA': 'Quarta',
    'QUINTA': 'Quinta', 'SEXTA': 'Sexta', 'SABADO': 'Sábado', 'DOMINGO': 'Domingo'
  }
  return map[ds] ?? ds
}

function origemLabel(origem: string): string {
  const map: Record<string, string> = {
    'ATUALIZACAO_RAPIDA': 'Atualização',
    'ABASTECIMENTO': 'Abastecimento',
    'MANUTENCAO': 'Manutenção',
    'CADASTRO': 'Cadastro',
    'MANUAL': 'Manual',
  }
  return map[origem] ?? origem
}

// ── Helpers visuais dos gráficos ────────────────────────────────
function maxBarWidth(items: { total: string }[]): number {
  if (!items.length) return 1
  return Math.max(...items.map(i => parseFloat(i.total)), 1)
}

function barPercent(valor: string, max: number): number {
  const n = parseFloat(valor)
  if (!max || isNaN(n)) return 0
  return Math.min((n / max) * 100, 100)
}

// Helper de cor para o Lucro Real (se for negativo, forçar VERMELHO)
function ehNegativo(valorStr: string): boolean {
  return parseFloat(valorStr) < 0
}



onMounted(async () => {
  if (!motoStore.carregado) await motoStore.carregarMotos()
  aplicarPeriodoRapido('HOJE')
})
</script>

<template>
  <AppLayout>
  <div class="historico-page">
    <main class="px-5 py-5 lg:px-8 lg:py-6 space-y-5 max-w-4xl mx-auto pb-28 lg:pb-8">

      <!-- Título -->
      <div>
        <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">CENTRAL DE DADOS</p>
        <h2 class="font-headline font-extrabold text-4xl tracking-tighter uppercase leading-none">HISTÓRICO</h2>
      </div>

      <!-- 2 ABAS TÁTICAS -->
      <div class="grid grid-cols-2 gap-1 bg-surface-container p-1">
        <button v-for="aba in abas" :key="aba.id"
          class="flex items-center justify-center gap-1.5 py-3 font-label text-[10px] font-bold tracking-widest uppercase transition-all duration-150 cursor-pointer"
          :class="abaAtiva === aba.id
            ? 'bg-primary-container text-on-primary-fixed shadow-sm'
            : 'text-on-surface-variant hover:bg-surface-container-high'"
          @click="abaAtiva = aba.id">
          <span class="material-symbols-outlined text-base">{{ aba.icon }}</span>
          {{ aba.label }}
        </button>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════ -->
      <!-- ABA 1: TRANSAÇÕES (EXTRATO SIMPLES)                           -->
      <!-- ═══════════════════════════════════════════════════════════════ -->
      <template v-if="abaAtiva === 'transacoes'">

        <p v-if="faixaPeriodo" class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
          {{ faixaPeriodo }}
        </p>


        <!-- Filtro de período -->
        <div class="space-y-3 bg-surface-container p-3">
          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
            PERÍODO DO HISTÓRICO
          </p>
          <div class="grid grid-cols-3 gap-2">
            <button
              class="py-2.5 font-label text-[10px] tracking-widest uppercase border transition-all duration-150 cursor-pointer"
              :class="modoPeriodo === 'HOJE'
                ? 'bg-slate-200 text-slate-900 dark:bg-slate-100 dark:text-slate-900 border-slate-300 shadow-sm font-black'
                : 'bg-white dark:bg-surface-container-high text-on-surface-variant border-outline-variant hover:bg-surface-variant dark:hover:bg-surface-bright shadow-2xs font-bold'"
              @click="aplicarPeriodoRapido('HOJE')"
            >
              HOJE
            </button>
            <button
              class="py-2.5 font-label text-[10px] tracking-widest uppercase border transition-all duration-150 cursor-pointer"
              :class="modoPeriodo === 'SEMANA'
                ? 'bg-slate-200 text-slate-900 dark:bg-slate-100 dark:text-slate-900 border-slate-300 shadow-sm font-black'
                : 'bg-white dark:bg-surface-container-high text-on-surface-variant border-outline-variant hover:bg-surface-variant dark:hover:bg-surface-bright shadow-2xs font-bold'"
              @click="aplicarPeriodoRapido('SEMANA')"
            >
              SEMANA
            </button>
            <button
              class="py-2.5 font-label text-[10px] tracking-widest uppercase border transition-all duration-150 cursor-pointer"
              :class="modoPeriodo === 'MES'
                ? 'bg-slate-200 text-slate-900 dark:bg-slate-100 dark:text-slate-900 border-slate-300 shadow-sm font-black'
                : 'bg-white dark:bg-surface-container-high text-on-surface-variant border-outline-variant hover:bg-surface-variant dark:hover:bg-surface-bright shadow-2xs font-bold'"
              @click="aplicarPeriodoRapido('MES')"
            >
              MÊS
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <AppDateInput v-model="dataInicio" tone="system" :max="dataFim || undefined" />
            <AppDateInput v-model="dataFim" tone="system" :min="dataInicio || undefined" />
          </div>
          <button
            class="w-full py-2.5 bg-white dark:bg-surface-container-high border border-outline dark:border-outline-variant text-on-surface font-label text-[10px] font-bold tracking-widest uppercase hover:bg-surface-variant dark:hover:bg-surface-bright transition-all shadow-sm active:scale-[0.98] flex items-center justify-center gap-1.5"
            @click="aplicarPeriodoPersonalizado"
          >
            <span class="material-symbols-outlined text-sm">check_circle</span>
            APLICAR PERÍODO
          </button>

          <div class="flex justify-end">
            <button
              class="h-8 px-2.5 flex items-center gap-1.5 bg-surface-container border border-outline-variant text-on-surface-variant hover:bg-surface-container-high transition-colors"
              @click="mostrarFiltros = !mostrarFiltros"
            >
              <span class="material-symbols-outlined text-sm">tune</span>
              <span class="font-label text-[9px] font-bold tracking-widest uppercase">Filtros</span>
              <span
                v-if="filtrosAtivos.length"
                class="w-1.5 h-1.5 rounded-full bg-primary-container"
              />
              <span class="material-symbols-outlined text-sm">
                {{ mostrarFiltros ? 'expand_less' : 'expand_more' }}
              </span>
            </button>
          </div>
        </div>

        <!-- Filtro de tipo -->
        <div class="grid grid-cols-3 gap-2">
          <button v-for="t in ['TODOS', 'GANHO', 'DESPESA']" :key="t"
            class="h-9 font-label text-[10px] font-bold tracking-wider uppercase transition-all border-b-2"
            :class="filtroTipo === t
              ? t === 'GANHO'
                ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                : t === 'DESPESA'
                  ? 'bg-secondary text-on-secondary border-secondary'
                  : 'bg-surface-container-high text-on-surface border-outline'
              : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline'"
            @click="mudarTipoFiltro(t as TipoLancamento | 'TODOS')">
            {{ t === 'TODOS' ? 'TODOS' : t === 'GANHO' ? 'GANHOS' : 'DESPESAS' }}
          </button>
        </div>

        <!-- Filtros avançados -->
        <div
          v-if="mostrarFiltros"
          class="space-y-2 bg-surface-container p-3 border border-outline-variant"
        >
          <input
            v-model="filtroBusca"
            type="text"
            placeholder="Buscar por descrição (ex: pneu, lâmpada)"
            class="tactical-input py-2.5 px-2 text-sm"
          />
          <input
            v-model="filtroCategoriaNome"
            type="text"
            placeholder="Categoria (ex: combustível)"
            class="tactical-input py-2.5 px-2 text-sm"
          />
          <div class="grid grid-cols-2 gap-2">
            <input
              v-model="filtroValorMin"
              type="text"
              inputmode="decimal"
              placeholder="Valor mínimo"
              class="tactical-input py-2.5 px-2 text-sm"
            />
            <input
              v-model="filtroValorMax"
              type="text"
              inputmode="decimal"
              placeholder="Valor máximo"
              class="tactical-input py-2.5 px-2 text-sm"
            />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button
              class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border border-outline-variant bg-surface-container text-on-surface hover:bg-surface-bright transition-colors"
              @click="limparFiltrosAvancados"
            >
              LIMPAR
            </button>
            <button
              class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border border-primary-container bg-primary-container text-on-primary-fixed hover:brightness-110 transition-all"
              @click="aplicarFiltrosAvancados"
            >
              APLICAR
            </button>
          </div>
        </div>

        <div v-if="filtrosAtivos.length" class="flex flex-wrap gap-2">
          <button
            v-for="chip in filtrosAtivos"
            :key="chip.chave"
            class="h-7 px-2 flex items-center gap-1 bg-surface-container border border-outline-variant text-on-surface-variant font-label text-[9px] uppercase tracking-wider"
            @click="removerFiltro(chip.chave)"
          >
            <span>{{ chip.texto }}</span>
            <span class="material-symbols-outlined text-xs">close</span>
          </button>
        </div>

        <!-- Erro -->
        <div v-if="erro"
          class="flex items-center gap-2 bg-error-container text-on-error-container text-xs font-label px-4 py-3">
          <span class="material-symbols-outlined text-sm">warning</span>{{ erro }}
        </div>

        <!-- Skeleton -->
        <template v-if="carregando && !lancamentos.length">
          <div class="space-y-2 animate-pulse">
            <div v-for="i in 5" :key="i" class="h-16 bg-surface-container-low" />
          </div>
        </template>

        <!-- Lista vazia -->
        <div v-else-if="!lancamentos.length && !carregando"
          class="flex flex-col items-center justify-center py-16 gap-3 text-on-surface-variant">
          <span class="material-symbols-outlined text-4xl opacity-30">receipt_long</span>
          <p class="font-label text-xs tracking-widest uppercase">Nenhum lançamento encontrado</p>
          <button class="btn-primary h-11 text-xs mt-2 w-auto px-6"
            @click="router.push({ name: 'lancar' })">
            <span class="material-symbols-outlined text-sm">add</span>
            LANÇAR AGORA
          </button>
        </div>

        <!-- Cabeçalho da Lista -->
        <div class="flex justify-between items-center py-1">
          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
            {{ totalRegistros }} REGISTRO{{ totalRegistros !== 1 ? 'S' : '' }}
          </p>
          <button
            v-if="lancamentosFiltrados.length > 1 || modoSelecao"
            class="h-7 px-2.5 flex items-center gap-1 font-label text-[9px] font-bold tracking-widest uppercase border transition-colors"
            :class="modoSelecao
              ? 'bg-red-600 text-white border-red-600'
              : 'bg-surface-container border-outline-variant text-on-surface-variant hover:bg-surface-bright'"
            @click="toggleModoSelecao"
          >
            <span class="material-symbols-outlined text-xs">{{ modoSelecao ? 'close' : 'delete_sweep' }}</span>
            {{ modoSelecao ? 'CANCELAR' : 'APAGAR VÁRIOS' }}
          </button>
        </div>

        <!-- Barra Flutuante de Ações Dinâmica (quando modoSelecao ativo) -->
        <div
          v-if="modoSelecao"
          class="bg-surface-container-high p-3 border border-outline-variant flex justify-between items-center gap-2 animate-in fade-in duration-150"
        >
          <div class="flex items-center gap-2">
            <button
              class="font-label text-[9px] font-bold tracking-widest uppercase text-on-surface-variant hover:text-on-surface"
              @click="cancelarSelecao"
            >
              CANCELAR
            </button>
          </div>

          <div class="flex items-center gap-2">
            <!-- Botão Excluir em Lote -->
            <button
              class="h-8 px-3 bg-red-600 text-white font-label text-[9px] font-extrabold tracking-widest uppercase flex items-center gap-1 disabled:opacity-40 hover:bg-red-500 transition-all"
              :disabled="!idsSelecionados.length || executandoExclusaoLote"
              @click="executarExclusaoLote"
            >
              <span class="material-symbols-outlined text-xs">delete</span>
              EXCLUIR SELECIONADOS ({{ idsSelecionados.length }})
            </button>
          </div>
        </div>

        <!-- Lista de lançamentos -->
        <ul v-if="lancamentosFiltrados.length" class="space-y-1">
          <li v-for="l in lancamentosFiltrados" :key="l.id"
            class="scannable-row flex items-center justify-between py-3 px-1 cursor-pointer transition-colors hover:bg-surface-container-high/50"
            :class="{ 'bg-surface-container-highest/60 border-l-2 border-outline-variant': modoSelecao && ehSelecionado(l.id) }"
            @click="clicarNaLinha(l)">
            <div class="flex items-center gap-3">

              <!-- Checkbox de seleção (EXIBIDO APENAS NO MODO SELEÇÃO) -->
              <div v-if="modoSelecao" class="flex items-center justify-center pr-1" @click.stop="toggleItemSelecao(l.id)">
                <input
                  type="checkbox"
                  :checked="ehSelecionado(l.id)"
                  class="w-4 h-4 accent-slate-400 dark:accent-slate-200 cursor-pointer"
                />
              </div>

              <!-- Ícone indicador -->
              <div class="w-8 h-8 flex items-center justify-center flex-shrink-0"
                :class="l.tipo === 'GANHO' ? 'bg-primary-container/10' : 'bg-secondary/10'">
                <span class="material-symbols-outlined text-base"
                  :class="l.tipo === 'GANHO' ? 'text-primary-container' : 'text-secondary'">
                  {{ l.tipo === 'GANHO' ? 'arrow_upward' : 'arrow_downward' }}
                </span>
              </div>
              <div>
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
                  {{ formatarData(l.data_lancamento) }}
                  <span v-if="l.dia_semana" class="opacity-60">· {{ formatarDiaSemana(l.dia_semana) }}</span>
                  <span v-if="l.periodo" class="opacity-60">· {{ l.periodo }}</span>
                </p>
                <p v-if="l.categoria_nome" class="font-label text-[9px] text-on-surface-variant uppercase opacity-80">
                  {{ l.categoria_nome }}
                </p>
                <p v-if="l.descricao" class="font-label text-[10px] text-on-surface">
                  {{ l.descricao }}
                </p>
                <p v-if="l.km_corrida" class="font-label text-[9px] text-on-surface-variant">
                  {{ parseFloat(l.km_corrida).toFixed(1) }} km
                  <span v-if="l.minutos_corrida">· {{ l.minutos_corrida }}min</span>
                </p>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <p class="font-headline font-bold text-sm"
                :class="l.tipo === 'GANHO' ? 'text-primary-container' : 'text-secondary'">
                {{ l.tipo === 'GANHO' ? '+' : '-' }}{{ formatarReais(l.valor) }}
              </p>
              <span v-if="!modoSelecao" class="material-symbols-outlined text-xs text-on-surface-variant opacity-40">chevron_right</span>
            </div>
          </li>
        </ul>

        <!-- Contagem -->
        <p v-if="lancamentosFiltrados.length > 0"
          class="text-center font-label text-[9px] text-on-surface-variant uppercase tracking-widest py-2">
          {{ totalRegistros }} registro{{ totalRegistros > 1 ? 's' : '' }}
        </p>

        <div
          v-if="totalPaginas > 1"
          class="flex items-center justify-center gap-3"
        >
          <button
            class="w-10 h-9 flex items-center justify-center border border-outline-variant bg-surface-container-high text-on-surface disabled:opacity-40"
            :disabled="paginaAtual <= 1 || carregando"
            @click="paginaAnterior"
          >
            <span class="material-symbols-outlined text-base">chevron_left</span>
          </button>
          <p class="text-center font-label text-[9px] text-on-surface-variant uppercase tracking-widest">
            PÁG {{ paginaAtual }} / {{ totalPaginas }}
          </p>
          <button
            class="w-10 h-9 flex items-center justify-center border border-outline-variant bg-surface-container-high text-on-surface disabled:opacity-40"
            :disabled="paginaAtual >= totalPaginas || carregando"
            @click="proximaPagina"
          >
            <span class="material-symbols-outlined text-base">chevron_right</span>
          </button>
        </div>
      </template>

      <!-- ═══════════════════════════════════════════════════════════════ -->
      <!-- ABA 2: RELATÓRIOS (KM + INTELIGÊNCIA PREMIUM CONSOLIDADO)    -->
      <!-- ═══════════════════════════════════════════════════════════════ -->
      <template v-else-if="abaAtiva === 'relatorios'">

        <!-- Skeleton -->
        <div v-if="carregandoRelatorios" class="space-y-3 animate-pulse">
          <div class="h-24 bg-surface-container-low" />
          <div class="h-36 bg-surface-container-low" />
          <div class="h-32 bg-surface-container-low" />
        </div>

        <template v-else>

          <!-- Banner Premium (Roxo/Violeta Inteligência) -->
          <div class="flex items-center justify-between bg-gradient-to-r from-purple-500/15 via-indigo-500/10 to-purple-600/5 border border-purple-500/30 px-3 py-2">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-purple-400 text-base">workspace_premium</span>
              <span class="font-label text-[9px] font-bold tracking-widest text-purple-600 dark:text-purple-300 uppercase">PAINEL DE INTELIGÊNCIA PREMIUM</span>
            </div>
          </div>

          <!-- ── 1. METRICAS E EVOLUÇÃO DE QUILOMETRAGEM (KM - CIANO / ÂMBAR) ────────── -->
          <div v-if="historicoKm" class="space-y-3">
            <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
              🏍️ EVOLUÇÃO E ODÔMETRO DA MOTO
            </p>
            <div class="grid grid-cols-3 gap-2">
              <!-- KM NO MÊS (Ciano Telemetria) -->
              <div class="bg-surface-container p-3 border-l-2 border-cyan-500">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-0.5">KM NO MÊS</p>
                <p class="font-headline font-bold text-lg text-cyan-600 dark:text-cyan-400">{{ historicoKm.km_mes.toLocaleString('pt-BR') }}</p>
                <p class="font-label text-[9px] text-on-surface-variant">km</p>
              </div>
              <!-- MÉDIA/DIA (Sky Blue) -->
              <div class="bg-surface-container p-3 border-l-2 border-sky-400">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-0.5">MÉDIA/DIA</p>
                <p class="font-headline font-bold text-lg text-sky-600 dark:text-sky-400">{{ historicoKm.media_dia }}</p>
                <p class="font-label text-[9px] text-on-surface-variant">km/dia</p>
              </div>
              <!-- TROCA ÓLEO (Âmbar Alerta Manutenção) -->
              <div class="bg-surface-container p-3 border-l-2 border-amber-500">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-0.5">TROCA ÓLEO</p>
                <p class="font-headline font-bold text-lg text-amber-600 dark:text-amber-400">
                  {{ historicoKm.previsao_troca_oleo_km !== null ? `${historicoKm.previsao_troca_oleo_km.toLocaleString('pt-BR')}` : '—' }}
                </p>
                <p class="font-label text-[9px] text-on-surface-variant">
                  {{ historicoKm.previsao_troca_oleo_km !== null ? 'km restantes' : 'sem dados' }}
                </p>
              </div>
            </div>

            <!-- Gráfico SVG do Odômetro (Linha e Pontos em Ciano) -->
            <div v-if="historicoKm.registros.length >= 2" class="bg-surface-container p-4">
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-3">EVOLUÇÃO ACUMULADA DO ODÔMETRO</p>
              <svg viewBox="0 0 320 140" class="w-full h-auto">
                <line v-for="i in 5" :key="'g'+i" :x1="30" :y1="10 + (i-1)*30" :x2="310" :y2="10 + (i-1)*30"
                  stroke="currentColor" class="text-outline-variant" stroke-width="0.5" opacity="0.3" />
                <polyline
                  :points="registrosParaGrafico.map((r, idx, arr) => {
                    const minKm = Math.min(...arr.map(a => a.km))
                    const maxKm = Math.max(...arr.map(a => a.km))
                    const range = maxKm - minKm || 1
                    const x = 35 + (idx / Math.max(arr.length - 1, 1)) * 270
                    const y = 120 - ((r.km - minKm) / range) * 100
                    return `${x},${y}`
                  }).join(' ')"
                  fill="none"
                  stroke="#22d3ee"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <circle v-for="(r, idx) in registrosParaGrafico" :key="'d'+r.id"
                  :cx="35 + (idx / Math.max(registrosParaGrafico.length - 1, 1)) * 270"
                  :cy="(() => {
                    const minKm = Math.min(...registrosParaGrafico.map(a => a.km))
                    const maxKm = Math.max(...registrosParaGrafico.map(a => a.km))
                    const range = maxKm - minKm || 1
                    return 120 - ((r.km - minKm) / range) * 100
                  })()"
                  r="3.5"
                  fill="#22d3ee"
                />
              </svg>
              <div class="flex justify-between mt-1">
                <span class="font-label text-[8px] text-on-surface-variant">
                  {{ formatarDataCriacao(registrosParaGrafico[0]?.data_criacao || '') }}
                </span>
                <span class="font-label text-[8px] text-on-surface-variant">
                  {{ formatarDataCriacao(registrosParaGrafico[registrosParaGrafico.length - 1]?.data_criacao || '') }}
                </span>
              </div>
            </div>
          </div>

          <!-- ── 2. COMPARATIVO VS MÊS ANTERIOR (VERDE & ROSA FINANCEIRO) ── -->
          <div v-if="inteligencia" class="space-y-2">
            <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
              📊 COMPARATIVO VS MÊS ANTERIOR
            </p>
            <div class="grid grid-cols-3 gap-2">

              <!-- CARD FATURAMENTO (VERDE LIMÃO) -->
              <div class="bg-surface-container p-3 border-l-2 border-primary-container">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-1">
                  FATURAMENTO
                </p>
                <p class="font-headline font-bold text-sm text-primary-container">
                  {{ formatarReais(inteligencia.comparativo.faturamento.valor_atual) }}
                </p>
                <div v-if="inteligencia.comparativo.faturamento.variacao_percentual !== null" class="flex items-center gap-0.5 mt-1">
                  <span class="material-symbols-outlined text-xs text-primary-container">
                    {{ inteligencia.comparativo.faturamento.variacao_percentual >= 0 ? 'trending_up' : 'trending_down' }}
                  </span>
                  <span class="font-label text-[9px] font-bold text-primary-container">
                    {{ inteligencia.comparativo.faturamento.variacao_percentual > 0 ? '+' : '' }}{{ inteligencia.comparativo.faturamento.variacao_percentual }}%
                  </span>
                </div>
                <p v-else class="font-label text-[8px] text-on-surface-variant mt-1 opacity-60">sem dados</p>
              </div>

              <!-- CARD DESPESAS (ROSA/VERMELHO) -->
              <div class="bg-surface-container p-3 border-l-2 border-secondary">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-1">
                  DESPESAS
                </p>
                <p class="font-headline font-bold text-sm text-secondary">
                  {{ formatarReais(inteligencia.comparativo.despesas.valor_atual) }}
                </p>
                <div v-if="inteligencia.comparativo.despesas.variacao_percentual !== null" class="flex items-center gap-0.5 mt-1">
                  <span class="material-symbols-outlined text-xs text-secondary">
                    {{ inteligencia.comparativo.despesas.variacao_percentual <= 0 ? 'trending_down' : 'trending_up' }}
                  </span>
                  <span class="font-label text-[9px] font-bold text-secondary">
                    {{ inteligencia.comparativo.despesas.variacao_percentual > 0 ? '+' : '' }}{{ inteligencia.comparativo.despesas.variacao_percentual }}%
                  </span>
                </div>
                <p v-else class="font-label text-[8px] text-on-surface-variant mt-1 opacity-60">sem dados</p>
              </div>

              <!-- CARD LUCRO REAL (VERDE SE >= 0, ROSA SE < 0) -->
              <div class="bg-surface-container p-3 border-l-2"
                :class="ehNegativo(inteligencia.comparativo.lucro.valor_atual) ? 'border-secondary' : 'border-primary-container'">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-1">
                  LUCRO REAL
                </p>
                <p class="font-headline font-bold text-sm"
                  :class="ehNegativo(inteligencia.comparativo.lucro.valor_atual) ? 'text-secondary font-black' : 'text-primary-container'">
                  {{ formatarReais(inteligencia.comparativo.lucro.valor_atual) }}
                </p>
                <div v-if="inteligencia.comparativo.lucro.variacao_percentual !== null" class="flex items-center gap-0.5 mt-1">
                  <span class="material-symbols-outlined text-xs"
                    :class="ehNegativo(inteligencia.comparativo.lucro.valor_atual) ? 'text-secondary' : 'text-primary-container'">
                    {{ inteligencia.comparativo.lucro.variacao_percentual >= 0 ? 'trending_up' : 'trending_down' }}
                  </span>
                  <span class="font-label text-[9px] font-bold"
                    :class="ehNegativo(inteligencia.comparativo.lucro.valor_atual) ? 'text-secondary' : 'text-primary-container'">
                    {{ inteligencia.comparativo.lucro.variacao_percentual > 0 ? '+' : '' }}{{ inteligencia.comparativo.lucro.variacao_percentual }}%
                  </span>
                </div>
                <p v-else class="font-label text-[8px] text-on-surface-variant mt-1 opacity-60">sem dados</p>
              </div>

            </div>
          </div>

          <!-- ── 3. RAIO-X DAS DESPESAS & MAIOR VILÃO ────────────────── -->
          <div v-if="inteligencia && inteligencia.despesas_por_categoria.length" class="space-y-2">
            <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
              💸 RAIO-X DAS DESPESAS
            </p>

            <!-- Maior Vilão destacado em ROSA/VERMELHO -->
            <div v-if="inteligencia.maior_vilao" class="bg-secondary/10 border border-secondary/30 p-3 flex items-center gap-3">
              <span class="material-symbols-outlined text-secondary text-xl">warning</span>
              <div>
                <p class="font-label text-[9px] font-bold tracking-widest text-secondary uppercase">MAIOR VILÃO DO MÊS</p>
                <p class="font-headline font-bold text-sm text-on-surface">
                  {{ inteligencia.maior_vilao.categoria_nome }} — <span class="text-secondary font-black">{{ formatarReais(inteligencia.maior_vilao.total) }}</span>
                  <span class="text-[9px] text-on-surface-variant font-normal opacity-80"> ({{ inteligencia.maior_vilao.percentual.toFixed(0) }}% dos gastos)</span>
                </p>
              </div>
            </div>

            <!-- Ticket médio de despesas -->
            <div class="bg-surface-container p-3 flex items-center gap-3">
              <span class="material-symbols-outlined text-on-surface-variant text-base">confirmation_number</span>
              <div>
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">TICKET MÉDIO DE DESPESA</p>
                <p class="font-headline font-bold text-sm text-secondary">{{ formatarReais(inteligencia.ticket_medio_despesa) }}</p>
              </div>
            </div>

            <!-- Barras de Despesas -->
            <div class="bg-surface-container p-3 space-y-2.5">
              <div v-for="cat in inteligencia.despesas_por_categoria" :key="cat.categoria_nome"
                class="flex items-center gap-2">
                <span class="w-20 font-label text-[9px] font-bold tracking-wider text-on-surface uppercase truncate">
                  {{ cat.categoria_nome }}
                </span>
                <div class="flex-1 h-5 bg-surface-container-high relative overflow-hidden">
                  <div class="h-full bg-secondary/80 transition-all duration-500"
                    :style="{ width: barPercent(cat.total, maxBarWidth(inteligencia!.despesas_por_categoria)) + '%' }" />
                </div>
                <span class="font-headline font-bold text-[10px] text-secondary w-20 text-right">
                  {{ formatarReais(cat.total) }}
                </span>
              </div>
            </div>
          </div>

          <!-- ── 4. RANKING DE MELHORES DIAS DE GANHO (VERDE) ────────────────── -->
          <div v-if="inteligencia && inteligencia.ranking_dias_ganho.length" class="space-y-2">
            <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
              🏆 RANKING — MELHORES DIAS DE GANHO
            </p>
            <div class="bg-surface-container p-3 space-y-2.5">
              <div v-for="(dia, idx) in inteligencia.ranking_dias_ganho" :key="dia.dia_semana"
                class="flex items-center gap-2">
                <span class="w-5 text-center font-label text-[9px] font-bold text-on-surface-variant">
                  {{ idx === 0 ? '🥇' : idx === inteligencia.ranking_dias_ganho.length - 1 ? '💸' : `${idx + 1}°` }}
                </span>
                <span class="w-16 font-label text-[9px] font-bold tracking-wider text-on-surface uppercase">
                  {{ diaSemanaCompleto(dia.dia_semana) }}
                </span>
                <div class="flex-1 h-5 bg-surface-container-high relative overflow-hidden">
                  <div class="h-full transition-all duration-500"
                    :class="idx === 0 ? 'bg-primary-container' : 'bg-primary-container/40'"
                    :style="{ width: barPercent(dia.total, maxBarWidth(inteligencia!.ranking_dias_ganho)) + '%' }" />
                </div>
                <span class="font-headline font-bold text-[10px] text-primary-container w-20 text-right">
                  {{ formatarReais(dia.total) }}
                </span>
              </div>
            </div>
          </div>

          <!-- ── 5. EFICIÊNCIA DO COMBUSTÍVEL (CIANO PARA TELEMETRIA + ROSA FINANCEIRO) ── -->
          <div v-if="inteligencia" class="space-y-2">
            <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
              ⛽ EFICIÊNCIA DO COMBUSTÍVEL
            </p>
            <div class="grid grid-cols-2 gap-2">
              <!-- KM/L (Ciano Telemetria) -->
              <div class="bg-surface-container p-3 border-l-2 border-cyan-500">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-0.5">KM/LITRO</p>
                <p class="font-headline font-bold text-lg text-cyan-600 dark:text-cyan-400">
                  {{ inteligencia.eficiencia_combustivel.dados_suficientes && inteligencia.eficiencia_combustivel.km_por_litro
                    ? inteligencia.eficiencia_combustivel.km_por_litro
                    : '—' }}
                </p>
                <p class="font-label text-[9px] text-on-surface-variant">
                  {{ inteligencia.eficiencia_combustivel.dados_suficientes ? 'km por litro' : 'dados insuficientes' }}
                </p>
              </div>
              <!-- CUSTO/KM (Rosa/Vermelho Financeiro) -->
              <div class="bg-surface-container p-3 border-l-2 border-secondary">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-0.5">CUSTO/KM</p>
                <p class="font-headline font-bold text-lg text-secondary">
                  {{ inteligencia.eficiencia_combustivel.dados_suficientes && inteligencia.eficiencia_combustivel.custo_por_km
                    ? `R$ ${inteligencia.eficiencia_combustivel.custo_por_km.toFixed(2)}`
                    : '—' }}
                </p>
                <p class="font-label text-[9px] text-on-surface-variant">
                  {{ inteligencia.eficiencia_combustivel.dados_suficientes ? 'por km rodado' : 'dados insuficientes' }}
                </p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <!-- LITROS NO MÊS (Ciano Telemetria) -->
              <div class="bg-surface-container p-3">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-0.5">LITROS NO MÊS</p>
                <p class="font-headline font-bold text-sm text-cyan-600 dark:text-cyan-400">{{ inteligencia.eficiencia_combustivel.total_litros.toFixed(1) }} L</p>
              </div>
              <!-- GASTO TOTAL (Rosa Financeiro) -->
              <div class="bg-surface-container p-3">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-0.5">GASTO TOTAL</p>
                <p class="font-headline font-bold text-sm text-secondary">{{ formatarReais(inteligencia.eficiencia_combustivel.total_gasto_combustivel) }}</p>
              </div>
            </div>
          </div>

          <!-- ── 6. RESUMO EXECUTIVO (INSIGHTS AUTOMÁTICOS DA IA - ROXO) ─────────── -->
          <div v-if="inteligencia && inteligencia.insights.length" class="space-y-2">
            <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
              📈 RESUMO EXECUTIVO DO MOTOBOM
            </p>
            <div class="bg-surface-container p-3 space-y-2 border border-purple-500/20">
              <div v-for="(insight, idx) in inteligencia.insights" :key="idx"
                class="flex items-start gap-2 py-1">
                <span class="material-symbols-outlined text-purple-400 text-sm mt-0.5">lightbulb</span>
                <p class="font-label text-xs text-on-surface leading-snug">{{ insight }}</p>
              </div>
            </div>
          </div>

          <!-- ── 7. HISTÓRICO COMPLETO DO ODÔMETRO (KM LOGS - CIANO) ─────────── -->
          <div v-if="historicoKm" class="bg-surface-container p-3">
            <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-3">
              EXTRATO DO ODÔMETRO · {{ historicoKm.registros.length }} registro{{ historicoKm.registros.length !== 1 ? 's' : '' }}
            </p>
            <div v-if="!historicoKm.registros.length" class="text-center py-6 text-on-surface-variant">
              <span class="material-symbols-outlined text-3xl opacity-30">speed</span>
              <p class="font-label text-xs tracking-widest uppercase mt-2">Nenhum registro de KM</p>
            </div>
            <div v-else class="max-h-80 overflow-y-auto pr-1 space-y-1">
              <ul class="space-y-1">
                <li v-for="r in historicoKm.registros" :key="r.id"
                  class="flex items-center justify-between py-2 px-1 scannable-row">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 flex items-center justify-center flex-shrink-0 bg-cyan-500/10">
                      <span class="material-symbols-outlined text-base text-cyan-500 dark:text-cyan-400">speed</span>
                    </div>
                    <div>
                      <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
                        {{ formatarDataCriacao(r.data_criacao) }}
                        <span class="opacity-60">· {{ origemLabel(r.origem) }}</span>
                      </p>
                      <p class="font-headline font-bold text-sm text-on-surface">
                        {{ r.km.toLocaleString('pt-BR') }} km
                      </p>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <span v-if="r.variacao !== null"
                      class="font-label text-[9px] font-bold"
                      :class="r.variacao >= 0 ? 'text-cyan-600 dark:text-cyan-400' : 'text-secondary'">
                      {{ r.variacao >= 0 ? '+' : '' }}{{ r.variacao.toLocaleString('pt-BR') }}
                    </span>
                    <button @click="removerRegistroKm(r.id)"
                      class="w-7 h-7 flex items-center justify-center text-on-surface-variant hover:text-secondary transition-colors">
                      <span class="material-symbols-outlined text-sm">delete</span>
                    </button>
                  </div>
                </li>
              </ul>
            </div>
          </div>

        </template>

      </template>

    </main>

    <!-- Modal de Edição de Lançamento -->
    <EditarLancamentoModal
      :visivel="modalEdicaoVisivel"
      :lancamento="lancamentoParaEditar"
      @fechar="modalEdicaoVisivel = false"
      @salvo="carregarTransacoes"
    />
  </div>
  </AppLayout>
</template>

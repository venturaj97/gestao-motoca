<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { listarLancamentos } from '@/api/lancamentos'
import type { LancamentoResposta, TipoLancamento } from '@/types'
import AppDateInput from '@/components/AppDateInput.vue'

const router   = useRouter()
const route    = useRoute()

// ── Estado ─────────────────────────────────────────────────────
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
const filtroValorMin = ref('')
const filtroValorMax = ref('')
type ModoPeriodo = 'HOJE' | 'SEMANA' | 'MES' | 'PERSONALIZADO'
const modoPeriodo = ref<ModoPeriodo>('HOJE')

// ── Computed ────────────────────────────────────────────────────
const lancamentosFiltrados = computed(() => lancamentos.value)

const tipoFiltroApi = computed(() =>
  filtroTipo.value === 'TODOS' ? undefined : filtroTipo.value
)

const totalGanhos = computed(() =>
  lancamentos.value
    .filter(l => l.tipo === 'GANHO')
    .reduce((acc, l) => acc + parseFloat(l.valor), 0)
)

const totalDespesas = computed(() =>
  lancamentos.value
    .filter(l => l.tipo === 'DESPESA')
    .reduce((acc, l) => acc + parseFloat(l.valor), 0)
)

const faixaPeriodo = computed(() => {
  if (!dataInicio.value || !dataFim.value) return ''
  const inicio = formatarIsoParaBr(dataInicio.value)
  const fim = formatarIsoParaBr(dataFim.value)
  return inicio === fim ? inicio : `${inicio} até ${fim}`
})

const filtrosAtivos = computed(() => {
  const chips: Array<{ chave: 'categoria' | 'min' | 'max'; texto: string }> = []
  if (filtroCategoriaNome.value.trim()) {
    chips.push({ chave: 'categoria', texto: `Categoria: ${filtroCategoriaNome.value.trim()}` })
  }
  if (filtroValorMin.value.trim()) {
    chips.push({ chave: 'min', texto: `Min: R$ ${filtroValorMin.value.trim()}` })
  }
  if (filtroValorMax.value.trim()) {
    chips.push({ chave: 'max', texto: `Max: R$ ${filtroValorMax.value.trim()}` })
  }
  return chips
})

function paraNumeroFiltro(valor: string): number | undefined {
  const txt = valor.trim()
  if (!txt) return undefined
  const n = Number(txt.replace(',', '.'))
  if (Number.isNaN(n) || n < 0) return undefined
  return n
}

// ── Carregar ────────────────────────────────────────────────────
async function carregar(pagina = paginaAtual.value) {
  carregando.value = true
  erro.value = ''
  try {
    const resposta = await listarLancamentos({
      tipo: tipoFiltroApi.value,
      data_inicio: dataInicio.value || undefined,
      data_fim: dataFim.value || undefined,
      categoria_nome: filtroCategoriaNome.value.trim() || undefined,
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

// ── Formatações ─────────────────────────────────────────────────
function formatarReais(valor: string | number): string {
  const n = typeof valor === 'string' ? parseFloat(valor) : valor
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
    carregar(1)
    return
  }
  if (modo === 'SEMANA') {
    dataInicio.value = formatarDataIso(obterInicioSemanaAtual())
    dataFim.value = formatarDataIso(obterFimSemanaAtual())
    carregar(1)
    return
  }
  dataInicio.value = formatarDataIso(obterInicioMesAtual())
  dataFim.value = formatarDataIso(obterFimMesAtual())
  carregar(1)
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
  carregar(1)
}

function mudarTipoFiltro(tipo: TipoLancamento | 'TODOS') {
  filtroTipo.value = tipo
  carregar(1)
}

function aplicarFiltrosAvancados() {
  const min = paraNumeroFiltro(filtroValorMin.value)
  const max = paraNumeroFiltro(filtroValorMax.value)
  if (min !== undefined && max !== undefined && min > max) {
    erro.value = 'Valor mínimo não pode ser maior que o valor máximo.'
    return
  }
  carregar(1)
}

function limparFiltrosAvancados() {
  filtroCategoriaNome.value = ''
  filtroValorMin.value = ''
  filtroValorMax.value = ''
  carregar(1)
}

function removerFiltro(chave: 'categoria' | 'min' | 'max') {
  if (chave === 'categoria') filtroCategoriaNome.value = ''
  if (chave === 'min') filtroValorMin.value = ''
  if (chave === 'max') filtroValorMax.value = ''
  carregar(1)
}

function paginaAnterior() {
  if (paginaAtual.value <= 1) return
  carregar(paginaAtual.value - 1)
}

function proximaPagina() {
  if (paginaAtual.value >= totalPaginas.value) return
  carregar(paginaAtual.value + 1)
}

function formatarDiaSemana(ds: string | null): string {
  if (!ds) return ''
  const map: Record<string, string> = {
    'MONDAY': 'SEG', 'TUESDAY': 'TER', 'WEDNESDAY': 'QUA',
    'THURSDAY': 'QUI', 'FRIDAY': 'SEX', 'SATURDAY': 'SAB', 'SUNDAY': 'DOM'
  }
  return map[ds] ?? ds.slice(0, 3)
}

const navItems = [
  { name: 'dashboard',  label: 'Início',    icon: 'dashboard'  },
  { name: 'historico',  label: 'Histórico', icon: 'history'    },
  { name: 'lancar',     label: 'Lançar',    icon: 'add_box'    },
  { name: 'manutencao', label: 'Manutenção',icon: 'build'      },
  { name: 'configuracoes', label: 'Config', icon: 'settings' },
]
function isActive(name: string) { return route.name === name }
function navIconStyle(name: string) {
  return isActive(name) ? { fontVariationSettings: '"FILL" 1' } : {}
}

onMounted(() => {
  aplicarPeriodoRapido('HOJE')
})
</script>

<template>
  <div class="bg-background text-on-surface font-body min-h-screen pb-24">

    <!-- TopBar -->
    <header class="bg-background flex justify-between items-center w-full px-5 h-16 sticky top-0 z-50 border-l-4 border-primary-container">
      <div class="flex items-center gap-3">
        <h1 class="text-primary-container font-headline font-black text-lg tracking-tight uppercase">GESTÃO MOTOCA</h1>
      </div>
      <button class="text-on-surface-variant hover:text-primary-container transition-colors"
        :class="{ 'animate-spin': carregando }"
        @click="carregar()">
        <span class="material-symbols-outlined text-xl">refresh</span>
      </button>
    </header>

    <main class="px-5 py-5 space-y-5 max-w-md mx-auto">

      <!-- Título -->
      <div>
        <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">HISTÓRICO DETALHADO</p>
        <h2 class="font-headline font-extrabold text-4xl tracking-tighter uppercase leading-none">HISTÓRICO</h2>
        <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mt-1">
          {{ faixaPeriodo }}
        </p>
      </div>

      <!-- Resumo rápido -->
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-surface-container p-3 border-l-2 border-primary-container">
          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-0.5">GANHOS</p>
          <p class="font-headline font-bold text-base text-primary-container">{{ formatarReais(totalGanhos) }}</p>
        </div>
        <div class="bg-surface-container p-3 border-l-2 border-secondary">
          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-0.5">DESPESAS</p>
          <p class="font-headline font-bold text-base text-secondary">{{ formatarReais(totalDespesas) }}</p>
        </div>
      </div>

      <!-- Filtro de período -->
      <div class="space-y-3 bg-surface-container p-3">
        <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
          PERÍODO DO HISTÓRICO
        </p>
        <div class="grid grid-cols-3 gap-2">
          <button
            class="py-2 font-label text-[9px] font-bold tracking-widest uppercase border"
            :class="modoPeriodo === 'HOJE'
              ? 'bg-primary-container text-on-primary-fixed border-primary-container'
              : 'bg-surface-container-high text-on-surface-variant border-outline-variant'"
            @click="aplicarPeriodoRapido('HOJE')"
          >
            HOJE
          </button>
          <button
            class="py-2 font-label text-[9px] font-bold tracking-widest uppercase border"
            :class="modoPeriodo === 'SEMANA'
              ? 'bg-primary-container text-on-primary-fixed border-primary-container'
              : 'bg-surface-container-high text-on-surface-variant border-outline-variant'"
            @click="aplicarPeriodoRapido('SEMANA')"
          >
            SEMANA
          </button>
          <button
            class="py-2 font-label text-[9px] font-bold tracking-widest uppercase border"
            :class="modoPeriodo === 'MES'
              ? 'bg-primary-container text-on-primary-fixed border-primary-container'
              : 'bg-surface-container-high text-on-surface-variant border-outline-variant'"
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
          class="w-full py-2 bg-surface-container-high border border-outline-variant text-on-surface font-label text-[9px] font-bold tracking-widest uppercase hover:bg-surface-bright transition-colors"
          @click="aplicarPeriodoPersonalizado"
        >
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

      <!-- Filtros -->
      <div
        v-if="mostrarFiltros"
        class="space-y-2 bg-surface-container p-3 border border-outline-variant"
      >
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

      <!-- Lista de lançamentos -->
      <ul v-else class="space-y-1">
        <li v-for="l in lancamentosFiltrados" :key="l.id"
          class="scannable-row flex items-center justify-between py-3 px-1">
          <div class="flex items-center gap-3">
            <!-- Ícone indicador -->
            <div class="w-8 h-8 flex items-center justify-center flex-shrink-0"
              :class="l.tipo === 'GANHO' ? 'bg-primary-container/10' : 'bg-secondary/10'">
              <span class="material-symbols-outlined text-base"
                :class="l.tipo === 'GANHO' ? 'text-primary-container' : 'text-secondary'">
                {{ l.tipo === 'GANHO' ? 'arrow_upward' : 'arrow_downward' }}
              </span>
            </div>
            <div>
              <!-- Data + dia semana -->
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
                {{ formatarData(l.data_lancamento) }}
                <span v-if="l.dia_semana" class="opacity-60">· {{ formatarDiaSemana(l.dia_semana) }}</span>
                <span v-if="l.periodo" class="opacity-60">· {{ l.periodo }}</span>
              </p>
              <p v-if="l.categoria_nome" class="font-label text-[9px] text-on-surface-variant uppercase opacity-80">
                {{ l.categoria_nome }}
              </p>
              <!-- Infos adicionais -->
              <p v-if="l.km_corrida" class="font-label text-[9px] text-on-surface-variant">
                {{ parseFloat(l.km_corrida).toFixed(1) }} km
                <span v-if="l.minutos_corrida">· {{ l.minutos_corrida }}min</span>
              </p>
            </div>
          </div>

          <!-- Valor -->
          <p class="font-headline font-bold text-sm"
            :class="l.tipo === 'GANHO' ? 'text-primary-container' : 'text-secondary'">
            {{ l.tipo === 'GANHO' ? '+' : '-' }}{{ formatarReais(l.valor) }}
          </p>
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

    </main>

    <!-- Bottom Nav -->
    <nav class="fixed bottom-0 left-0 w-full z-50 h-20 bg-background border-t-4 border-surface-container grid grid-cols-5">
      <button v-for="item in navItems" :key="item.name"
        class="flex flex-col items-center justify-center h-full w-full transition-colors duration-100"
        :class="isActive(item.name)
          ? 'bg-primary-container text-on-primary-fixed'
          : 'text-on-surface-variant hover:bg-surface-container'"
        @click="router.push({ name: item.name })">
        <span class="material-symbols-outlined" :style="navIconStyle(item.name)">{{ item.icon }}</span>
        <span class="font-label text-[9px] font-bold uppercase tracking-[0.08em] mt-0.5">{{ item.label }}</span>
      </button>
    </nav>
  </div>
</template>

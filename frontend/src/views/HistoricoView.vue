<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { listarLancamentos } from '@/api/lancamentos'
import type { LancamentoResposta, TipoLancamento } from '@/types'

const router   = useRouter()
const route    = useRoute()

// ── Estado ─────────────────────────────────────────────────────
const lancamentos  = ref<LancamentoResposta[]>([])
const carregando   = ref(false)
const erro         = ref('')
const filtroTipo   = ref<TipoLancamento | 'TODOS'>('TODOS')
const dataInicio   = ref('')
const dataFim      = ref('')

// ── Computed ────────────────────────────────────────────────────
const lancamentosFiltrados = computed(() => {
  if (filtroTipo.value === 'TODOS') return lancamentos.value
  return lancamentos.value.filter(l => l.tipo === filtroTipo.value)
})

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

// ── Carregar ────────────────────────────────────────────────────
async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    lancamentos.value = await listarLancamentos({
      data_inicio: dataInicio.value || undefined,
      data_fim: dataFim.value || undefined,
    })
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
  { name: 'moto',       label: 'Moto',      icon: 'motorcycle' },
]
function isActive(name: string) { return route.name === name }
function navIconStyle(name: string) {
  return isActive(name) ? { fontVariationSettings: '"FILL" 1' } : {}
}

onMounted(carregar)
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
        @click="carregar">
        <span class="material-symbols-outlined text-xl">refresh</span>
      </button>
    </header>

    <main class="px-5 py-5 space-y-5 max-w-md mx-auto">

      <!-- Título -->
      <div>
        <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">MONITOR TÁTICO</p>
        <h2 class="font-headline font-extrabold text-4xl tracking-tighter uppercase leading-none">HISTÓRICO</h2>
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
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block font-label text-[9px] font-bold tracking-[0.2em] text-on-surface-variant mb-1 uppercase">DE</label>
          <input v-model="dataInicio" type="date"
            class="tactical-input py-2 text-sm"
            @change="carregar" />
        </div>
        <div>
          <label class="block font-label text-[9px] font-bold tracking-[0.2em] text-on-surface-variant mb-1 uppercase">ATÉ</label>
          <input v-model="dataFim" type="date"
            class="tactical-input py-2 text-sm"
            @change="carregar" />
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
          @click="filtroTipo = t as any">
          {{ t === 'TODOS' ? 'TODOS' : t === 'GANHO' ? 'GANHOS' : 'DESPESAS' }}
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
        {{ lancamentosFiltrados.length }} registro{{ lancamentosFiltrados.length > 1 ? 's' : '' }}
      </p>

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

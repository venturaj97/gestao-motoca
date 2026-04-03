<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { useMotoStore } from '@/stores/moto'
import { criarLancamento } from '@/api/lancamentos'
import { listarCategorias } from '@/api/categorias'
import type { CategoriaResposta, TipoLancamento, PeriodoLancamento } from '@/types'

const router    = useRouter()
const route     = useRoute()
const motoStore = useMotoStore()

// Tipo inicial via query param (?tipo=GANHO ou ?tipo=DESPESA)
const tipoInicial = (route.query.tipo as TipoLancamento) || 'GANHO'

// ── Estado ─────────────────────────────────────────────────────
const tipo          = ref<TipoLancamento>(tipoInicial)
const categoriaId   = ref<number | null>(null)
const valor         = ref('')
const descricao     = ref('')
const periodo       = ref<PeriodoLancamento | ''>('')
const minutosCorrida = ref('')
const kmCorrida     = ref('')
const dataLancamento = ref(new Date().toISOString().slice(0, 10))

const categorias    = ref<CategoriaResposta[]>([])
const carregando    = ref(false)
const enviando      = ref(false)
const erro          = ref('')
const sucesso       = ref(false)

// ── Computed ────────────────────────────────────────────────────
const categoriasFiltradas = computed(() =>
  categorias.value.filter(c => c.ativo && c.tipo === tipo.value)
)

const ehCorrida = computed(() =>
  periodo.value === 'CORRIDA'
)

const motoId = computed(() => motoStore.motoAtiva?.id)

// ── Carregar categorias ─────────────────────────────────────────
async function carregar() {
  carregando.value = true
  try {
    categorias.value = await listarCategorias()
  } catch {
    erro.value = 'Erro ao carregar categorias.'
  } finally {
    carregando.value = false
  }
}

// ── Submissão ───────────────────────────────────────────────────
async function handleSubmit() {
  erro.value = ''

  const valorNum = parseFloat(valor.value.replace(',', '.'))
  if (!valor.value || isNaN(valorNum) || valorNum <= 0) {
    erro.value = 'Informe um valor válido.'
    return
  }
  if (!categoriaId.value) {
    erro.value = 'Selecione uma categoria.'
    return
  }

  enviando.value = true
  try {
    await criarLancamento({
      tipo: tipo.value,
      categoria_id: categoriaId.value,
      valor: valorNum,
      descricao: descricao.value || undefined,
      periodo: periodo.value || undefined,
      minutos_corrida: ehCorrida.value && minutosCorrida.value
        ? parseInt(minutosCorrida.value) : undefined,
      km_corrida: ehCorrida.value && kmCorrida.value
        ? parseFloat(kmCorrida.value) : undefined,
      data_lancamento: dataLancamento.value || undefined,
      moto_usuario_id: motoId.value,
    })
    sucesso.value = true
    setTimeout(() => router.push({ name: 'dashboard' }), 1200)
  } catch {
    erro.value = 'Erro ao registrar lançamento. Tente novamente.'
  } finally {
    enviando.value = false
  }
}

function formatarInput(e: Event) {
  const input = e.target as HTMLInputElement
  // Permite apenas números e vírgula/ponto
  input.value = input.value.replace(/[^0-9.,]/g, '')
  valor.value = input.value
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
    <header class="bg-background flex justify-between items-center w-full px-5 h-16 sticky top-0 z-50 border-l-4"
      :class="tipo === 'GANHO' ? 'border-primary-container' : 'border-secondary'">
      <div class="flex items-center gap-3">
        <button class="text-on-surface-variant hover:text-on-surface transition-colors p-1"
          @click="router.push({ name: 'dashboard' })">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <h1 class="font-headline font-black text-lg tracking-tight uppercase"
          :class="tipo === 'GANHO' ? 'text-primary-container' : 'text-secondary'">
          GESTÃO MOTOCA
        </h1>
      </div>
      <span class="font-label text-[10px] tracking-widest text-on-surface-variant uppercase">
        LANÇAMENTO
      </span>
    </header>

    <main class="px-5 py-6 space-y-6 max-w-md mx-auto">

      <!-- Título + toggle de tipo -->
      <div class="space-y-4">
        <div>
          <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">
            REGISTRAR
          </p>
          <h2 class="font-headline font-extrabold text-4xl tracking-tighter uppercase leading-none"
            :class="tipo === 'GANHO' ? 'text-on-surface' : 'text-secondary'">
            {{ tipo === 'GANHO' ? 'GANHO' : 'DESPESA' }}
          </h2>
        </div>

        <!-- Toggle GANHO / DESPESA -->
        <div class="grid grid-cols-2 gap-2">
          <button
            class="h-12 font-label font-black text-[11px] tracking-widest uppercase transition-all border-b-2"
            :class="tipo === 'GANHO'
              ? 'bg-primary-container text-on-primary-fixed border-primary-container'
              : 'bg-surface-container text-on-surface-variant border-transparent hover:border-primary-container'"
            @click="tipo = 'GANHO'; categoriaId = null; periodo = ''"
          >
            <span class="material-symbols-outlined text-sm align-middle mr-1">add_circle</span>
            GANHO
          </button>
          <button
            class="h-12 font-label font-black text-[11px] tracking-widest uppercase transition-all border-b-2"
            :class="tipo === 'DESPESA'
              ? 'bg-secondary text-on-secondary border-secondary'
              : 'bg-surface-container text-on-surface-variant border-transparent hover:border-secondary'"
            @click="tipo = 'DESPESA'; categoriaId = null; periodo = ''"
          >
            <span class="material-symbols-outlined text-sm align-middle mr-1">remove_circle</span>
            DESPESA
          </button>
        </div>
      </div>

      <!-- Formulário -->
      <form class="space-y-5" @submit.prevent="handleSubmit">

        <!-- Valor -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            VALOR (R$)
          </label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 font-headline font-bold text-on-surface-variant">R$</span>
            <input
              :value="valor"
              inputmode="decimal"
              placeholder="0,00"
              class="tactical-input pl-10 py-4 text-2xl font-bold"
              @input="formatarInput"
            />
          </div>
        </div>

        <!-- Categoria -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            CATEGORIA
          </label>
          <div v-if="carregando" class="h-12 bg-surface-container-low animate-pulse" />
          <div v-else class="grid grid-cols-2 gap-2">
            <button
              v-for="cat in categoriasFiltradas"
              :key="cat.id"
              type="button"
              class="h-11 px-3 font-label text-[10px] font-bold tracking-wider uppercase transition-all text-left border-l-2"
              :class="categoriaId === cat.id
                ? tipo === 'GANHO'
                  ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                  : 'bg-secondary text-on-secondary border-secondary'
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline'"
              @click="categoriaId = cat.id"
            >
              {{ cat.nome }}
            </button>
            <div v-if="categoriasFiltradas.length === 0"
              class="col-span-2 text-center font-label text-xs text-on-surface-variant py-4">
              Nenhuma categoria cadastrada para {{ tipo === 'GANHO' ? 'ganhos' : 'despesas' }}.
            </div>
          </div>
        </div>

        <!-- Período (apenas para GANHO) -->
        <div v-if="tipo === 'GANHO'">
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            PERÍODO <span class="font-normal text-outline">(opcional)</span>
          </label>
          <div class="grid grid-cols-3 gap-2">
            <button v-for="p in ['DIARIO', 'SEMANAL', 'CORRIDA']" :key="p"
              type="button"
              class="h-10 font-label text-[10px] font-bold tracking-wider uppercase transition-all border-b-2"
              :class="periodo === p
                ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-primary-container'"
              @click="periodo = (periodo === p ? '' : p as PeriodoLancamento)"
            >
              {{ p === 'DIARIO' ? 'DIÁRIO' : p === 'SEMANAL' ? 'SEMANAL' : 'CORRIDA' }}
            </button>
          </div>
        </div>

        <!-- Campos de corrida -->
        <div v-if="ehCorrida" class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              MINUTOS
            </label>
            <input v-model="minutosCorrida" type="number" min="0"
              placeholder="Ex: 45"
              class="tactical-input py-3 text-lg" />
          </div>
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              KM CORRIDA
            </label>
            <input v-model="kmCorrida" type="number" min="0" step="0.1"
              placeholder="Ex: 8.5"
              class="tactical-input py-3 text-lg" />
          </div>
        </div>

        <!-- Descrição -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            DESCRIÇÃO <span class="font-normal text-outline">(opcional)</span>
          </label>
          <input v-model="descricao" type="text"
            placeholder="Ex: Corrida aeroporto"
            class="tactical-input py-3" />
        </div>

        <!-- Data -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            DATA
          </label>
          <input v-model="dataLancamento" type="date"
            class="tactical-input py-3 text-base" />
        </div>

        <!-- Erro -->
        <div v-if="erro"
          class="flex items-start gap-3 bg-error-container text-on-error-container text-sm font-label px-4 py-3 border-l-4 border-error">
          <span class="material-symbols-outlined text-base mt-0.5 flex-shrink-0">error</span>
          {{ erro }}
        </div>

        <!-- Sucesso -->
        <div v-if="sucesso"
          class="flex items-center gap-3 bg-primary-container/20 text-primary-container text-sm font-label px-4 py-3 border-l-4 border-primary-container">
          <span class="material-symbols-outlined text-base flex-shrink-0">check_circle</span>
          Lançamento registrado! Redirecionando…
        </div>

        <!-- Botão -->
        <button type="submit" :disabled="enviando || sucesso"
          class="btn-primary h-16 text-base disabled:opacity-40 disabled:cursor-not-allowed"
          :class="tipo === 'DESPESA' ? 'bg-secondary text-on-secondary hover:brightness-110' : ''">
          <span v-if="enviando" class="material-symbols-outlined animate-spin">refresh</span>
          <template v-else>
            <span class="material-symbols-outlined">
              {{ tipo === 'GANHO' ? 'add_circle' : 'remove_circle' }}
            </span>
            REGISTRAR {{ tipo === 'GANHO' ? 'GANHO' : 'DESPESA' }}
          </template>
        </button>

      </form>
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

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { useMotoStore } from '@/stores/moto'
import { criarLancamentosLote } from '@/api/lancamentos'
import { listarCategorias } from '@/api/categorias'
import type { CategoriaResposta, TipoLancamento, PeriodoLancamento, GrupoDespesa } from '@/types'

const router    = useRouter()
const route     = useRoute()
const motoStore = useMotoStore()

// Tipo inicial via query param (?tipo=GANHO ou ?tipo=DESPESA)
const tipoInicial = (route.query.tipo as TipoLancamento) || 'GANHO'

// ── Estado ─────────────────────────────────────────────────────
const tipo          = ref<TipoLancamento>(tipoInicial)
const categoriasSelecionadas = ref<number[]>([])
const valoresPorCategoria = ref<Record<number, string>>({})
const descricao     = ref('')
const periodo       = ref<PeriodoLancamento>('DIARIO')
const minutosCorrida = ref('')
const kmCorrida     = ref('')
const dataLancamento = ref(new Date().toISOString().slice(0, 10))
const mostrarDescricao = ref(false)
const grupoDespesaAtivo = ref<GrupoDespesa>('GERAL')

const hoje = new Date().toISOString().slice(0, 10)
const ontem = new Date(Date.now() - 86400000).toISOString().slice(0, 10)

const categorias    = ref<CategoriaResposta[]>([])
const carregando    = ref(false)
const enviando      = ref(false)
const erro          = ref('')
const sucesso       = ref(false)

// ── Computed ────────────────────────────────────────────────────
const categoriasFiltradas = computed(() =>
  categorias.value.filter(c => c.ativo && c.tipo === tipo.value)
)

const categoriasSelecionadasDetalhes = computed(() =>
  categoriasFiltradas.value.filter(c => categoriasSelecionadas.value.includes(c.id))
)

const totalSelecionado = computed(() =>
  categoriasSelecionadasDetalhes.value.reduce((acc, cat) => {
    const valor = parseFloat((valoresPorCategoria.value[cat.id] || '').replace(',', '.'))
    return acc + (isNaN(valor) ? 0 : valor)
  }, 0)
)

const categoriasDespesaPorGrupo = computed(() => {
  const todas = categoriasFiltradas.value.filter((c) => c.tipo === 'DESPESA')
  const abastecimento = todas.filter((c) => c.grupo_despesa === 'ABASTECIMENTO')
  const manutencao = todas.filter((c) => c.grupo_despesa === 'MANUTENCAO')
  const imposto = todas.filter((c) => c.grupo_despesa === 'IMPOSTO')
  const geral = todas.filter((c) => c.grupo_despesa === 'GERAL' || c.grupo_despesa === null)

  return {
    ABASTECIMENTO: abastecimento,
    MANUTENCAO: manutencao,
    IMPOSTO: imposto,
    GERAL: geral,
  } as Record<GrupoDespesa, CategoriaResposta[]>
})

const categoriasVisiveis = computed(() => {
  if (tipo.value === 'GANHO') return categoriasFiltradas.value.filter((c) => c.tipo === 'GANHO')
  return categoriasDespesaPorGrupo.value[grupoDespesaAtivo.value]
})

const ehCorrida = computed(() =>
  periodo.value === 'CORRIDA'
)

const corridaPermitida = computed(() =>
  tipo.value === 'GANHO' && categoriasSelecionadas.value.length === 1
)

const motoId = computed(() => motoStore.motoAtiva?.id)

watch([tipo, categoriasSelecionadas], () => {
  if (tipo.value === 'GANHO' && periodo.value === 'CORRIDA' && !corridaPermitida.value) {
    periodo.value = 'DIARIO'
  }
})

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

function resetarSelecaoCategorias() {
  categoriasSelecionadas.value = []
  valoresPorCategoria.value = {}
}

function alterarTipo(novoTipo: TipoLancamento) {
  tipo.value = novoTipo
  periodo.value = 'DIARIO'
  erro.value = ''
  sucesso.value = false
  if (novoTipo === 'DESPESA') grupoDespesaAtivo.value = 'GERAL'
  resetarSelecaoCategorias()
}

function alternarCategoria(catId: number) {
  const idx = categoriasSelecionadas.value.indexOf(catId)
  if (idx >= 0) {
    categoriasSelecionadas.value.splice(idx, 1)
    delete valoresPorCategoria.value[catId]
    return
  }
  categoriasSelecionadas.value.push(catId)
  if (!valoresPorCategoria.value[catId]) valoresPorCategoria.value[catId] = ''
}

function formatarValorCategoriaInput(catId: number, e: Event) {
  const input = e.target as HTMLInputElement
  input.value = input.value.replace(/[^0-9.,]/g, '')
  valoresPorCategoria.value[catId] = input.value
}

// ── Submissão ───────────────────────────────────────────────────
async function handleSubmit() {
  erro.value = ''
  sucesso.value = false

  if (categoriasSelecionadas.value.length === 0) {
    erro.value = 'Selecione pelo menos uma categoria.'
    return
  }

  // Validação de Período (apenas para Ganho)
  if (tipo.value === 'GANHO' && !periodo.value) {
    erro.value = 'Selecione o período do ganho.'
    return
  }
  if (tipo.value === 'GANHO' && periodo.value === 'CORRIDA' && !corridaPermitida.value) {
    erro.value = 'Para lançamento por corrida, selecione apenas uma categoria.'
    return
  }

  // Validação de Data (Obrigatória)
  if (!dataLancamento.value) {
    erro.value = 'A data do lançamento é obrigatória.'
    return
  }

  const categoriasComValor = categoriasSelecionadas.value.map((catId) => {
    const bruto = valoresPorCategoria.value[catId] || ''
    const valorNum = parseFloat(bruto.replace(',', '.'))
    return { catId, valorNum }
  })

  const semValor = categoriasComValor.find((item) => isNaN(item.valorNum) || item.valorNum <= 0)
  if (semValor) {
    const cat = categoriasFiltradas.value.find((c) => c.id === semValor.catId)
    erro.value = `Informe um valor válido para ${cat?.nome ?? 'a categoria selecionada'}.`
    return
  }

  enviando.value = true
  try {
    await criarLancamentosLote(
      categoriasComValor.map((item) => ({
        tipo: tipo.value,
        categoria_id: item.catId,
        valor: item.valorNum,
        descricao: mostrarDescricao.value ? (descricao.value || undefined) : undefined,
        periodo: tipo.value === 'GANHO' ? periodo.value : undefined,
        minutos_corrida: ehCorrida.value && minutosCorrida.value
          ? parseInt(minutosCorrida.value) : undefined,
        km_corrida: ehCorrida.value && kmCorrida.value
          ? parseFloat(kmCorrida.value) : undefined,
        data_lancamento: dataLancamento.value,
        moto_usuario_id: motoId.value,
      }))
    )
    sucesso.value = true
    limparFormularioAposSucesso()
    setTimeout(() => {
      sucesso.value = false
    }, 1800)
  } catch {
    erro.value = 'Erro ao registrar lançamento. Tente novamente.'
  } finally {
    enviando.value = false
  }
}

function limparFormularioAposSucesso() {
  resetarSelecaoCategorias()
  descricao.value = ''
  mostrarDescricao.value = false
  minutosCorrida.value = ''
  kmCorrida.value = ''
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
            @click="alterarTipo('GANHO')"
          >
            <span class="material-symbols-outlined text-sm align-middle mr-1">add_circle</span>
            GANHO
          </button>
          <button
            class="h-12 font-label font-black text-[11px] tracking-widest uppercase transition-all border-b-2"
            :class="tipo === 'DESPESA'
              ? 'bg-secondary text-on-secondary border-secondary'
              : 'bg-surface-container text-on-surface-variant border-transparent hover:border-secondary'"
            @click="alterarTipo('DESPESA')"
          >
            <span class="material-symbols-outlined text-sm align-middle mr-1">remove_circle</span>
            DESPESA
          </button>
        </div>
      </div>

      <!-- Formulário -->
      <form class="space-y-5" @submit.prevent="handleSubmit">

        <!-- Categoria -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            CATEGORIAS
          </label>
          <div v-if="carregando" class="h-12 bg-surface-container-low animate-pulse" />
          <div v-else class="space-y-3">
            <div v-if="tipo === 'DESPESA'" class="grid grid-cols-2 gap-2">
              <button
                type="button"
                class="h-9 font-label text-[9px] font-bold tracking-[0.12em] uppercase transition-all border-b-2"
                :class="grupoDespesaAtivo === 'GERAL'
                  ? 'bg-surface-bright text-on-surface border-secondary'
                  : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
                @click="grupoDespesaAtivo = 'GERAL'"
              >
                DIA A DIA
              </button>
              <button
                type="button"
                class="h-9 font-label text-[9px] font-bold tracking-[0.12em] uppercase transition-all border-b-2"
                :class="grupoDespesaAtivo === 'ABASTECIMENTO'
                  ? 'bg-surface-bright text-on-surface border-secondary'
                  : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
                @click="grupoDespesaAtivo = 'ABASTECIMENTO'"
              >
                ABASTECER
              </button>
              <button
                type="button"
                class="h-9 font-label text-[9px] font-bold tracking-[0.12em] uppercase transition-all border-b-2"
                :class="grupoDespesaAtivo === 'MANUTENCAO'
                  ? 'bg-surface-bright text-on-surface border-secondary'
                  : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
                @click="grupoDespesaAtivo = 'MANUTENCAO'"
              >
                MANUTENÇÃO
              </button>
              <button
                type="button"
                class="h-9 font-label text-[9px] font-bold tracking-[0.12em] uppercase transition-all border-b-2"
                :class="grupoDespesaAtivo === 'IMPOSTO'
                  ? 'bg-surface-bright text-on-surface border-secondary'
                  : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
                @click="grupoDespesaAtivo = 'IMPOSTO'"
              >
                IMPOSTO
              </button>
            </div>

            <div v-if="tipo === 'DESPESA'" class="pt-1 border-t border-outline-variant/40">
              <p class="font-label text-[9px] font-bold tracking-[0.14em] uppercase text-on-surface-variant pt-2">
                Categorias do grupo selecionado
              </p>
            </div>

            <div class="space-y-2">
            <button
              v-for="cat in categoriasVisiveis"
              :key="cat.id"
              type="button"
              class="w-full h-11 px-3 font-label text-[10px] font-bold tracking-wider uppercase transition-all text-left border-b-2 flex items-center justify-between gap-2"
              :class="categoriasSelecionadas.includes(cat.id)
                ? tipo === 'GANHO'
                  ? 'bg-primary-container/15 text-primary-container border-primary-container'
                  : 'bg-secondary/15 text-secondary border-secondary'
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline'"
              @click="alternarCategoria(cat.id)"
            >
              <div class="flex items-center gap-2 min-w-0">
                <span class="material-symbols-outlined text-sm">
                  {{ categoriasSelecionadas.includes(cat.id) ? 'check_box' : 'check_box_outline_blank' }}
                </span>
                <span class="truncate">{{ cat.nome }}</span>
              </div>
              <span class="font-label text-[9px] tracking-widest">
                {{ categoriasSelecionadas.includes(cat.id) ? 'OK' : '' }}
              </span>
            </button>
            </div>
            <div v-if="categoriasVisiveis.length === 0"
              class="col-span-2 text-center font-label text-xs text-on-surface-variant py-4">
              Nenhuma categoria neste grupo.
            </div>

            <div v-if="categoriasSelecionadasDetalhes.length > 0" class="space-y-2 pt-1">
              <p class="font-label text-[9px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
                VALOR POR CATEGORIA
              </p>
              <div
                v-for="cat in categoriasSelecionadasDetalhes"
                :key="cat.id"
                class="bg-surface-container-low p-3 border-l-2"
                :class="tipo === 'GANHO' ? 'border-primary-container' : 'border-secondary'"
              >
                <div class="flex items-center justify-between gap-3">
                  <p class="font-label text-[10px] font-bold tracking-wider uppercase text-on-surface truncate">
                    {{ cat.nome }}
                  </p>
                  <div class="relative w-32">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-xs">R$</span>
                    <input
                      :value="valoresPorCategoria[cat.id] || ''"
                      inputmode="decimal"
                      placeholder="0,00"
                      class="tactical-input pl-8 py-2 text-sm font-bold"
                      :class="tipo === 'DESPESA' ? 'focus:!border-secondary' : 'focus:!border-primary-container'"
                      @input="formatarValorCategoriaInput(cat.id, $event)"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div v-if="categoriasSelecionadasDetalhes.length > 0" class="bg-surface-container p-3 flex items-center justify-between">
              <p class="font-label text-[10px] font-bold tracking-[0.12em] uppercase text-on-surface-variant">
                Total selecionado
              </p>
              <p class="font-headline font-bold text-lg"
                :class="tipo === 'GANHO' ? 'text-primary-container' : 'text-secondary'">
                {{ totalSelecionado.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Período -->
        <div v-if="tipo === 'GANHO'">
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            PERÍODO
          </label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="p in ['DIARIO', 'CORRIDA']"
              :key="p"
              type="button"
              :disabled="p === 'CORRIDA' && !corridaPermitida"
              class="h-10 font-label text-[10px] font-bold tracking-wider uppercase transition-all border-b-2 disabled:opacity-40 disabled:cursor-not-allowed"
              :class="periodo === p
                ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-primary-container'"
              @click="periodo = p as PeriodoLancamento"
            >
              {{ p === 'DIARIO' ? 'DIÁRIO' : 'CORRIDA' }}
            </button>
          </div>
          <p v-if="!corridaPermitida" class="font-label text-[9px] text-on-surface-variant mt-2">
            Corrida fica disponível apenas com 1 categoria selecionada.
          </p>
        </div>

        <!-- Campos de corrida -->
        <div v-if="ehCorrida" class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              MINUTOS
            </label>
            <input v-model="minutosCorrida" type="number" min="0"
              placeholder="Ex: 45"
              class="tactical-input py-3 text-lg focus:!border-primary-container" />
          </div>
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              KM CORRIDA
            </label>
            <input v-model="kmCorrida" type="number" min="0" step="0.1"
              placeholder="Ex: 8.5"
              class="tactical-input py-3 text-lg focus:!border-primary-container" />
          </div>
        </div>

        <!-- Botão Abrir Descrição / Campo de Descrição -->
        <div class="space-y-2">
          <div v-if="!mostrarDescricao">
            <button
              type="button"
              class="flex items-center gap-2 font-label text-[10px] font-bold tracking-widest text-on-surface-variant uppercase transition-colors"
              :class="tipo === 'DESPESA' ? 'hover:text-secondary' : 'hover:text-primary-container'"
              @click="mostrarDescricao = true"
            >
              <span class="material-symbols-outlined text-lg">add</span>
              CRIAR DESCRIÇÃO
            </button>
          </div>
          <div v-else>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              DESCRIÇÃO
            </label>
            <div class="relative">
              <input v-model="descricao" type="text"
                placeholder="Ex: Corrida aeroporto"
                class="tactical-input py-3 pr-10"
                :class="tipo === 'DESPESA' ? 'focus:!border-secondary' : 'focus:!border-primary-container'"
              />
              <button
                type="button"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-error transition-colors"
                @click="mostrarDescricao = false; descricao = ''"
              >
                <span class="material-symbols-outlined text-lg">close</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Data -->
        <div class="space-y-3">
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            DATA DO LANÇAMENTO
          </label>
          
          <!-- Seleção Rápida -->
          <div class="grid grid-cols-2 gap-2">
            <button 
              type="button"
              class="h-10 font-label text-[10px] font-bold tracking-widest uppercase transition-all border-b-2"
              :class="dataLancamento === hoje 
                ? (tipo === 'DESPESA'
                  ? 'bg-secondary text-on-secondary border-secondary'
                  : 'bg-primary-container text-on-primary-fixed border-primary-container') 
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
              @click="dataLancamento = hoje"
            >
              HOJE
            </button>
            <button 
              type="button"
              class="h-10 font-label text-[10px] font-bold tracking-widest uppercase transition-all border-b-2"
              :class="dataLancamento === ontem 
                ? (tipo === 'DESPESA'
                  ? 'bg-secondary text-on-secondary border-secondary'
                  : 'bg-primary-container text-on-primary-fixed border-primary-container') 
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
              @click="dataLancamento = ontem"
            >
              ONTEM
            </button>
          </div>

          <!-- Input Customizado com Ícone -->
          <div class="relative group">
            <div
              class="absolute left-4 top-1/2 -translate-y-1/2 flex items-center pointer-events-none text-on-surface-variant transition-colors"
              :class="tipo === 'DESPESA' ? 'group-focus-within:text-secondary' : 'group-focus-within:text-primary-container'"
            >
              <span class="material-symbols-outlined text-lg">calendar_month</span>
            </div>
            <input 
              v-model="dataLancamento" 
              type="date"
              class="tactical-input pl-12 py-4 text-lg font-bold tracking-tight uppercase"
              :class="tipo === 'DESPESA' ? 'focus:!border-secondary' : 'focus:!border-primary-container'"
            />
          </div>
        </div>

        <!-- Erro -->
        <div v-if="erro"
          class="flex items-start gap-3 bg-error-container text-on-error-container text-sm font-label px-4 py-3 border-l-4 border-error">
          <span class="material-symbols-outlined text-base mt-0.5 flex-shrink-0">error</span>
          {{ erro }}
        </div>

        <!-- Sucesso -->
        <div
          v-if="sucesso"
          class="flex items-center gap-3 text-sm font-label px-4 py-3 border-l-4"
          :class="tipo === 'DESPESA'
            ? 'bg-secondary/15 text-secondary border-secondary'
            : 'bg-primary-container/20 text-primary-container border-primary-container'"
        >
          <span class="material-symbols-outlined text-base flex-shrink-0">check_circle</span>
          Lançamentos registrados! Pode lançar outros.
        </div>

        <!-- Botão -->
        <button type="submit" :disabled="enviando"
          class="btn-primary h-16 text-base disabled:opacity-40 disabled:cursor-not-allowed"
          :class="tipo === 'DESPESA' ? 'bg-secondary text-on-secondary hover:brightness-110' : ''">
          <span v-if="enviando" class="material-symbols-outlined animate-spin">refresh</span>
          <template v-else>
            <span class="material-symbols-outlined">
              {{ tipo === 'GANHO' ? 'add_circle' : 'remove_circle' }}
            </span>
            REGISTRAR {{ tipo === 'GANHO' ? 'GANHOS' : 'DESPESAS' }}
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

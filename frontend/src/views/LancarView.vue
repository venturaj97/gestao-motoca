<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { useMotoStore } from '@/stores/moto'
import { criarLancamentosLote } from '@/api/lancamentos'
import { criarAbastecimento } from '@/api/abastecimentos'
import { listarCategorias } from '@/api/categorias'
import type { CategoriaResposta, TipoLancamento, PeriodoLancamento, GrupoDespesa } from '@/types'
import LancarDateInput from '@/components/LancarDateInput.vue'
import AppLayout from '@/components/AppLayout.vue'

const router    = useRouter()
const route     = useRoute()
const motoStore = useMotoStore()

const tipoInicial = (route.query.tipo as TipoLancamento) || 'GANHO'

// ── Estado ─────────────────────────────────────────────────────
const tipo              = ref<TipoLancamento>(tipoInicial)
const periodo           = ref<PeriodoLancamento>('DIARIO')
const descricao         = ref('')
const mostrarDescricao = ref(false)

// Data local (sem bug de timezone UTC)
function hojeLocal(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
const hoje = hojeLocal()
const dOntem = new Date(); dOntem.setDate(dOntem.getDate() - 1)
const ontem = `${dOntem.getFullYear()}-${String(dOntem.getMonth() + 1).padStart(2, '0')}-${String(dOntem.getDate()).padStart(2, '0')}`
const dataLancamento = ref(hoje)

// Estado para lançamento simples (valor único)
const valorUnico        = ref('')
const categoriaUnicaId = ref<number | null>(null)
const litros            = ref('')

// Estado para modo detalhado (múltiplas categorias / corridas)
const categoriasSelecionadas = ref<number[]>([])
const valoresPorCategoria    = ref<Record<number, string>>({})
const minutosCorrida         = ref('')
const kmCorrida              = ref('')
const grupoDespesaAtivo      = ref<GrupoDespesa>('GERAL')

const categorias  = ref<CategoriaResposta[]>([])
const carregando  = ref(false)
const enviando    = ref(false)
const erro        = ref('')
const sucesso     = ref(false)
const mensagemSucesso = ref('')

const MAX_VALOR_CENTAVOS = 99_999_999
const MAX_DIGITOS_VALOR  = String(MAX_VALOR_CENTAVOS).length

// ── Computed ────────────────────────────────────────────────────
const categoriasFiltradas = computed(() =>
  categorias.value.filter(c => c.ativo && c.tipo === tipo.value)
)

const categoriasDespesaPorGrupo = computed(() => {
  const todas = categoriasFiltradas.value.filter(c => c.tipo === 'DESPESA')
  return {
    ABASTECIMENTO: todas.filter(c => c.grupo_despesa === 'ABASTECIMENTO'),
    MANUTENCAO:    todas.filter(c => c.grupo_despesa === 'MANUTENCAO'),
    IMPOSTO:       todas.filter(c => c.grupo_despesa === 'IMPOSTO'),
    GERAL:         todas.filter(c => c.grupo_despesa === 'GERAL' || c.grupo_despesa === null),
  } as Record<GrupoDespesa, CategoriaResposta[]>
})

const categoriasVisiveis = computed(() => {
  if (tipo.value === 'GANHO') return categoriasFiltradas.value
  return categoriasDespesaPorGrupo.value[grupoDespesaAtivo.value]
})

const categoriasSelecionadasDetalhes = computed(() =>
  categoriasFiltradas.value.filter(c => categoriasSelecionadas.value.includes(c.id))
)

const totalSelecionado = computed(() =>
  categoriasSelecionadasDetalhes.value.reduce((acc, cat) =>
    acc + valorTextoParaNumero(valoresPorCategoria.value[cat.id] || ''), 0)
)

const ehSimples   = computed(() => periodo.value === 'DIARIO')
const motoId      = computed(() => motoStore.motoAtiva?.id)

const ehCombustivel = computed(() => {
  if (tipo.value !== 'DESPESA' || !categoriaUnicaId.value) return false
  const cat = categoriasFiltradas.value.find(c => c.id === categoriaUnicaId.value)
  if (!cat) return false
  const nome = cat.nome.toLowerCase()
  return cat.grupo_despesa === 'ABASTECIMENTO' || nome.includes('combustivel') || nome.includes('combustível') || nome.includes('gasolina')
})

const valorUnicoNumero = computed(() => textoParaCentavos(valorUnico.value) / 100)

function selecionarCategoriaPadrao() {
  const lista = categoriasFiltradas.value
  if (lista.length === 0) {
    categoriaUnicaId.value = null
    return
  }
  if (tipo.value === 'GANHO') {
    const salvo = localStorage.getItem('ultima_categoria_ganho_id')
    if (salvo) {
      const idSalvo = parseInt(salvo, 10)
      if (lista.some(c => c.id === idSalvo)) {
        categoriaUnicaId.value = idSalvo
        return
      }
    }
  }
  categoriaUnicaId.value = lista[0]?.id ?? null
}

watch(categoriasFiltradas, () => {
  selecionarCategoriaPadrao()
}, { immediate: true })

watch(tipo, () => {
  periodo.value = 'DIARIO'
  litros.value = ''
  selecionarCategoriaPadrao()
})

// ── Carregar ────────────────────────────────────────────────────
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

// ── Helpers de formatação ───────────────────────────────────────
function textoParaCentavos(valor: string): number {
  const digits = valor.replace(/\D/g, '').slice(0, MAX_DIGITOS_VALOR)
  if (!digits) return 0
  const n = parseInt(digits, 10)
  return isNaN(n) || n <= 0 ? 0 : Math.min(n, MAX_VALOR_CENTAVOS)
}
function centavosParaTexto(c: number): string {
  return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(c / 100)
}
function valorTextoParaNumero(v: string) { return textoParaCentavos(v) / 100 }

function formatarValorUnicoInput(e: Event) {
  const c = textoParaCentavos((e.target as HTMLInputElement).value)
  valorUnico.value = c > 0 ? centavosParaTexto(c) : ''
}
function handlePasteValorUnico(e: ClipboardEvent) {
  const c = textoParaCentavos(e.clipboardData?.getData('text') ?? '')
  valorUnico.value = c > 0 ? centavosParaTexto(c) : ''
}
function formatarValorCategoriaInput(catId: number, e: Event) {
  const c = textoParaCentavos((e.target as HTMLInputElement).value)
  valoresPorCategoria.value[catId] = c > 0 ? centavosParaTexto(c) : ''
}
function handlePasteValorCategoria(catId: number, e: ClipboardEvent) {
  const c = textoParaCentavos(e.clipboardData?.getData('text') ?? '')
  valoresPorCategoria.value[catId] = c > 0 ? centavosParaTexto(c) : ''
}

function alterarTipo(novoTipo: TipoLancamento) {
  tipo.value = novoTipo
  periodo.value = 'DIARIO'
  erro.value = ''
  sucesso.value = false
  litros.value = ''
  if (novoTipo === 'DESPESA') grupoDespesaAtivo.value = 'GERAL'
  categoriasSelecionadas.value = []
  valoresPorCategoria.value = {}
}

function alternarCategoria(catId: number) {
  const idx = categoriasSelecionadas.value.indexOf(catId)
  if (idx >= 0) {
    categoriasSelecionadas.value.splice(idx, 1)
    delete valoresPorCategoria.value[catId]
  } else {
    categoriasSelecionadas.value.push(catId)
    valoresPorCategoria.value[catId] = ''
  }
}

// ── Submissão ───────────────────────────────────────────────────
async function handleSubmit() {
  erro.value = ''
  sucesso.value = false

  if (ehSimples.value) {
    if (valorUnicoNumero.value <= 0) { erro.value = 'Informe o valor do lançamento.'; return }
    if (tipo.value === 'DESPESA' && !categoriaUnicaId.value) {
      erro.value = 'Selecione uma categoria para a despesa.'
      return
    }
    if (ehCombustivel.value) {
      const litrosNum = parseFloat(litros.value)
      if (isNaN(litrosNum) || litrosNum <= 0) {
        erro.value = 'Informe a quantidade de litros abastecidos.'
        return
      }
    }
    if (!dataLancamento.value) { erro.value = 'A data do lançamento é obrigatória.'; return }
    await enviarSimples()
    return
  }

  // DETALHADO (CORRIDA)
  if (categoriasSelecionadas.value.length === 0) { erro.value = 'Selecione pelo menos uma categoria.'; return }
  if (!dataLancamento.value) { erro.value = 'A data do lançamento é obrigatória.'; return }
  const itens = categoriasSelecionadas.value.map(catId => ({
    catId, valorNum: valorTextoParaNumero(valoresPorCategoria.value[catId] || '')
  }))
  const semValor = itens.find(i => i.valorNum <= 0)
  if (semValor) {
    const cat = categoriasFiltradas.value.find(c => c.id === semValor.catId)
    erro.value = `Informe um valor para ${cat?.nome ?? 'a categoria'}.`
    return
  }

  enviando.value = true
  try {
    const retorno = await criarLancamentosLote(itens.map((i, idx) => ({
      tipo: tipo.value,
      categoria_id: i.catId,
      valor: i.valorNum,
      descricao: mostrarDescricao.value ? (descricao.value || undefined) : undefined,
      periodo: 'CORRIDA',
      minutos_corrida: idx === 0 && minutosCorrida.value ? parseInt(minutosCorrida.value) : undefined,
      km_corrida: idx === 0 && kmCorrida.value ? parseFloat(kmCorrida.value) : undefined,
      data_lancamento: dataLancamento.value,
      moto_usuario_id: motoId.value,
    })))
    await motoStore.carregarMotos()
    mostrarSucesso(retorno.quantidade, Number(retorno.total_valor))
    categoriasSelecionadas.value = []
    valoresPorCategoria.value = {}
    minutosCorrida.value = ''
    kmCorrida.value = ''
    mostrarDescricao.value = false
    descricao.value = ''
  } catch {
    erro.value = 'Erro ao registrar lançamento. Tente novamente.'
  } finally {
    enviando.value = false
  }
}

async function enviarSimples() {
  if (!categoriaUnicaId.value) return
  enviando.value = true
  try {
    const litrosNum = parseFloat(litros.value)
    if (tipo.value === 'DESPESA' && ehCombustivel.value && !isNaN(litrosNum) && litrosNum > 0) {
      await criarAbastecimento({
        categoria_id: categoriaUnicaId.value,
        valor_total: valorUnicoNumero.value,
        litros: litrosNum,
        data_abastecimento: dataLancamento.value,
        descricao: mostrarDescricao.value ? (descricao.value || undefined) : undefined,
        moto_usuario_id: motoId.value,
      })
      mostrarSucesso(1, valorUnicoNumero.value)
    } else {
      const retorno = await criarLancamentosLote([{
        tipo: tipo.value,
        categoria_id: categoriaUnicaId.value,
        valor: valorUnicoNumero.value,
        descricao: mostrarDescricao.value ? (descricao.value || undefined) : undefined,
        periodo: tipo.value === 'GANHO' ? 'DIARIO' : undefined,
        data_lancamento: dataLancamento.value,
        moto_usuario_id: motoId.value,
      }])
      if (tipo.value === 'GANHO' && categoriaUnicaId.value) {
        localStorage.setItem('ultima_categoria_ganho_id', String(categoriaUnicaId.value))
      }
      mostrarSucesso(retorno.quantidade, Number(retorno.total_valor))
    }
    await motoStore.carregarMotos()
    valorUnico.value = ''
    litros.value = ''
    mostrarDescricao.value = false
    descricao.value = ''
  } catch {
    erro.value = 'Erro ao registrar lançamento. Tente novamente.'
  } finally {
    enviando.value = false
  }
}

function mostrarSucesso(quantidade: number, total: number) {
  mensagemSucesso.value = `${quantidade} lançamento(s) • ${total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`
  sucesso.value = true
  setTimeout(() => { sucesso.value = false }, 2500)
}


onMounted(carregar)
</script>

<template>
  <AppLayout>
  <div class="bg-background text-on-surface font-body min-h-screen">

    <!-- Back button topbar override for mobile: show back button -->
    <div class="px-5 py-4 lg:hidden">
      <button
        class="flex items-center gap-1 text-on-surface-variant hover:text-on-surface transition-colors text-sm font-bold"
        @click="router.push({ name: 'dashboard' })"
      >
        <span class="material-symbols-outlined text-base">arrow_back</span>
        VOLTAR
      </button>
    </div>

    <main class="px-5 py-2 lg:py-6 space-y-6 max-w-2xl mx-auto pb-28 lg:pb-8">

      <!-- Toggle GANHO / DESPESA -->
      <div class="space-y-4">
        <div>
          <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">REGISTRAR</p>
          <h2
            class="font-headline font-extrabold text-4xl tracking-tighter uppercase leading-none"
            :class="tipo === 'GANHO' ? 'text-on-surface' : 'text-secondary'"
          >
            {{ tipo === 'GANHO' ? 'GANHO' : 'DESPESA' }}
          </h2>
        </div>
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

      <form id="form-lancamento" class="space-y-5" @submit.prevent="handleSubmit">

        <!-- Modos de Lançamento (Ganho: Rápido x Detalhado) -->
        <div v-if="tipo === 'GANHO'">
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            MODO DE LANÇAMENTO
          </label>
          <div class="grid grid-cols-2 gap-2">
            <button
              type="button"
              class="h-10 font-label text-[10px] font-bold tracking-wider uppercase transition-all border-b-2"
              :class="periodo === 'DIARIO'
                ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
              @click="periodo = 'DIARIO'"
            >RÁPIDO</button>
            <button
              type="button"
              class="h-10 font-label text-[10px] font-bold tracking-wider uppercase transition-all border-b-2"
              :class="periodo === 'CORRIDA'
                ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-primary-container'"
              @click="periodo = 'CORRIDA'"
            >DETALHADO</button>
          </div>
        </div>

        <!-- ── MODO RÁPIDO SIMPLES ────────────── -->
        <template v-if="ehSimples">

          <!-- Valor total -->
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              VALOR DO LANÇAMENTO
            </label>
            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-sm font-bold">R$</span>
              <input
                :value="valorUnico"
                inputmode="numeric"
                placeholder="0,00"
                maxlength="11"
                class="tactical-input pl-10 py-4 text-2xl font-headline font-black w-full"
                :class="tipo === 'DESPESA' ? 'focus:!border-secondary' : 'focus:!border-primary-container'"
                @input="formatarValorUnicoInput"
                @paste.prevent="handlePasteValorUnico"
              />
            </div>
          </div>

          <!-- Data do Lançamento -->
          <div class="space-y-3">
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
              DATA DO LANÇAMENTO
            </label>
            <div class="grid grid-cols-2 gap-2">
              <button
                type="button"
                class="h-10 font-label text-[10px] font-bold tracking-widest uppercase transition-all border-b-2"
                :class="dataLancamento === hoje
                  ? (tipo === 'DESPESA' ? 'bg-secondary text-on-secondary border-secondary' : 'bg-primary-container text-on-primary-fixed border-primary-container')
                  : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
                @click="dataLancamento = hoje"
              >HOJE</button>
              <button
                type="button"
                class="h-10 font-label text-[10px] font-bold tracking-widest uppercase transition-all border-b-2"
                :class="dataLancamento === ontem
                  ? (tipo === 'DESPESA' ? 'bg-secondary text-on-secondary border-secondary' : 'bg-primary-container text-on-primary-fixed border-primary-container')
                  : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
                @click="dataLancamento = ontem"
              >ONTEM</button>
            </div>
            <LancarDateInput v-model="dataLancamento" :tone="tipo === 'DESPESA' ? 'despesa' : 'ganho'" />
          </div>

          <!-- Categoria -->
          <div v-if="!carregando && categoriasFiltradas.length > 0">
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              CATEGORIA
              <span v-if="tipo === 'GANHO'" class="font-normal normal-case tracking-normal text-[9px] ml-1 opacity-60">(opcional)</span>
              <span v-else class="font-normal text-secondary text-[9px] ml-1">*obrigatório</span>
            </label>
            <select
              v-model="categoriaUnicaId"
              class="tactical-input w-full py-3 text-sm font-bold bg-surface-container"
              :class="tipo === 'DESPESA' ? 'focus:!border-secondary' : 'focus:!border-primary-container'"
            >
              <option v-if="tipo === 'DESPESA'" :value="null" disabled>Selecione uma categoria...</option>
              <option v-for="cat in categoriasFiltradas" :key="cat.id" :value="cat.id">
                {{ cat.nome }}
              </option>
            </select>
          </div>

          <!-- Campo Litros (apenas para Combustível / Abastecimento em DESPESA) -->
          <div v-if="ehCombustivel">
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              LITROS <span class="font-normal text-secondary text-[9px] ml-1">*obrigatório</span>
            </label>
            <div class="relative">
              <input
                v-model="litros"
                type="number"
                step="0.01"
                min="0"
                placeholder="Ex: 5.50"
                class="tactical-input w-full py-3 px-4 text-base font-bold bg-surface-container focus:!border-secondary"
              />
              <span class="absolute right-4 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-xs font-bold">L</span>
            </div>
          </div>

        </template>

        <!-- ── MODO DETALHADO (GANHO apenas) ─────────────── -->
        <template v-else>

          <!-- Categorias multi-select -->
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              CATEGORIAS
            </label>
            <div v-if="carregando" class="h-12 bg-surface-container-low animate-pulse" />
            <div v-else class="space-y-3">
              <div class="space-y-2">
                <button
                  v-for="cat in categoriasVisiveis"
                  :key="cat.id"
                  type="button"
                  class="w-full h-11 px-3 font-label text-[10px] font-bold tracking-wider uppercase transition-all text-left border-b-2 flex items-center justify-between gap-2"
                  :class="categoriasSelecionadas.includes(cat.id)
                    ? 'bg-primary-container/15 text-primary-container border-primary-container'
                    : 'bg-surface-container-high text-on-surface-variant border-transparent hover:border-outline'"
                  @click="alternarCategoria(cat.id)"
                >
                  <div class="flex items-center gap-2 min-w-0">
                    <span class="material-symbols-outlined text-sm">
                      {{ categoriasSelecionadas.includes(cat.id) ? 'check_box' : 'check_box_outline_blank' }}
                    </span>
                    <span class="truncate">{{ cat.nome }}</span>
                  </div>
                </button>
              </div>

              <!-- Valores por categoria -->
              <div v-if="categoriasSelecionadasDetalhes.length > 0" class="space-y-2 pt-1">
                <p class="font-label text-[9px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
                  VALOR POR CATEGORIA
                </p>
                <div
                  v-for="cat in categoriasSelecionadasDetalhes"
                  :key="cat.id"
                  class="bg-surface-container-low p-3 border-l-2 border-primary-container"
                >
                  <div class="flex items-center justify-between gap-3">
                    <p class="font-label text-[10px] font-bold tracking-wider uppercase text-on-surface truncate">
                      {{ cat.nome }}
                    </p>
                    <div class="relative w-32">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-xs">R$</span>
                      <input
                        :value="valoresPorCategoria[cat.id] || ''"
                        inputmode="numeric"
                        placeholder="0,00"
                        maxlength="10"
                        class="tactical-input pl-8 py-2 text-sm font-bold focus:!border-primary-container"
                        @input="formatarValorCategoriaInput(cat.id, $event)"
                        @paste.prevent="handlePasteValorCategoria(cat.id, $event)"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div
                v-if="categoriasSelecionadasDetalhes.length > 0"
                class="bg-surface-container p-3 flex items-center justify-between"
              >
                <p class="font-label text-[10px] font-bold tracking-[0.12em] uppercase text-on-surface-variant">Total</p>
                <p class="font-headline font-bold text-lg text-primary-container">
                  {{ totalSelecionado.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}
                </p>
              </div>
            </div>
          </div>

          <!-- Campos de corrida (minutos / km) -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">MINUTOS</label>
              <input v-model="minutosCorrida" type="number" min="0" placeholder="Ex: 45"
                class="tactical-input py-3 text-lg focus:!border-primary-container" />
            </div>
            <div>
              <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">KM</label>
              <input v-model="kmCorrida" type="number" min="0" step="0.1" placeholder="Ex: 8.5"
                class="tactical-input py-3 text-lg focus:!border-primary-container" />
            </div>
          </div>

          <!-- Data -->
          <div class="space-y-3">
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
              DATA DO LANÇAMENTO
            </label>
            <div class="grid grid-cols-2 gap-2">
              <button type="button"
                class="h-10 font-label text-[10px] font-bold tracking-widest uppercase transition-all border-b-2"
                :class="dataLancamento === hoje
                  ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                  : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
                @click="dataLancamento = hoje"
              >HOJE</button>
              <button type="button"
                class="h-10 font-label text-[10px] font-bold tracking-widest uppercase transition-all border-b-2"
                :class="dataLancamento === ontem
                  ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                  : 'bg-surface-container text-on-surface-variant border-transparent hover:border-outline-variant'"
                @click="dataLancamento = ontem"
              >ONTEM</button>
            </div>
            <LancarDateInput v-model="dataLancamento" tone="ganho" />
          </div>

        </template>

        <!-- Descrição (opcional) -->
        <div class="space-y-2">
          <div v-if="!mostrarDescricao">
            <button
              type="button"
              class="flex items-center gap-2 font-label text-[10px] font-bold tracking-widest text-on-surface-variant uppercase transition-colors"
              :class="tipo === 'DESPESA' ? 'hover:text-secondary' : 'hover:text-primary-container'"
              @click="mostrarDescricao = true"
            >
              <span class="material-symbols-outlined text-lg">add</span>
              ADICIONAR DESCRIÇÃO
            </button>
          </div>
          <div v-else>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">DESCRIÇÃO</label>
            <div class="relative">
              <input v-model="descricao" type="text" placeholder="Ex: Corrida extra, diária iFood"
                class="tactical-input py-3 pr-10"
                :class="tipo === 'DESPESA' ? 'focus:!border-secondary' : 'focus:!border-primary-container'"
              />
              <button type="button"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-error"
                @click="mostrarDescricao = false; descricao = ''"
              >
                <span class="material-symbols-outlined text-lg">close</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Erro -->
        <div v-if="erro"
          class="flex items-start gap-3 bg-error-container text-on-error-container text-sm font-label px-4 py-3 border-l-4 border-error"
        >
          <span class="material-symbols-outlined text-base mt-0.5 flex-shrink-0">error</span>
          {{ erro }}
        </div>

        <!-- Sucesso -->
        <div v-if="sucesso"
          class="flex items-center gap-3 text-sm font-label px-4 py-3 border-l-4"
          :class="tipo === 'DESPESA'
            ? 'bg-secondary/15 text-secondary border-secondary'
            : 'bg-primary-container/20 text-primary-container border-primary-container'"
        >
          <span class="material-symbols-outlined text-base flex-shrink-0">check_circle</span>
          {{ mensagemSucesso }}
        </div>
        <!-- Botão de registrar -->
        <div class="pt-2">
          <button
            type="submit"
            :disabled="enviando"
            class="btn-primary h-14 text-base w-full disabled:opacity-40 disabled:cursor-not-allowed shadow-lg"
            :class="tipo === 'DESPESA' ? 'bg-secondary text-on-secondary hover:brightness-110' : ''"
          >
            <span v-if="enviando" class="material-symbols-outlined animate-spin">refresh</span>
            <template v-else>
              <span class="material-symbols-outlined">{{ tipo === 'GANHO' ? 'add_circle' : 'remove_circle' }}</span>
              REGISTRAR {{ tipo === 'GANHO' ? 'GANHO' : 'DESPESA' }}
            </template>
          </button>
        </div>

      </form>
    </main>

  </div>
  </AppLayout>
</template>

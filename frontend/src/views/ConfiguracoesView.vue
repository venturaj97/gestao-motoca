<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMotoStore } from '@/stores/moto'
import { atualizarMoto } from '@/api/motos'
import { listarCategorias, criarCategoria, atualizarCategoria, excluirCategoria } from '@/api/categorias'
import { listarLancamentos, atualizarLancamento, excluirLancamento } from '@/api/lancamentos'
import type {
  CategoriaResposta,
  GrupoDespesa,
  LancamentoCriar,
  LancamentoResposta,
  MotoUsuarioAtualizar,
  PeriodoLancamento,
  TipoLancamento,
} from '@/types'
import AppDateInput from '@/components/AppDateInput.vue'

const router = useRouter()
const route = useRoute()
const motoStore = useMotoStore()

type AbaConfig = 'MOTO' | 'CATEGORIAS' | 'LANCAMENTOS'
const abaAtiva = ref<AbaConfig>('MOTO')

const navItems = [
  { name: 'dashboard', label: 'Início', icon: 'dashboard' },
  { name: 'historico', label: 'Histórico', icon: 'history' },
  { name: 'lancar', label: 'Lançar', icon: 'add_box' },
  { name: 'manutencao', label: 'Manutenção', icon: 'build' },
  { name: 'configuracoes', label: 'Config', icon: 'settings' },
]

function isActive(name: string) { return route.name === name }
function navIconStyle(name: string) {
  return isActive(name) ? { fontVariationSettings: '"FILL" 1' } : {}
}

const moto = computed(() => motoStore.motoAtiva)

const editandoMoto = ref(false)
const enviandoMoto = ref(false)
const erroMoto = ref('')
const sucessoMoto = ref('')
const kmAtual = ref('')
const cor = ref('')

function iniciarEdicaoMoto() {
  if (!moto.value) return
  kmAtual.value = moto.value.km_atual?.toString() ?? ''
  cor.value = moto.value.cor ?? ''
  editandoMoto.value = true
  erroMoto.value = ''
}

function cancelarEdicaoMoto() {
  editandoMoto.value = false
  erroMoto.value = ''
}

async function salvarMoto() {
  if (!moto.value) return
  erroMoto.value = ''
  sucessoMoto.value = ''

  const km = kmAtual.value ? parseInt(kmAtual.value, 10) : undefined
  if (kmAtual.value && (isNaN(km!) || km! < 0)) {
    erroMoto.value = 'KM inválido.'
    return
  }

  enviandoMoto.value = true
  try {
    const payload: MotoUsuarioAtualizar = {}
    if (km !== undefined) payload.km_atual = km
    if (cor.value.trim()) payload.cor = cor.value.trim()

    const atualizada = await atualizarMoto(moto.value.id, payload)
    const idx = motoStore.motos.findIndex(m => m.id === atualizada.id)
    if (idx >= 0) motoStore.motos[idx] = atualizada
    sucessoMoto.value = 'Moto atualizada com sucesso.'
    editandoMoto.value = false
  } catch {
    erroMoto.value = 'Não foi possível salvar os dados da moto.'
  } finally {
    enviandoMoto.value = false
  }
}

const categorias = ref<CategoriaResposta[]>([])
const carregandoCategorias = ref(false)
const enviandoCategoria = ref(false)
const erroCategoria = ref('')
const sucessoCategoria = ref('')

const novaCategoriaNome = ref('')
const novaCategoriaTipo = ref<TipoLancamento>('DESPESA')
const novaCategoriaGrupo = ref<GrupoDespesa>('GERAL')

const editCategoriaId = ref<number | null>(null)
const editCategoriaNome = ref('')
const editCategoriaGrupo = ref<GrupoDespesa>('GERAL')

const gruposDespesa: GrupoDespesa[] = ['GERAL', 'MANUTENCAO', 'ABASTECIMENTO', 'IMPOSTO']

const categoriasGanhos = computed(() => categorias.value.filter(c => c.tipo === 'GANHO'))
const categoriasDespesas = computed(() => categorias.value.filter(c => c.tipo === 'DESPESA'))

async function carregarCategorias() {
  carregandoCategorias.value = true
  erroCategoria.value = ''
  try {
    categorias.value = await listarCategorias()
  } catch {
    erroCategoria.value = 'Erro ao carregar categorias.'
  } finally {
    carregandoCategorias.value = false
  }
}

async function criarNovaCategoria() {
  if (!novaCategoriaNome.value.trim()) {
    erroCategoria.value = 'Informe o nome da categoria.'
    return
  }
  enviandoCategoria.value = true
  erroCategoria.value = ''
  sucessoCategoria.value = ''
  try {
    await criarCategoria({
      nome: novaCategoriaNome.value.trim(),
      tipo: novaCategoriaTipo.value,
      grupo_despesa: novaCategoriaTipo.value === 'DESPESA' ? novaCategoriaGrupo.value : null,
    })
    novaCategoriaNome.value = ''
    novaCategoriaTipo.value = 'DESPESA'
    novaCategoriaGrupo.value = 'GERAL'
    sucessoCategoria.value = 'Categoria criada.'
    await carregarCategorias()
  } catch {
    erroCategoria.value = 'Não foi possível criar a categoria.'
  } finally {
    enviandoCategoria.value = false
  }
}

function iniciarEdicaoCategoria(cat: CategoriaResposta) {
  editCategoriaId.value = cat.id
  editCategoriaNome.value = cat.nome
  editCategoriaGrupo.value = (cat.grupo_despesa ?? 'GERAL') as GrupoDespesa
}

function cancelarEdicaoCategoria() {
  editCategoriaId.value = null
  editCategoriaNome.value = ''
}

async function salvarCategoria() {
  if (!editCategoriaId.value) return
  if (!editCategoriaNome.value.trim()) {
    erroCategoria.value = 'Nome da categoria é obrigatório.'
    return
  }
  enviandoCategoria.value = true
  erroCategoria.value = ''
  try {
    const atual = categorias.value.find(c => c.id === editCategoriaId.value)
    await atualizarCategoria(editCategoriaId.value, {
      nome: editCategoriaNome.value.trim(),
      grupo_despesa: atual?.tipo === 'DESPESA' ? editCategoriaGrupo.value : null,
    })
    sucessoCategoria.value = 'Categoria atualizada.'
    editCategoriaId.value = null
    await carregarCategorias()
  } catch {
    erroCategoria.value = 'Não foi possível atualizar a categoria.'
  } finally {
    enviandoCategoria.value = false
  }
}

async function removerCategoria(id: number) {
  if (!confirm('Deseja excluir esta categoria?')) return
  erroCategoria.value = ''
  sucessoCategoria.value = ''
  try {
    await excluirCategoria(id)
    sucessoCategoria.value = 'Categoria removida.'
    await carregarCategorias()
  } catch {
    erroCategoria.value = 'Não foi possível remover a categoria.'
  }
}

const lancamentos = ref<LancamentoResposta[]>([])
const carregandoLancamentos = ref(false)
const erroLancamento = ref('')
const sucessoLancamento = ref('')
const lancTipoFiltro = ref<TipoLancamento | 'TODOS'>('TODOS')
const lancDataInicio = ref(new Date().toISOString().slice(0, 10))
const lancDataFim = ref(new Date().toISOString().slice(0, 10))
const lancPagina = ref(1)
const lancTotalPaginas = ref(1)
const lancTotal = ref(0)

const editLancId = ref<number | null>(null)
const editLancCategoriaId = ref<number | null>(null)
const editLancValor = ref('')
const editLancDescricao = ref('')
const editLancData = ref('')
const editLancPeriodo = ref<PeriodoLancamento | null>(null)
const editLancMinutos = ref<number | null>(null)
const editLancKm = ref<string | null>(null)
const editLancTipo = ref<TipoLancamento>('DESPESA')
const editLancMotoId = ref<number | null>(null)
const enviandoLancamento = ref(false)

const categoriasParaEdicaoLancamento = computed(() =>
  categorias.value.filter(c => c.tipo === editLancTipo.value)
)

async function carregarLancamentos(pagina = lancPagina.value) {
  carregandoLancamentos.value = true
  erroLancamento.value = ''
  try {
    const res = await listarLancamentos({
      tipo: lancTipoFiltro.value === 'TODOS' ? undefined : lancTipoFiltro.value,
      data_inicio: lancDataInicio.value || undefined,
      data_fim: lancDataFim.value || undefined,
      pagina,
      limite: 10,
    })
    lancamentos.value = res.itens
    lancPagina.value = res.pagina
    lancTotalPaginas.value = res.total_paginas
    lancTotal.value = res.total
  } catch {
    erroLancamento.value = 'Não foi possível carregar lançamentos.'
  } finally {
    carregandoLancamentos.value = false
  }
}

function iniciarEdicaoLancamento(l: LancamentoResposta) {
  editLancId.value = l.id
  editLancCategoriaId.value = l.categoria_id
  editLancValor.value = String(Number(l.valor).toFixed(2)).replace('.', ',')
  editLancDescricao.value = l.descricao ?? ''
  editLancData.value = l.data_lancamento
  editLancPeriodo.value = l.periodo
  editLancMinutos.value = l.minutos_corrida
  editLancKm.value = l.km_corrida
  editLancTipo.value = l.tipo
  editLancMotoId.value = l.moto_usuario_id
}

function cancelarEdicaoLancamento() {
  editLancId.value = null
  editLancValor.value = ''
  editLancDescricao.value = ''
}

async function salvarLancamento() {
  if (!editLancId.value || !editLancCategoriaId.value) return
  const valor = Number(editLancValor.value.replace(',', '.'))
  if (!valor || valor <= 0) {
    erroLancamento.value = 'Valor inválido.'
    return
  }

  const payload: LancamentoCriar = {
    categoria_id: editLancCategoriaId.value,
    tipo: editLancTipo.value,
    valor,
    descricao: editLancDescricao.value || undefined,
    periodo: editLancTipo.value === 'GANHO' ? (editLancPeriodo.value ?? undefined) : undefined,
    minutos_corrida: editLancPeriodo.value === 'CORRIDA' ? (editLancMinutos.value ?? undefined) : undefined,
    km_corrida: editLancPeriodo.value === 'CORRIDA' && editLancKm.value ? Number(editLancKm.value) : undefined,
    data_lancamento: editLancData.value || undefined,
    moto_usuario_id: editLancMotoId.value ?? undefined,
  }

  enviandoLancamento.value = true
  erroLancamento.value = ''
  sucessoLancamento.value = ''
  try {
    await atualizarLancamento(editLancId.value, payload)
    sucessoLancamento.value = 'Lançamento atualizado.'
    editLancId.value = null
    await carregarLancamentos(1)
  } catch {
    erroLancamento.value = 'Não foi possível atualizar o lançamento.'
  } finally {
    enviandoLancamento.value = false
  }
}

async function removerLancamento(id: number) {
  if (!confirm('Deseja excluir este lançamento?')) return
  erroLancamento.value = ''
  sucessoLancamento.value = ''
  try {
    await excluirLancamento(id)
    sucessoLancamento.value = 'Lançamento excluído.'
    await carregarLancamentos(1)
  } catch {
    erroLancamento.value = 'Não foi possível excluir o lançamento.'
  }
}

function periodoRapidoLancamentos(dias: number) {
  const fim = new Date()
  const ini = new Date()
  ini.setDate(fim.getDate() - dias)
  lancDataFim.value = fim.toISOString().slice(0, 10)
  lancDataInicio.value = ini.toISOString().slice(0, 10)
  carregarLancamentos(1)
}

function formatarReais(valor: string | number): string {
  const n = typeof valor === 'string' ? parseFloat(valor) : valor
  if (isNaN(n)) return 'R$ 0,00'
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatarKm(km: number): string {
  return km.toLocaleString('pt-BR') + ' KM'
}

function tipoClasseBadge(tipo: TipoLancamento): string {
  return tipo === 'GANHO'
    ? 'bg-primary-container/10 text-primary-container border-primary-container/40'
    : 'bg-secondary/10 text-secondary border-secondary/40'
}

onMounted(async () => {
  await Promise.all([carregarCategorias(), carregarLancamentos(1)])
})
</script>

<template>
  <div class="bg-background text-on-surface font-body min-h-screen pb-24">
    <header class="bg-background flex justify-between items-center w-full px-5 h-16 sticky top-0 z-50 border-l-4 border-primary-container">
      <h1 class="text-primary-container font-headline font-black text-lg tracking-tight uppercase">GESTÃO MOTOCA</h1>
      <span class="font-label text-[10px] tracking-widest text-on-surface-variant uppercase">CONFIGURAÇÕES</span>
    </header>

    <main class="px-5 py-5 space-y-4 max-w-md mx-auto">
      <div>
        <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">CENTRO DE CONTROLE</p>
        <h2 class="font-headline font-extrabold text-3xl uppercase tracking-tight">CONFIGURAÇÕES</h2>
      </div>

      <div class="grid grid-cols-3 gap-2">
        <button
          class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border"
          :class="abaAtiva === 'MOTO' ? 'bg-primary-container text-on-primary-fixed border-primary-container' : 'bg-surface-container text-on-surface-variant border-outline-variant'"
          @click="abaAtiva = 'MOTO'"
        >MOTO</button>
        <button
          class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border"
          :class="abaAtiva === 'CATEGORIAS' ? 'bg-primary-container text-on-primary-fixed border-primary-container' : 'bg-surface-container text-on-surface-variant border-outline-variant'"
          @click="abaAtiva = 'CATEGORIAS'"
        >CATEGORIAS</button>
        <button
          class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border"
          :class="abaAtiva === 'LANCAMENTOS' ? 'bg-primary-container text-on-primary-fixed border-primary-container' : 'bg-surface-container text-on-surface-variant border-outline-variant'"
          @click="abaAtiva = 'LANCAMENTOS'"
        >LANÇAMENTOS</button>
      </div>

      <section v-if="abaAtiva === 'MOTO'" class="space-y-3">
        <div v-if="moto" class="bg-surface-container p-4 space-y-2 border-l-2 border-primary-container">
          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">MOTO ATIVA</p>
          <p class="font-headline font-bold text-xl">{{ [moto.marca_manual, moto.modelo_manual].filter(Boolean).join(' ') || 'Moto' }}</p>
          <p class="font-label text-xs text-on-surface-variant">{{ formatarKm(moto.km_atual) }}</p>
          <p class="font-label text-xs text-on-surface-variant">Cor: {{ moto.cor || '—' }}</p>
        </div>

        <div v-if="erroMoto" class="bg-error-container text-on-error-container text-xs px-3 py-2">{{ erroMoto }}</div>
        <div v-if="sucessoMoto" class="bg-primary-container/20 text-primary-container text-xs px-3 py-2">{{ sucessoMoto }}</div>

        <div v-if="editandoMoto" class="bg-surface-container p-3 space-y-2">
          <input v-model="kmAtual" type="number" min="0" placeholder="KM atual" class="tactical-input py-2 text-sm" />
          <input v-model="cor" type="text" placeholder="Cor" class="tactical-input py-2 text-sm" />
          <div class="grid grid-cols-2 gap-2">
            <button class="h-10 border border-outline-variant text-xs uppercase font-label" @click="cancelarEdicaoMoto">Cancelar</button>
            <button class="h-10 bg-primary-container text-on-primary-fixed text-xs uppercase font-label" @click="salvarMoto" :disabled="enviandoMoto">
              {{ enviandoMoto ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </div>
        <button v-else class="h-10 w-full border border-outline-variant text-xs uppercase font-label bg-surface-container" @click="iniciarEdicaoMoto">
          Editar dados da moto
        </button>
      </section>

      <section v-if="abaAtiva === 'CATEGORIAS'" class="space-y-3">
        <div v-if="erroCategoria" class="bg-error-container text-on-error-container text-xs px-3 py-2">{{ erroCategoria }}</div>
        <div v-if="sucessoCategoria" class="bg-primary-container/20 text-primary-container text-xs px-3 py-2">{{ sucessoCategoria }}</div>

        <div class="bg-surface-container p-3 space-y-2">
          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">Nova categoria</p>
          <input v-model="novaCategoriaNome" type="text" placeholder="Nome da categoria" class="tactical-input py-2 text-sm" />
          <div class="grid grid-cols-2 gap-2">
            <select v-model="novaCategoriaTipo" class="tactical-input py-2 text-sm">
              <option value="GANHO">GANHO</option>
              <option value="DESPESA">DESPESA</option>
            </select>
            <select v-if="novaCategoriaTipo === 'DESPESA'" v-model="novaCategoriaGrupo" class="tactical-input py-2 text-sm">
              <option v-for="g in gruposDespesa" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>
          <button class="h-10 w-full bg-primary-container text-on-primary-fixed text-xs uppercase font-label" @click="criarNovaCategoria" :disabled="enviandoCategoria">
            {{ enviandoCategoria ? 'Salvando...' : 'Criar categoria' }}
          </button>
        </div>

        <div v-if="carregandoCategorias" class="h-20 bg-surface-container-low animate-pulse"></div>
        <div v-else class="space-y-2">
          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">Ganhos</p>
          <div v-for="cat in categoriasGanhos" :key="cat.id" class="bg-surface-container p-2 border-l-2 border-primary-container">
            <div v-if="editCategoriaId !== cat.id" class="flex items-center justify-between gap-2">
              <div class="space-y-1">
                <p class="font-label text-xs">{{ cat.nome }}</p>
                <span class="inline-flex items-center h-5 px-1.5 border text-[9px] uppercase font-label tracking-wider" :class="tipoClasseBadge('GANHO')">GANHO</span>
              </div>
              <div class="flex gap-1">
                <button
                  class="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-primary-container border border-outline-variant"
                  title="Editar"
                  @click="iniciarEdicaoCategoria(cat)"
                >
                  <span class="material-symbols-outlined text-base">edit</span>
                </button>
                <button
                  class="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-secondary border border-outline-variant"
                  title="Excluir"
                  @click="removerCategoria(cat.id)"
                >
                  <span class="material-symbols-outlined text-base">delete</span>
                </button>
              </div>
            </div>
            <div v-else class="space-y-2">
              <input v-model="editCategoriaNome" type="text" class="tactical-input py-2 text-sm" />
              <div class="grid grid-cols-2 gap-2">
                <button class="h-9 border border-outline-variant text-xs" @click="cancelarEdicaoCategoria">Cancelar</button>
                <button class="h-9 bg-primary-container text-on-primary-fixed text-xs" @click="salvarCategoria">Salvar</button>
              </div>
            </div>
          </div>

          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mt-3">Despesas</p>
          <div v-for="cat in categoriasDespesas" :key="cat.id" class="bg-surface-container p-2 border-l-2 border-secondary">
            <div v-if="editCategoriaId !== cat.id" class="flex items-center justify-between gap-2">
              <div>
                <p class="font-label text-xs">{{ cat.nome }}</p>
                <div class="flex items-center gap-1.5 mt-1">
                  <span class="inline-flex items-center h-5 px-1.5 border text-[9px] uppercase font-label tracking-wider" :class="tipoClasseBadge('DESPESA')">DESPESA</span>
                  <p class="font-label text-[9px] text-on-surface-variant">{{ cat.grupo_despesa }}</p>
                </div>
              </div>
              <div class="flex gap-1">
                <button
                  class="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-primary-container border border-outline-variant"
                  title="Editar"
                  @click="iniciarEdicaoCategoria(cat)"
                >
                  <span class="material-symbols-outlined text-base">edit</span>
                </button>
                <button
                  class="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-secondary border border-outline-variant"
                  title="Excluir"
                  @click="removerCategoria(cat.id)"
                >
                  <span class="material-symbols-outlined text-base">delete</span>
                </button>
              </div>
            </div>
            <div v-else class="space-y-2">
              <input v-model="editCategoriaNome" type="text" class="tactical-input py-2 text-sm" />
              <select v-model="editCategoriaGrupo" class="tactical-input py-2 text-sm">
                <option v-for="g in gruposDespesa" :key="g" :value="g">{{ g }}</option>
              </select>
              <div class="grid grid-cols-2 gap-2">
                <button class="h-9 border border-outline-variant text-xs" @click="cancelarEdicaoCategoria">Cancelar</button>
                <button class="h-9 bg-primary-container text-on-primary-fixed text-xs" @click="salvarCategoria">Salvar</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-if="abaAtiva === 'LANCAMENTOS'" class="space-y-3">
        <div class="space-y-2 bg-surface-container p-3">
          <div class="grid grid-cols-3 gap-2">
            <button class="h-9 text-[9px] uppercase border border-outline-variant" @click="periodoRapidoLancamentos(0)">Hoje</button>
            <button class="h-9 text-[9px] uppercase border border-outline-variant" @click="periodoRapidoLancamentos(7)">7 dias</button>
            <button class="h-9 text-[9px] uppercase border border-outline-variant" @click="periodoRapidoLancamentos(30)">30 dias</button>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <AppDateInput v-model="lancDataInicio" tone="system" />
            <AppDateInput v-model="lancDataFim" tone="system" />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <select v-model="lancTipoFiltro" class="tactical-input py-2 text-sm">
              <option value="TODOS">TODOS</option>
              <option value="GANHO">GANHO</option>
              <option value="DESPESA">DESPESA</option>
            </select>
            <button class="h-10 bg-surface-container-high border border-outline-variant text-xs uppercase" @click="carregarLancamentos(1)">Aplicar</button>
          </div>
        </div>

        <div v-if="erroLancamento" class="bg-error-container text-on-error-container text-xs px-3 py-2">{{ erroLancamento }}</div>
        <div v-if="sucessoLancamento" class="bg-primary-container/20 text-primary-container text-xs px-3 py-2">{{ sucessoLancamento }}</div>

        <div v-if="carregandoLancamentos" class="h-20 bg-surface-container-low animate-pulse"></div>
        <div v-else-if="!lancamentos.length" class="text-center text-on-surface-variant text-xs py-6 uppercase">Nenhum lançamento</div>
        <ul v-else class="space-y-2">
          <li
            v-for="l in lancamentos"
            :key="l.id"
            class="bg-surface-container p-2 border-l-2"
            :class="l.tipo === 'GANHO' ? 'border-primary-container' : 'border-secondary'"
          >
            <div v-if="editLancId !== l.id" class="flex items-start justify-between gap-2">
              <div>
                <p class="font-label text-[9px] text-on-surface-variant uppercase">{{ l.data_lancamento }} · {{ l.tipo }}</p>
                <p class="font-label text-xs">{{ l.categoria_nome || 'Sem categoria' }}</p>
                <p v-if="l.descricao" class="font-label text-[10px] text-on-surface-variant">{{ l.descricao }}</p>
                <span
                  class="inline-flex items-center mt-1 h-5 px-1.5 border text-[9px] uppercase font-label tracking-wider"
                  :class="tipoClasseBadge(l.tipo)"
                >
                  {{ l.tipo }}
                </span>
              </div>
              <div class="text-right">
                <p class="font-headline text-sm" :class="l.tipo === 'GANHO' ? 'text-primary-container' : 'text-secondary'">{{ formatarReais(l.valor) }}</p>
                <div class="flex gap-1 justify-end mt-1">
                  <button
                    class="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-primary-container border border-outline-variant"
                    title="Editar"
                    @click="iniciarEdicaoLancamento(l)"
                  >
                    <span class="material-symbols-outlined text-base">edit</span>
                  </button>
                  <button
                    class="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-secondary border border-outline-variant"
                    title="Excluir"
                    @click="removerLancamento(l.id)"
                  >
                    <span class="material-symbols-outlined text-base">delete</span>
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="space-y-2">
              <select v-model.number="editLancCategoriaId" class="tactical-input py-2 text-sm">
                <option v-for="cat in categoriasParaEdicaoLancamento" :key="cat.id" :value="cat.id">{{ cat.nome }}</option>
              </select>
              <input v-model="editLancValor" type="text" inputmode="decimal" class="tactical-input py-2 text-sm" placeholder="Valor" />
              <input v-model="editLancDescricao" type="text" class="tactical-input py-2 text-sm" placeholder="Descrição" />
              <AppDateInput v-model="editLancData" :tone="editLancTipo === 'DESPESA' ? 'despesa' : 'system'" />
              <div class="grid grid-cols-2 gap-2">
                <button class="h-9 border border-outline-variant text-xs" @click="cancelarEdicaoLancamento">Cancelar</button>
                <button class="h-9 bg-primary-container text-on-primary-fixed text-xs" :disabled="enviandoLancamento" @click="salvarLancamento">
                  {{ enviandoLancamento ? 'Salvando...' : 'Salvar' }}
                </button>
              </div>
            </div>
          </li>
        </ul>

        <div class="flex items-center justify-center gap-3" v-if="lancTotalPaginas > 1">
          <button class="w-9 h-9 border border-outline-variant" :disabled="lancPagina <= 1" @click="carregarLancamentos(lancPagina - 1)">
            <span class="material-symbols-outlined text-base">chevron_left</span>
          </button>
          <p class="font-label text-[9px] text-on-surface-variant uppercase">Pág {{ lancPagina }} / {{ lancTotalPaginas }} · {{ lancTotal }}</p>
          <button class="w-9 h-9 border border-outline-variant" :disabled="lancPagina >= lancTotalPaginas" @click="carregarLancamentos(lancPagina + 1)">
            <span class="material-symbols-outlined text-base">chevron_right</span>
          </button>
        </div>
      </section>
    </main>

    <nav class="fixed bottom-0 left-0 w-full z-50 h-20 bg-background border-t-4 border-surface-container grid grid-cols-5">
      <button
        v-for="item in navItems"
        :key="item.name"
        class="flex flex-col items-center justify-center h-full w-full transition-colors duration-100"
        :class="isActive(item.name) ? 'bg-primary-container text-on-primary-fixed' : 'text-on-surface-variant hover:bg-surface-container'"
        @click="router.push({ name: item.name })"
      >
        <span class="material-symbols-outlined" :style="navIconStyle(item.name)">{{ item.icon }}</span>
        <span class="font-label text-[9px] font-bold uppercase tracking-[0.08em] mt-0.5">{{ item.label }}</span>
      </button>
    </nav>
  </div>
</template>

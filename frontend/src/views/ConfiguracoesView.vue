<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMotoStore } from '@/stores/moto'
import { useAuthStore } from '@/stores/auth'
import PaywallOverlay from '@/components/PaywallOverlay.vue'
import { cancelarAssinaturaStripe } from '@/api/assinaturas'
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
import AppLayout from '@/components/AppLayout.vue'

import { alterarSenhaLogado } from '@/api/recuperacao'

const router = useRouter()
const route = useRoute()
const motoStore = useMotoStore()
const authStore = useAuthStore()

type AbaConfig = 'MOTO' | 'CATEGORIAS' | 'LANCAMENTOS' | 'SEGURANCA' | 'PLANO'
const abaAtiva = ref<AbaConfig>('MOTO')

const avisoAssinatura = ref('')
const carregandoCancelamento = ref(false)

// Estados para alteração de senha estando logado
const senhaAtual = ref('')
const novaSenha = ref('')
const confirmaNovaSenha = ref('')
const mostrarSenhaAtual = ref(false)
const mostrarNovaSenha = ref(false)
const mostrarConfirmaNovaSenha = ref(false)
const enviandoSenha = ref(false)
const erroSenha = ref('')
const sucessoSenha = ref('')

async function handleAlterarSenha() {
  if (!senhaAtual.value || !novaSenha.value) {
    erroSenha.value = 'Preencha a senha atual e a nova senha.'
    return
  }
  if (novaSenha.value !== confirmaNovaSenha.value) {
    erroSenha.value = 'A confirmação de senha não confere.'
    return
  }
  if (novaSenha.value.length < 6) {
    erroSenha.value = 'A nova senha deve ter no mínimo 6 caracteres.'
    return
  }

  erroSenha.value = ''
  sucessoSenha.value = ''
  enviandoSenha.value = true

  try {
    const res = await alterarSenhaLogado({
      senha_atual: senhaAtual.value,
      nova_senha: novaSenha.value,
    })
    sucessoSenha.value = res.mensagem || 'Senha alterada com sucesso.'
    senhaAtual.value = ''
    novaSenha.value = ''
    confirmaNovaSenha.value = ''
  } catch (e: any) {
    erroSenha.value = e?.response?.data?.detail || 'Erro ao alterar senha. Verifique a senha atual.'
  } finally {
    enviandoSenha.value = false
  }
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

function formatarDataIsoLocal(d: Date = new Date()): string {
  const ano = d.getFullYear()
  const mes = String(d.getMonth() + 1).padStart(2, '0')
  const dia = String(d.getDate()).padStart(2, '0')
  return `${ano}-${mes}-${dia}`
}

function formatarIsoParaBr(iso: string): string {
  if (!iso) return ''
  const [ano, mes, dia] = iso.split('-')
  if (!ano || !mes || !dia) return iso
  return `${dia}/${mes}/${ano}`
}

const lancamentos = ref<LancamentoResposta[]>([])
const carregandoLancamentos = ref(false)
const erroLancamento = ref('')
const sucessoLancamento = ref('')
const lancTipoFiltro = ref<TipoLancamento | 'TODOS'>('TODOS')
const lancDataInicio = ref(formatarDataIsoLocal())
const lancDataFim = ref(formatarDataIsoLocal())
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
  lancDataFim.value = formatarDataIsoLocal(fim)
  lancDataInicio.value = formatarDataIsoLocal(ini)
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

async function cancelarMinhaAssinatura() {
  if (!confirm('Deseja realmente cancelar a sua assinatura PRO? Seu acesso continuará ativo até o final do período pago.')) return
  try {
    carregandoCancelamento.value = true
    const res = await cancelarAssinaturaStripe()
    avisoAssinatura.value = res.mensagem
    await authStore.carregarStatusAssinatura()
  } catch (e: any) {
    avisoAssinatura.value = e?.response?.data?.detail || 'Erro ao cancelar assinatura.'
  } finally {
    carregandoCancelamento.value = false
  }
}

onMounted(async () => {
  if (route.query.assinatura === 'sucesso') {
    abaAtiva.value = 'PLANO'
    avisoAssinatura.value = '🎉 Pagamento confirmado! Sua conta agora é Gestão Motoca PRO.'
    await authStore.carregarUsuario()
  } else if (route.query.assinatura === 'cancelado') {
    abaAtiva.value = 'PLANO'
    avisoAssinatura.value = 'O pagamento não foi concluído. Se precisar de ajuda, entre em contato.'
  }
  await Promise.all([carregarCategorias(), carregarLancamentos(1)])
})
</script>

<template>
  <AppLayout>
  <div class="bg-background text-on-surface font-body min-h-screen">
    <main class="px-5 py-5 lg:px-8 lg:py-6 space-y-4 max-w-4xl mx-auto pb-28 lg:pb-8">
      <div>
        <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">CENTRO DE CONTROLE</p>
        <h2 class="font-headline font-extrabold text-3xl uppercase tracking-tight">CONFIGURAÇÕES</h2>
      </div>

      <div class="grid grid-cols-5 gap-1 font-mono">
        <button
          class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border truncate px-1"
          :class="abaAtiva === 'MOTO' ? 'bg-primary-container text-on-primary-fixed border-primary-container' : 'bg-surface-container text-on-surface-variant border-outline-variant'"
          @click="abaAtiva = 'MOTO'"
        >MOTO</button>
        <button
          class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border truncate px-1"
          :class="abaAtiva === 'CATEGORIAS' ? 'bg-primary-container text-on-primary-fixed border-primary-container' : 'bg-surface-container text-on-surface-variant border-outline-variant'"
          @click="abaAtiva = 'CATEGORIAS'"
        >CATEGORIAS</button>
        <button
          class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border truncate px-1"
          :class="abaAtiva === 'LANCAMENTOS' ? 'bg-primary-container text-on-primary-fixed border-primary-container' : 'bg-surface-container text-on-surface-variant border-outline-variant'"
          @click="abaAtiva = 'LANCAMENTOS'"
        >LANÇAMENTOS</button>
        <button
          class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border truncate px-1"
          :class="abaAtiva === 'SEGURANCA' ? 'bg-primary-container text-on-primary-fixed border-primary-container' : 'bg-surface-container text-on-surface-variant border-outline-variant'"
          @click="abaAtiva = 'SEGURANCA'"
        >SENHA</button>
        <button
          class="h-10 font-label text-[9px] font-bold tracking-widest uppercase border truncate px-1 flex items-center justify-center gap-0.5"
          :class="abaAtiva === 'PLANO' ? 'bg-amber-500 text-slate-950 border-amber-400 font-black' : 'bg-amber-500/10 text-amber-400 border-amber-500/30'"
          @click="abaAtiva = 'PLANO'"
        >
          <span>⭐</span>
          <span>PLANO</span>
        </button>
      </div>

      <section v-if="abaAtiva === 'MOTO'" class="space-y-3">
        <div v-if="!moto" class="flex flex-col items-center justify-center py-12 gap-4 text-on-surface-variant bg-surface-container p-5">
          <span class="material-symbols-outlined text-5xl opacity-30">two_wheeler</span>
          <p class="font-label text-xs tracking-widest uppercase">Nenhuma moto vinculada</p>
          <button
            class="btn-primary h-11 w-auto px-6 text-xs"
            @click="router.push({ name: 'vincular-moto' })"
          >
            <span class="material-symbols-outlined text-sm">link</span>
            VINCULAR MOTO
          </button>
        </div>

        <template v-else>
          <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase">
            MOTO ATIVA
          </p>

          <div class="bg-surface-container-low p-4 relative border-l-4 border-primary-container overflow-hidden">
            <span class="material-symbols-outlined absolute right-4 top-4 text-5xl text-primary-container opacity-10">two_wheeler</span>

            <div class="space-y-3">
              <div>
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-1">QUILOMETRAGEM</p>
                <p class="font-headline font-black text-2xl text-on-surface">
                  {{ moto.km_atual !== null ? formatarKm(moto.km_atual) : '—' }}
                </p>
              </div>

              <div class="h-[1px] bg-surface-container"></div>

              <div v-if="moto.placa" class="flex justify-between items-center">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">PLACA</p>
                <p class="font-headline font-black text-base tracking-widest text-on-surface">{{ moto.placa }}</p>
              </div>

              <div class="flex justify-between items-center">
                <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">COR</p>
                <p class="font-label text-xs font-bold text-on-surface uppercase">{{ moto.cor || '—' }}</p>
              </div>
            </div>
          </div>
        </template>

        <div v-if="erroMoto" class="bg-error-container text-on-error-container text-xs px-3 py-2">{{ erroMoto }}</div>
        <div v-if="sucessoMoto" class="bg-primary-container/20 text-primary-container text-xs px-3 py-2">{{ sucessoMoto }}</div>

        <div v-if="editandoMoto && moto" class="bg-surface-container-low border-l-4 border-outline-variant p-4 space-y-3">
          <p class="font-label text-[9px] font-bold tracking-[0.25em] text-primary-container uppercase">ATUALIZAR DADOS DA MOTO</p>
          <div class="grid grid-cols-2 gap-2 bg-surface-container p-2 border border-outline-variant">
            <div>
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">KM ATUAL</p>
              <p class="font-headline text-sm font-bold text-on-surface">
                {{ moto.km_atual !== null ? formatarKm(moto.km_atual) : '—' }}
              </p>
            </div>
            <div>
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">COR ATUAL</p>
              <p class="font-label text-xs font-bold text-on-surface uppercase">{{ moto.cor || '—' }}</p>
            </div>
          </div>

          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-1 uppercase">NOVO KM</label>
            <div class="relative">
              <input v-model="kmAtual" type="number" min="0" :placeholder="moto.km_atual?.toString() ?? '0'" class="tactical-input py-2.5 pl-3 pr-12 text-sm" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-xs font-bold">KM</span>
            </div>
          </div>

          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-1 uppercase">COR</label>
            <input v-model="cor" type="text" placeholder="Ex: Preta, Vermelha" class="tactical-input py-2.5 px-3 text-sm" />
          </div>

          <div class="grid grid-cols-2 gap-2 pt-1">
            <button class="h-10 border border-outline-variant bg-surface-container text-xs uppercase font-label" @click="cancelarEdicaoMoto">Cancelar</button>
            <button class="h-10 bg-primary-container text-on-primary-fixed text-xs uppercase font-label font-bold" @click="salvarMoto" :disabled="enviandoMoto">
              {{ enviandoMoto ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </div>
        <button v-else-if="moto" class="h-10 w-full border border-outline-variant text-xs uppercase font-label bg-surface-container hover:bg-surface-container-high" @click="iniciarEdicaoMoto">
          Editar dados da moto
        </button>
      </section>

      <section v-if="abaAtiva === 'CATEGORIAS'" class="space-y-3">
        <div v-if="erroCategoria" class="bg-error-container text-on-error-container text-xs px-3 py-2">{{ erroCategoria }}</div>
        <div v-if="sucessoCategoria" class="bg-primary-container/20 text-primary-container text-xs px-3 py-2">{{ sucessoCategoria }}</div>

        <div class="bg-surface-container p-3 space-y-2">
          <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">Nova categoria</p>
          <input v-model="novaCategoriaNome" type="text" placeholder="Nome da categoria" class="tactical-input px-3.5 py-2 text-sm" />
          <div class="grid grid-cols-2 gap-2">
            <select v-model="novaCategoriaTipo" class="tactical-input px-3.5 py-2 text-sm">
              <option value="GANHO">GANHO</option>
              <option value="DESPESA">DESPESA</option>
            </select>
            <select v-if="novaCategoriaTipo === 'DESPESA'" v-model="novaCategoriaGrupo" class="tactical-input px-3.5 py-2 text-sm">
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
              <input v-model="editCategoriaNome" type="text" class="tactical-input px-3.5 py-2 text-sm" />
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
              <input v-model="editCategoriaNome" type="text" class="tactical-input px-3.5 py-2 text-sm" />
              <select v-model="editCategoriaGrupo" class="tactical-input px-3.5 py-2 text-sm">
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
            <AppDateInput v-model="lancDataInicio" tone="system" :max="lancDataFim || undefined" />
            <AppDateInput v-model="lancDataFim" tone="system" :min="lancDataInicio || undefined" />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <select v-model="lancTipoFiltro" class="tactical-input px-3.5 py-2 text-sm">
              <option value="TODOS">TODOS</option>
              <option value="GANHO">GANHO</option>
              <option value="DESPESA">DESPESA</option>
            </select>
            <button class="h-10 bg-white dark:bg-surface-container-high border border-outline dark:border-outline-variant text-on-surface font-label text-xs font-bold uppercase hover:bg-surface-variant dark:hover:bg-surface-bright transition-all shadow-sm active:scale-[0.98] flex items-center justify-center gap-1" @click="carregarLancamentos(1)">
              <span class="material-symbols-outlined text-sm">check_circle</span>
              Aplicar
            </button>
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
                <p class="font-label text-[9px] text-on-surface-variant uppercase">{{ formatarIsoParaBr(l.data_lancamento) }} · {{ l.tipo }}</p>
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
              <select v-model.number="editLancCategoriaId" class="tactical-input px-3.5 py-2 text-sm">
                <option v-for="cat in categoriasParaEdicaoLancamento" :key="cat.id" :value="cat.id">{{ cat.nome }}</option>
              </select>
              <input v-model="editLancValor" type="text" inputmode="decimal" class="tactical-input px-3.5 py-2 text-sm" placeholder="Valor" />
              <input v-model="editLancDescricao" type="text" class="tactical-input px-3.5 py-2 text-sm" placeholder="Descrição" />
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

      <section v-if="abaAtiva === 'SEGURANCA'" class="space-y-4">
        <div class="bg-surface-container-low p-5 border-l-4 border-primary-container space-y-4">
          <div>
            <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">SEGURANÇA E CONTA</p>
            <h3 class="font-headline font-black text-xl text-on-surface uppercase">ALTERAR MINHA SENHA</h3>
          </div>

          <form class="space-y-4" @submit.prevent="handleAlterarSenha">
            <div>
              <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-1 uppercase">SENHA ATUAL</label>
              <div class="relative">
                <input
                  v-model="senhaAtual"
                  :type="mostrarSenhaAtual ? 'text' : 'password'"
                  required
                  placeholder="••••••••"
                  class="tactical-input h-11 px-3 pr-10"
                />
                <button
                  type="button"
                  tabindex="-1"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface focus:outline-none flex items-center justify-center"
                  @click="mostrarSenhaAtual = !mostrarSenhaAtual"
                  :title="mostrarSenhaAtual ? 'Ocultar senha' : 'Exibir senha'"
                >
                  <span class="material-symbols-outlined text-lg">
                    {{ mostrarSenhaAtual ? 'visibility_off' : 'visibility' }}
                  </span>
                </button>
              </div>
            </div>

            <div>
              <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-1 uppercase">NOVA SENHA</label>
              <div class="relative">
                <input
                  v-model="novaSenha"
                  :type="mostrarNovaSenha ? 'text' : 'password'"
                  required
                  minlength="6"
                  placeholder="••••••••"
                  class="tactical-input h-11 px-3 pr-10"
                />
                <button
                  type="button"
                  tabindex="-1"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface focus:outline-none flex items-center justify-center"
                  @click="mostrarNovaSenha = !mostrarNovaSenha"
                  :title="mostrarNovaSenha ? 'Ocultar senha' : 'Exibir senha'"
                >
                  <span class="material-symbols-outlined text-lg">
                    {{ mostrarNovaSenha ? 'visibility_off' : 'visibility' }}
                  </span>
                </button>
              </div>
            </div>

            <div>
              <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-1 uppercase">CONFIRMAR NOVA SENHA</label>
              <div class="relative">
                <input
                  v-model="confirmaNovaSenha"
                  :type="mostrarConfirmaNovaSenha ? 'text' : 'password'"
                  required
                  minlength="6"
                  placeholder="••••••••"
                  class="tactical-input h-11 px-3 pr-10"
                />
                <button
                  type="button"
                  tabindex="-1"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface focus:outline-none flex items-center justify-center"
                  @click="mostrarConfirmaNovaSenha = !mostrarConfirmaNovaSenha"
                  :title="mostrarConfirmaNovaSenha ? 'Ocultar senha' : 'Exibir senha'"
                >
                  <span class="material-symbols-outlined text-lg">
                    {{ mostrarConfirmaNovaSenha ? 'visibility_off' : 'visibility' }}
                  </span>
                </button>
              </div>
            </div>

            <div v-if="erroSenha" class="bg-error-container text-on-error-container text-xs p-3 font-label">
              {{ erroSenha }}
            </div>
            <div v-if="sucessoSenha" class="bg-primary-container/20 text-primary-fixed border-l-2 border-primary-fixed text-xs p-3 font-label">
              {{ sucessoSenha }}
            </div>

            <button
              type="submit"
              :disabled="enviandoSenha"
              class="btn-primary h-12 w-full text-xs tracking-widest uppercase disabled:opacity-50"
            >
              <span v-if="enviandoSenha" class="material-symbols-outlined animate-spin mr-1">refresh</span>
              ATUALIZAR SENHA
            </button>
          </form>
        </div>
      </section>

      <!-- ── ABA PLANO & ASSINATURA ── -->
      <section v-if="abaAtiva === 'PLANO'" class="space-y-4">
        <!-- Aviso / Notificação de Retorno de Checkout -->
        <div v-if="avisoAssinatura" class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs font-semibold text-amber-300">
          {{ avisoAssinatura }}
        </div>

        <!-- Se o Usuário for PRO -->
        <div v-if="authStore.ehPro" class="rounded-2xl border border-amber-500/30 bg-gradient-to-b from-amber-500/10 via-slate-900/90 to-slate-950 p-6 space-y-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-500/20 text-2xl text-amber-300 border border-amber-400/40">
                ⭐
              </div>
              <div>
                <span class="rounded-full bg-amber-500/20 px-2.5 py-0.5 text-[10px] font-bold uppercase text-amber-300 border border-amber-400/40">
                  {{ authStore.statusAssinatura?.em_trial ? 'Período de Teste Grátis (7 Dias)' : 'Plano PRO Ativo' }}
                </span>
                <h3 class="text-xl font-black text-white mt-1">Gestão Motoca PRO</h3>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div class="rounded-xl border border-slate-800 bg-slate-900/60 p-3.5 space-y-1">
              <span class="text-slate-400">Status do Acesso</span>
              <p class="text-sm font-bold text-emerald-400 flex items-center gap-1">
                <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Ativo & Ilimitado
              </p>
            </div>

            <div class="rounded-xl border border-slate-800 bg-slate-900/60 p-3.5 space-y-1">
              <span class="text-slate-400">
                {{ authStore.statusAssinatura?.em_trial ? 'Dias de Teste Restantes' : 'Validade / Renovação' }}
              </span>
              <p class="text-sm font-bold text-slate-200">
                <template v-if="authStore.statusAssinatura?.em_trial">
                  {{ authStore.statusAssinatura.dias_trial_restantes }} dias grátis
                </template>
                <template v-else-if="authStore.usuario?.plano_expira_em">
                  {{ new Date(authStore.usuario.plano_expira_em).toLocaleDateString('pt-BR') }}
                </template>
                <template v-else>
                  Ativo
                </template>
              </p>
            </div>
          </div>

          <!-- Ação: Cancelar Assinatura (somente se tiver assinatura Stripe) -->
          <div v-if="authStore.statusAssinatura?.stripe_subscription_id" class="pt-2">
            <button
              type="button"
              @click="cancelarMinhaAssinatura"
              :disabled="carregandoCancelamento"
              class="text-xs text-red-400 hover:text-red-300 underline font-semibold transition-colors disabled:opacity-50"
            >
              <span v-if="carregandoCancelamento">Cancelando...</span>
              <span v-else>Cancelar renovação da assinatura</span>
            </button>
          </div>
        </div>

        <!-- Se o Usuário for FREE -->
        <div v-else>
          <PaywallOverlay />
        </div>
      </section>
    </main>

  </div>
  </AppLayout>
</template>

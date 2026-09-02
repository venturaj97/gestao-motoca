<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMotoStore } from '@/stores/moto'
import { criarManutencao } from '@/api/manutencoes'
import { listarCategorias } from '@/api/categorias'
import AppLayout from '@/components/AppLayout.vue'
import type { CategoriaResposta } from '@/types'
import AppDateInput from '@/components/AppDateInput.vue'

const router    = useRouter()
const motoStore = useMotoStore()

// ── Estado ─────────────────────────────────────────────────────
const categoriaId     = ref<number | null>(null)
const valorTotal      = ref('')
const kmAtual         = ref('')
const descricaoServico = ref('')
const oficina         = ref('')
const tipoServico     = ref('')
function hojeLocal(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const dataManutencao  = ref(hojeLocal())

const categoriasFiltradas = ref<CategoriaResposta[]>([])
const carregando = ref(false)
const enviando   = ref(false)
const erro       = ref('')
const sucesso    = ref(false)
const perguntarNovaManutencao = ref(false)

const motoId = ref(motoStore.motoAtiva?.id)

const tiposServico = ['Óleo', 'Pneu', 'Freio', 'Elétrico', 'Funilaria', 'Revisão', 'Outro']

// ── Carregar categorias ─────────────────────────────────────────
async function carregar() {
  carregando.value = true
  try {
    const todas = await listarCategorias()
    categoriasFiltradas.value = todas.filter(c => c.ativo && c.tipo === 'DESPESA')
    // Auto-seleciona categoria de manutenção se existir
    const manut = categoriasFiltradas.value.find(c =>
      c.nome.toLowerCase().includes('manut') || c.nome.toLowerCase().includes('reparo')
    )
    if (manut) categoriaId.value = manut.id
  } catch {
    erro.value = 'Erro ao carregar categorias.'
  } finally {
    carregando.value = false
  }
}

// ── Submissão ───────────────────────────────────────────────────
async function handleSubmit() {
  erro.value = ''

  const vTotal = parseFloat(valorTotal.value.replace(',', '.'))
  if (!valorTotal.value || isNaN(vTotal) || vTotal <= 0) {
    erro.value = 'Informe o valor da manutenção.'
    return
  }
  if (!categoriaId.value) {
    erro.value = 'Selecione uma categoria.'
    return
  }

  enviando.value = true
  try {
    await criarManutencao({
      categoria_id: categoriaId.value,
      valor_total: vTotal,
      km_atual: kmAtual.value ? parseInt(kmAtual.value) : undefined,
      descricao_servico: descricaoServico.value || undefined,
      oficina: oficina.value || undefined,
      tipo_servico: tipoServico.value || undefined,
      data_manutencao: dataManutencao.value || undefined,
      moto_usuario_id: motoId.value,
    })
    sucesso.value = true
    if (kmAtual.value && motoStore.motoAtiva) {
      motoStore.motoAtiva.km_atual = parseInt(kmAtual.value)
    }
    perguntarNovaManutencao.value = true
  } catch {
    erro.value = 'Erro ao registrar manutenção. Tente novamente.'
  } finally {
    enviando.value = false
  }
}

function prepararNovaManutencao() {
  valorTotal.value = ''
  kmAtual.value = ''
  descricaoServico.value = ''
  oficina.value = ''
  tipoServico.value = ''
  dataManutencao.value = hojeLocal()
  sucesso.value = false
  perguntarNovaManutencao.value = false
}

function irParaInicio() {
  sucesso.value = false
  perguntarNovaManutencao.value = false
  router.push({ name: 'dashboard' })
}


onMounted(carregar)
</script>

<template>
  <AppLayout>
  <div class="bg-background text-on-surface font-body min-h-screen">
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

      <!-- Título -->
      <div>
        <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">REGISTRAR</p>
        <h2 class="font-headline font-extrabold text-4xl tracking-tighter uppercase leading-none">MANUTENÇÃO</h2>
        <p v-if="motoStore.motoAtiva" class="font-label text-[10px] text-primary-container tracking-widest uppercase mt-1">
          <span class="material-symbols-outlined text-xs align-middle">two_wheeler</span>
          {{ [motoStore.motoAtiva.marca_manual, motoStore.motoAtiva.modelo_manual].filter(Boolean).join(' ') || 'Moto ativa' }}
        </p>
      </div>

      <form class="space-y-5" @submit.prevent="handleSubmit">

        <!-- Tipo de serviço -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            TIPO DE SERVIÇO
          </label>
          <div class="flex flex-wrap gap-2">
            <button v-for="ts in tiposServico" :key="ts"
              type="button"
              class="h-9 px-3 font-label text-[10px] font-bold tracking-wider uppercase transition-all border-b-2"
              :class="tipoServico === ts
                ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-primary-container'"
              @click="tipoServico = (tipoServico === ts ? '' : ts)">
              {{ ts }}
            </button>
          </div>
        </div>

        <!-- Valor -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">VALOR (R$)</label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 font-headline font-bold text-on-surface-variant">R$</span>
            <input :value="valorTotal" inputmode="decimal" placeholder="0,00"
              class="tactical-input pl-10 pr-3.5 py-4 text-2xl font-bold"
              @input="e => valorTotal = (e.target as HTMLInputElement).value" />
          </div>
        </div>

        <!-- Categoria -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">CATEGORIA</label>
          <div v-if="carregando" class="h-10 bg-surface-container-low animate-pulse" />
          <div v-else class="flex flex-wrap gap-2">
            <button v-for="cat in categoriasFiltradas" :key="cat.id"
              type="button"
              class="h-10 px-4 font-label text-[10px] font-bold tracking-wider uppercase transition-all border-b-2"
              :class="categoriaId === cat.id
                ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-primary-container'"
              @click="categoriaId = cat.id">
              {{ cat.nome }}
            </button>
          </div>
        </div>

        <!-- Descrição do serviço -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            DESCRIÇÃO DO SERVIÇO <span class="font-normal text-outline">(opcional)</span>
          </label>
          <input v-model="descricaoServico" type="text"
            placeholder="Ex: Troca de óleo 10W40"
            class="tactical-input px-3.5 py-3" />
        </div>

        <!-- Oficina -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            OFICINA <span class="font-normal text-outline">(opcional)</span>
          </label>
          <input v-model="oficina" type="text"
            placeholder="Ex: Auto Center Silva"
            class="tactical-input px-3.5 py-3" />
        </div>

        <!-- KM Atual -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            KM ATUAL <span class="font-normal text-outline">(opcional)</span>
          </label>
          <div class="relative">
            <input v-model="kmAtual" type="number" min="0"
              :placeholder="motoStore.motoAtiva?.km_atual?.toString() ?? 'Ex: 12450'"
              class="tactical-input pl-3.5 pr-12 py-3 text-lg" />
            <span class="absolute right-3 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-xs font-bold">KM</span>
          </div>
        </div>

        <!-- Data -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">DATA</label>
          <AppDateInput v-model="dataManutencao" tone="despesa" />
        </div>

        <!-- Erro -->
        <div v-if="erro"
          class="flex items-start gap-3 bg-error-container text-on-error-container text-sm font-label px-4 py-3 rounded-xl border border-error/30">
          <span class="material-symbols-outlined text-base mt-0.5 flex-shrink-0" aria-hidden="true">error</span>
          {{ erro }}
        </div>

        <!-- Sucesso -->
        <div v-if="sucesso"
          class="flex items-center gap-3 bg-primary-container/20 text-primary-container text-sm font-label px-4 py-3 rounded-xl border border-primary-container/30">
          <span class="material-symbols-outlined text-base flex-shrink-0" aria-hidden="true">check_circle</span>
          Manutenção registrada com sucesso!
        </div>

        <!-- Botão -->
        <button type="submit" :disabled="enviando || perguntarNovaManutencao"
          class="btn-primary h-16 text-base disabled:opacity-40 disabled:cursor-not-allowed">
          <span v-if="enviando" class="material-symbols-outlined animate-spin">refresh</span>
          <template v-else>
            <span class="material-symbols-outlined">build</span>
            REGISTRAR MANUTENÇÃO
          </template>
        </button>

      </form>
    </main>

    <!-- Modal pós-sucesso -->
    <div
      v-if="perguntarNovaManutencao"
      class="fixed inset-0 z-[80] bg-black/60 flex items-center justify-center px-5"
    >
      <div class="w-full max-w-sm bg-surface-container-high border border-outline-variant p-5 space-y-4">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-on-surface-variant">help</span>
          <p class="font-label text-[10px] font-bold tracking-[0.12em] text-on-surface uppercase">
            Nova manutenção
          </p>
        </div>

        <p class="font-body text-sm text-on-surface">
          Deseja registrar outra manutenção?
        </p>

        <div class="grid grid-cols-2 gap-2">
          <button
            type="button"
            class="h-11 bg-surface-bright text-on-surface font-label text-[10px] font-bold tracking-wider uppercase transition-colors hover:bg-surface-container"
            @click="prepararNovaManutencao"
          >
            Sim, nova
          </button>
          <button
            type="button"
            class="h-11 bg-surface-container-low text-on-surface-variant font-label text-[10px] font-bold tracking-wider uppercase border border-outline-variant transition-colors hover:text-on-surface hover:bg-surface-container"
            @click="irParaInicio"
          >
            Ir para início
          </button>
        </div>
      </div>
    </div>

  </div>
  </AppLayout>
</template>

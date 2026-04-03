<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMotoStore } from '@/stores/moto'
import { criarManutencao } from '@/api/manutencoes'
import { listarCategorias } from '@/api/categorias'
import type { CategoriaResposta } from '@/types'

const router    = useRouter()
const route     = useRoute()
const motoStore = useMotoStore()

// ── Estado ─────────────────────────────────────────────────────
const categoriaId     = ref<number | null>(null)
const valorTotal      = ref('')
const kmAtual         = ref('')
const descricaoServico = ref('')
const oficina         = ref('')
const tipoServico     = ref('')
const dataManutencao  = ref(new Date().toISOString().slice(0, 10))

const categoriasFiltradas = ref<CategoriaResposta[]>([])
const carregando = ref(false)
const enviando   = ref(false)
const erro       = ref('')
const sucesso    = ref(false)

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
    setTimeout(() => router.push({ name: 'dashboard' }), 1200)
  } catch {
    erro.value = 'Erro ao registrar manutenção. Tente novamente.'
  } finally {
    enviando.value = false
  }
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
        <button class="text-on-surface-variant hover:text-on-surface transition-colors p-1"
          @click="router.push({ name: 'dashboard' })">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <h1 class="text-primary-container font-headline font-black text-lg tracking-tight uppercase">
          GESTÃO MOTOCA
        </h1>
      </div>
      <span class="font-label text-[10px] tracking-widest text-on-surface-variant uppercase">
        MANUTENÇÃO
      </span>
    </header>

    <main class="px-5 py-6 space-y-6 max-w-md mx-auto">

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
              class="tactical-input pl-10 py-4 text-2xl font-bold"
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
            class="tactical-input py-3" />
        </div>

        <!-- Oficina -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            OFICINA <span class="font-normal text-outline">(opcional)</span>
          </label>
          <input v-model="oficina" type="text"
            placeholder="Ex: Auto Center Silva"
            class="tactical-input py-3" />
        </div>

        <!-- KM Atual -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            KM ATUAL <span class="font-normal text-outline">(opcional)</span>
          </label>
          <div class="relative">
            <input v-model="kmAtual" type="number" min="0"
              :placeholder="motoStore.motoAtiva?.km_atual?.toString() ?? 'Ex: 12450'"
              class="tactical-input py-3 pr-12 text-lg" />
            <span class="absolute right-3 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-xs font-bold">KM</span>
          </div>
        </div>

        <!-- Data -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">DATA</label>
          <input v-model="dataManutencao" type="date" class="tactical-input py-3 text-base" />
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
          Manutenção registrada! Redirecionando…
        </div>

        <!-- Botão -->
        <button type="submit" :disabled="enviando || sucesso"
          class="btn-primary h-16 text-base disabled:opacity-40 disabled:cursor-not-allowed">
          <span v-if="enviando" class="material-symbols-outlined animate-spin">refresh</span>
          <template v-else>
            <span class="material-symbols-outlined">build</span>
            REGISTRAR MANUTENÇÃO
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

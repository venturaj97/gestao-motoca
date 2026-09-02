<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMotoStore } from '@/stores/moto'
import { criarAbastecimento } from '@/api/abastecimentos'
import { listarCategorias } from '@/api/categorias'
import type { CategoriaResposta } from '@/types'
import AppDateInput from '@/components/AppDateInput.vue'
import AppLayout from '@/components/AppLayout.vue'

const router    = useRouter()
const motoStore = useMotoStore()

// ── Estado ─────────────────────────────────────────────────────
const categoriaId      = ref<number | null>(null)
const valorTotal       = ref('')
const litros           = ref('')
const kmAtual          = ref('')
const posto            = ref('')
const tipoCombustivel  = ref('')
const descricao        = ref('')
function hojeLocal(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const dataAbastecimento = ref(hojeLocal())

const categoriasFiltradas = ref<CategoriaResposta[]>([])
const carregando   = ref(false)
const enviando     = ref(false)
const erro         = ref('')
const sucesso      = ref(false)

const motoId = ref(motoStore.motoAtiva?.id)

// Calcula valor por litro
const valorPorLitro = ref('')
function calcularVPL() {
  const v = parseFloat(valorTotal.value.replace(',', '.'))
  const l = parseFloat(litros.value.replace(',', '.'))
  if (v > 0 && l > 0) {
    valorPorLitro.value = 'R$ ' + (v / l).toFixed(3).replace('.', ',') + '/L'
  } else {
    valorPorLitro.value = ''
  }
}

// ── Carregar categorias ─────────────────────────────────────────
async function carregar() {
  carregando.value = true
  try {
    const todas = await listarCategorias()
    // Filtra apenas categorias de DESPESA ativas (abastecimento é despesa)
    categoriasFiltradas.value = todas.filter(c => c.ativo && c.tipo === 'DESPESA')
    // Auto-seleciona se houver exatamente uma categoria de combustível
    const combustivel = categoriasFiltradas.value.find(c =>
      c.nome.toLowerCase().includes('combustível') ||
      c.nome.toLowerCase().includes('gasolina') ||
      c.nome.toLowerCase().includes('abastec')
    )
    if (combustivel) categoriaId.value = combustivel.id
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
  const vLitros = parseFloat(litros.value.replace(',', '.'))

  if (!valorTotal.value || isNaN(vTotal) || vTotal <= 0) {
    erro.value = 'Informe o valor total do abastecimento.'
    return
  }
  if (!litros.value || isNaN(vLitros) || vLitros <= 0) {
    erro.value = 'Informe a quantidade de litros.'
    return
  }
  if (!categoriaId.value) {
    erro.value = 'Selecione uma categoria.'
    return
  }

  enviando.value = true
  try {
    await criarAbastecimento({
      categoria_id: categoriaId.value,
      valor_total: vTotal,
      litros: vLitros,
      km_atual: kmAtual.value ? parseInt(kmAtual.value) : undefined,
      posto: posto.value || undefined,
      tipo_combustivel: tipoCombustivel.value || undefined,
      descricao: descricao.value || undefined,
      data_abastecimento: dataAbastecimento.value || undefined,
      moto_usuario_id: motoId.value,
    })
    sucesso.value = true
    // Atualiza KM na store se foi informado
    if (kmAtual.value && motoStore.motoAtiva) {
      motoStore.motoAtiva.km_atual = parseInt(kmAtual.value)
    }
    setTimeout(() => router.push({ name: 'dashboard' }), 1200)
  } catch {
    erro.value = 'Erro ao registrar abastecimento. Tente novamente.'
  } finally {
    enviando.value = false
  }
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
        <h2 class="font-headline font-extrabold text-4xl tracking-tighter uppercase leading-none">ABASTECER</h2>
        <p v-if="motoStore.motoAtiva" class="font-label text-[10px] text-primary-container tracking-widest uppercase mt-1">
          <span class="material-symbols-outlined text-xs align-middle">two_wheeler</span>
          {{ [motoStore.motoAtiva.marca_manual, motoStore.motoAtiva.modelo_manual].filter(Boolean).join(' ') || 'Moto ativa' }}
        </p>
      </div>

      <form class="space-y-5" @submit.prevent="handleSubmit">

        <!-- Valor + Litros lado a lado -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">VALOR TOTAL (R$)</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-sm">R$</span>
              <input :value="valorTotal" inputmode="decimal" placeholder="0,00"
                class="tactical-input pl-8 pr-3.5 py-3 text-xl font-bold"
                @input="e => { valorTotal = (e.target as HTMLInputElement).value; calcularVPL() }" />
            </div>
          </div>
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">LITROS</label>
            <div class="relative">
              <input :value="litros" inputmode="decimal" placeholder="0,000"
                class="tactical-input pl-3.5 pr-8 py-3 text-xl font-bold"
                @input="e => { litros = (e.target as HTMLInputElement).value; calcularVPL() }" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-xs">L</span>
            </div>
          </div>
        </div>

        <!-- Valor por litro calculado -->
        <div v-if="valorPorLitro"
          class="flex items-center gap-2 px-4 py-2 bg-primary-container/10 border-l-2 border-primary-container">
          <span class="material-symbols-outlined text-primary-container text-sm">local_gas_station</span>
          <span class="font-label text-xs font-bold text-primary-container tracking-wider">{{ valorPorLitro }}</span>
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

        <!-- Tipo combustível -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">COMBUSTÍVEL</label>
          <div class="grid grid-cols-3 gap-2">
            <button v-for="c in ['Gasolina', 'Etanol', 'GNV']" :key="c"
              type="button"
              class="h-10 font-label text-[10px] font-bold tracking-wider uppercase transition-all border-b-2"
              :class="tipoCombustivel === c
                ? 'bg-primary-container text-on-primary-fixed border-primary-container'
                : 'bg-surface-container text-on-surface-variant border-transparent hover:border-primary-container'"
              @click="tipoCombustivel = (tipoCombustivel === c ? '' : c)">
              {{ c }}
            </button>
          </div>
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

        <!-- Posto -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            POSTO <span class="font-normal text-outline">(opcional)</span>
          </label>
          <input v-model="posto" type="text" placeholder="Ex: Ipiranga Av. Brasil"
            class="tactical-input px-3.5 py-3" />
        </div>

        <!-- Data -->
        <div>
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">DATA</label>
          <AppDateInput v-model="dataAbastecimento" tone="despesa" />
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
          Abastecimento registrado! Redirecionando…
        </div>

        <!-- Botão -->
        <button type="submit" :disabled="enviando || sucesso"
          class="btn-primary h-16 text-base disabled:opacity-40 disabled:cursor-not-allowed">
          <span v-if="enviando" class="material-symbols-outlined animate-spin">refresh</span>
          <template v-else>
            <span class="material-symbols-outlined">local_gas_station</span>
            REGISTRAR ABASTECIMENTO
          </template>
        </button>

      </form>
    </main>

  </div>
  </AppLayout>
</template>

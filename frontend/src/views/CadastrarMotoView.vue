<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { listarMarcas, listarModelos, listarAnos, cadastrarMotoManual } from '@/api/motos'
import { useMotoStore } from '@/stores/moto'

const router = useRouter()
const motoStore = useMotoStore()

// ── Dados dos selects ─────────────────────────────────────
const marcas = ref<string[]>([])
const modelos = ref<{ id: number; nome: string }[]>([])
const anos = ref<{ id: number; ano: number }[]>([])

// ── Seleções do usuário ───────────────────────────────────
const marcaSelecionada = ref('')
const modeloSelecionado = ref<{ id: number; nome: string } | null>(null)
const anoSelecionado = ref<{ id: number; ano: number } | null>(null)
const cor = ref('')
const kmAtual = ref('')

// ── Estado de loading ─────────────────────────────────────
const carregandoMarcas = ref(false)
const carregandoModelos = ref(false)
const carregandoAnos = ref(false)
const salvando = ref(false)
const erro = ref('')

// ── Inicialização: carrega marcas ─────────────────────────
async function inicializar() {
  carregandoMarcas.value = true
  try {
    const res = await listarMarcas()
    marcas.value = res.marcas
  } catch {
    erro.value = 'Erro ao carregar marcas. Verifique a conexão.'
  } finally {
    carregandoMarcas.value = false
  }
}
inicializar()

// ── Watch: ao mudar marca, carrega modelos ────────────────
watch(marcaSelecionada, async (novaMarca) => {
  modeloSelecionado.value = null
  anoSelecionado.value = null
  modelos.value = []
  anos.value = []

  if (!novaMarca) return
  carregandoModelos.value = true
  try {
    // A API retorna lista direta: [{id, marca, modelo, cilindrada_cc}]
    const res = await listarModelos(novaMarca)
    const lista = Array.isArray(res) ? res : (res as any).modelos ?? []
    modelos.value = lista.map((m: any) => ({ id: m.id, nome: m.modelo }))
  } catch {
    erro.value = 'Erro ao carregar modelos.'
  } finally {
    carregandoModelos.value = false
  }
})

// ── Watch: ao mudar modelo, carrega anos ──────────────────
watch(modeloSelecionado, async (novoModelo) => {
  anoSelecionado.value = null
  anos.value = []

  if (!novoModelo) return
  carregandoAnos.value = true
  try {
    // A API retorna { modelo_id, anos: [{id, ano}] }
    const res = await listarAnos(novoModelo.id)
    anos.value = Array.isArray(res) ? res : (res as any).anos ?? []
  } catch {
    erro.value = 'Erro ao carregar anos.'
  } finally {
    carregandoAnos.value = false
  }
})

// ── Computed: formulário válido? ──────────────────────────
const podeSalvar = computed(() => {
  const km = parseInt(kmAtual.value)
  return (
    marcaSelecionada.value &&
    modeloSelecionado.value &&
    anoSelecionado.value &&
    !isNaN(km) && km >= 0
  )
})

// ── Handler: selecionar modelo via string do select ───────
function onModeloChange(e: Event) {
  const id = parseInt((e.target as HTMLSelectElement).value)
  modeloSelecionado.value = modelos.value.find(m => m.id === id) ?? null
}

function onAnoChange(e: Event) {
  const id = parseInt((e.target as HTMLSelectElement).value)
  anoSelecionado.value = anos.value.find(a => a.id === id) ?? null
}

// ── Salvar ────────────────────────────────────────────────
async function salvar() {
  erro.value = ''
  const km = parseInt(kmAtual.value)
  if (!podeSalvar.value || isNaN(km)) {
    erro.value = 'Preencha todos os campos obrigatórios.'
    return
  }

  salvando.value = true
  try {
    const moto = await cadastrarMotoManual({
      moto_versao_id: anoSelecionado.value!.id,
      km_atual: km,
      cor: cor.value.trim() || undefined,
    })
    motoStore.adicionarMoto(moto)
    motoStore.carregado = true
    router.push({ name: 'dashboard' })
  } catch (e: any) {
    erro.value = e?.response?.data?.detail ?? 'Erro ao salvar. Tente novamente.'
  } finally {
    salvando.value = false
  }
}
</script>

<template>
  <div class="bg-background text-on-surface font-body min-h-screen flex flex-col">

    <!-- TopBar compacta -->
    <header class="flex items-center gap-3 px-5 h-14 border-l-4 border-primary-container bg-background sticky top-0 z-10">
      <button
        class="text-on-surface-variant hover:text-on-surface transition-colors p-1"
        @click="router.push({ name: 'vincular-moto' })"
      >
        <span class="material-symbols-outlined">arrow_back</span>
      </button>
      <div>
        <p class="font-label text-[9px] tracking-[0.25em] text-primary-container uppercase">CADASTRO MANUAL</p>
        <h1 class="font-headline font-black text-lg tracking-tight leading-none uppercase">DADOS DA MOTO</h1>
      </div>
    </header>

    <main class="flex-1 flex flex-col px-5 pb-6 pt-5 max-w-md mx-auto w-full gap-4">

      <!-- Erro global -->
      <div v-if="erro" class="bg-error-container text-on-error-container font-label text-xs px-4 py-3 tracking-wide">
        {{ erro }}
      </div>

      <!-- MARCA -->
      <div class="space-y-1">
        <label class="font-label text-[9px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
          MARCA *
        </label>
        <div
          class="bg-surface-container-low border-b-2 transition-all"
          :class="marcaSelecionada ? 'border-primary-container' : 'border-outline-variant'"
        >
          <select
            v-model="marcaSelecionada"
            :disabled="carregandoMarcas"
            class="w-full bg-transparent border-none text-on-surface font-headline font-medium
                   py-3 px-4 focus:ring-0 focus:outline-none appearance-none cursor-pointer
                   disabled:opacity-50 disabled:cursor-wait"
          >
            <option value="" disabled>
              {{ carregandoMarcas ? 'Carregando...' : 'Selecione a marca' }}
            </option>
            <option v-for="m in marcas" :key="m" :value="m" class="bg-surface-container text-on-surface">
              {{ m }}
            </option>
          </select>
        </div>
      </div>

      <!-- MODELO -->
      <div class="space-y-1">
        <label
          class="font-label text-[9px] font-bold tracking-[0.2em] uppercase transition-colors"
          :class="marcaSelecionada ? 'text-on-surface-variant' : 'text-outline'"
        >
          MODELO *
        </label>
        <div
          class="bg-surface-container-low border-b-2 transition-all"
          :class="modeloSelecionado ? 'border-primary-container' : 'border-outline-variant'"
        >
          <select
            :value="modeloSelecionado?.id ?? ''"
            :disabled="!marcaSelecionada || carregandoModelos"
            class="w-full bg-transparent border-none text-on-surface font-headline font-medium
                   py-3 px-4 focus:ring-0 focus:outline-none appearance-none cursor-pointer
                   disabled:opacity-40 disabled:cursor-not-allowed"
            @change="onModeloChange"
          >
            <option value="" disabled>
              {{ !marcaSelecionada ? 'Selecione a marca primeiro' : carregandoModelos ? 'Carregando...' : 'Selecione o modelo' }}
            </option>
            <option v-for="m in modelos" :key="m.id" :value="m.id" class="bg-surface-container text-on-surface">
              {{ m.nome }}
            </option>
          </select>
        </div>
      </div>

      <!-- ANO + COR (grid 2 colunas) -->
      <div class="grid grid-cols-2 gap-3">
        <!-- ANO -->
        <div class="space-y-1">
          <label
            class="font-label text-[9px] font-bold tracking-[0.2em] uppercase transition-colors"
            :class="modeloSelecionado ? 'text-on-surface-variant' : 'text-outline'"
          >
            ANO *
          </label>
          <div
            class="bg-surface-container-low border-b-2 transition-all"
            :class="anoSelecionado ? 'border-primary-container' : 'border-outline-variant'"
          >
            <select
              :value="anoSelecionado?.id ?? ''"
              :disabled="!modeloSelecionado || carregandoAnos"
              class="w-full bg-transparent border-none text-on-surface font-headline font-medium
                     py-3 px-4 focus:ring-0 focus:outline-none appearance-none cursor-pointer
                     disabled:opacity-40 disabled:cursor-not-allowed"
              @change="onAnoChange"
            >
              <option value="" disabled>
                {{ !modeloSelecionado ? '—' : carregandoAnos ? '...' : 'Ano' }}
              </option>
              <option v-for="a in anos" :key="a.id" :value="a.id" class="bg-surface-container text-on-surface">
                {{ a.ano }}
              </option>
            </select>
          </div>
        </div>

        <!-- COR -->
        <div class="space-y-1">
          <label class="font-label text-[9px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
            COR
          </label>
          <div
            class="bg-surface-container-low border-b-2 transition-all"
            :class="cor ? 'border-primary-container' : 'border-outline-variant'"
          >
            <input
              v-model="cor"
              type="text"
              placeholder="Preto, Vermelho..."
              class="w-full bg-transparent border-none text-on-surface font-body
                     py-3 px-4 focus:ring-0 focus:outline-none placeholder:text-outline/40 placeholder:text-sm"
            />
          </div>
        </div>
      </div>

      <!-- KM ATUAL -->
      <div class="space-y-1">
        <label class="font-label text-[9px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
          QUILOMETRAGEM ATUAL *
        </label>
        <div
          class="bg-surface-container-low border-b-2 transition-all flex items-center"
          :class="kmAtual ? 'border-primary-container' : 'border-outline-variant'"
        >
          <input
            v-model="kmAtual"
            type="number"
            min="0"
            placeholder="12450"
            class="flex-1 bg-transparent border-none text-on-surface font-headline font-bold text-xl
                   py-3 px-4 focus:ring-0 focus:outline-none placeholder:text-outline/40 placeholder:text-base
                   placeholder:font-body"
          />
          <span class="pr-4 font-label text-[9px] font-bold text-outline-variant uppercase tracking-widest">KM</span>
        </div>
      </div>

      <!-- Indicador de progresso do formulário -->
      <div class="flex gap-1 py-1">
        <div class="h-[2px] flex-1 transition-all"
          :class="marcaSelecionada ? 'bg-primary-container' : 'bg-surface-container-high'"></div>
        <div class="h-[2px] flex-1 transition-all"
          :class="modeloSelecionado ? 'bg-primary-container' : 'bg-surface-container-high'"></div>
        <div class="h-[2px] flex-1 transition-all"
          :class="anoSelecionado ? 'bg-primary-container' : 'bg-surface-container-high'"></div>
        <div class="h-[2px] flex-1 transition-all"
          :class="kmAtual ? 'bg-primary-container' : 'bg-surface-container-high'"></div>
      </div>

      <!-- Botão salvar (sticky no bottom) -->
      <div class="mt-auto pt-2">
        <button
          :disabled="!podeSalvar || salvando"
          class="w-full h-14 bg-primary-container text-on-primary-fixed font-headline font-black
                 text-sm tracking-[0.2em] uppercase flex items-center justify-center gap-3
                 transition-all active:scale-[0.98] hover:brightness-110
                 disabled:opacity-30 disabled:cursor-not-allowed"
          @click="salvar"
        >
          <span v-if="salvando" class="material-symbols-outlined animate-spin">refresh</span>
          <template v-else>
            SALVAR MOTO
            <span class="material-symbols-outlined text-sm">arrow_forward_ios</span>
          </template>
        </button>
      </div>

    </main>
  </div>
</template>

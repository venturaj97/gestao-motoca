<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { consultarPlaca, cadastrarMotoPorPlaca } from '@/api/motos'
import { useMotoStore } from '@/stores/moto'
import type { ConsultaPlacaResposta } from '@/types'

const router = useRouter()
const motoStore = useMotoStore()

// ── Estado ──────────────────────────────────────────────────
const placa = ref('')
const kmInicial = ref('')
const etapa = ref<'digitar' | 'confirmar' | 'km'>('digitar')
const carregando = ref(false)
const erro = ref('')
const dadosConsulta = ref<ConsultaPlacaResposta | null>(null)

// ── Computed ─────────────────────────────────────────────────
const placaFormatada = computed(() => {
  const v = placa.value.replace(/[^A-Za-z0-9]/g, '').toUpperCase()
  if (v.length <= 3) return v
  return v.slice(0, 3) + '-' + v.slice(3, 7)
})

const placaValida = computed(() => {
  const raw = placa.value.replace(/[^A-Za-z0-9]/g, '')
  // Mercosul: AAA0A00 (7 chars) ou padrão antigo: AAA0000 (7 chars)
  return raw.length === 7
})

// Nome do veículo a partir dos dados da consulta
const nomeVeiculo = computed(() => {
  if (!dadosConsulta.value) return ''
  const d = dadosConsulta.value.dados as Record<string, string>
  const marca = d.marca || d.MARCA || ''
  const modelo = d.modelo || d.MODELO || ''
  const ano = d.ano_modelo || d.ANO_MODELO || d.ano || d.ANO || ''
  return [marca, modelo, ano].filter(Boolean).join(' · ')
})

// ── Handlers ─────────────────────────────────────────────────
function handleInput(e: Event) {
  const raw = (e.target as HTMLInputElement).value
    .replace(/[^A-Za-z0-9]/g, '')  // remove tudo que não for letra ou número
    .toUpperCase()
    .slice(0, 7)
  placa.value = raw
}

// Bloqueia digitação de especiais (traço, ponto, espaço etc) direto no teclado
function handleKeydown(e: KeyboardEvent) {
  const allowed = /^[A-Za-z0-9]$/.test(e.key)
  const control = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Enter'].includes(e.key)
  if (!allowed && !control) {
    e.preventDefault()
  }
}

async function consultar() {
  if (!placaValida.value) {
    erro.value = 'Placa inválida. Informe 7 caracteres (ex: ABC1D23 ou ABC1234).'
    return
  }
  erro.value = ''
  carregando.value = true
  try {
    const raw = placa.value.replace(/[^A-Za-z0-9]/g, '').toUpperCase()
    dadosConsulta.value = await consultarPlaca(raw)
    etapa.value = 'confirmar'
  } catch (e: any) {
    const status = e?.response?.status
    if (status === 404) {
      erro.value = 'Placa não encontrada. Verifique os dados ou cadastre manualmente.'
    } else if (status === 409) {
      erro.value = 'Esta placa já está vinculada à sua conta.'
    } else {
      erro.value = 'Erro ao consultar placa. Tente novamente.'
    }
  } finally {
    carregando.value = false
  }
}

function irParaKm() {
  const km = parseInt(kmInicial.value)
  if (!kmInicial.value || isNaN(km) || km < 0) {
    erro.value = 'Informe o quilometragem atual da moto.'
    return
  }
  erro.value = ''
  etapa.value = 'km'
}

async function vincular() {
  const km = parseInt(kmInicial.value)
  if (isNaN(km) || km < 0) {
    erro.value = 'KM inválido.'
    return
  }
  erro.value = ''
  carregando.value = true
  try {
    const raw = placa.value.replace(/[^A-Za-z0-9]/g, '').toUpperCase()
    const moto = await cadastrarMotoPorPlaca({ placa: raw, km_atual: km })
    motoStore.adicionarMoto(moto)
    // Marca como carregado para o guard não recarregar
    motoStore.carregado = true
    router.push({ name: 'dashboard' })
  } catch (e: any) {
    const status = e?.response?.status
    if (status === 409) {
      erro.value = 'Esta placa já está vinculada à sua conta.'
    } else {
      erro.value = 'Erro ao vincular moto. Tente novamente.'
    }
    etapa.value = 'confirmar'
  } finally {
    carregando.value = false
  }
}

function voltar() {
  erro.value = ''
  if (etapa.value === 'confirmar') {
    etapa.value = 'digitar'
    dadosConsulta.value = null
  } else if (etapa.value === 'km') {
    etapa.value = 'confirmar'
  }
}
</script>

<template>
  <div class="bg-background text-on-background font-body min-h-screen flex flex-col">

    <!-- TopBar -->
    <header class="bg-background flex justify-between items-center w-full px-6 py-4 h-16 sticky top-0 z-50 border-l-4 border-primary-container">
      <div class="flex items-center gap-3">
        <button
          v-if="etapa !== 'digitar'"
          class="text-on-surface-variant hover:text-on-surface transition-colors p-1 mr-1"
          @click="voltar"
        >
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <span class="text-primary-container font-headline font-bold text-xl tracking-wider uppercase">
          GESTÃO MOTOCA
        </span>
      </div>
      <span class="text-on-surface-variant font-label text-[10px] tracking-widest uppercase">
        {{ etapa === 'digitar' ? 'REGISTRO' : etapa === 'confirmar' ? 'VERIFICAR' : 'ODÔMETRO' }}
      </span>
    </header>

    <main class="flex-grow flex flex-col items-center px-6 pt-8 pb-24 max-w-md mx-auto w-full">

      <!-- ══════════════════════════════════════════
           ETAPA 1 — Digitar placa
      ══════════════════════════════════════════ -->
      <template v-if="etapa === 'digitar'">

        <!-- Header -->
        <div class="w-full mb-10">
          <div class="flex items-center gap-2 mb-3">
            <div class="h-[3px] w-8 bg-primary-container"></div>
            <span class="font-label text-[10px] font-bold tracking-[0.25em] text-primary-container uppercase">
              SISTEMA DE REGISTRO
            </span>
          </div>
          <h1 class="font-headline text-5xl font-extrabold tracking-tighter leading-none mb-3">
            VINCULAR<br/>MOTO
          </h1>
          <p class="text-on-surface-variant text-sm leading-relaxed max-w-[85%]">
            Insira a placa Mercosul ou modelo antigo para sincronizar os dados do veículo.
          </p>
        </div>

        <!-- Placa input estilo Mercosul -->
        <div class="w-full space-y-6">
          <div class="relative group">
            <!-- Cantos decorativos táticos -->
            <div class="absolute -top-3 -left-3 w-5 h-5 border-t-2 border-l-2 border-primary-container opacity-40"></div>
            <div class="absolute -bottom-3 -right-3 w-5 h-5 border-b-2 border-r-2 border-primary-container opacity-40"></div>

            <!-- Placa estilo Mercosul -->
            <div class="bg-[#d4d4d4] p-1.5 shadow-[inset_0_2px_4px_rgba(0,0,0,0.5)]">
              <div class="bg-white border-[3px] border-black flex flex-col">
                <!-- Header azul Mercosul -->
                <div class="bg-[#003399] h-7 flex items-center justify-between px-3">
                  <div class="flex items-center gap-1">
                    <div class="w-3 h-2 bg-green-500 opacity-80 rounded-sm"></div>
                    <div class="w-3 h-2 bg-yellow-400 opacity-80 rounded-sm"></div>
                  </div>
                  <span class="text-white font-headline font-bold text-[10px] tracking-widest">
                    BRASIL
                  </span>
                  <div class="w-6"></div>
                </div>
              <!-- Input da placa -->
                <div class="py-4 px-2 flex items-center justify-center">
                  <input
                    type="text"
                    :value="placaFormatada"
                    maxlength="7"
                    placeholder="Digite a placa"
                    autocomplete="off"
                    autocorrect="off"
                    spellcheck="false"
                    inputmode="text"
                    class="w-full bg-transparent border-none text-center font-headline text-6xl
                           font-bold text-black tracking-tighter focus:ring-0 focus:outline-none
                           uppercase placeholder:text-zinc-300 placeholder:text-3xl"
                    @input="handleInput"
                    @keydown="handleKeydown"
                    @keyup.enter="consultar"
                    @paste.prevent="(e) => {
                      const txt = e.clipboardData?.getData('text') ?? ''
                      const clean = txt.replace(/[^A-Za-z0-9]/g, '').toUpperCase().slice(0, 7)
                      placa = clean
                    }"
                  />
                </div>
              </div>
            </div>

            <!-- Aviso: sem traço -->
            <div class="flex items-center gap-2 mt-2 px-1">
              <span class="material-symbols-outlined text-primary-container text-sm">info</span>
              <p class="font-label text-[10px] tracking-wide text-on-surface-variant">
                Apenas letras e números — sem traço, ponto ou espaço.
              </p>
            </div>

            <!-- Exemplos decorativos de placa (não clicáveis) -->
            <div class="mt-5">
              <p class="font-label text-[9px] tracking-[0.2em] text-on-surface-variant uppercase mb-3">
                FORMATOS DE PLACA ACEITOS
              </p>
              <div class="flex gap-3">

                <!-- Placa Mercosul -->
                <div class="flex-1 flex flex-col items-center gap-1.5">
                  <div class="w-full bg-[#d4d4d4] p-1 shadow-inner">
                    <div class="bg-white border-[2px] border-black">
                      <div class="bg-[#003399] h-5 flex items-center justify-between px-2">
                        <div class="flex items-center gap-0.5">
                          <div class="w-2 h-1.5 bg-green-500 opacity-80 rounded-sm"></div>
                          <div class="w-2 h-1.5 bg-yellow-400 opacity-80 rounded-sm"></div>
                        </div>
                        <span class="text-white font-headline font-bold text-[7px] tracking-widest">BRASIL</span>
                        <div class="w-4"></div>
                      </div>
                      <div class="py-1.5 px-1 text-center">
                        <span class="font-headline font-black text-black tracking-tighter text-xl">
                          KVU8F92
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center gap-1">
                    <div class="h-[2px] w-3 bg-primary-container"></div>
                    <span class="font-label text-[9px] tracking-widest text-primary-container uppercase font-bold">MERCOSUL</span>
                  </div>
                  <p class="font-label text-[8px] text-on-surface-variant text-center">3 letras · 1 nº · 1 letra · 2 nº</p>
                </div>

                <!-- Separador -->
                <div class="flex items-center">
                  <span class="text-outline-variant font-label text-xs">ou</span>
                </div>

                <!-- Placa Antiga -->
                <div class="flex-1 flex flex-col items-center gap-1.5">
                  <div class="w-full bg-[#d4d4d4] p-1 shadow-inner">
                    <div class="bg-white border-[2px] border-black">
                      <div class="bg-[#e0e0e0] h-5 flex items-center justify-center border-b border-zinc-300">
                        <span class="font-headline font-bold text-black text-[7px] tracking-widest">AM · MANAUS</span>
                      </div>
                      <div class="py-1.5 px-1 text-center">
                        <span class="font-headline font-black text-black tracking-tighter text-xl">
                          KVU·8592
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center gap-1">
                    <div class="h-[2px] w-3 bg-on-surface-variant"></div>
                    <span class="font-label text-[9px] tracking-widest text-on-surface-variant uppercase font-bold">ANTIGO</span>
                  </div>
                  <p class="font-label text-[8px] text-on-surface-variant text-center">3 letras · 4 números</p>
                </div>

              </div>
            </div>

          </div>

          <!-- Erro -->
          <div v-if="erro" class="bg-error-container text-on-error-container font-label text-sm px-4 py-3 tracking-wide">
            {{ erro }}
          </div>

          <!-- Botão consultar -->
          <button
            :disabled="!placaValida || carregando"
            class="w-full h-16 bg-primary-container text-on-primary-fixed font-headline font-black
                   text-base tracking-widest uppercase flex items-center justify-center gap-3
                   transition-all active:scale-[0.98] active:brightness-110
                   disabled:opacity-40 disabled:cursor-not-allowed"
            @click="consultar"
          >
            <span v-if="carregando" class="material-symbols-outlined animate-spin">refresh</span>
            <template v-else>
              <span class="material-symbols-outlined">search</span>
              CONSULTAR PLACA
            </template>
          </button>

          <!-- Links secundários -->
          <div class="flex flex-col gap-5 items-center pt-2">
            <button
              class="font-label text-[11px] font-bold tracking-widest text-primary hover:text-primary-container
                     uppercase border-b border-primary/30 pb-0.5 transition-colors"
              @click="router.push({ name: 'cadastrar-moto' })"
            >
              Cadastrar manualmente
            </button>
            <button
              class="font-label text-[11px] font-bold tracking-widest text-on-surface-variant
                     hover:text-on-surface uppercase transition-colors"
              @click="router.push({ name: 'dashboard' })"
            >
              Pular por enquanto →
            </button>
          </div>
        </div>

        <!-- Rodapé técnico decorativo -->
        <div class="mt-auto pt-16 w-full flex justify-between items-end opacity-[0.12]">
          <div class="font-mono text-[8px] leading-tight">
            SYS_VER: 2.0.4-TACTICAL<br/>
            ENCRYPT: AES-256-GCM<br/>
            SIGNAL: HIGH_RES_DATA
          </div>
          <div class="h-10 w-10 border border-on-surface-variant flex items-center justify-center">
            <span class="material-symbols-outlined text-xs">qr_code_2</span>
          </div>
        </div>
      </template>

      <!-- ══════════════════════════════════════════
           ETAPA 2 — Confirmar dados da placa
      ══════════════════════════════════════════ -->
      <template v-else-if="etapa === 'confirmar' && dadosConsulta">

        <div class="w-full mb-8">
          <div class="flex items-center gap-2 mb-3">
            <div class="h-[3px] w-8 bg-primary-container"></div>
            <span class="font-label text-[10px] font-bold tracking-[0.25em] text-primary-container uppercase">
              DADOS ENCONTRADOS
            </span>
          </div>
          <h2 class="font-headline text-4xl font-extrabold tracking-tighter leading-none">
            CONFIRMAR<br/>VEÍCULO
          </h2>
        </div>

        <!-- Card de dados do veículo -->
        <div class="w-full bg-surface-container-low border-l-4 border-primary-container p-6 mb-6 relative">
          <div class="absolute top-4 right-4">
            <span class="material-symbols-outlined text-primary-container text-3xl">
              verified
            </span>
          </div>

          <p class="font-label text-[10px] tracking-[0.2em] text-primary-container mb-1 uppercase">
            PLACA CONSULTADA
          </p>
          <p class="font-headline text-3xl font-black tracking-widest text-on-surface mb-4">
            {{ dadosConsulta.placa_consultada }}
          </p>

          <p class="font-label text-[10px] tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            VEÍCULO IDENTIFICADO
          </p>
          <p class="font-headline font-bold text-lg text-on-surface leading-tight">
            {{ nomeVeiculo || 'Dados parciais disponíveis' }}
          </p>

          <!-- Tags de status da API -->
          <div class="flex gap-2 mt-4">
            <span
              v-if="dadosConsulta.fipe_disponivel"
              class="text-[9px] font-label font-bold tracking-wider px-2 py-1 bg-primary-container/20 text-primary-fixed-dim uppercase"
            >
              FIPE ✓
            </span>
            <span
              v-if="dadosConsulta.extra_disponivel"
              class="text-[9px] font-label font-bold tracking-wider px-2 py-1 bg-surface-container text-on-surface-variant uppercase"
            >
              EXTRA ✓
            </span>
          </div>
        </div>

        <!-- Erro -->
        <div v-if="erro" class="w-full bg-error-container text-on-error-container font-label text-sm px-4 py-3 tracking-wide mb-4">
          {{ erro }}
        </div>

        <!-- Campo KM -->
        <div class="w-full mb-6">
          <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
            QUILOMETRAGEM ATUAL (KM)
          </label>
          <div class="relative">
            <input
              v-model="kmInicial"
              type="number"
              min="0"
              placeholder="Ex: 12450"
              class="w-full h-16 bg-surface-container-lowest border-0 border-b-2 border-outline-variant
                     focus:border-primary-container focus:outline-none focus:ring-0
                     text-on-surface font-headline font-bold text-2xl tracking-wide
                     placeholder:text-outline placeholder:text-base px-4 transition-all"
            />
            <span class="absolute right-4 top-1/2 -translate-y-1/2 font-label text-outline-variant text-sm font-bold">
              KM
            </span>
          </div>
        </div>

        <!-- Botão vincular -->
        <button
          :disabled="carregando"
          class="w-full h-16 bg-primary-container text-on-primary-fixed font-headline font-black
                 text-base tracking-widest uppercase flex items-center justify-center gap-3
                 transition-all active:scale-[0.98] active:brightness-110
                 disabled:opacity-40 disabled:cursor-not-allowed"
          @click="vincular"
        >
          <span v-if="carregando" class="material-symbols-outlined animate-spin">refresh</span>
          <template v-else>
            <span class="material-symbols-outlined">link</span>
            VINCULAR MOTO
          </template>
        </button>

        <button
          class="mt-4 w-full h-12 font-label font-bold text-[11px] tracking-widest text-on-surface-variant
                 hover:text-on-surface uppercase flex items-center justify-center gap-2 transition-colors"
          @click="voltar"
        >
          <span class="material-symbols-outlined text-sm">arrow_back</span>
          Digitar outra placa
        </button>

      </template>

    </main>
  </div>
</template>

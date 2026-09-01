<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { loadStripe, type StripeEmbeddedCheckout } from '@stripe/stripe-js'
import { criarCheckoutStripe, obterPrecosAssinatura } from '@/api/assinaturas'
import type { PrecosAssinaturaResposta } from '@/types'

const props = defineProps<{
  titulo?: string
  descricao?: string
  mostrarModal?: boolean
}>()

const emit = defineEmits(['fechar'])

const carregando = ref(false)
const erro = ref('')
const periodoSelecionado = ref<'mensal' | 'anual'>('mensal')
const precos = ref<PrecosAssinaturaResposta | null>(null)
const modoEmbedded = ref(false)

let embeddedCheckoutInstance: StripeEmbeddedCheckout | null = null

onMounted(async () => {
  try {
    precos.value = await obterPrecosAssinatura()
  } catch (e) {
    console.error('Erro ao carregar preços:', e)
  }
})

onUnmounted(() => {
  destruirCheckout()
})

function destruirCheckout() {
  if (embeddedCheckoutInstance) {
    try {
      embeddedCheckoutInstance.destroy()
    } catch (e) {
      console.error('Erro ao destruir checkout:', e)
    }
    embeddedCheckoutInstance = null
  }
}

function voltarParaPlanos() {
  destruirCheckout()
  modoEmbedded.value = false
  erro.value = ''
}

async function assinar() {
  try {
    carregando.value = true
    erro.value = ''
    
    const priceId = periodoSelecionado.value === 'anual' 
      ? precos.value?.anual.price_id 
      : precos.value?.mensal.price_id

    const publishableKey = precos.value?.stripe_publishable_key

    if (!priceId || !publishableKey) {
      erro.value = 'Configuração de pagamento indisponível no momento.'
      return
    }

    const { client_secret, checkout_url } = await criarCheckoutStripe(priceId)

    if (client_secret) {
      modoEmbedded.value = true
      await nextTick()

      const stripe = await loadStripe(publishableKey)
      if (!stripe) {
        erro.value = 'Não foi possível carregar a integração com o Stripe.'
        modoEmbedded.value = false
        return
      }

      destruirCheckout()

      const initEmbedded = (stripe as any).createEmbeddedCheckoutPage || (stripe as any).initEmbeddedCheckout
      const checkout = await initEmbedded.call(stripe, { clientSecret: client_secret })
      embeddedCheckoutInstance = checkout
      if (embeddedCheckoutInstance) {
        embeddedCheckoutInstance.mount('#stripe-checkout-mount')
      }
    } else if (checkout_url) {
      window.location.href = checkout_url
    } else {
      erro.value = 'Erro ao gerar sessão de pagamento.'
    }
  } catch (err: any) {
    console.error('Erro no checkout:', err)
    erro.value = err?.response?.data?.detail || err?.message || 'Erro ao iniciar checkout. Tente novamente.'
    modoEmbedded.value = false
  } finally {
    carregando.value = false
  }
}
</script>

<template>
  <div class="relative overflow-hidden rounded-2xl border border-amber-500/30 bg-gradient-to-b from-amber-500/10 via-slate-900/90 to-slate-950 p-4 md:p-8 shadow-2xl backdrop-blur-xl">
    <!-- Efeito de brilho em segundo plano -->
    <div class="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-amber-500/10 blur-3xl"></div>
    <div class="pointer-events-none absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-yellow-500/10 blur-3xl"></div>

    <!-- MODO EMBEDDED CHECKOUT (Formulário Incorporado) -->
    <div v-if="modoEmbedded" class="relative z-10 space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <button
          type="button"
          @click="voltarParaPlanos"
          class="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:bg-slate-700 hover:text-white transition-all"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Voltar para escolha de plano
        </button>

        <span class="rounded-full bg-amber-500/20 px-3 py-1 text-[10px] font-extrabold uppercase tracking-wider text-amber-300 border border-amber-500/30">
          {{ periodoSelecionado === 'anual' ? 'Plano Anual' : 'Plano Mensal' }}
        </span>
      </div>

      <!-- Container do Stripe Checkout Incorporado -->
      <div class="min-h-[450px] w-full rounded-2xl bg-white p-2 md:p-4 shadow-inner overflow-hidden">
        <div id="stripe-checkout-mount"></div>
      </div>
    </div>

    <!-- MODO APRESENTAÇÃO / SELEÇÃO DE PLANO -->
    <div v-else class="relative z-10 flex flex-col items-center text-center">
      <!-- Badge PRO -->
      <div class="mb-4 inline-flex items-center gap-2 rounded-full border border-amber-400/40 bg-amber-500/20 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-amber-300 shadow-lg shadow-amber-500/10">
        <span>⭐</span>
        <span>Recurso Exclusivo Gestão Motoca PRO</span>
      </div>

      <h2 class="text-2xl font-black tracking-tight text-white md:text-3xl">
        {{ titulo || 'Desbloqueie o Máximo Potencial do Seu Dia a Dia' }}
      </h2>
      
      <p class="mt-2 max-w-lg text-sm text-slate-300 md:text-base">
        {{ descricao || 'Tenha acesso total a Relatórios Inteligentes, Metas Semanais/Mensais e Cofres de Economia para acelerar seus resultados.' }}
      </p>

      <!-- Benefícios PRO -->
      <div class="my-6 grid w-full max-w-md grid-cols-1 gap-3 text-left sm:grid-cols-2">
        <div class="flex items-center gap-2.5 rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-xs text-slate-200 backdrop-blur-sm">
          <span class="text-base">📊</span>
          <span>Relatórios de Rendimento e Custo por KM</span>
        </div>
        <div class="flex items-center gap-2.5 rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-xs text-slate-200 backdrop-blur-sm">
          <span class="text-base">🎯</span>
          <span>Metas Semanais e Alertas de Progresso</span>
        </div>
        <div class="flex items-center gap-2.5 rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-xs text-slate-200 backdrop-blur-sm">
          <span class="text-base">🏦</span>
          <span>Cofres para Manutenção e IPVA</span>
        </div>
        <div class="flex items-center gap-2.5 rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-xs text-slate-200 backdrop-blur-sm">
          <span class="text-base">💡</span>
          <span>Recomendações Inteligentes</span>
        </div>
      </div>

      <!-- Seletor de Plano -->
      <div class="mb-6 flex w-full max-w-xs rounded-xl bg-slate-900/80 p-1 border border-slate-800">
        <button
          type="button"
          @click="periodoSelecionado = 'mensal'"
          :class="[
            'flex-1 rounded-lg py-2 text-xs font-semibold transition-all duration-200',
            periodoSelecionado === 'mensal'
              ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-slate-950 font-bold shadow'
              : 'text-slate-400 hover:text-white'
          ]"
        >
          Mensal (R$ 9,90/mês)
        </button>
        <button
          type="button"
          @click="periodoSelecionado = 'anual'"
          :class="[
            'flex-1 rounded-lg py-2 text-xs font-semibold transition-all duration-200 relative',
            periodoSelecionado === 'anual'
              ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-slate-950 font-bold shadow'
              : 'text-slate-400 hover:text-white'
          ]"
        >
          Anual (R$ 89,90)
          <span class="absolute -top-2 -right-1 rounded-full bg-emerald-500 px-1.5 py-0.5 text-[9px] font-black uppercase text-slate-950">
            -24%
          </span>
        </button>
      </div>

      <!-- Mensagem de Erro -->
      <div v-if="erro" class="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
        {{ erro }}
      </div>

      <!-- Botão de Ação -->
      <button
        type="button"
        @click="assinar"
        :disabled="carregando"
        class="w-full max-w-xs rounded-xl bg-gradient-to-r from-amber-400 via-amber-500 to-yellow-500 px-6 py-3.5 text-sm font-extrabold text-slate-950 shadow-lg shadow-amber-500/25 transition-all hover:scale-[1.02] hover:from-amber-300 hover:to-yellow-400 active:scale-95 disabled:opacity-50"
      >
        <span v-if="carregando" class="flex items-center justify-center gap-2">
          <svg class="h-4 w-4 animate-spin text-slate-950" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Iniciando Pagamento...
        </span>
        <span v-else class="flex items-center justify-center gap-2">
          <span>Quero Ser PRO Agora</span>
          <span>🚀</span>
        </span>
      </button>

      <!-- Métodos de Pagamento Aceitos -->
      <div class="mt-4 flex flex-wrap items-center justify-center gap-3 text-[11px] text-slate-400">
        <span class="flex items-center gap-1">
          <svg class="h-4 w-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Pix, Google Pay & Apple Pay
        </span>
        <span>•</span>
        <span class="flex items-center gap-1">
          <svg class="h-4 w-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Cartão de Crédito
        </span>
        <span>•</span>
        <span class="flex items-center gap-1">
          <svg class="h-4 w-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Cancela quando quiser
        </span>
      </div>
    </div>
  </div>
</template>

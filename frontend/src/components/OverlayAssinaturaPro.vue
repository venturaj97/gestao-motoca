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
const periodoSelecionado = ref<'mensal' | 'anual' | 'pix_avulso'>('pix_avulso')
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
    
    // Tenta carregar os preços caso a busca no onMounted tenha falhado ou ainda não finalizou
    if (!precos.value) {
      try {
        precos.value = await obterPrecosAssinatura()
      } catch (e: any) {
        console.error('Erro ao carregar preços no checkout:', e)
        erro.value = e?.response?.data?.detail || 'Não foi possível carregar as informações de pagamento do servidor. Tente novamente.'
        return
      }
    }

    let priceId = ''
    if (periodoSelecionado.value === 'anual') {
      priceId = precos.value?.anual?.price_id || ''
    } else if (periodoSelecionado.value === 'pix_avulso') {
      priceId = precos.value?.pix_avulso?.price_id || precos.value?.mensal?.price_id || ''
    } else {
      priceId = precos.value?.mensal?.price_id || ''
    }

    const publishableKey = precos.value?.stripe_publishable_key

    if (!publishableKey) {
      erro.value = 'A chave pública do Stripe (STRIPE_PUBLISHABLE_KEY) não está configurada no servidor.'
      return
    }

    if (!priceId) {
      erro.value = 'O ID do preço não está configurado no servidor.'
      return
    }

    const { client_secret, checkout_url } = await criarCheckoutStripe(priceId)

    if (client_secret) {
      modoEmbedded.value = true
      await nextTick()

      const stripe = await loadStripe(publishableKey)
      if (!stripe) {
        erro.value = 'Não foi possível carregar a integração com o Stripe. Verifique a chave de integração.'
        modoEmbedded.value = false
        return
      }

      destruirCheckout()

      const initEmbedded = (stripe as any).createEmbeddedCheckoutPage || (stripe as any).initEmbeddedCheckout
      const checkout = await initEmbedded.call(stripe, {
        clientSecret: client_secret,
      })
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
  <div
    role="region"
    aria-label="Plano Gestão Motoca PRO"
    class="relative overflow-hidden rounded-2xl border border-amber-500/30 bg-gradient-to-b from-amber-500/10 via-slate-900/95 to-slate-950 p-5 md:p-8 shadow-2xl backdrop-blur-xl"
  >
    <!-- Efeito de iluminação sutil de fundo -->
    <div class="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-amber-500/10 blur-3xl"></div>
    <div class="pointer-events-none absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-emerald-500/10 blur-3xl"></div>

    <!-- MODO EMBEDDED CHECKOUT (Formulário Incorporado) -->
    <div v-if="modoEmbedded" class="relative z-10 space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <button
          type="button"
          @click="voltarParaPlanos"
          aria-label="Voltar para a escolha de planos"
          class="flex min-h-[44px] items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-700 hover:text-white transition-all focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Voltar para escolha de plano
        </button>

        <span class="rounded-full bg-amber-500/20 px-3 py-1.5 text-[11px] font-extrabold uppercase tracking-wider text-amber-300 border border-amber-500/30">
          {{ periodoSelecionado === 'anual' ? 'Plano Anual' : periodoSelecionado === 'pix_avulso' ? 'Pix Avulso (30 dias)' : 'Plano Mensal' }}
        </span>
      </div>

      <!-- Container do Stripe Checkout Incorporado com Tema Escuro -->
      <div class="min-h-[450px] w-full rounded-2xl bg-slate-900/90 border border-slate-800/80 p-3 md:p-5 shadow-2xl overflow-hidden backdrop-blur-md">
        <div id="stripe-checkout-mount"></div>
      </div>
    </div>

    <!-- MODO APRESENTAÇÃO / SELEÇÃO DE PLANO -->
    <div v-else class="relative z-10 flex flex-col items-center text-center">
      <!-- Badge PRO -->
      <div class="mb-4 inline-flex items-center gap-2 rounded-full border border-amber-400/40 bg-amber-500/15 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-amber-300 shadow-md">
        <span aria-hidden="true">⭐</span>
        <span>Recurso Exclusivo Gestão Motoca PRO</span>
      </div>

      <h2 class="text-2xl font-extrabold tracking-tight text-white md:text-3xl">
        {{ titulo || 'Desbloqueie o Máximo Potencial do Seu Dia a Dia' }}
      </h2>
      
      <p class="mt-2 max-w-lg text-sm text-slate-300 md:text-base leading-relaxed">
        {{ descricao || 'Tenha acesso total a Relatórios Inteligentes, Metas Semanais/Mensais e Cofres de Economia para acelerar seus resultados.' }}
      </p>

      <!-- Benefícios PRO -->
      <div class="my-6 grid w-full max-w-md grid-cols-1 gap-3 text-left sm:grid-cols-2">
        <div class="flex items-center gap-3 rounded-xl border border-slate-800/80 bg-slate-900/70 p-3.5 text-xs text-slate-200 backdrop-blur-sm shadow-sm">
          <span class="text-base" aria-hidden="true">📊</span>
          <span>Relatórios de Rendimento e Custo por KM</span>
        </div>
        <div class="flex items-center gap-3 rounded-xl border border-slate-800/80 bg-slate-900/70 p-3.5 text-xs text-slate-200 backdrop-blur-sm shadow-sm">
          <span class="text-base" aria-hidden="true">🎯</span>
          <span>Metas Semanais e Alertas de Progresso</span>
        </div>
        <div class="flex items-center gap-3 rounded-xl border border-slate-800/80 bg-slate-900/70 p-3.5 text-xs text-slate-200 backdrop-blur-sm shadow-sm">
          <span class="text-base" aria-hidden="true">🏦</span>
          <span>Cofres para Manutenção e IPVA</span>
        </div>
        <div class="flex items-center gap-3 rounded-xl border border-slate-800/80 bg-slate-900/70 p-3.5 text-xs text-slate-200 backdrop-blur-sm shadow-sm">
          <span class="text-base" aria-hidden="true">💡</span>
          <span>Recomendações Inteligentes</span>
        </div>
      </div>

      <!-- Seletor de Plano -->
      <div class="mb-6 flex w-full max-w-md flex-col gap-2 sm:flex-row rounded-xl bg-slate-950/80 p-1.5 border border-slate-800" role="radiogroup" aria-label="Selecione o plano de assinatura">
        <button
          type="button"
          role="radio"
          :aria-checked="periodoSelecionado === 'pix_avulso'"
          @click="periodoSelecionado = 'pix_avulso'"
          :class="[
            'flex-1 min-h-[44px] rounded-lg py-2.5 px-3 text-xs font-black transition-all duration-200 relative flex items-center justify-center',
            periodoSelecionado === 'pix_avulso'
              ? 'bg-emerald-500 text-emerald-950 shadow-md ring-1 ring-emerald-400'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          ]"
        >
          ⚡ Pix Avulso (R$ 9,99)
        </button>
        <button
          type="button"
          role="radio"
          :aria-checked="periodoSelecionado === 'mensal'"
          @click="periodoSelecionado = 'mensal'"
          :class="[
            'flex-1 min-h-[44px] rounded-lg py-2.5 px-3 text-xs font-black transition-all duration-200 flex items-center justify-center',
            periodoSelecionado === 'mensal'
              ? 'bg-amber-400 text-amber-950 shadow-md ring-1 ring-amber-300'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          ]"
        >
          Mensal (R$ 9,90/mês)
        </button>
        <button
          type="button"
          role="radio"
          :aria-checked="periodoSelecionado === 'anual'"
          @click="periodoSelecionado = 'anual'"
          :class="[
            'flex-1 min-h-[44px] rounded-lg py-2.5 px-3 text-xs font-black transition-all duration-200 relative flex items-center justify-center',
            periodoSelecionado === 'anual'
              ? 'bg-amber-400 text-amber-950 shadow-md ring-1 ring-amber-300'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          ]"
        >
          Anual (R$ 89,90)
          <span class="absolute -top-2.5 -right-1 rounded-full bg-emerald-400 px-2 py-0.5 text-[9px] font-black uppercase text-emerald-950 border border-emerald-950/20 shadow">
            -24%
          </span>
        </button>
      </div>

      <!-- Mensagem de Erro -->
      <div v-if="erro" class="mb-4 w-full max-w-md rounded-xl border border-red-500/40 bg-red-500/15 p-3 text-xs font-medium text-red-300">
        {{ erro }}
      </div>

      <!-- Botão de Ação -->
      <button
        type="button"
        @click="assinar"
        :disabled="carregando"
        class="w-full max-w-xs min-h-[48px] rounded-xl bg-amber-400 px-6 py-3.5 text-sm font-black text-amber-950 shadow-lg shadow-amber-500/20 transition-all hover:bg-amber-300 active:scale-95 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-amber-300"
      >
        <span v-if="carregando" class="flex items-center justify-center gap-2">
          <svg class="h-4 w-4 animate-spin text-amber-950" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Iniciando Pagamento...
        </span>
        <span v-else class="flex items-center justify-center gap-2">
          <span v-if="periodoSelecionado === 'pix_avulso'">Pagar R$ 9,99 com Pix ⚡</span>
          <span v-else-if="periodoSelecionado === 'anual'">Assinar Plano Anual 🚀</span>
          <span v-else>Quero Ser PRO Agora 🚀</span>
        </span>
      </button>

      <!-- Métodos de Pagamento Aceitos -->
      <div class="mt-5 flex flex-wrap items-center justify-center gap-3 text-[11px] font-medium text-slate-400">
        <span class="flex items-center gap-1.5">
          <svg class="h-4 w-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Pix, Google Pay & Apple Pay
        </span>
        <span aria-hidden="true">•</span>
        <span class="flex items-center gap-1.5">
          <svg class="h-4 w-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Cartão de Crédito
        </span>
        <span aria-hidden="true">•</span>
        <span class="flex items-center gap-1.5">
          <svg class="h-4 w-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Cancela quando quiser
        </span>
      </div>
    </div>
  </div>
</template>

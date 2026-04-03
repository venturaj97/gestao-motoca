<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMotoStore } from '@/stores/moto'
import { obterVisaoMes } from '@/api/visaoMes'
import type { VisaoMesResposta } from '@/types'

const router  = useRouter()
const route   = useRoute()
const auth    = useAuthStore()
const motoStore = useMotoStore()

// ── Estado ───────────────────────────────────────────────────
const visao        = ref<VisaoMesResposta | null>(null)
const carregando   = ref(true)
const erroCarregar = ref('')

// ── Dados derivados do usuário e da moto ─────────────────────
const primeiroNome = computed(() => {
  const nome = auth.usuario?.nome ?? ''
  return nome.split(' ')[0].toUpperCase()
})

const motoAtiva = computed(() => motoStore.motoAtiva)

const nomeMoto = computed(() => {
  const m = motoAtiva.value
  if (!m) return '—'
  const marca  = m.marca_manual  ?? ''
  const modelo = m.modelo_manual ?? ''
  return [marca, modelo].filter(Boolean).join(' ') || '—'
})

// ── Dados financeiros do mês ──────────────────────────────────
const ganho    = computed(() => visao.value?.ganho?.total_periodo    ?? '0.00')
const despesa  = computed(() => visao.value?.despesa?.total_periodo  ?? '0.00')
const saldo    = computed(() => visao.value?.saldo_mes               ?? '0.00')
const kmAtual  = computed(() => motoAtiva.value?.km_atual            ?? null)

// ── Formatações ───────────────────────────────────────────────
function formatarReais(valor: string | number): string {
  const n = typeof valor === 'string' ? parseFloat(valor) : valor
  if (isNaN(n)) return 'R$ 0,00'
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatarKm(km: number): string {
  return km.toLocaleString('pt-BR') + ' KM'
}

const hojeFormatado = computed(() => {
  return new Date().toLocaleDateString('pt-BR', {
    weekday: 'long', day: '2-digit', month: 'long',
  }).toUpperCase()
})

const saldoPositivo = computed(() => {
  const n = parseFloat(saldo.value)
  return isNaN(n) || n >= 0
})

// ── Alertas de manutenção (usa resumo_executivo do backend) ───
const alertas = computed(() => visao.value?.resumo_executivo ?? [])

// ── Carregar dados ────────────────────────────────────────────
async function carregar() {
  carregando.value   = true
  erroCarregar.value = ''
  try {
    const motoId = motoAtiva.value?.id
    visao.value  = await obterVisaoMes(undefined, undefined, motoId)
  } catch {
    erroCarregar.value = 'Não foi possível carregar os dados do mês.'
  } finally {
    carregando.value = false
  }
}

// ── Logout ────────────────────────────────────────────────────
function logout() {
  auth.logout()
  motoStore.limpar()
  router.push({ name: 'login' })
}

// ── Nav ───────────────────────────────────────────────────────
const navItems = [
  { name: 'dashboard',  label: 'Início',    icon: 'dashboard'       },
  { name: 'historico',  label: 'Histórico', icon: 'history'         },
  { name: 'lancar',     label: 'Lançar',    icon: 'add_box'         },
  { name: 'manutencao', label: 'Manutenção',icon: 'build'           },
  { name: 'moto',       label: 'Moto',      icon: 'motorcycle'      },
]

function isActive(name: string) {
  return route.name === name
}

function navIconStyle(name: string): Record<string, string> {
  return isActive(name) ? { fontVariationSettings: '"FILL" 1' } : {}
}

onMounted(carregar)
</script>

<template>
  <div class="bg-background text-on-surface font-body min-h-screen pb-24">

    <!-- ══ TopBar ══════════════════════════════════════════════ -->
    <header class="bg-background flex justify-between items-center w-full px-5 h-16 sticky top-0 z-50 border-l-4 border-primary-container">
      <div class="flex items-center gap-3">
        <!-- Avatar inicial do usuário -->
        <div class="w-9 h-9 bg-surface-container-highest flex items-center justify-center">
          <span class="font-headline font-black text-primary-container text-sm">
            {{ primeiroNome.charAt(0) }}
          </span>
        </div>
        <h1 class="text-primary-container font-headline font-black text-lg tracking-tight uppercase">
          GESTÃO MOTOCA
        </h1>
      </div>

      <div class="flex items-center gap-3">
        <!-- Recarregar -->
        <button
          class="text-on-surface-variant hover:text-primary-container transition-colors"
          :class="{ 'animate-spin': carregando }"
          @click="carregar"
        >
          <span class="material-symbols-outlined text-xl">refresh</span>
        </button>
        <!-- Logout -->
        <button
          class="text-on-surface-variant hover:text-secondary transition-colors"
          title="Sair"
          @click="logout"
        >
          <span class="material-symbols-outlined text-xl">logout</span>
        </button>
      </div>
    </header>

    <!-- ══ Conteúdo principal ══════════════════════════════════ -->
    <main class="px-5 py-5 space-y-6 max-w-md mx-auto">

      <!-- Boas-vindas -->
      <section class="space-y-0.5">
        <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase">
          {{ hojeFormatado }}
        </p>
        <h2 class="font-headline font-extrabold text-3xl uppercase tracking-tight">
          OLÁ, {{ primeiroNome }}
        </h2>
        <p v-if="nomeMoto !== '—'" class="font-label text-[10px] text-primary-container tracking-widest uppercase">
          <span class="material-symbols-outlined text-xs align-middle">two_wheeler</span>
          {{ nomeMoto }}
        </p>
      </section>

      <!-- Erro de carregamento -->
      <div v-if="erroCarregar" class="bg-error-container text-on-error-container font-label text-xs px-4 py-3 flex items-center gap-2">
        <span class="material-symbols-outlined text-sm">warning</span>
        {{ erroCarregar }}
      </div>

      <!-- Skeleton enquanto carrega -->
      <template v-if="carregando && !visao">
        <div class="space-y-4 animate-pulse">
          <div class="h-32 bg-surface-container-low"></div>
          <div class="grid grid-cols-2 gap-3">
            <div class="h-20 bg-surface-container-low"></div>
            <div class="h-20 bg-surface-container-low"></div>
          </div>
        </div>
      </template>

      <!-- Dados reais -->
      <template v-else>

        <!-- ── Card principal: Saldo do mês ─────────────────── -->
        <div class="bg-surface-container-low p-5 relative overflow-hidden">
          <!-- Glow decorativo -->
          <div class="absolute top-0 right-0 w-40 h-40 bg-primary-container/10 blur-3xl rounded-full -mr-20 -mt-20 pointer-events-none"></div>

          <p class="font-label text-[9px] font-bold tracking-[0.3em] text-on-surface-variant uppercase mb-2">
            SALDO DO MÊS
          </p>
          <div class="flex items-baseline gap-2">
            <span
              class="font-headline font-black text-5xl leading-none"
              :class="saldoPositivo ? 'text-primary-container' : 'text-secondary'"
            >
              {{ formatarReais(saldo) }}
            </span>
          </div>

          <!-- Indicador tendência fictício de exemplo -->
          <div class="mt-3 flex items-center gap-1.5 text-[9px] font-label font-bold"
               :class="saldoPositivo ? 'text-primary-container' : 'text-secondary'">
            <span class="material-symbols-outlined text-sm">
              {{ saldoPositivo ? 'trending_up' : 'trending_down' }}
            </span>
            <span>{{ saldoPositivo ? 'SALDO POSITIVO' : 'SALDO NEGATIVO' }}</span>
          </div>
        </div>

        <!-- ── Monitor tático (link) ──────────────────────────  -->
        <button
          class="w-full flex items-center justify-between p-4 bg-surface-container border border-outline-variant
                 hover:bg-surface-container-high transition-all active:scale-[0.98] group"
          @click="router.push({ name: 'historico' })"
        >
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-primary-container">analytics</span>
            <span class="font-label text-xs font-bold tracking-[0.2em] uppercase">MONITOR TÁTICO</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="font-label text-[9px] tracking-tight text-on-surface-variant">LIVE DATA</span>
            <span class="material-symbols-outlined text-sm animate-pulse text-primary-container">sensors</span>
          </div>
        </button>

        <!-- ── Grid de métricas secundárias ──────────────────── -->
        <div class="grid grid-cols-2 gap-3">
          <!-- Ganhos -->
          <div class="bg-surface-container p-4">
            <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant mb-1 uppercase">GANHOS</p>
            <p class="font-headline font-bold text-lg text-on-surface">{{ formatarReais(ganho) }}</p>
          </div>

          <!-- Despesas -->
          <div class="bg-surface-container p-4">
            <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant mb-1 uppercase">DESPESAS</p>
            <p class="font-headline font-bold text-lg text-secondary">{{ formatarReais(despesa) }}</p>
          </div>

          <!-- KM atual (ocupa linha inteira) -->
          <div class="bg-surface-container p-4 col-span-2 flex justify-between items-center border-l-4 border-primary-container">
            <div>
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant mb-1 uppercase">KM ATUAL</p>
              <p class="font-headline font-bold text-lg text-on-surface">
                {{ kmAtual !== null ? formatarKm(kmAtual) : '—' }}
              </p>
            </div>
            <span class="material-symbols-outlined text-primary-container opacity-40 text-4xl">speed</span>
          </div>
        </div>

        <!-- ── Ações rápidas ──────────────────────────────────── -->
        <section class="space-y-3">
          <h3 class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
            AÇÕES RÁPIDAS
          </h3>
          <div class="grid grid-cols-2 gap-3">
            <!-- Lançar Ganho -->
            <button
              class="flex flex-col items-center justify-center gap-3 bg-surface-container-high py-6
                     hover:bg-surface-bright transition-colors active:scale-[0.97] group"
              @click="router.push({ name: 'lancar' })"
            >
              <div class="w-12 h-12 bg-primary-container/10 flex items-center justify-center text-primary-container">
                <span class="material-symbols-outlined text-2xl">add_circle</span>
              </div>
              <span class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant
                           group-hover:text-primary-container transition-colors uppercase">
                LANÇAR GANHO
              </span>
            </button>

            <!-- Lançar Despesa -->
            <button
              class="flex flex-col items-center justify-center gap-3 bg-surface-container-high py-6
                     hover:bg-surface-bright transition-colors active:scale-[0.97] group"
              @click="router.push({ name: 'lancar' })"
            >
              <div class="w-12 h-12 bg-secondary-container/20 flex items-center justify-center text-secondary">
                <span class="material-symbols-outlined text-2xl">remove_circle</span>
              </div>
              <span class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant
                           group-hover:text-secondary transition-colors uppercase">
                LANÇAR DESPESA
              </span>
            </button>

            <!-- Manutenção -->
            <button
              class="flex items-center gap-3 bg-surface-container p-4 hover:bg-surface-bright transition-colors group active:scale-[0.97]"
              @click="router.push({ name: 'manutencao' })"
            >
              <span class="material-symbols-outlined text-primary-container text-xl group-hover:scale-110 transition-transform">build</span>
              <span class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">MANUTENÇÃO</span>
            </button>

            <!-- Abastecer -->
            <button
              class="flex items-center gap-3 bg-surface-container p-4 hover:bg-surface-bright transition-colors group active:scale-[0.97]"
              @click="router.push({ name: 'abastecer' })"
            >
              <span class="material-symbols-outlined text-primary-container text-xl group-hover:scale-110 transition-transform">local_gas_station</span>
              <span class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">ABASTECER</span>
            </button>
          </div>
        </section>

        <!-- ── Alertas / Resumo executivo ─────────────────────── -->
        <div
          v-if="alertas.length"
          class="bg-surface-container-lowest p-5 border-l-4 border-secondary"
        >
          <p class="font-label text-[9px] font-bold tracking-widest text-secondary uppercase mb-2">
            ALERTAS DO MÊS
          </p>
          <ul class="space-y-1.5">
            <li
              v-for="(alerta, i) in alertas"
              :key="i"
              class="flex items-start gap-2 text-xs text-on-surface-variant font-body"
            >
              <span class="material-symbols-outlined text-secondary text-sm mt-0.5 flex-shrink-0">warning</span>
              {{ alerta }}
            </li>
          </ul>
        </div>

      </template>
    </main>

    <!-- ══ Bottom Navigation Bar ═══════════════════════════════ -->
    <nav class="fixed bottom-0 left-0 w-full z-50 h-20 bg-background border-t-4 border-surface-container grid grid-cols-5">
      <button
        v-for="item in navItems"
        :key="item.name"
        class="flex flex-col items-center justify-center h-full w-full transition-colors duration-100"
        :class="isActive(item.name)
          ? 'bg-primary-container text-on-primary-fixed'
          : 'text-on-surface-variant hover:bg-surface-container'"
        @click="router.push({ name: item.name })"
      >
        <span
          class="material-symbols-outlined"
          :style="navIconStyle(item.name)"
        >
          {{ item.icon }}
        </span>
        <span class="font-label text-[9px] font-bold uppercase tracking-[0.08em] mt-0.5">
          {{ item.label }}
        </span>
      </button>
    </nav>

  </div>
</template>

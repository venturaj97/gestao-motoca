<template>
  <div class="pb-28">
    <AppTopBar />

    <main class="space-y-8 px-6 py-6">
      <PageIntro :title="dashboardTitle" :eyebrow="dashboardEyebrow" />
      <div v-if="monthlyViewQuery.isLoading.value" class="grid gap-4">
        <LoadingBlock />
        <LoadingBlock />
      </div>

      <div v-else class="flex gap-2 overflow-auto pb-2">
        <button class="bg-primary-container px-6 py-2 font-command text-xs font-bold uppercase tracking-[0.18em] text-black">Hoje</button>
        <button class="bg-surface-container px-6 py-2 font-command text-xs font-bold uppercase tracking-[0.18em] text-zinc-400">Semana</button>
        <button class="bg-surface-container px-6 py-2 font-command text-xs font-bold uppercase tracking-[0.18em] text-zinc-400">Mês</button>
      </div>

      <div v-if="monthlyViewQuery.isError.value" class="border-l-4 border-secondary bg-secondary-container/10 p-5 text-sm text-zinc-100">
        {{ dashboardError }}
      </div>

      <template v-else-if="monthlyView">
        <div class="relative overflow-hidden bg-surface-container-low p-6">
          <div class="absolute right-[-2rem] top-[-2rem] h-28 w-28 rounded-full bg-primary-container/10 blur-3xl" />
          <p class="tactical-label mb-2">Saldo do mês</p>
          <p class="font-command text-5xl font-black tracking-tight text-primary-container">
            {{ formatCurrency(monthlyView.saldo_mes) }}
          </p>
          <div class="mt-4 flex items-center gap-2 text-xs font-command font-bold uppercase tracking-[0.18em] text-primary-container">
            <span class="material-symbols-outlined text-base">monitoring</span>
            {{ monthlyView.ano }}/{{ String(monthlyView.mes).padStart(2, '0') }}
          </div>
        </div>

        <RouterLink
          to="/monitor"
          class="flex items-center justify-between border-2 border-zinc-700 bg-surface-container px-4 py-4 font-command text-xs font-bold uppercase tracking-[0.18em]"
        >
          <span class="flex items-center gap-3">
            <span class="material-symbols-outlined text-primary-container">analytics</span>
            Monitor tático
          </span>
          <span class="text-zinc-400">LIVE DATA</span>
        </RouterLink>

        <div class="grid grid-cols-2 gap-4">
          <TacticalStatCard label="Ganhos" :value="formatCurrency(monthlyView.ganho.total_periodo)" />
          <TacticalStatCard label="Despesas" :value="formatCurrency(monthlyView.despesa.total_periodo)" value-class="text-secondary" />
          <TacticalStatCard
            class="col-span-2"
            label="Lançamentos"
            :value="`${monthlyView.ganho.quantidade_lancamentos + monthlyView.despesa.quantidade_lancamentos} no período`"
            accent="border-primary-container"
          />
        </div>

        <section class="space-y-4">
          <p class="tactical-label">Ações rápidas</p>
          <div class="grid grid-cols-2 gap-4">
            <RouterLink to="/lancar/ganho" class="flex flex-col items-center justify-center gap-3 bg-surface-container-high py-6">
              <span class="material-symbols-outlined text-3xl text-primary-container">add_circle</span>
              <span class="font-command text-[10px] font-bold uppercase tracking-[0.18em]">Lançar ganho</span>
            </RouterLink>
            <RouterLink to="/lancar/despesa" class="flex flex-col items-center justify-center gap-3 bg-surface-container-high py-6">
              <span class="material-symbols-outlined text-3xl text-secondary">remove_circle</span>
              <span class="font-command text-[10px] font-bold uppercase tracking-[0.18em]">Lançar despesa</span>
            </RouterLink>
            <RouterLink to="/manutencao" class="flex items-center gap-3 bg-surface-container p-4">
              <span class="material-symbols-outlined text-primary-container">build</span>
              <span class="font-command text-[10px] font-bold uppercase tracking-[0.18em]">Manutenção</span>
            </RouterLink>
            <RouterLink to="/abastecimento" class="flex items-center gap-3 bg-surface-container p-4">
              <span class="material-symbols-outlined text-primary-container">local_gas_station</span>
              <span class="font-command text-[10px] font-bold uppercase tracking-[0.18em]">Abastecer</span>
            </RouterLink>
          </div>
        </section>

        <div v-if="monthlyView.resumo_executivo.length" class="tactical-card">
          <p class="tactical-label mb-3">Resumo executivo</p>
          <ul class="space-y-2 text-sm text-zinc-300">
            <li v-for="item in monthlyView.resumo_executivo.slice(0, 3)" :key="item">{{ item }}</li>
          </ul>
        </div>

        <div v-if="monthlyView.alertas_mensais.length" class="status-strip border-secondary bg-surface-container-lowest flex items-center justify-between">
          <div>
            <p class="tactical-label text-secondary">Alertas de meta</p>
            <p class="font-command text-lg font-bold">{{ monthlyView.alertas_mensais.length }} exigem atenção</p>
          </div>
          <span class="material-symbols-outlined text-secondary">warning</span>
        </div>

        <EmptyStateCard
          v-else
          eyebrow="Sem alertas"
          title="Operação estável"
          description="Ainda não há alertas mensais críticos para este período."
        />
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppTopBar from '@/components/AppTopBar.vue'
import EmptyStateCard from '@/components/EmptyStateCard.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import PageIntro from '@/components/PageIntro.vue'
import TacticalStatCard from '@/components/TacticalStatCard.vue'
import { useMonthlyViewQuery } from '@/modules/dashboard/queries'
import { getApiErrorMessage } from '@/shared/api/errors'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const monthlyViewQuery = useMonthlyViewQuery()

const monthlyView = computed(() => monthlyViewQuery.data.value)
const dashboardError = computed(() => getApiErrorMessage(monthlyViewQuery.error.value, 'Não foi possível carregar a visão mensal.'))
const dashboardTitle = computed(() => `BEM-VINDO, ${(auth.user?.nome ?? 'PILOTO').toUpperCase()}`)
const dashboardEyebrow = computed(() =>
  new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
    .format(new Date())
    .toUpperCase(),
)

const formatCurrency = (value: string) =>
  new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(Number(value))
</script>

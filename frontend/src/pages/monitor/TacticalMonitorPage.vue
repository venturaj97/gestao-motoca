<template>
  <div class="pb-28">
    <AppTopBar eyebrow="LIVE DATA" />
    <main class="space-y-6 px-4 py-4">
      <PageIntro title="MONITOR TÁTICO" eyebrow="Inteligência operacional" description="Visão analítica rápida dos melhores períodos, metas e sinais do mês." />

      <div class="grid gap-4">
        <TacticalStatCard label="Melhor dia" value="SEXTA-FEIRA" hint="R$ 412,00 de lucro médio" accent="border-primary-container" />
        <TacticalStatCard label="Semana de pico" value="2ª SEMANA" hint="Maior sequência de ganhos consistentes" />
      </div>

      <div class="tactical-card">
        <p class="tactical-label mb-3">Resumo executivo</p>
        <ul class="space-y-2 text-sm text-zinc-300">
          <li>Ganhos por corrida acima da média no período noturno.</li>
          <li>Despesa com combustível representa 18% da receita do mês.</li>
          <li>Manutenção preventiva recomendada ainda nesta semana.</li>
        </ul>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <TacticalStatCard label="Ticket médio" value="R$ 21,70" />
        <TacticalStatCard label="Meta mensal" value="63%" value-class="text-primary-container" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppTopBar from '@/components/AppTopBar.vue'
import PageIntro from '@/components/PageIntro.vue'
import TacticalStatCard from '@/components/TacticalStatCard.vue'
</script>

<template>
  <div class="pb-28">
    <AppTopBar />
    <main class="space-y-6 px-4 py-4">
      <PageIntro title="HISTÓRICO" eyebrow="Telemetria financeira" />

      <div class="status-strip border-primary-container bg-surface-container-low flex items-center justify-between">
        <div>
          <p class="tactical-label text-primary-container">Saldo do período</p>
          <p class="font-command text-2xl font-black">+ R$ 272,50</p>
        </div>
        <span class="material-symbols-outlined text-primary-container">monitoring</span>
      </div>

      <section v-for="group in groups" :key="group.date" class="space-y-3">
        <div class="flex items-center gap-4">
          <h3 class="font-command text-lg font-black tracking-tight text-zinc-500">{{ group.date }}</h3>
          <div class="h-px flex-1 bg-surface-container-high" />
          <span class="font-command text-[10px] font-bold uppercase tracking-[0.16em] text-primary-dim">
            {{ group.balance }}
          </span>
        </div>

        <div class="space-y-1">
          <article
            v-for="item in group.items"
            :key="item.title"
            class="flex items-center gap-4 bg-surface-container p-4"
            :class="item.positive ? 'border-l-4 border-primary-container' : 'border-l-4 border-secondary-container'"
          >
            <div class="flex-1">
              <p class="tactical-label mb-1">{{ item.label }}</p>
              <p class="truncate text-sm">{{ item.title }}</p>
            </div>
            <div class="text-right">
              <p class="font-command text-lg font-bold" :class="item.positive ? 'text-primary-container' : 'text-secondary'">
                {{ item.value }}
              </p>
              <p class="text-[10px] font-command font-bold text-zinc-600">{{ item.time }}</p>
            </div>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppTopBar from '@/components/AppTopBar.vue'
import PageIntro from '@/components/PageIntro.vue'

const groups = [
  {
    date: '24 OUT',
    balance: 'SALDO: + R$ 272,50',
    items: [
      { label: 'ENTREGA #8821', title: 'Restaurante Sabor Urbano', value: '+ R$ 24,50', time: '14:32', positive: true },
      { label: 'COMBUSTÍVEL', title: 'Posto Petro-Norte', value: '- R$ 52,00', time: '11:15', positive: false },
    ],
  },
  {
    date: '23 OUT',
    balance: 'SALDO: + R$ 210,00',
    items: [
      { label: 'ENTREGA #8790', title: 'Logística Rápida SA', value: '+ R$ 85,00', time: '19:20', positive: true },
      { label: 'MANUTENÇÃO', title: 'Oficina do Grau', value: '- R$ 120,00', time: '16:00', positive: false },
    ],
  },
]
</script>

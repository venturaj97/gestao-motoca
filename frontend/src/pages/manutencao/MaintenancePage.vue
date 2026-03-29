<template>
  <div class="pb-28">
    <AppTopBar />
    <main class="space-y-6 px-4 py-4">
      <PageIntro title="MANUTENÇÃO" eyebrow="Vida útil" description="Acompanhe itens críticos e registre serviços de forma tática." />

      <div class="status-strip border-secondary bg-surface-container-lowest flex items-center justify-between">
        <div>
          <p class="tactical-label text-secondary">ALERTA</p>
          <p class="font-command text-lg font-bold">ÓLEO EM 150 KM</p>
        </div>
        <span class="material-symbols-outlined text-secondary">warning</span>
      </div>

      <div class="grid gap-3">
        <div class="tactical-card border-l-4 border-primary-container">
          <p class="tactical-label mb-2">Estado atual</p>
          <p class="font-command text-2xl font-black text-primary-container">NOMINAL</p>
          <p class="mt-2 text-sm text-zinc-400">Freios, corrente e pneus dentro da faixa segura.</p>
        </div>
        <div class="tactical-card border-l-4 border-secondary">
          <p class="tactical-label mb-2 text-secondary">Próxima revisão</p>
          <p class="font-command text-2xl font-black">15.000 KM</p>
          <p class="mt-2 text-sm text-zinc-400">Revisão geral recomendada em oficina de confiança.</p>
        </div>
      </div>

      <button class="flex h-16 w-full items-center justify-center bg-surface-container font-command text-sm font-bold uppercase tracking-[0.18em]">
        Registrar manutenção
      </button>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppTopBar from '@/components/AppTopBar.vue'
import PageIntro from '@/components/PageIntro.vue'
</script>

<template>
  <div class="pb-28">
    <AppTopBar border-class="border-b-4 border-surface-container-low bg-background" />

    <main class="flex min-h-[calc(100vh-9rem)] flex-col gap-4 p-4">
      <PageIntro title="SELECIONAR LANÇAMENTO" eyebrow="Fluxo de Telemetria" />

      <div class="flex flex-1 flex-col gap-4">
        <RouterLink
          to="/lancar/ganho"
          class="relative flex flex-1 flex-col items-center justify-center overflow-hidden bg-primary-container text-black"
        >
          <span class="absolute left-4 top-4 font-command text-xs font-black uppercase opacity-25">Transaction_Type: IN</span>
          <span class="material-symbols-outlined mb-3 text-8xl">arrow_upward</span>
          <span class="font-command text-2xl font-black uppercase tracking-[0.18em]">Lançar ganho</span>
        </RouterLink>

        <RouterLink
          to="/lancar/despesa"
          class="relative flex flex-1 flex-col items-center justify-center overflow-hidden bg-secondary text-background"
        >
          <span class="absolute left-4 top-4 font-command text-xs font-black uppercase opacity-25">Transaction_Type: OUT</span>
          <span class="material-symbols-outlined mb-3 text-8xl">arrow_downward</span>
          <span class="font-command text-2xl font-black uppercase tracking-[0.18em]">Lançar despesa</span>
        </RouterLink>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import AppTopBar from '@/components/AppTopBar.vue'
import PageIntro from '@/components/PageIntro.vue'
</script>

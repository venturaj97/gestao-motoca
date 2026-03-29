<template>
  <div class="pb-28">
    <AppTopBar />
    <main class="mx-auto flex max-w-md flex-col gap-4 px-4 pb-24 pt-4">
      <div class="flex gap-1 bg-surface-container-low p-1">
        <button class="flex-1 bg-primary-container py-3 font-command text-xs font-bold uppercase tracking-[0.15em] text-black">Corrida/entrega</button>
        <button class="flex-1 py-3 font-command text-xs font-bold uppercase tracking-[0.15em] text-zinc-500">Ganho total</button>
      </div>

      <div class="grid grid-cols-3 gap-1">
        <button class="bg-surface-container-high py-4 border-b-2 border-primary-container">
          <span class="material-symbols-outlined text-primary-container">motorcycle</span>
          <p class="mt-1 font-command text-[10px] font-bold uppercase tracking-[0.14em]">Corrida</p>
        </button>
        <button class="bg-surface-container-low py-4">
          <span class="material-symbols-outlined text-zinc-400">delivery_dining</span>
          <p class="mt-1 font-command text-[10px] font-bold uppercase tracking-[0.14em] text-zinc-500">Entrega</p>
        </button>
        <button class="bg-surface-container-low py-4">
          <span class="material-symbols-outlined text-zinc-400">payments</span>
          <p class="mt-1 font-command text-[10px] font-bold uppercase tracking-[0.14em] text-zinc-500">Extra</p>
        </button>
      </div>

      <div class="bg-surface-container-lowest p-4 border-l-4 border-primary-container text-right">
        <p class="tactical-label mb-1">Valor (R$)</p>
        <div class="flex items-baseline justify-end gap-1">
          <span class="font-command text-lg text-primary-container">R$</span>
          <span class="font-command text-5xl font-black tracking-tight text-primary-container">45,00</span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <TacticalStatCard label="Duração (min)" value="18" />
        <TacticalStatCard label="Distância (km)" value="4.2" />
      </div>

      <div class="grid grid-cols-3 gap-1 bg-surface-container-lowest">
        <button v-for="digit in digits" :key="digit" class="h-14 bg-surface-container font-command text-2xl font-bold hover:bg-surface-bright">
          {{ digit }}
        </button>
      </div>

      <button class="bg-primary-container py-5 font-command text-lg font-black uppercase tracking-[0.2em] text-black shadow-tactical">
        Confirmar lançamento
      </button>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppTopBar from '@/components/AppTopBar.vue'
import TacticalStatCard from '@/components/TacticalStatCard.vue'

const digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', ',', '0', '⌫']
</script>

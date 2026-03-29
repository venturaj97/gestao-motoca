<template>
  <section class="space-y-8">
    <div class="border-l-4 border-primary-container pl-5">
      <p class="tactical-label mb-2 text-primary-container">ODÔMETRO DE PARTIDA</p>
      <h1 class="font-command text-4xl font-black uppercase tracking-tight">KM INICIAL</h1>
    </div>

    <div class="bg-surface-container-lowest p-6 text-right border-l-4 border-primary-container">
      <p class="tactical-label mb-2">Quilometragem atual</p>
      <p class="font-command text-5xl font-black tracking-tight text-primary-container">12.450</p>
      <p class="mt-2 text-sm text-zinc-400">Informe a leitura atual para destravar os lançamentos.</p>
    </div>

    <div class="grid grid-cols-3 gap-1 bg-surface-container-lowest">
      <button v-for="digit in digits" :key="digit" class="h-16 bg-surface-container text-2xl font-command font-bold hover:bg-surface-bright">
        {{ digit }}
      </button>
    </div>

    <RouterLink
      to="/dashboard"
      class="flex h-16 items-center justify-center bg-primary-container font-command text-base font-black uppercase tracking-[0.18em] text-black"
    >
      Confirmar quilometragem
    </RouterLink>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

const digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', ',', '0', '⌫']
</script>

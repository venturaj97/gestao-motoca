<template>
  <section class="space-y-8">
    <div class="border-l-4 border-primary-container pl-5">
      <p class="tactical-label mb-2 text-primary-container">VÍNCULO DE VEÍCULO</p>
      <h1 class="font-command text-4xl font-black uppercase tracking-tight">CONSULTA DE PLACA</h1>
    </div>

    <div class="space-y-2">
      <label class="tactical-label">Placa</label>
      <input class="tactical-input text-center font-command text-3xl font-bold tracking-[0.3em]" placeholder="ABC1D23" />
    </div>

    <div class="status-strip border-primary-container bg-surface-container-low">
      <p class="tactical-label mb-1 text-primary-container">Modo rápido</p>
      <p class="text-sm text-zinc-300">Consulta automática para acelerar o cadastro da sua moto.</p>
    </div>

    <div class="grid gap-3">
      <RouterLink
        to="/onboarding/km-inicial"
        class="flex h-16 items-center justify-center bg-primary-container font-command text-sm font-black uppercase tracking-[0.18em] text-black"
      >
        Consultar placa
      </RouterLink>
      <RouterLink
        to="/onboarding/cadastro-manual"
        class="flex h-16 items-center justify-center bg-surface-container font-command text-sm font-bold uppercase tracking-[0.18em]"
      >
        Cadastro manual
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

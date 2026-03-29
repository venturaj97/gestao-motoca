<template>
  <section class="space-y-8">
    <div class="border-l-4 border-primary-container pl-5">
      <p class="tactical-label mb-2 text-primary-container">VÍNCULO DE VEÍCULO</p>
      <h1 class="font-command text-4xl font-black uppercase tracking-tight">CADASTRO MANUAL</h1>
    </div>

    <form class="space-y-4">
      <div class="space-y-2">
        <label class="tactical-label">Marca</label>
        <input class="tactical-input" placeholder="HONDA" />
      </div>
      <div class="space-y-2">
        <label class="tactical-label">Modelo</label>
        <input class="tactical-input" placeholder="CG 160 FAN" />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2">
          <label class="tactical-label">Ano</label>
          <input class="tactical-input" placeholder="2024" />
        </div>
        <div class="space-y-2">
          <label class="tactical-label">Cor</label>
          <input class="tactical-input" placeholder="PRETA" />
        </div>
      </div>
    </form>

    <RouterLink
      to="/onboarding/km-inicial"
      class="flex h-20 items-center justify-center bg-primary-container font-command text-lg font-black uppercase tracking-[0.18em] text-black"
    >
      Continuar
    </RouterLink>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

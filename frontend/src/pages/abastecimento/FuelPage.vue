<template>
  <div class="pb-28">
    <AppTopBar />
    <main class="space-y-6 px-4 py-4">
      <PageIntro title="ABASTECER" eyebrow="Fluxo rápido" description="Registre combustível, valor e odômetro sem sair do modo operação." />

      <div class="grid gap-4">
        <div class="space-y-2">
          <label class="tactical-label">Posto</label>
          <input class="tactical-input" placeholder="POSTO PETRO-NORTE" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <label class="tactical-label">Valor total</label>
            <input class="tactical-input" placeholder="R$ 52,00" />
          </div>
          <div class="space-y-2">
            <label class="tactical-label">Litros</label>
            <input class="tactical-input" placeholder="8,5" />
          </div>
        </div>
        <div class="space-y-2">
          <label class="tactical-label">KM atual</label>
          <input class="tactical-input" placeholder="12.450" />
        </div>
      </div>

      <TacticalStatCard label="Consumo médio projetado" value="38,5 KM/L" accent="border-primary-container" />

      <button class="flex h-16 w-full items-center justify-center bg-primary-container font-command text-sm font-black uppercase tracking-[0.18em] text-black">
        Confirmar abastecimento
      </button>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppTopBar from '@/components/AppTopBar.vue'
import PageIntro from '@/components/PageIntro.vue'
import TacticalStatCard from '@/components/TacticalStatCard.vue'
</script>

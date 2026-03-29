<template>
  <div class="pb-28">
    <AppTopBar />
    <main class="space-y-6 px-4 py-4">
      <PageIntro title="LANÇAR DESPESA" eyebrow="Saída operacional" description="Escolha o tipo de despesa e siga com o registro mais rápido." />

      <div class="grid gap-3">
        <RouterLink to="/abastecimento" class="block">
          <TacticalButton tone="surface" icon="local_gas_station" :chevron="true">Abastecimento</TacticalButton>
        </RouterLink>
        <RouterLink to="/manutencao" class="block">
          <TacticalButton tone="surface" icon="build" :chevron="true">Manutenção</TacticalButton>
        </RouterLink>
        <TacticalButton tone="danger" icon="receipt_long">Despesa avulsa</TacticalButton>
      </div>

      <div class="status-strip border-secondary bg-surface-container-low">
        <p class="tactical-label mb-1 text-secondary">Atenção operacional</p>
        <p class="text-sm text-zinc-300">
          Despesas impactam o lucro líquido imediatamente. Registre tudo no mesmo dia.
        </p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import AppTopBar from '@/components/AppTopBar.vue'
import PageIntro from '@/components/PageIntro.vue'
import TacticalButton from '@/components/TacticalButton.vue'
</script>

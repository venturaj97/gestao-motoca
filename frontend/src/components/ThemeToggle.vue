<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <button
    type="button"
    class="fixed right-3 top-3 z-[70] h-10 w-10 border border-outline-variant bg-surface-container-high
           text-on-surface shadow-lg shadow-black/10 flex items-center justify-center shrink-0
           transition-colors hover:bg-surface-bright"
    :title="theme.escuro ? 'Ativar modo claro' : 'Ativar modo escuro'"
    :aria-label="theme.escuro ? 'Ativar modo claro' : 'Ativar modo escuro'"
    @click="theme.alternarTema"
  >
    <span class="material-symbols-outlined text-xl">
      {{ theme.escuro ? 'light_mode' : 'dark_mode' }}
    </span>
  </button>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <button
    type="button"
    class="fixed right-4 top-4 z-[70] h-11 w-11 border border-outline-variant bg-surface-container-high
           text-on-surface shadow-lg shadow-black/10 flex items-center justify-center
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

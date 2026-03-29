<template>
  <div :class="['tactical-card', accent && `border-l-4 ${accent}`]">
    <p class="tactical-label mb-1">{{ label }}</p>
    <p :class="['font-command text-2xl font-bold tracking-tight', valueClass]">{{ value }}</p>
    <p v-if="hint" class="mt-2 text-xs text-zinc-400">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string
    value: string
    hint?: string
    valueClass?: string
    accent?: string
  }>(),
  {
    hint: '',
    valueClass: 'text-on-surface',
    accent: '',
  },
)
</script>

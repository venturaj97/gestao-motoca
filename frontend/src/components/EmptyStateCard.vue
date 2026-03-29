<template>
  <div class="border-l-4 border-outline bg-surface-container-low p-5">
    <p class="tactical-label mb-2">{{ eyebrow }}</p>
    <h3 class="font-command text-lg font-bold uppercase tracking-tight">{{ title }}</h3>
    <p class="mt-2 text-sm text-zinc-400">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
  eyebrow?: string
}>()
</script>

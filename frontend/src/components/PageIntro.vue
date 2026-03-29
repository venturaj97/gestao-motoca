<template>
  <section class="space-y-1">
    <p v-if="eyebrow" class="tactical-label">{{ eyebrow }}</p>
    <h2 class="font-command text-3xl font-extrabold uppercase leading-tight tracking-tight">
      {{ title }}
    </h2>
    <p v-if="description" class="max-w-sm text-sm text-zinc-400">
      {{ description }}
    </p>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  eyebrow?: string
  description?: string
}>()
</script>

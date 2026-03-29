<template>
  <button
    :class="[
      'flex items-center justify-between gap-3 px-4 py-4 font-command text-xs font-bold uppercase tracking-[0.2em] transition active:scale-[0.98]',
      tone === 'primary' && 'bg-primary-container text-black',
      tone === 'danger' && 'bg-secondary text-background',
      tone === 'surface' && 'bg-surface-container text-on-surface hover:bg-surface-bright',
    ]"
  >
    <span class="flex items-center gap-3">
      <span v-if="icon" class="material-symbols-outlined">{{ icon }}</span>
      <slot />
    </span>
    <span v-if="chevron" class="material-symbols-outlined">chevron_right</span>
  </button>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    tone?: 'primary' | 'surface' | 'danger'
    icon?: string
    chevron?: boolean
  }>(),
  {
    tone: 'surface',
    icon: '',
    chevron: false,
  },
)
</script>

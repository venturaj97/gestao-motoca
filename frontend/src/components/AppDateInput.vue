<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue: string
    tone?: 'system' | 'despesa'
    min?: string
    max?: string
  }>(),
  {
    tone: 'system',
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="relative">
    <input
      type="date"
      :value="modelValue"
      :min="min"
      :max="max"
      class="app-date-input w-full bg-background border border-outline-variant px-2 py-2 pr-8 text-xs text-on-surface"
      @input="onInput"
    />
    <span
      class="material-symbols-outlined app-date-icon"
      :class="tone === 'despesa' ? 'text-secondary' : 'text-primary-container'"
    >
      calendar_month
    </span>
  </div>
</template>

<style scoped>
.app-date-input:focus {
  outline: none;
  box-shadow: none;
}

.app-date-icon {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  pointer-events: none;
}

.app-date-input::-webkit-calendar-picker-indicator {
  opacity: 0;
  cursor: pointer;
}

.app-date-input::-webkit-inner-spin-button,
.app-date-input::-webkit-clear-button {
  display: none;
}
</style>

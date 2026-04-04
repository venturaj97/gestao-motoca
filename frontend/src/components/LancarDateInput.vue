<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: string
    tone?: 'ganho' | 'despesa'
  }>(),
  {
    tone: 'ganho',
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const inputRef = ref<HTMLInputElement | null>(null)

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}

function abrirCalendario() {
  const el = inputRef.value
  if (!el) return
  const withPicker = el as HTMLInputElement & { showPicker?: () => void }
  if (typeof withPicker.showPicker === 'function') {
    withPicker.showPicker()
    return
  }
  el.focus()
  el.click()
}
</script>

<template>
  <div class="relative">
    <button
      type="button"
      class="absolute left-3 top-1/2 -translate-y-1/2 z-10"
      :class="props.tone === 'despesa' ? 'text-secondary' : 'text-primary-container'"
      @click="abrirCalendario"
    >
      <span class="material-symbols-outlined text-lg">calendar_month</span>
    </button>

    <input
      ref="inputRef"
      type="date"
      :value="props.modelValue"
      class="lancar-date-input tactical-input w-full pl-10 pr-3 py-3 text-base font-bold tracking-tight"
      :class="props.tone === 'despesa' ? 'focus:!border-secondary' : 'focus:!border-primary-container'"
      @input="onInput"
    />
  </div>
</template>

<style scoped>
.lancar-date-input::-webkit-calendar-picker-indicator {
  opacity: 0;
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.lancar-date-input::-webkit-inner-spin-button,
.lancar-date-input::-webkit-clear-button {
  display: none;
}
</style>

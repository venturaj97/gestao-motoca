import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

export type TemaVisual = 'dark' | 'light'

const STORAGE_KEY = 'tema_visual'

function temaInicial(): TemaVisual {
  const salvo = localStorage.getItem(STORAGE_KEY)
  return salvo === 'light' ? 'light' : 'dark'
}

export const useThemeStore = defineStore('theme', () => {
  const tema = ref<TemaVisual>(temaInicial())
  const escuro = computed(() => tema.value === 'dark')

  function alternarTema() {
    tema.value = escuro.value ? 'light' : 'dark'
  }

  watch(
    tema,
    (novoTema) => {
      localStorage.setItem(STORAGE_KEY, novoTema)
      document.documentElement.classList.toggle('dark', novoTema === 'dark')
    },
    { immediate: true },
  )

  return {
    tema,
    escuro,
    alternarTema,
  }
})

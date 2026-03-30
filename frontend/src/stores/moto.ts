import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MotoUsuarioResposta } from '@/types'
import { listarMinhasMotos } from '@/api/motos'

export const useMotoStore = defineStore('moto', () => {
  const motos = ref<MotoUsuarioResposta[]>([])
  const carregando = ref(false)
  const carregado = ref(false)

  // Moto ativa (backend garante que só existe 1 ativa por vez)
  const motoAtiva = computed(() =>
    motos.value.find((m) => m.ativa) ?? null
  )

  const temMoto = computed(() => motos.value.length > 0)

  async function carregarMotos() {
    try {
      carregando.value = true
      const res = await listarMinhasMotos()
      motos.value = res.motos
      carregado.value = true
    } catch {
      motos.value = []
    } finally {
      carregando.value = false
    }
  }

  function adicionarMoto(moto: MotoUsuarioResposta) {
    motos.value.push(moto)
  }

  function limpar() {
    motos.value = []
    carregado.value = false
  }

  return {
    motos,
    carregando,
    carregado,
    motoAtiva,
    temMoto,
    carregarMotos,
    adicionarMoto,
    limpar,
  }
})

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MotoUsuarioResposta, MotoAtualizarKmEntrada } from '@/types'
import { listarMinhasMotos, atualizarKmMinhaMoto } from '@/api/motos'

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

  async function atualizarKm(dados: MotoAtualizarKmEntrada) {
    const res = await atualizarKmMinhaMoto(dados)
    const idx = motos.value.findIndex((m) => m.id === res.id)
    if (idx !== -1) {
      motos.value[idx] = res
    } else {
      motos.value.push(res)
    }
    return res
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
    atualizarKm,
    limpar,
  }
})

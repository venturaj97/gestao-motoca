<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMotoStore } from '@/stores/moto'
import { atualizarMoto } from '@/api/motos'
import type { MotoUsuarioAtualizar } from '@/types'

const router    = useRouter()
const route     = useRoute()
const motoStore = useMotoStore()

const moto = computed(() => motoStore.motoAtiva)

// ── Estado de edição ────────────────────────────────────────────
const editando  = ref(false)
const enviando  = ref(false)
const erro      = ref('')
const sucesso   = ref(false)

const kmAtual   = ref('')
const cor       = ref('')

function iniciarEdicao() {
  if (!moto.value) return
  kmAtual.value = moto.value.km_atual?.toString() ?? ''
  cor.value     = moto.value.cor ?? ''
  editando.value = true
  erro.value    = ''
  sucesso.value = false
}

function cancelar() {
  editando.value = false
  erro.value    = ''
}

async function salvar() {
  if (!moto.value) return
  erro.value = ''

  const km = kmAtual.value ? parseInt(kmAtual.value) : undefined
  if (kmAtual.value && (isNaN(km!) || km! < 0)) {
    erro.value = 'KM inválido.'
    return
  }

  enviando.value = true
  try {
    const payload: MotoUsuarioAtualizar = {}
    if (km !== undefined) payload.km_atual = km
    if (cor.value) payload.cor = cor.value

    const atualizada = await atualizarMoto(moto.value.id, payload)
    // Atualiza a store
    const idx = motoStore.motos.findIndex(m => m.id === atualizada.id)
    if (idx >= 0) motoStore.motos[idx] = atualizada

    sucesso.value  = true
    editando.value = false
    setTimeout(() => sucesso.value = false, 3000)
  } catch {
    erro.value = 'Erro ao salvar alterações. Tente novamente.'
  } finally {
    enviando.value = false
  }
}

// ── Formatações ─────────────────────────────────────────────────
function formatarKm(km: number): string {
  return km.toLocaleString('pt-BR') + ' KM'
}

function origemLabel(origem: string): string {
  return origem === 'placa' ? 'VIA PLACA' : origem === 'manual' ? 'MANUAL' : origem.toUpperCase()
}

const navItems = [
  { name: 'dashboard',  label: 'Início',    icon: 'dashboard'  },
  { name: 'historico',  label: 'Histórico', icon: 'history'    },
  { name: 'lancar',     label: 'Lançar',    icon: 'add_box'    },
  { name: 'manutencao', label: 'Manutenção',icon: 'build'      },
  { name: 'moto',       label: 'Moto',      icon: 'motorcycle' },
]
function isActive(name: string) { return route.name === name }
function navIconStyle(name: string) {
  return isActive(name) ? { fontVariationSettings: '"FILL" 1' } : {}
}
</script>

<template>
  <div class="bg-background text-on-surface font-body min-h-screen pb-24">

    <!-- TopBar -->
    <header class="bg-background flex justify-between items-center w-full px-5 h-16 sticky top-0 z-50 border-l-4 border-primary-container">
      <h1 class="text-primary-container font-headline font-black text-lg tracking-tight uppercase">GESTÃO MOTOCA</h1>
      <span class="font-label text-[10px] tracking-widest text-on-surface-variant uppercase">MINHA MOTO</span>
    </header>

    <main class="px-5 py-6 space-y-6 max-w-md mx-auto">

      <!-- Sem moto (fallback) -->
      <div v-if="!moto" class="flex flex-col items-center justify-center py-20 gap-4 text-on-surface-variant">
        <span class="material-symbols-outlined text-5xl opacity-30">two_wheeler</span>
        <p class="font-label text-xs tracking-widest uppercase">Nenhuma moto vinculada</p>
        <button class="btn-primary h-12 w-auto px-8 text-xs"
          @click="router.push({ name: 'vincular-moto' })">
          <span class="material-symbols-outlined text-sm">link</span>
          VINCULAR MOTO
        </button>
      </div>

      <template v-else>

        <!-- Título -->
        <div>
          <p class="font-label text-[9px] font-bold tracking-[0.25em] text-on-surface-variant uppercase mb-1">VEÍCULO ATIVO</p>
          <h2 class="font-headline font-extrabold text-4xl tracking-tighter uppercase leading-none">
            {{ [moto.marca_manual, moto.modelo_manual].filter(Boolean).join(' ') || 'MOTO' }}
          </h2>
          <p v-if="moto.ano_manual" class="font-label text-[10px] text-primary-container tracking-widest uppercase mt-1">
            {{ moto.ano_manual }}
          </p>
        </div>

        <!-- Card principal -->
        <div class="bg-surface-container-low p-5 relative border-l-4 border-primary-container overflow-hidden">
          <!-- Ícone decorativo -->
          <span class="material-symbols-outlined absolute right-4 top-4 text-5xl text-primary-container opacity-10">two_wheeler</span>

          <div class="space-y-4">

            <!-- KM -->
            <div>
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase mb-1">QUILOMETRAGEM</p>
              <p class="font-headline font-black text-3xl text-on-surface">
                {{ moto.km_atual !== null ? formatarKm(moto.km_atual) : '—' }}
              </p>
            </div>

            <div class="h-[1px] bg-surface-container" />

            <!-- Placa -->
            <div v-if="moto.placa" class="flex justify-between items-center">
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">PLACA</p>
              <p class="font-headline font-black text-lg tracking-widest text-on-surface">{{ moto.placa }}</p>
            </div>

            <!-- Cor -->
            <div v-if="moto.cor" class="flex justify-between items-center">
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">COR</p>
              <p class="font-label text-xs font-bold text-on-surface uppercase">{{ moto.cor }}</p>
            </div>

            <!-- Origem -->
            <div class="flex justify-between items-center">
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">ORIGEM DOS DADOS</p>
              <span class="font-label text-[9px] font-bold tracking-wider px-2 py-1 bg-primary-container/10 text-primary-container uppercase">
                {{ origemLabel(moto.origem_dados) }}
              </span>
            </div>

            <!-- Status -->
            <div class="flex justify-between items-center">
              <p class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">STATUS</p>
              <span class="font-label text-[9px] font-bold tracking-wider px-2 py-1 uppercase"
                :class="moto.ativa ? 'bg-primary-container/10 text-primary-container' : 'bg-surface-container text-on-surface-variant'">
                {{ moto.ativa ? '● ATIVA' : '● INATIVA' }}
              </span>
            </div>

          </div>
        </div>

        <!-- Sucesso -->
        <div v-if="sucesso"
          class="flex items-center gap-3 bg-primary-container/20 text-primary-container text-sm font-label px-4 py-3 border-l-4 border-primary-container">
          <span class="material-symbols-outlined text-base flex-shrink-0">check_circle</span>
          Dados atualizados com sucesso!
        </div>

        <!-- Formulário de edição -->
        <div v-if="editando" class="bg-surface-container-low p-5 space-y-5">
          <p class="font-label text-[9px] font-bold tracking-[0.25em] text-primary-container uppercase">EDITAR DADOS</p>

          <!-- KM -->
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              ATUALIZAR KM
            </label>
            <div class="relative">
              <input v-model="kmAtual" type="number" min="0"
                :placeholder="moto.km_atual?.toString() ?? '0'"
                class="tactical-input py-3 pr-12 text-lg" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 font-label text-on-surface-variant text-xs font-bold">KM</span>
            </div>
          </div>

          <!-- Cor -->
          <div>
            <label class="block font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              COR <span class="font-normal text-outline">(opcional)</span>
            </label>
            <input v-model="cor" type="text" placeholder="Ex: Preta, Vermelha"
              class="tactical-input py-3" />
          </div>

          <!-- Erro -->
          <div v-if="erro"
            class="flex items-start gap-3 bg-error-container text-on-error-container text-sm font-label px-4 py-3 border-l-4 border-error">
            <span class="material-symbols-outlined text-base mt-0.5 flex-shrink-0">error</span>
            {{ erro }}
          </div>

          <!-- Ações -->
          <div class="grid grid-cols-2 gap-3">
            <button type="button" class="btn-secondary h-12 text-xs" @click="cancelar">
              CANCELAR
            </button>
            <button type="button" :disabled="enviando"
              class="btn-primary h-12 text-xs disabled:opacity-40"
              @click="salvar">
              <span v-if="enviando" class="material-symbols-outlined animate-spin text-sm">refresh</span>
              <template v-else>
                <span class="material-symbols-outlined text-sm">save</span>
                SALVAR
              </template>
            </button>
          </div>
        </div>

        <!-- Botão editar -->
        <button v-if="!editando"
          class="btn-secondary h-14 text-sm"
          @click="iniciarEdicao">
          <span class="material-symbols-outlined">edit</span>
          ATUALIZAR KM / COR
        </button>

      </template>
    </main>

    <!-- Bottom Nav -->
    <nav class="fixed bottom-0 left-0 w-full z-50 h-20 bg-background border-t-4 border-surface-container grid grid-cols-5">
      <button v-for="item in navItems" :key="item.name"
        class="flex flex-col items-center justify-center h-full w-full transition-colors duration-100"
        :class="isActive(item.name)
          ? 'bg-primary-container text-on-primary-fixed'
          : 'text-on-surface-variant hover:bg-surface-container'"
        @click="router.push({ name: item.name })">
        <span class="material-symbols-outlined" :style="navIconStyle(item.name)">{{ item.icon }}</span>
        <span class="font-label text-[9px] font-bold uppercase tracking-[0.08em] mt-0.5">{{ item.label }}</span>
      </button>
    </nav>
  </div>
</template>

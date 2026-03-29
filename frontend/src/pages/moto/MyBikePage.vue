<template>
  <div class="pb-28">
    <AppTopBar icon="logout" icon-action="logout" />

    <main class="space-y-8 px-6 pb-24 pt-6">
      <section class="flex items-end justify-between">
        <div>
          <p class="tactical-label mb-1">Piloto ativo</p>
          <h2 class="font-command text-2xl font-black uppercase tracking-tight">{{ auth.user?.nome ?? 'Usuário' }}</h2>
        </div>
        <button class="border-l-2 border-primary bg-surface-container p-3" @click="editing = !editing">
          <span class="material-symbols-outlined text-primary">edit</span>
        </button>
      </section>

      <div v-if="motosQuery.isLoading.value" class="grid gap-3">
        <LoadingBlock />
        <LoadingBlock />
      </div>

      <div v-else-if="motosQuery.isError.value" class="border-l-4 border-secondary bg-secondary-container/10 p-5 text-sm text-zinc-100">
        {{ motosError }}
      </div>

      <EmptyStateCard
        v-else-if="!motos.length"
        eyebrow="Primeira moto"
        title="Nenhuma moto cadastrada"
        description="Cadastre sua primeira moto para liberar lançamentos, abastecimentos e manutenção."
      />

      <div v-else class="space-y-6">
      <div class="relative">
        <div class="absolute -inset-1 bg-gradient-to-r from-primary/20 to-transparent blur opacity-25" />
        <div class="relative border-l-4 border-primary bg-surface-container-low p-6">
          <div class="mb-6 flex items-start justify-between gap-4">
            <div>
              <p class="tactical-label mb-2 text-primary">Veículo de missão</p>
              <h3 class="font-command text-3xl font-extrabold tracking-tight">{{ primaryMotoLabel }}</h3>
              <p class="text-sm font-medium tracking-tight text-zinc-400">
                ANO MODELO {{ selectedMoto?.ano ?? '--' }} • {{ selectedMoto?.origem_dados ?? 'MANUAL' }}
              </p>
            </div>
            <div v-if="selectedMoto?.placa" class="border-[3px] border-[#003399] bg-white text-center text-black">
              <div class="bg-[#003399] px-3 py-1 text-[10px] font-extrabold text-white">BRASIL</div>
              <div class="px-4 py-2 font-black tracking-tight">{{ selectedMoto.placa }}</div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <TacticalStatCard label="Odômetro total" :value="`${selectedMoto?.km_atual ?? 0} KM`" value-class="text-primary-container" />
            <TacticalStatCard label="Status" :value="selectedMoto?.ativa ? 'ATIVA' : 'INATIVA'" :value-class="selectedMoto?.ativa ? 'text-primary-container' : 'text-secondary'" />
          </div>
        </div>
      </div>

      <div class="grid gap-3">
        <TacticalButton tone="primary" icon="two_wheeler" :chevron="true" @click="cycleMoto">
          Trocar motocicleta
        </TacticalButton>
        <TacticalButton tone="surface" icon="description" :chevron="true" @click="editing = !editing">
          Editar dados técnicos
        </TacticalButton>
        <TacticalButton
          :tone="selectedMoto?.ativa ? 'danger' : 'surface'"
          icon="toggle_on"
          :chevron="false"
          @click="toggleActive"
        >
          {{ selectedMoto?.ativa ? 'Desativar moto' : 'Ativar moto' }}
        </TacticalButton>
      </div>

      <section v-if="editing" class="space-y-4 bg-surface-container-low p-5">
        <p class="tactical-label">Editar moto</p>
        <div class="grid gap-4">
          <div class="space-y-2">
            <label class="tactical-label">Marca</label>
            <input v-model="editForm.marca_manual" class="tactical-input" />
          </div>
          <div class="space-y-2">
            <label class="tactical-label">Modelo</label>
            <input v-model="editForm.modelo_manual" class="tactical-input" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="tactical-label">Ano</label>
              <input v-model.number="editForm.ano_manual" class="tactical-input" type="number" />
            </div>
            <div class="space-y-2">
              <label class="tactical-label">Cor</label>
              <input v-model="editForm.cor" class="tactical-input" />
            </div>
          </div>
          <div class="space-y-2">
            <label class="tactical-label">KM atual</label>
            <input v-model.number="editForm.km_atual" class="tactical-input" type="number" />
          </div>
        </div>
        <div class="flex gap-3">
          <button class="flex-1 bg-primary-container py-4 font-command text-xs font-black uppercase tracking-[0.18em] text-black" @click="saveEdit">
            Salvar
          </button>
          <button class="flex-1 bg-surface-container py-4 font-command text-xs font-bold uppercase tracking-[0.18em]" @click="editing = false">
            Cancelar
          </button>
        </div>
      </section>

      <section>
        <p class="tactical-label mb-4">Resumo de operação</p>
        <div class="space-y-1">
          <div v-for="item in summary" :key="item.label" class="flex items-center justify-between bg-surface-container-low p-4">
            <span class="text-sm text-zinc-400">{{ item.label }}</span>
            <span class="font-command font-bold" :class="item.highlight ? 'text-primary-container' : ''">{{ item.value }}</span>
          </div>
        </div>
      </section>

      <section class="space-y-4">
        <p class="tactical-label">Todas as motos</p>
        <div class="space-y-2">
          <article
            v-for="moto in motos"
            :key="moto.id"
            class="flex items-center justify-between bg-surface-container p-4"
            :class="moto.ativa ? 'border-l-4 border-primary-container' : 'border-l-4 border-outline'"
          >
            <div>
              <p class="font-command text-sm font-bold uppercase tracking-tight">
                {{ formatMotoLabel(moto) }}
              </p>
              <p class="mt-1 text-xs text-zinc-400">
                {{ moto.placa ?? 'Sem placa' }} • {{ moto.km_atual }} KM
              </p>
            </div>
            <div class="flex gap-2">
              <button class="bg-surface-container-high px-3 py-2 text-xs font-bold uppercase tracking-[0.12em]" @click="selectMoto(moto.id)">
                Ver
              </button>
              <button class="bg-secondary-container px-3 py-2 text-xs font-bold uppercase tracking-[0.12em]" @click="removeMoto(moto.id)">
                Excluir
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="space-y-4 bg-surface-container-low p-5">
        <div class="flex gap-2">
          <button
            class="flex-1 py-3 font-command text-xs font-bold uppercase tracking-[0.15em]"
            :class="mode === 'manual' ? 'bg-primary-container text-black' : 'bg-surface-container text-zinc-400'"
            @click="mode = 'manual'"
          >
            Manual
          </button>
          <button
            class="flex-1 py-3 font-command text-xs font-bold uppercase tracking-[0.15em]"
            :class="mode === 'placa' ? 'bg-primary-container text-black' : 'bg-surface-container text-zinc-400'"
            @click="mode = 'placa'"
          >
            Por placa
          </button>
        </div>

        <div v-if="formError" class="border-l-4 border-secondary bg-secondary-container/10 p-4 text-sm text-zinc-100">
          {{ formError }}
        </div>

        <template v-if="mode === 'manual'">
          <div class="grid gap-4">
            <div class="space-y-2">
              <label class="tactical-label">Marca</label>
              <input v-model="manualForm.marca_manual" class="tactical-input" />
            </div>
            <div class="space-y-2">
              <label class="tactical-label">Modelo</label>
              <input v-model="manualForm.modelo_manual" class="tactical-input" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="tactical-label">Ano</label>
                <input v-model.number="manualForm.ano_manual" class="tactical-input" type="number" />
              </div>
              <div class="space-y-2">
                <label class="tactical-label">Cor</label>
                <input v-model="manualForm.cor" class="tactical-input" />
              </div>
            </div>
            <div class="space-y-2">
              <label class="tactical-label">KM atual</label>
              <input v-model.number="manualForm.km_atual" class="tactical-input" type="number" />
            </div>
            <button class="bg-primary-container py-4 font-command text-xs font-black uppercase tracking-[0.18em] text-black" @click="submitManual">
              Cadastrar manualmente
            </button>
          </div>
        </template>

        <template v-else>
          <div class="grid gap-4">
            <div class="space-y-2">
              <label class="tactical-label">Placa</label>
              <input v-model="plateForm.placa" class="tactical-input uppercase" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="tactical-label">KM atual</label>
                <input v-model.number="plateForm.km_atual" class="tactical-input" type="number" />
              </div>
              <div class="space-y-2">
                <label class="tactical-label">Cor</label>
                <input v-model="plateForm.cor" class="tactical-input" />
              </div>
            </div>
            <button class="bg-surface-container py-4 font-command text-xs font-bold uppercase tracking-[0.18em]" @click="previewPlate">
              Consultar placa
            </button>
            <div v-if="platePreview" class="border-l-4 border-primary-container bg-surface-container p-4">
              <p class="tactical-label mb-2">Prévia da consulta</p>
              <p class="font-command text-sm font-bold uppercase">
                {{ platePreview.dados.marca ?? '--' }} {{ platePreview.dados.modelo ?? '' }}
              </p>
              <p class="mt-1 text-xs text-zinc-400">Placa consultada: {{ platePreview.placa_consultada }}</p>
            </div>
            <button class="bg-primary-container py-4 font-command text-xs font-black uppercase tracking-[0.18em] text-black" @click="submitPlate">
              Cadastrar por placa
            </button>
          </div>
        </template>
      </section>
      </div>

      <button class="flex w-full items-center justify-center gap-2 border-t border-surface-container-high pt-8 font-command text-xs font-bold uppercase tracking-[0.18em] text-secondary" @click="handleLogout">
        <span class="material-symbols-outlined text-sm">logout</span>
        Sair da conta
      </button>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import TacticalButton from '@/components/TacticalButton.vue'
import TacticalStatCard from '@/components/TacticalStatCard.vue'
import AppTopBar from '@/components/AppTopBar.vue'
import EmptyStateCard from '@/components/EmptyStateCard.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import {
  useCreateMotoByPlateMutation,
  useCreateMotoManualMutation,
  useDeleteMotoMutation,
  useMotosQuery,
  usePlateLookupMutation,
  useSetMotoActiveMutation,
  useUpdateMotoMutation,
} from '@/modules/motos/queries'
import { getApiErrorMessage } from '@/shared/api/errors'
import type { Moto } from '@/shared/types/motos'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const motosQuery = useMotosQuery()
const createManualMutation = useCreateMotoManualMutation()
const createPlateMutation = useCreateMotoByPlateMutation()
const updateMotoMutation = useUpdateMotoMutation()
const deleteMotoMutation = useDeleteMotoMutation()
const setMotoActiveMutation = useSetMotoActiveMutation()
const plateLookupMutation = usePlateLookupMutation()

const selectedMotoId = ref<number | null>(null)
const editing = ref(false)
const mode = ref<'manual' | 'placa'>('manual')
const formError = ref('')

const manualForm = reactive({
  marca_manual: '',
  modelo_manual: '',
  ano_manual: new Date().getFullYear(),
  km_atual: 0,
  cor: '',
})

const plateForm = reactive({
  placa: '',
  km_atual: 0,
  cor: '',
})

const editForm = reactive({
  marca_manual: '',
  modelo_manual: '',
  ano_manual: new Date().getFullYear(),
  km_atual: 0,
  cor: '',
})

const motos = computed(() => motosQuery.data.value?.motos ?? [])
const selectedMoto = computed(() => {
  if (!motos.value.length) return null
  return motos.value.find((moto) => moto.id === selectedMotoId.value) ?? motos.value[0]
})
const primaryMotoLabel = computed(() => (selectedMoto.value ? formatMotoLabel(selectedMoto.value) : 'SEM MOTO'))
const motosError = computed(() => getApiErrorMessage(motosQuery.error.value, 'Não foi possível carregar suas motos.'))
const platePreview = computed(() => plateLookupMutation.data.value ?? null)

watch(
  motos,
  (list) => {
    if (!list.length) {
      selectedMotoId.value = null
      return
    }

    if (!selectedMotoId.value || !list.some((moto) => moto.id === selectedMotoId.value)) {
      selectedMotoId.value = list.find((moto) => moto.ativa)?.id ?? list[0].id
    }
  },
  { immediate: true },
)

watch(
  selectedMoto,
  (moto) => {
    if (!moto) return

    editForm.marca_manual = moto.marca ?? ''
    editForm.modelo_manual = moto.modelo ?? ''
    editForm.ano_manual = moto.ano ?? new Date().getFullYear()
    editForm.km_atual = moto.km_atual
    editForm.cor = moto.cor ?? ''
  },
  { immediate: true },
)

const formatMotoLabel = (moto: Moto) =>
  [moto.marca, moto.modelo].filter(Boolean).join(' ') || `Moto #${moto.id}`

const summary = computed(() => [
  { label: 'Consumo médio', value: '38.5 KM/L', highlight: true },
  { label: 'Último abastecimento', value: motos.value.length ? 'Dados em breve' : 'Cadastre uma moto', highlight: false },
  { label: 'Custo p/ KM', value: 'R$ 0,24', highlight: false },
])

const cycleMoto = () => {
  if (motos.value.length < 2 || !selectedMoto.value) return

  const currentIndex = motos.value.findIndex((moto) => moto.id === selectedMoto.value?.id)
  const next = motos.value[(currentIndex + 1) % motos.value.length]
  selectedMotoId.value = next.id
}

const selectMoto = (motoId: number) => {
  selectedMotoId.value = motoId
  editing.value = false
}

const toggleActive = async () => {
  if (!selectedMoto.value) return

  formError.value = ''

  try {
    await setMotoActiveMutation.mutateAsync({
      motoId: selectedMoto.value.id,
      ativa: !selectedMoto.value.ativa,
    })
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'Não foi possível alterar o status da moto.')
  }
}

const saveEdit = async () => {
  if (!selectedMoto.value) return

  formError.value = ''

  try {
    await updateMotoMutation.mutateAsync({
      motoId: selectedMoto.value.id,
      payload: {
        marca_manual: editForm.marca_manual,
        modelo_manual: editForm.modelo_manual,
        ano_manual: editForm.ano_manual,
        km_atual: editForm.km_atual,
        cor: editForm.cor,
      },
    })
    editing.value = false
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'Não foi possível salvar a moto.')
  }
}

const removeMoto = async (motoId: number) => {
  const confirmed = window.confirm('Deseja realmente excluir esta moto?')
  if (!confirmed) return

  formError.value = ''

  try {
    await deleteMotoMutation.mutateAsync(motoId)
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'Não foi possível excluir a moto.')
  }
}

const submitManual = async () => {
  formError.value = ''

  try {
    await createManualMutation.mutateAsync({
      marca_manual: manualForm.marca_manual,
      modelo_manual: manualForm.modelo_manual,
      ano_manual: manualForm.ano_manual,
      km_atual: manualForm.km_atual,
      cor: manualForm.cor,
    })
    manualForm.marca_manual = ''
    manualForm.modelo_manual = ''
    manualForm.ano_manual = new Date().getFullYear()
    manualForm.km_atual = 0
    manualForm.cor = ''
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'Não foi possível cadastrar a moto manualmente.')
  }
}

const previewPlate = async () => {
  formError.value = ''

  try {
    await plateLookupMutation.mutateAsync(plateForm.placa)
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'Não foi possível consultar a placa.')
  }
}

const submitPlate = async () => {
  formError.value = ''

  try {
    await createPlateMutation.mutateAsync({
      placa: plateForm.placa,
      km_atual: plateForm.km_atual,
      cor: plateForm.cor,
    })
    plateForm.placa = ''
    plateForm.km_atual = 0
    plateForm.cor = ''
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'Não foi possível cadastrar a moto por placa.')
  }
}

const handleLogout = async () => {
  auth.logout()
  await router.push('/auth/login')
}
</script>

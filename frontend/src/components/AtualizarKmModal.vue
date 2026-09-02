<script setup lang="ts">
import { ref, watch } from 'vue'
import { useMotoStore } from '@/stores/moto'
import AppDateInput from '@/components/AppDateInput.vue'

const props = defineProps<{
  show: boolean
  kmAtual: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'salvo'): void
}>()

function obterDataHojeIso(): string {
  const hoje = new Date()
  const ano = hoje.getFullYear()
  const mes = String(hoje.getMonth() + 1).padStart(2, '0')
  const dia = String(hoje.getDate()).padStart(2, '0')
  return `${ano}-${mes}-${dia}`
}

const motoStore = useMotoStore()

const novoKm = ref<number | ''>('')
const trocouOleo = ref(false)
const valorOleo = ref<number | ''>('')
const oficina = ref('')
const dataLancamento = ref(obterDataHojeIso())

const salvando = ref(false)
const erroMsg = ref('')

watch(
  () => props.show,
  (val) => {
    if (val) {
      novoKm.value = props.kmAtual || ''
      trocouOleo.value = false
      valorOleo.value = ''
      oficina.value = ''
      dataLancamento.value = obterDataHojeIso()
      erroMsg.value = ''
    }
  },
  { immediate: true }
)

async function handleSalvar() {
  erroMsg.value = ''
  if (!novoKm.value || typeof novoKm.value !== 'number' || novoKm.value < 0) {
    erroMsg.value = 'Informe uma quilometragem válida.'
    return
  }

  if (novoKm.value < props.kmAtual) {
    erroMsg.value = `O novo KM (${novoKm.value.toLocaleString('pt-BR')} km) não pode ser menor que o atual (${props.kmAtual.toLocaleString('pt-BR')} km).`
    return
  }

  if (trocouOleo.value) {
    if (!valorOleo.value || typeof valorOleo.value !== 'number' || valorOleo.value <= 0) {
      erroMsg.value = 'Informe o valor gasto na troca de óleo.'
      return
    }
  }

  try {
    salvando.value = true
    await motoStore.atualizarKm({
      km_atual: novoKm.value,
      trocou_oleo: trocouOleo.value,
      valor_oleo: trocouOleo.value && valorOleo.value ? valorOleo.value : undefined,
      oficina: trocouOleo.value && oficina.value.trim() ? oficina.value.trim() : undefined,
      data_lancamento: trocouOleo.value && dataLancamento.value ? dataLancamento.value : undefined,
    })
    emit('salvo')
    emit('close')
  } catch (err: any) {
    erroMsg.value = err?.response?.data?.detail ?? 'Erro ao atualizar quilometragem. Tente novamente.'
  } finally {
    salvando.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fade-in"
      @click.self="emit('close')"
    >
      <div
        class="bg-surface border-2 border-primary-container p-6 w-full max-w-md space-y-5 shadow-2xl relative transition-all"
      >
        <!-- Topo Modal -->
        <div class="flex justify-between items-start border-b border-outline-variant pb-3">
          <div>
            <div class="flex items-center gap-2 text-primary-container font-headline font-black uppercase tracking-wider text-sm">
              <span class="material-symbols-outlined text-xl">speed</span>
              ATUALIZAR ODÔMETRO
            </div>
            <p class="font-label text-[10px] text-on-surface-variant uppercase mt-0.5">
              Rodagem atual cadastrada: <strong class="text-on-surface font-bold">{{ kmAtual.toLocaleString('pt-BR') }} KM</strong>
            </p>
          </div>
          <button
            class="text-on-surface-variant hover:text-on-surface p-1 transition-colors"
            @click="emit('close')"
          >
            <span class="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        <!-- Erro Banner -->
        <div v-if="erroMsg" class="bg-error-container text-on-error-container p-3 text-xs font-medium rounded-lg border border-error/30">
          {{ erroMsg }}
        </div>

        <!-- Formulário -->
        <form class="space-y-4" @submit.prevent="handleSalvar">
          <!-- Campo Novo KM -->
          <div class="space-y-1">
            <label class="font-label text-[10px] font-bold tracking-widest text-on-surface-variant uppercase">
              NOVA QUILOMETRAGEM (KM)
            </label>
            <div class="relative flex items-center">
              <input
                v-model.number="novoKm"
                type="number"
                min="0"
                step="1"
                placeholder="Ex: 14500"
                class="tactical-input py-2.5 px-3 text-lg"
                required
              />
              <span class="absolute right-3 text-xs font-bold text-outline uppercase pointer-events-none">KM</span>
            </div>
          </div>

          <!-- Pergunta / Toggle Troca de Óleo -->
          <div class="p-3.5 bg-surface-container-low border border-outline-variant space-y-3">
            <label class="flex items-center gap-3 cursor-pointer select-none">
              <input
                v-model="trocouOleo"
                type="checkbox"
                class="w-4 h-4 text-primary-container border-outline-variant rounded-none focus:ring-0 cursor-pointer accent-primary-container"
              />
              <span class="font-headline text-xs font-extrabold uppercase tracking-wide text-on-surface flex items-center gap-1.5">
                <span class="material-symbols-outlined text-amber-500 text-sm">oil_barrel</span>
                Aproveitou para trocar o óleo?
              </span>
            </label>

            <!-- Campos expandidos se trocou óleo -->
            <div v-if="trocouOleo" class="space-y-3 pt-2 border-t border-outline-variant/60 animate-fade-in">
              <div class="grid grid-cols-2 gap-2">
                <div class="space-y-1">
                  <label class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
                    VALOR DO ÓLEO (R$) *
                  </label>
                  <input
                    v-model.number="valorOleo"
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="Ex: 45,00"
                    class="tactical-input py-2 px-3 text-sm"
                    :required="trocouOleo"
                  />
                </div>

                <div class="space-y-1">
                  <label class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
                    DATA DA TROCA
                  </label>
                  <AppDateInput v-model="dataLancamento" tone="system" />
                </div>
              </div>

              <div class="space-y-1">
                <label class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase">
                  OFICINA / POSTO (OPCIONAL)
                </label>
                <input
                  v-model="oficina"
                  type="text"
                  placeholder="Ex: Oficina Central Motos"
                  class="tactical-input py-2 px-3 text-sm"
                />
              </div>

              <p class="text-[10px] text-amber-600 dark:text-amber-300 font-medium">
                ℹ️ Esta troca de óleo será lançada automaticamente no seu histórico de manutenções!
              </p>
            </div>
          </div>

          <!-- Botões Ação -->
          <div class="grid grid-cols-2 gap-2 pt-2">
            <button
              type="button"
              class="btn-secondary py-3 text-xs"
              @click="emit('close')"
            >
              CANCELAR
            </button>
            <button
              type="submit"
              class="btn-primary py-3 text-xs"
              :disabled="salvando"
            >
              <span v-if="salvando" class="material-symbols-outlined text-sm animate-spin">refresh</span>
              <span v-else>SALVAR KM</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

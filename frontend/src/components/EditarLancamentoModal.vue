<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { atualizarLancamento, excluirLancamento } from '@/api/lancamentos'
import { listarCategorias } from '@/api/categorias'
import type { LancamentoResposta, CategoriaResposta } from '@/types'
import AppDateInput from '@/components/AppDateInput.vue'

const props = defineProps<{
  visivel: boolean
  lancamento: LancamentoResposta | null
}>()

const emit = defineEmits<{
  (e: 'fechar'): void
  (e: 'salvo'): void
}>()

// ── Estado do Formulário ─────────────────────────────────────────
const valor = ref('')
const descricao = ref('')
const dataLancamento = ref('')
const categoriaId = ref<number | null>(null)

const categorias = ref<CategoriaResposta[]>([])
const carregando = ref(false)
const salvando = ref(false)
const excluindo = ref(false)
const erro = ref('')

const categoriasFiltradas = computed(() => {
  if (!props.lancamento) return []
  return categorias.value.filter(c => c.ativo && c.tipo === props.lancamento?.tipo)
})

function preencherFormulario() {
  if (!props.lancamento) return
  valor.value = props.lancamento.valor
  descricao.value = props.lancamento.descricao || ''
  dataLancamento.value = props.lancamento.data_lancamento
  categoriaId.value = props.lancamento.categoria_id
  erro.value = ''
}

watch(() => props.lancamento, () => {
  preencherFormulario()
}, { immediate: true })

async function carregarCategorias() {
  try {
    carregando.value = true
    categorias.value = await listarCategorias()
  } catch {
    erro.value = 'Erro ao carregar categorias.'
  } finally {
    carregando.value = false
  }
}

onMounted(() => {
  carregarCategorias()
})

async function salvar() {
  if (!props.lancamento) return
  const valNum = parseFloat(valor.value.replace(',', '.'))
  if (isNaN(valNum) || valNum <= 0) {
    erro.value = 'Informe um valor válido maior que zero.'
    return
  }
  if (!categoriaId.value) {
    erro.value = 'Selecione uma categoria.'
    return
  }
  if (!dataLancamento.value) {
    erro.value = 'Informe a data do lançamento.'
    return
  }

  salvando.value = true
  erro.value = ''

  try {
    await atualizarLancamento(props.lancamento.id, {
      categoria_id: categoriaId.value,
      tipo: props.lancamento.tipo,
      valor: valNum,
      descricao: descricao.value.trim() || undefined,
      periodo: props.lancamento.periodo || (props.lancamento.tipo === 'GANHO' ? 'DIARIO' : undefined),
      minutos_corrida: props.lancamento.minutos_corrida || undefined,
      km_corrida: props.lancamento.km_corrida ? parseFloat(props.lancamento.km_corrida) : undefined,
      data_lancamento: dataLancamento.value,
      moto_usuario_id: props.lancamento.moto_usuario_id || undefined,
    })
    emit('salvo')
    emit('fechar')
  } catch {
    erro.value = 'Erro ao salvar alterações.'
  } finally {
    salvando.value = false
  }
}

async function excluir() {
  if (!props.lancamento) return
  if (!confirm('Tem certeza que deseja excluir este lançamento?')) return

  excluindo.value = true
  erro.value = ''

  try {
    await excluirLancamento(props.lancamento.id)
    emit('salvo')
    emit('fechar')
  } catch {
    erro.value = 'Erro ao excluir lançamento.'
  } finally {
    excluindo.value = false
  }
}
</script>

<template>
  <div
    v-if="visivel && lancamento"
    class="fixed inset-0 z-[100] bg-black/60 backdrop-blur-xs flex items-center justify-center p-4"
    @click.self="emit('fechar')"
  >
    <div class="bg-surface-container border border-outline-variant w-full max-w-sm p-5 space-y-4 shadow-xl animate-in fade-in zoom-in-95 duration-150">
      
      <!-- Cabeçalho -->
      <div class="flex items-center justify-between border-b border-outline-variant pb-3">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-on-surface">edit</span>
          <h3 class="font-headline font-bold text-base uppercase tracking-tight">EDITAR LANÇAMENTO</h3>
        </div>
        <button
          class="text-on-surface-variant hover:text-on-surface transition-colors"
          @click="emit('fechar')"
        >
          <span class="material-symbols-outlined text-xl">close</span>
        </button>
      </div>

      <!-- Erro -->
      <div
        v-if="erro"
        class="bg-error-container text-on-error-container text-xs font-label p-3 flex items-center gap-2"
      >
        <span class="material-symbols-outlined text-sm">warning</span>
        {{ erro }}
      </div>

      <!-- Formulário -->
      <div class="space-y-3">

        <!-- Valor -->
        <div>
          <label class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase block mb-1">
            VALOR (R$)
          </label>
          <input
            v-model="valor"
            type="text"
            inputmode="decimal"
            placeholder="0.00"
            class="tactical-input py-2.5 px-3 text-base font-bold"
          />
        </div>

        <!-- Data -->
        <div>
          <label class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase block mb-1">
            DATA
          </label>
          <AppDateInput v-model="dataLancamento" tone="system" />
        </div>

        <!-- Categoria -->
        <div>
          <label class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase block mb-1">
            CATEGORIA
          </label>
          <select
            v-model="categoriaId"
            class="tactical-input py-2.5 px-3 text-sm bg-surface-container-high text-on-surface w-full"
          >
            <option :value="null" disabled>Selecione uma categoria</option>
            <option
              v-for="cat in categoriasFiltradas"
              :key="cat.id"
              :value="cat.id"
            >
              {{ cat.nome }}
            </option>
          </select>
        </div>

        <!-- Descrição -->
        <div>
          <label class="font-label text-[9px] font-bold tracking-widest text-on-surface-variant uppercase block mb-1">
            DESCRIÇÃO (OPCIONAL)
          </label>
          <input
            v-model="descricao"
            type="text"
            placeholder="Ex: Troca de pneu, iFood, etc."
            class="tactical-input py-2.5 px-3 text-sm"
          />
        </div>

      </div>

      <!-- Ações -->
      <div class="flex items-center justify-between gap-2 pt-3 border-t border-outline-variant">
        <button
          class="h-10 px-3 bg-red-600/90 text-white font-label text-[10px] font-extrabold tracking-widest uppercase hover:bg-red-600 transition-colors flex items-center gap-1 disabled:opacity-50"
          :disabled="excluindo || salvando"
          @click="excluir"
        >
          <span v-if="excluindo" class="material-symbols-outlined text-sm animate-spin">refresh</span>
          <span v-else class="material-symbols-outlined text-sm">delete</span>
          EXCLUIR
        </button>

        <div class="flex items-center gap-2">
          <button
            class="h-10 px-3 bg-surface-container-high border border-outline-variant font-label text-[10px] font-bold tracking-widest uppercase text-on-surface hover:bg-surface-bright transition-colors"
            @click="emit('fechar')"
          >
            CANCELAR
          </button>
          <button
            class="h-10 px-4 bg-white text-black dark:bg-slate-100 dark:text-slate-900 font-label text-[10px] font-extrabold tracking-widest uppercase hover:bg-slate-200 transition-all flex items-center justify-center gap-1 disabled:opacity-50"
            :disabled="salvando || excluindo"
            @click="salvar"
          >
            <span v-if="salvando" class="material-symbols-outlined text-sm animate-spin">refresh</span>
            <span v-else class="material-symbols-outlined text-sm">check</span>
            SALVAR
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

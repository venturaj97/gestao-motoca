<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Permite fechar a notificação temporariamente na sessão
const fechado = ref(sessionStorage.getItem('notificacao_free_fechada') === 'true')

function fecharNotificacao() {
  fechado.value = true
  sessionStorage.setItem('notificacao_free_fechada', 'true')
}

function irParaPlanos() {
  router.push({ name: 'configuracoes', query: { aba: 'PLANO' } })
}
</script>

<template>
  <div v-if="authStore.usuario && !authStore.ehPro && !fechado" class="mb-4">
    <div
      class="relative overflow-hidden rounded-xl border border-amber-500/30 bg-gradient-to-r from-amber-500/15 via-slate-900/90 to-slate-950 p-3.5 sm:p-4 shadow-lg backdrop-blur-md"
    >
      <!-- Efeito de iluminação suave -->
      <div class="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full bg-amber-500/10 blur-xl"></div>

      <!-- Botão de Fechar -->
      <button
        type="button"
        class="absolute top-2.5 right-2.5 text-slate-400 hover:text-white transition-colors p-1 rounded-md hover:bg-slate-800/60 z-10"
        title="Ocultar notificação"
        @click="fecharNotificacao"
      >
        <span class="material-symbols-outlined text-base">close</span>
      </button>

      <div class="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pr-6 sm:pr-0">
        <!-- Texto conciso -->
        <div class="flex items-center gap-3">
          <div class="hidden sm:flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30 shrink-0">
            <span class="material-symbols-outlined text-lg">workspace_premium</span>
          </div>
          <div>
            <div class="flex items-center gap-2 mb-0.5">
              <span class="rounded-full bg-amber-500/20 px-2 py-0.5 text-[9px] font-black uppercase text-amber-300 border border-amber-500/30">
                PRO ⭐
              </span>
              <span class="text-xs font-bold text-white uppercase tracking-tight">Evolua no Gestão Motoca</span>
            </div>
            <p class="text-[11px] sm:text-xs text-slate-300 leading-snug max-w-xl">
              Desbloqueie Relatórios por KM, Metas Semanais e Cofres de Economia para acelerar seus ganhos.
            </p>
          </div>
        </div>

        <!-- Botão CTA -->
        <button
          type="button"
          class="h-9 px-4 rounded-lg bg-gradient-to-r from-amber-400 to-yellow-500 text-slate-950 font-headline font-black text-[11px] uppercase shadow hover:from-amber-300 hover:to-yellow-400 transition-all flex items-center justify-center gap-1.5 shrink-0 w-full sm:w-auto"
          @click="irParaPlanos"
        >
          <span>Seja PRO</span>
          <span class="material-symbols-outlined text-sm">arrow_forward</span>
        </button>
      </div>
    </div>
  </div>
</template>

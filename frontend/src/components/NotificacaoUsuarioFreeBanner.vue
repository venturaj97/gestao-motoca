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
  <div v-if="authStore.usuario && !authStore.ehPro && !fechado" class="mb-6">
    <div
      class="relative overflow-hidden rounded-2xl border border-amber-500/30 bg-gradient-to-r from-amber-500/15 via-slate-900/90 to-slate-950 p-5 sm:p-6 shadow-xl backdrop-blur-md"
    >
      <!-- Efeito de iluminação suave em segundo plano -->
      <div class="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-amber-500/10 blur-2xl"></div>
      <div class="pointer-events-none absolute -bottom-16 -left-16 h-48 w-48 rounded-full bg-yellow-500/10 blur-2xl"></div>

      <!-- Botão de Fechar -->
      <button
        type="button"
        class="absolute top-3.5 right-3.5 text-slate-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-slate-800/60 z-10"
        title="Ocultar notificação"
        @click="fecharNotificacao"
      >
        <span class="material-symbols-outlined text-lg">close</span>
      </button>

      <div class="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-5">
        <!-- Conteúdo textual e ícone principal -->
        <div class="space-y-3 max-w-3xl">
          <div class="inline-flex items-center gap-2 rounded-full border border-amber-400/40 bg-amber-500/20 px-3 py-1 text-[10px] font-black uppercase tracking-widest text-amber-300 shadow-sm">
            <span class="material-symbols-outlined text-xs">workspace_premium</span>
            <span>Vantagens Exclusivas para Você</span>
          </div>

          <h3 class="font-headline text-lg sm:text-xl font-black tracking-tight text-white uppercase">
            Aproveite ao Máximo o Gestão Motoca! 🚀
          </h3>

          <p class="font-body text-xs sm:text-sm text-slate-300 leading-relaxed">
            Como usuário no plano FREE, você tem acesso às ferramentas essenciais do seu dia a dia. Desbloqueie a <strong class="text-amber-300">Exibição de Relatórios Inteligentes</strong> para ver o custo exato por KM da sua moto e o <strong class="text-amber-300">Módulo de Metas & Cofres de Economia</strong> para guardar seu dinheiro e realizar todos os seus sonhos!
          </p>

          <!-- Destaques dos Recursos em Mini Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
            <div class="flex items-center gap-2.5 rounded-xl border border-slate-800 bg-slate-900/70 p-3 text-xs text-slate-200">
              <span class="material-symbols-outlined text-amber-400 text-xl flex-shrink-0">analytics</span>
              <div>
                <span class="font-bold block text-amber-300">Exibição de Relatórios</span>
                <span class="text-[11px] text-slate-400">Lucro real, raio-X de despesas e rendimento por KM</span>
              </div>
            </div>

            <div class="flex items-center gap-2.5 rounded-xl border border-slate-800 bg-slate-900/70 p-3 text-xs text-slate-200">
              <span class="material-symbols-outlined text-amber-400 text-xl flex-shrink-0">savings</span>
              <div>
                <span class="font-bold block text-amber-300">Módulo de Metas & Cofre</span>
                <span class="text-[11px] text-slate-400">Guarde seu dinheiro para a moto e realize seus sonhos</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Botão Call To Action -->
        <div class="w-full lg:w-auto flex flex-col sm:flex-row lg:flex-col items-stretch lg:items-end justify-end gap-2.5 flex-shrink-0 pt-2 lg:pt-0">
          <button
            type="button"
            class="h-12 px-6 rounded-xl bg-gradient-to-r from-amber-400 via-amber-500 to-yellow-500 text-slate-950 font-headline font-black text-xs tracking-wider uppercase shadow-lg shadow-amber-500/20 hover:from-amber-300 hover:to-yellow-400 active:scale-95 transition-all flex items-center justify-center gap-2 cursor-pointer whitespace-nowrap"
            @click="irParaPlanos"
          >
            <span>Seja PRO e Tenha Vantagens ⭐</span>
            <span class="material-symbols-outlined text-base">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

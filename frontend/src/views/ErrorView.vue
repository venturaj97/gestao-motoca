<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function irParaInicio() {
  if (authStore.estaLogado) {
    router.push({ name: 'dashboard' })
  } else {
    router.push({ name: 'inicio' })
  }
}

function recarregar() {
  window.location.reload()
}
</script>

<template>
  <div class="min-h-screen bg-background text-on-surface flex flex-col items-center justify-center p-6 relative overflow-hidden">
    <!-- Efeitos de fundo sutis -->
    <div class="pointer-events-none absolute -top-32 -right-32 h-96 w-96 rounded-full bg-error/10 blur-3xl"></div>
    <div class="pointer-events-none absolute -bottom-32 -left-32 h-96 w-96 rounded-full bg-primary-container/10 blur-3xl"></div>

    <main class="relative z-10 max-w-lg w-full text-center space-y-6">
      <!-- Badge de Status -->
      <div class="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-1.5 text-xs font-black uppercase tracking-widest text-red-300 shadow-sm">
        <span aria-hidden="true">⚠️</span>
        <span>SISTEMA • FALHA INESPERADA</span>
      </div>

      <!-- Ícone Visual de Erro -->
      <div class="mx-auto flex h-28 w-28 items-center justify-center rounded-3xl border border-red-500/30 bg-surface-container-low shadow-2xl backdrop-blur-md">
        <span class="material-symbols-outlined text-6xl text-red-400" aria-hidden="true">warning</span>
      </div>

      <!-- Título Principal -->
      <div class="space-y-2">
        <h1 class="font-headline text-3xl sm:text-4xl font-black tracking-tight text-white uppercase leading-tight">
          Ops! Tivemos um Imprevisto
        </h1>
        <p class="font-body text-sm sm:text-base text-on-surface-variant max-w-md mx-auto leading-relaxed">
          Ocorreu um erro temporário durante o processamento. Seus dados de rodagem e financeiro permanecem 100% seguros.
        </p>
      </div>

      <!-- Botões de Ação -->
      <div class="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3 w-full">
        <button
          type="button"
          aria-label="Voltar para a página inicial"
          class="w-full sm:w-auto min-h-[48px] px-8 py-3.5 rounded-xl bg-primary-container text-on-primary-fixed font-headline font-black text-xs uppercase tracking-widest shadow-lg shadow-primary-container/20 hover:opacity-90 active:scale-95 transition-all flex items-center justify-center gap-2"
          @click="irParaInicio"
        >
          <span class="material-symbols-outlined text-base" aria-hidden="true">home</span>
          VOLTAR PARA O INÍCIO
        </button>

        <button
          type="button"
          aria-label="Recarregar a página"
          class="w-full sm:w-auto min-h-[48px] px-6 py-3.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface font-headline font-bold text-xs uppercase tracking-wider hover:bg-surface-container transition-all flex items-center justify-center gap-2"
          @click="recarregar"
        >
          <span class="material-symbols-outlined text-base" aria-hidden="true">refresh</span>
          TENTAR NOVAMENTE
        </button>
      </div>
    </main>
  </div>
</template>

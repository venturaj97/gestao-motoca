<script setup lang="ts">
import { useRouter } from 'vue-router'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()

const recursos = [
  {
    icon: 'payments',
    titulo: 'GANHOS E DESPESAS',
    texto: 'Registre corridas, diárias, gastos de rua e veja exatamente o lucro líquido do seu trabalho.',
  },
  {
    icon: 'two_wheeler',
    titulo: 'CONTROLE DA MOTO',
    texto: 'Acompanhe odômetro, trocas de óleo, combustível e histórico de manutenção em tempo real.',
  },
  {
    icon: 'analytics',
    titulo: 'VISÃO EXECUTIVA',
    texto: 'Tenha relatórios claros por dia, semana e mês com alertas para tomada de decisão consciente.',
  },
]
</script>

<template>
  <main class="min-h-screen bg-background text-on-surface font-body flex flex-col">
    <!-- Theme Toggle Flutuante -->
    <ThemeToggle />

    <!-- Hero Section -->
    <section class="relative overflow-hidden border-b border-outline-variant/60">
      <div class="absolute inset-0 bg-gradient-to-br from-primary-container/10 via-background to-surface-container-low opacity-80 pointer-events-none"></div>

      <header class="relative z-10 flex items-center justify-between px-6 py-6 max-w-6xl mx-auto w-full">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 bg-primary-container text-on-primary-fixed flex items-center justify-center shadow-md">
            <span class="material-symbols-outlined text-2xl">two_wheeler</span>
          </div>
          <div>
            <h1 class="font-headline font-black text-primary-container text-lg tracking-wider uppercase leading-none">
              GESTÃO MOTOCA
            </h1>
            <p class="font-label text-[9px] tracking-[0.25em] text-on-surface-variant uppercase mt-1">
              Controle real da sua jornada
            </p>
          </div>
        </div>

        <button
          class="hidden sm:flex h-11 items-center gap-2 border-2 border-primary-container/40 bg-surface-container px-5
                 font-label text-[11px] font-black tracking-widest uppercase text-primary-container hover:bg-primary-container hover:text-on-primary-fixed transition-all"
          @click="router.push({ name: 'login' })"
        >
          <span class="material-symbols-outlined text-base">login</span>
          ENTRAR
        </button>
      </header>

      <div class="relative z-10 px-6 py-12 sm:py-20 max-w-6xl mx-auto w-full">
        <div class="max-w-2xl space-y-6">
          <div class="inline-flex items-center gap-2.5 px-3 py-1 bg-primary-container/10 border-l-4 border-primary-container">
            <span class="font-label text-[10px] font-black tracking-[0.2em] text-primary-container uppercase">
              PLATAFORMA PARA PILOTOS E ENTREGADORES
            </span>
          </div>

          <h2 class="font-headline text-4xl sm:text-6xl font-black leading-[0.95] tracking-tight uppercase">
            SABER QUANTO SOBRA DE VERDADE NO SEU BOLSO.
          </h2>

          <p class="text-base sm:text-lg leading-relaxed text-on-surface-variant font-body">
            Pare de chutar o seu lucro. Cadastre seus ganhos e custos de combustível, manutenção e diárias com total precisão.
          </p>

          <div class="pt-2 flex flex-col sm:flex-row gap-3">
            <button
              class="h-14 sm:px-8 bg-primary-container text-on-primary-fixed font-headline font-black
                     text-xs tracking-widest uppercase flex items-center justify-center gap-3 hover:brightness-110
                     active:scale-[0.98] transition-all shadow-lg cursor-pointer"
              @click="router.push({ name: 'cadastro' })"
            >
              <span class="material-symbols-outlined">rocket_launch</span>
              CRIAR MINHA CONTA GRÁTIS
            </button>

            <button
              class="h-14 sm:px-8 bg-surface-container border-2 border-outline-variant text-on-surface font-headline
                     text-xs font-bold tracking-widest uppercase flex items-center justify-center gap-3 hover:bg-surface-bright
                     active:scale-[0.98] transition-all cursor-pointer"
              @click="router.push({ name: 'login' })"
            >
              <span class="material-symbols-outlined">login</span>
              JÁ TENHO CADASTRO
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Recursos / Cards -->
    <section class="flex-1 px-6 py-12 bg-surface-container-low">
      <div class="max-w-6xl mx-auto grid gap-6 md:grid-cols-3">
        <article
          v-for="recurso in recursos"
          :key="recurso.titulo"
          class="bg-surface-container p-6 border-t-4 border-primary-container shadow-sm flex flex-col justify-between"
        >
          <div>
            <div class="w-12 h-12 bg-primary-container/15 text-primary-container flex items-center justify-center mb-4">
              <span class="material-symbols-outlined text-2xl">{{ recurso.icon }}</span>
            </div>
            <h3 class="font-headline text-lg font-black tracking-wide text-on-surface uppercase mb-2">
              {{ recurso.titulo }}
            </h3>
            <p class="text-xs leading-relaxed text-on-surface-variant font-body">
              {{ recurso.texto }}
            </p>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import heroUrl from '@/assets/hero.png'

const router = useRouter()

const recursos = [
  {
    icon: 'payments',
    titulo: 'Ganhos e despesas',
    texto: 'Registre corridas, diarias, gastos e veja o que realmente sobra.',
  },
  {
    icon: 'two_wheeler',
    titulo: 'Moto no centro',
    texto: 'Controle placa, abastecimentos, manutencoes e custos da sua moto.',
  },
  {
    icon: 'analytics',
    titulo: 'Visao do mes',
    texto: 'Acompanhe saldo, indicadores e alertas para decidir melhor.',
  },
]
</script>

<template>
  <main class="min-h-screen bg-background text-on-background font-body">
    <section class="relative overflow-hidden">
      <img
        :src="heroUrl"
        alt=""
        class="absolute inset-0 h-full w-full object-cover opacity-20 dark:opacity-28"
      />
      <div class="absolute inset-0 bg-background/86 dark:bg-background/82"></div>

      <header class="relative z-10 flex items-center justify-between px-4 pt-4 sm:px-8 sm:pt-6">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 bg-primary-container text-on-primary-fixed flex items-center justify-center">
            <span class="material-symbols-outlined text-xl">two_wheeler</span>
          </div>
          <div>
            <p class="font-headline font-black text-primary-container text-sm tracking-widest uppercase">
              Gestao Motoca
            </p>
            <p class="font-label text-[9px] tracking-[0.2em] text-on-surface-variant uppercase">
              Controle real da rua
            </p>
          </div>
        </div>

        <button
          class="hidden sm:flex h-11 items-center gap-2 border border-outline-variant bg-surface-container/80 px-4
                 font-label text-[11px] font-bold tracking-widest uppercase text-on-surface hover:bg-surface-bright"
          @click="router.push({ name: 'login' })"
        >
          <span class="material-symbols-outlined text-sm">login</span>
          Entrar
        </button>
      </header>

      <div class="relative z-10 px-4 sm:px-8 pt-10 pb-5 sm:pt-14 sm:pb-8">
        <div class="w-full max-w-3xl">
          <div class="mb-4 flex items-center gap-3">
            <div class="h-[3px] w-8 bg-primary-container"></div>
            <span class="font-label text-[9px] font-bold tracking-[0.24em] text-primary-container uppercase">
              Feito para motoboy
            </span>
          </div>

          <h1 class="font-headline text-4xl sm:text-6xl font-black leading-[0.95] tracking-normal uppercase">
            Gestao Motoca
          </h1>

          <p class="mt-4 max-w-xl text-[15px] sm:text-lg leading-relaxed text-on-surface-variant">
            Controle ganhos, gastos, abastecimentos e manutencoes em um so lugar.
            Veja quanto sobra de verdade no fim do dia.
          </p>

          <div class="mt-6 grid gap-2 sm:flex sm:items-center">
            <button
              class="h-14 sm:min-w-56 bg-primary-container text-on-primary-fixed font-headline font-black
                     text-sm tracking-widest uppercase flex items-center justify-center gap-3 hover:brightness-105
                     active:scale-[0.98] transition-all"
              @click="router.push({ name: 'cadastro' })"
            >
              <span class="material-symbols-outlined">rocket_launch</span>
              Comecar agora
            </button>

            <button
              class="h-14 sm:min-w-56 bg-surface-container border border-outline-variant text-on-surface font-headline
                     text-sm font-bold tracking-widest uppercase flex items-center justify-center gap-3 hover:bg-surface-bright
                     active:scale-[0.98] transition-all"
              @click="router.push({ name: 'login' })"
            >
              <span class="material-symbols-outlined">login</span>
              Ja faco minha gestao
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="px-4 sm:px-8 pb-24 pt-3 bg-surface">
      <div class="mx-auto grid max-w-6xl gap-2 md:grid-cols-3">
        <article
          v-for="recurso in recursos"
          :key="recurso.titulo"
          class="bg-surface-container border border-outline-variant p-4 flex gap-3 md:block"
        >
          <div class="flex h-10 w-10 shrink-0 items-center justify-center bg-primary-container/15 text-primary-container md:mb-4">
            <span class="material-symbols-outlined text-xl">{{ recurso.icon }}</span>
          </div>
          <div>
            <h2 class="font-headline text-base md:text-xl font-black tracking-normal text-on-surface">
              {{ recurso.titulo }}
            </h2>
            <p class="mt-1 text-sm leading-snug text-on-surface-variant md:leading-relaxed">
              {{ recurso.texto }}
            </p>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

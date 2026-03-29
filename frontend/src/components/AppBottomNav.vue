<template>
  <nav class="fixed bottom-0 left-0 right-0 z-40 border-t-4 border-surface-container bg-background">
    <div class="mx-auto grid h-20 max-w-md grid-cols-5">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="flex flex-col items-center justify-center gap-1 text-[10px] font-bold uppercase tracking-[0.12em] transition"
        :class="isActive(item.to) ? 'bg-primary-container text-black' : 'text-zinc-500 hover:bg-surface-container'"
      >
        <span class="material-symbols-outlined">{{ item.icon }}</span>
        <span class="font-command">{{ item.label }}</span>
      </RouterLink>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute, RouterLink } from 'vue-router'

const route = useRoute()

const items = [
  { to: '/dashboard', icon: 'dashboard', label: 'Início' },
  { to: '/historico', icon: 'history', label: 'Histórico' },
  { to: '/lancar', icon: 'add_box', label: 'Lançar' },
  { to: '/manutencao', icon: 'build', label: 'Manutenção' },
  { to: '/moto', icon: 'two_wheeler', label: 'Moto' },
]

const isActive = (to: string) => route.path === to || route.path.startsWith(`${to}/`)
</script>

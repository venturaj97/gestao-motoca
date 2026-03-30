<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="bg-background min-h-screen flex flex-col items-center justify-center gap-6">
    <p class="text-primary-container font-headline text-xl tracking-widest">
      DASHBOARD — EM CONSTRUÇÃO
    </p>
    <p class="text-on-surface-variant font-body text-sm">
      Logado como: <span class="text-primary-fixed font-bold">{{ authStore.usuario?.nome || '...' }}</span>
    </p>
    <button
      class="flex items-center gap-2 px-6 py-3 bg-secondary-container text-on-secondary-container
             font-label font-bold text-xs tracking-widest uppercase transition-all active:scale-95
             hover:brightness-110"
      @click="logout"
    >
      <span class="material-symbols-outlined text-sm">logout</span>
      SAIR / DESLOGAR
    </button>
  </div>
</template>

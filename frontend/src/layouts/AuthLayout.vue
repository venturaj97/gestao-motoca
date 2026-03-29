<template>
  <main class="min-h-screen overflow-hidden bg-background text-on-surface">
    <div class="relative flex min-h-screen items-center justify-center px-6 py-10">
      <div class="absolute left-[-10%] top-[-10%] h-64 w-64 bg-primary-container/10 blur-[120px]" />
      <div class="absolute bottom-[-10%] right-[-10%] h-56 w-56 bg-secondary-container/10 blur-[100px]" />
      <div class="relative z-10 w-full max-w-md">
        <RouterView />
      </div>
    </div>
    <footer class="flex h-8 items-center justify-between border-t border-outline-variant/20 bg-surface-container-low px-6">
      <span class="tactical-label text-[9px]">SERVIDOR ATIVO: BRA-SP-01</span>
      <span class="tactical-label text-[9px]">TACTICAL BUILD</span>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

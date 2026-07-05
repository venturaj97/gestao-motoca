<script setup lang="ts">
import { RouterView } from 'vue-router'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <div class="app-shell" :class="{ dark: theme.escuro }">
    <RouterView />
    <ThemeToggle />
  </div>
</template>

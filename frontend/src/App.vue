<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <div class="app-shell" :class="{ dark: theme.escuro }">
    <RouterView />
  </div>
</template>

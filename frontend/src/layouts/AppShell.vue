<template>
  <div class="tactical-shell">
    <RouterView />
    <AppBottomNav />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppBottomNav from '@/components/AppBottomNav.vue'
</script>

<template>
  <header :class="['sticky top-0 z-40 flex h-16 items-center justify-between px-5', borderClass]">
    <div class="flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center overflow-hidden bg-surface-container-highest">
        <span class="material-symbols-outlined text-primary-container">two_wheeler</span>
      </div>
      <div>
        <p v-if="eyebrow" class="tactical-label text-primary-container">{{ eyebrow }}</p>
        <h1 class="font-command text-lg font-black tracking-tight text-primary-container">
          GESTÃO MOTOCA
        </h1>
      </div>
    </div>
    <div class="flex items-center gap-3">
      <p v-if="userName" class="hidden text-right text-[11px] font-medium text-zinc-400 sm:block">
        {{ userName }}
      </p>
      <button class="p-2 text-zinc-400 transition hover:text-primary-container" @click="handleIconClick">
        <span class="material-symbols-outlined">{{ icon }}</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = withDefaults(
  defineProps<{
    eyebrow?: string
    icon?: string
    borderClass?: string
    iconAction?: 'logout' | 'none'
  }>(),
  {
    eyebrow: '',
    icon: 'settings',
    borderClass: 'border-l-4 border-primary-container bg-background',
    iconAction: 'none',
  },
)

const router = useRouter()
const auth = useAuthStore()
const userName = computed(() => auth.user?.nome ?? '')

const handleIconClick = async () => {
  if (props.iconAction !== 'logout') return

  auth.logout()
  await router.push('/auth/login')
}
</script>

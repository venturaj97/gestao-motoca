<template>
  <section>
    <div class="mb-12 border-l-4 border-primary-container pl-6">
      <p class="tactical-label mb-2 text-primary-container">SISTEMA OPERACIONAL</p>
      <h1 class="font-command text-5xl font-black leading-none tracking-tighter">NOVA CONTA</h1>
    </div>

    <form class="space-y-6" @submit.prevent="handleSubmit">
      <div class="space-y-2">
        <label class="tactical-label">Nome completo</label>
        <input v-model="form.nome" class="tactical-input" placeholder="INSIRA SEU NOME" />
      </div>

      <div class="space-y-2">
        <label class="tactical-label">E-mail operacional</label>
        <input v-model="form.email" class="tactical-input" placeholder="ENDEREÇO DE ACESSO" type="email" />
      </div>

      <div class="space-y-2">
        <label class="tactical-label">Chave de acesso</label>
        <input v-model="form.senha" class="tactical-input" placeholder="••••••••" type="password" />
      </div>

      <div v-if="auth.errorMessage" class="border-l-4 border-secondary bg-secondary-container/10 p-4 text-sm text-zinc-100">
        {{ auth.errorMessage }}
      </div>

      <button
        class="flex h-20 w-full items-center justify-center gap-4 bg-gradient-to-br from-primary to-primary-container font-command text-xl font-black uppercase tracking-[0.16em] text-on-primary-fixed transition active:scale-[0.98]"
        :disabled="auth.loading"
        type="submit"
      >
        {{ auth.loading ? 'CRIANDO...' : 'CRIAR CONTA' }}
        <span class="material-symbols-outlined">double_arrow</span>
      </button>
    </form>

    <div class="mt-8 flex items-center justify-between border-t border-outline-variant/20 py-6">
      <p class="tactical-label text-[11px]">Já tem conta?</p>
      <RouterLink
        to="/auth/login"
        class="font-command text-sm font-bold uppercase tracking-[0.18em] text-primary-container"
      >
        Login
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  nome: '',
  email: '',
  senha: '',
})

const handleSubmit = async () => {
  const success = await auth.register(form)

  if (!success) return

  await router.push('/dashboard')
}
</script>

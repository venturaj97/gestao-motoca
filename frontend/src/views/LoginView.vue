<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const senha = ref('')
const erro = ref('')
const carregando = ref(false)
const mostrarSenha = ref(false)

async function handleLogin() {
  erro.value = ''
  if (!email.value || !senha.value) {
    erro.value = 'Preencha e-mail e senha.'
    return
  }
  try {
    carregando.value = true
    const resposta = await login({ email: email.value, senha: senha.value })
    authStore.salvarToken(resposta.access_token)
    await authStore.carregarUsuario()
    router.push({ name: 'dashboard' })
  } catch (e: any) {
    const status = e?.response?.status
    if (status === 401) {
      erro.value = 'E-mail ou senha inválidos.'
    } else {
      erro.value = 'Erro ao conectar. Tente novamente.'
    }
  } finally {
    carregando.value = false
  }
}
</script>

<template>
  <div class="bg-background text-on-background font-body min-h-screen flex flex-col tactical-grid">

    <!-- Brand Header -->
    <header class="w-full flex justify-center pt-12 pb-8">
      <div class="flex flex-col items-center">
        <div class="w-16 h-16 bg-primary-container flex items-center justify-center mb-4">
          <span class="material-symbols-outlined text-on-primary-fixed text-4xl">two_wheeler</span>
        </div>
        <h1 class="font-headline font-bold text-primary-fixed tracking-widest text-sm uppercase">
          GESTÃO MOTOCA
        </h1>
      </div>
    </header>

    <!-- Form Card -->
    <main class="flex-grow flex items-center justify-center px-6">
      <div class="w-full max-w-md bg-surface-container-low p-8 relative">

        <!-- Tactical corner accent -->
        <div class="absolute top-0 left-0 w-8 h-[2px] bg-primary-container"></div>
        <div class="absolute top-0 left-0 w-[2px] h-8 bg-primary-container"></div>

        <div class="mb-12">
          <h2 class="font-headline text-5xl font-bold tracking-tighter text-on-background mb-2">
            ENTRAR
          </h2>
          <div class="h-1 w-12 bg-primary-container"></div>
        </div>

        <form class="space-y-8" @submit.prevent="handleLogin">

          <!-- Email -->
          <div class="group">
            <label class="block font-label text-[10px] tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              E-MAIL
            </label>
            <div class="relative">
              <input
                v-model="email"
                type="email"
                placeholder="operador@gestaomotoca.com"
                autocomplete="email"
                class="tactical-input py-4 px-4 pr-10"
              />
              <div class="absolute right-0 top-4 text-outline group-focus-within:text-primary-fixed transition-colors pointer-events-none">
                <span class="material-symbols-outlined">alternate_email</span>
              </div>
            </div>
          </div>

          <!-- Senha -->
          <div class="group">
            <label class="block font-label text-[10px] tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              SENHA
            </label>
            <div class="relative">
              <input
                v-model="senha"
                :type="mostrarSenha ? 'text' : 'password'"
                placeholder="••••••••"
                autocomplete="current-password"
                class="tactical-input py-4 px-4 pr-10"
              />
              <button
                type="button"
                tabindex="-1"
                class="absolute right-0 top-4 text-outline hover:text-primary-fixed transition-colors"
                @click="mostrarSenha = !mostrarSenha"
              >
                <span class="material-symbols-outlined">
                  {{ mostrarSenha ? 'visibility_off' : 'visibility' }}
                </span>
              </button>
            </div>
          </div>

          <!-- Erro -->
          <div v-if="erro" class="bg-error-container text-on-error-container text-sm font-label px-4 py-3 tracking-wide">
            {{ erro }}
          </div>

          <!-- Submit -->
          <div class="pt-4">
            <button
              type="submit"
              :disabled="carregando"
              class="btn-primary h-16 text-lg tracking-widest disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="carregando" class="material-symbols-outlined animate-spin">refresh</span>
              <span v-else>CONECTAR AGORA</span>
              <span v-if="!carregando" class="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
        </form>

        <!-- Links secundários -->
        <div class="mt-8 flex flex-col gap-4">
          <div class="h-[1px] w-full bg-surface-container"></div>
          <button
            class="text-left font-label text-[11px] tracking-wider text-on-surface-variant hover:text-primary-fixed transition-colors uppercase flex items-center gap-2"
            @click="$router.push({ name: 'cadastro' })"
          >
            <span class="material-symbols-outlined text-sm">person_add</span>
            Criar nova conta
          </button>
        </div>
      </div>
    </main>

    <!-- Footer tactical -->
    <footer class="p-6 flex justify-between items-end">
      <div class="text-[10px] font-label text-outline uppercase tracking-[0.3em]">
        SISTEMA OPERACIONAL V1.0
      </div>
      <div class="flex flex-col items-end">
        <span class="text-[9px] font-label text-outline uppercase tracking-widest">STATUS REDE</span>
        <span class="text-[10px] font-headline text-primary-fixed flex items-center gap-1">
          ONLINE <span class="w-1.5 h-1.5 bg-primary-fixed rounded-full"></span>
        </span>
      </div>
    </footer>

  </div>
</template>

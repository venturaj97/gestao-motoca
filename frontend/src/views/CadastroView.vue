<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { criarUsuario, login } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const nome = ref('')
const email = ref('')
const senha = ref('')
const erro = ref('')
const carregando = ref(false)
const sucesso = ref(false)

// Validação de formato de email
function emailValido(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)
}

async function handleCadastro() {
  erro.value = ''

  if (!nome.value.trim() || !email.value.trim() || !senha.value) {
    erro.value = 'Preencha todos os campos.'
    return
  }
  if (!emailValido(email.value)) {
    erro.value = 'Informe um e-mail válido (ex: nome@dominio.com).'
    return
  }
  if (senha.value.length < 6) {
    erro.value = 'A senha deve ter pelo menos 6 caracteres.'
    return
  }

  try {
    carregando.value = true

    // 1. Cria a conta
    await criarUsuario({ nome: nome.value.trim(), email: email.value.trim(), senha: senha.value })

    // 2. Faz login automático com as mesmas credenciais
    const resposta = await login({ email: email.value.trim(), senha: senha.value })
    authStore.salvarToken(resposta.access_token)
    await authStore.carregarUsuario()

    sucesso.value = true

    // 3. Redireciona para o dashboard
    setTimeout(() => router.push({ name: 'dashboard' }), 800)

  } catch (e: any) {
    const status = e?.response?.status
    const detail = e?.response?.data?.detail
    if (status === 409) {
      erro.value = 'Este e-mail já está cadastrado.'
    } else if (status === 422 && detail?.includes('72')) {
      erro.value = 'Senha muito longa (máximo 72 caracteres).'
    } else {
      erro.value = 'Erro ao criar conta. Tente novamente.'
    }
  } finally {
    carregando.value = false
  }
}
</script>

<template>
  <div class="bg-background text-on-background font-body min-h-screen flex flex-col relative overflow-hidden">

    <!-- Background blobs decorativos -->
    <div class="absolute top-0 left-0 w-full h-full opacity-5 pointer-events-none">
      <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-container blur-[120px]"></div>
      <div class="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-secondary-container blur-[100px]"></div>
    </div>

    <main class="flex-grow flex items-center justify-center p-6 sm:p-12 z-10">
      <div class="w-full max-w-md">

        <!-- Header -->
        <div class="mb-12 border-l-4 border-primary-container pl-6">
          <h2 class="font-headline font-black text-primary-container text-xs tracking-[0.3em] mb-2">
            SISTEMA OPERACIONAL
          </h2>
          <h1 class="font-headline font-bold text-5xl sm:text-6xl text-on-background leading-none tracking-tighter">
            NOVA CONTA
          </h1>
        </div>

        <!-- Sucesso -->
        <div v-if="sucesso" class="bg-primary-container text-on-primary-fixed font-label font-bold px-6 py-4 text-sm tracking-widest mb-6">
          ✓ CONTA CRIADA! Redirecionando...
        </div>

        <!-- Formulário -->
        <form v-else class="space-y-6" @submit.prevent="handleCadastro">

          <!-- Nome -->
          <div class="space-y-2">
            <label class="font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
              NOME COMPLETO
            </label>
            <div class="relative group">
              <input
                v-model="nome"
                type="text"
                placeholder="INSIRA SEU NOME"
                class="w-full h-16 bg-surface-container-lowest border-0 border-b-2 border-outline-variant
                       focus:border-primary-container focus:outline-none focus:ring-0
                       text-on-surface font-headline font-medium tracking-wide placeholder:text-outline
                       transition-all px-4"
              />
              <div class="absolute right-4 top-1/2 -translate-y-1/2 text-outline-variant group-focus-within:text-primary-container transition-colors">
                <span class="material-symbols-outlined">person</span>
              </div>
            </div>
          </div>

          <!-- Email -->
          <div class="space-y-2">
            <label class="font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
              E-MAIL OPERACIONAL
            </label>
            <div class="relative group">
              <input
                v-model="email"
                type="email"
                placeholder="ENDEREÇO DE ACESSO"
                autocomplete="email"
                class="w-full h-16 bg-surface-container-lowest border-0 border-b-2 border-outline-variant
                       focus:border-primary-container focus:outline-none focus:ring-0
                       text-on-surface font-headline font-medium tracking-wide placeholder:text-outline
                       transition-all px-4"
              />
              <div class="absolute right-4 top-1/2 -translate-y-1/2 text-outline-variant group-focus-within:text-primary-container transition-colors">
                <span class="material-symbols-outlined">alternate_email</span>
              </div>
            </div>
          </div>

          <!-- Senha -->
          <div class="space-y-2">
            <label class="font-label text-[10px] font-bold tracking-[0.2em] text-on-surface-variant uppercase">
              CHAVE DE ACESSO
            </label>
            <div class="relative group">
              <input
                v-model="senha"
                type="password"
                placeholder="••••••••"
                autocomplete="new-password"
                class="w-full h-16 bg-surface-container-lowest border-0 border-b-2 border-outline-variant
                       focus:border-primary-container focus:outline-none focus:ring-0
                       text-on-surface font-headline font-medium tracking-wide placeholder:text-outline
                       transition-all px-4"
              />
              <div class="absolute right-4 top-1/2 -translate-y-1/2 text-outline-variant group-focus-within:text-primary-container transition-colors">
                <span class="material-symbols-outlined">lock</span>
              </div>
            </div>
          </div>

          <!-- Erro -->
          <div v-if="erro" class="bg-error-container text-on-error-container text-sm font-label px-4 py-3 tracking-wide">
            {{ erro }}
          </div>

          <!-- Submit -->
          <div class="pt-6">
            <button
              type="submit"
              :disabled="carregando"
              class="w-full h-20 bg-tactical-gradient text-on-primary-fixed font-headline font-black
                     text-xl tracking-widest uppercase flex items-center justify-center gap-4
                     active:scale-95 transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="carregando" class="material-symbols-outlined animate-spin">refresh</span>
              <template v-else>
                CRIAR CONTA
                <span class="material-symbols-outlined">double_arrow</span>
              </template>
            </button>
          </div>
        </form>

        <!-- Link para login -->
        <div class="mt-8 flex items-center justify-between py-6 border-t border-outline-variant/20">
          <p class="font-label text-[11px] tracking-widest text-on-surface-variant uppercase">
            Já tem conta?
          </p>
          <button
            class="font-headline font-bold text-primary-container hover:text-primary text-sm tracking-widest flex items-center gap-2 group"
            @click="router.push({ name: 'login' })"
          >
            LOGIN
            <span class="material-symbols-outlined text-sm group-hover:translate-x-1 transition-transform">
              arrow_forward
            </span>
          </button>
        </div>

      </div>
    </main>

    <!-- Bottom status bar -->
    <footer class="h-8 bg-surface-container-low flex items-center px-6 justify-between border-t border-outline-variant/10 z-10">
      <div class="flex items-center gap-4">
        <div class="w-2 h-2 bg-primary-container animate-pulse rounded-full"></div>
        <span class="text-[9px] font-label font-bold tracking-widest text-outline uppercase">
          SERVIDOR ATIVO: LOCAL
        </span>
      </div>
      <span class="text-[9px] font-label font-bold tracking-widest text-outline uppercase">v1.0.0</span>
    </footer>

  </div>
</template>

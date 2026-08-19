<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/api/auth'
import { solicitarRecuperacao, redefinirSenha } from '@/api/recuperacao'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const senha = ref('')
const erro = ref('')
const carregando = ref(false)
const mostrarSenha = ref(false)

// Estados para recuperação de senha
const mostrarModalRecuperacao = ref(false)
const etapaRecuperacao = ref<1 | 2>(1)
const emailRecuperacao = ref('')
const pinRecuperacao = ref('')
const novaSenhaRecuperacao = ref('')
const sucessoRecuperacao = ref('')
const erroRecuperacao = ref('')
const carregandoRecuperacao = ref(false)

function abrirModalRecuperacao() {
  emailRecuperacao.value = email.value || ''
  pinRecuperacao.value = ''
  novaSenhaRecuperacao.value = ''
  sucessoRecuperacao.value = ''
  erroRecuperacao.value = ''
  etapaRecuperacao.value = 1
  mostrarModalRecuperacao.value = true
}

async function solicitarPin() {
  if (!emailRecuperacao.value) {
    erroRecuperacao.value = 'Informe o seu e-mail.'
    return
  }
  erroRecuperacao.value = ''
  carregandoRecuperacao.value = true
  try {
    const res = await solicitarRecuperacao(emailRecuperacao.value)
    sucessoRecuperacao.value = res.mensagem || 'Código de verificação enviado para o seu e-mail.'
    etapaRecuperacao.value = 2
  } catch (e: any) {
    erroRecuperacao.value = e?.response?.data?.detail || 'Erro ao enviar e-mail. Verifique o e-mail digitado.'
  } finally {
    carregandoRecuperacao.value = false
  }
}

async function executarRedefinicao() {
  if (!pinRecuperacao.value || pinRecuperacao.value.length !== 6) {
    erroRecuperacao.value = 'O código PIN deve conter 6 dígitos.'
    return
  }
  if (!novaSenhaRecuperacao.value || novaSenhaRecuperacao.value.length < 6) {
    erroRecuperacao.value = 'A nova senha deve conter no mínimo 6 caracteres.'
    return
  }
  erroRecuperacao.value = ''
  carregandoRecuperacao.value = true
  try {
    const res = await redefinirSenha({
      email: emailRecuperacao.value,
      codigo_pin: pinRecuperacao.value,
      nova_senha: novaSenhaRecuperacao.value,
    })
    alert(res.mensagem || 'Senha redefinida com sucesso!')
    mostrarModalRecuperacao.value = false
    email.value = emailRecuperacao.value
    senha.value = novaSenhaRecuperacao.value
  } catch (e: any) {
    erroRecuperacao.value = e?.response?.data?.detail || 'Código inválido ou expirado. Tente novamente.'
  } finally {
    carregandoRecuperacao.value = false
  }
}

async function handleLogin() {
  // Só limpa o erro após validação — mantém a mensagem visível
  if (!email.value || !senha.value) {
    erro.value = 'Preencha e-mail e senha.'
    return
  }
  erro.value = ''
  carregando.value = true
  try {
    const resposta = await login({ email: email.value, senha: senha.value })
    authStore.salvarToken(resposta.access_token, resposta.refresh_token)
    await authStore.carregarUsuario()
    router.push({ name: 'dashboard' })
  } catch (e: any) {
    const status = e?.response?.status
    if (status === 401) {
      erro.value = 'E-mail ou senha incorretos. Verifique e tente novamente.'
    } else {
      erro.value = 'Não foi possível conectar ao servidor. Tente novamente.'
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
          <div
            v-if="erro"
            class="flex items-start gap-3 bg-error-container text-on-error-container
                   text-sm font-label px-4 py-3 border-l-4 border-error"
          >
            <span class="material-symbols-outlined text-base mt-0.5 flex-shrink-0">error</span>
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
          <div class="flex flex-col sm:flex-row justify-between gap-3">
            <button
              class="text-left font-label text-[11px] tracking-wider text-on-surface-variant hover:text-primary-fixed transition-colors uppercase flex items-center gap-2"
              @click="$router.push({ name: 'cadastro' })"
            >
              <span class="material-symbols-outlined text-sm">person_add</span>
              Criar nova conta
            </button>
            <button
              type="button"
              class="text-left font-label text-[11px] tracking-wider text-primary-fixed hover:underline transition-colors uppercase flex items-center gap-2"
              @click="abrirModalRecuperacao"
            >
              <span class="material-symbols-outlined text-sm">lock_reset</span>
              Esqueci minha senha
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Modal de Recuperação de Senha -->
    <div
      v-if="mostrarModalRecuperacao"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
    >
      <div class="w-full max-w-md bg-surface-container-low p-6 sm:p-8 relative border border-outline/30 shadow-2xl">
        <!-- Tactical corner accent -->
        <div class="absolute top-0 left-0 w-8 h-[2px] bg-primary-container"></div>
        <div class="absolute top-0 left-0 w-[2px] h-8 bg-primary-container"></div>

        <div class="flex justify-between items-center mb-6">
          <h3 class="font-headline text-2xl font-bold tracking-tight text-on-background">
            {{ etapaRecuperacao === 1 ? 'RECUPERAR SENHA' : 'DIGITAR CÓDIGO PIN' }}
          </h3>
          <button
            type="button"
            class="text-on-surface-variant hover:text-on-background transition-colors p-1"
            @click="mostrarModalRecuperacao = false"
          >
            <span class="material-symbols-outlined text-xl">close</span>
          </button>
        </div>

        <!-- Etapa 1: Solicitar Código PIN por E-mail -->
        <form v-if="etapaRecuperacao === 1" class="space-y-6" @submit.prevent="solicitarPin">
          <p class="text-xs font-body text-on-surface-variant leading-relaxed">
            Informe o e-mail cadastrado. Enviaremos um <strong>código de verificação de 6 dígitos</strong> para você redefinir sua senha.
          </p>

          <div>
            <label class="block font-label text-[10px] tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              SEU E-MAIL
            </label>
            <input
              v-model="emailRecuperacao"
              type="email"
              required
              placeholder="seu-email@exemplo.com"
              class="tactical-input py-3 px-4"
            />
          </div>

          <div v-if="erroRecuperacao" class="bg-error-container text-on-error-container text-xs p-3 font-label">
            {{ erroRecuperacao }}
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              class="px-4 py-3 text-xs font-label uppercase text-on-surface-variant hover:bg-surface-container"
              @click="mostrarModalRecuperacao = false"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="carregandoRecuperacao"
              class="btn-primary py-3 px-6 text-xs tracking-wider disabled:opacity-50"
            >
              <span v-if="carregandoRecuperacao" class="material-symbols-outlined animate-spin text-sm mr-1">refresh</span>
              ENVIAR CÓDIGO
            </button>
          </div>
        </form>

        <!-- Etapa 2: Confirmar PIN e Nova Senha -->
        <form v-else class="space-y-6" @submit.prevent="executarRedefinicao">
          <p class="text-xs font-body text-on-surface-variant leading-relaxed">
            Enviamos um e-mail para <strong>{{ emailRecuperacao }}</strong>. Digite o código de 6 dígitos recebido e sua nova senha:
          </p>

          <div v-if="sucessoRecuperacao" class="bg-primary-container/20 text-primary-fixed border-l-2 border-primary-fixed text-xs p-3 font-label">
            {{ sucessoRecuperacao }}
          </div>

          <div>
            <label class="block font-label text-[10px] tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              CÓDIGO PIN (6 DÍGITOS)
            </label>
            <input
              v-model="pinRecuperacao"
              type="text"
              maxlength="6"
              required
              placeholder="123456"
              class="tactical-input py-3 px-4 font-mono text-lg tracking-widest text-center"
            />
          </div>

          <div>
            <label class="block font-label text-[10px] tracking-[0.2em] text-on-surface-variant mb-2 uppercase">
              NOVA SENHA
            </label>
            <input
              v-model="novaSenhaRecuperacao"
              type="password"
              required
              minlength="6"
              placeholder="••••••••"
              class="tactical-input py-3 px-4"
            />
          </div>

          <div v-if="erroRecuperacao" class="bg-error-container text-on-error-container text-xs p-3 font-label">
            {{ erroRecuperacao }}
          </div>

          <div class="flex justify-between items-center pt-2">
            <button
              type="button"
              class="text-xs font-label uppercase text-on-surface-variant hover:text-primary-fixed"
              @click="etapaRecuperacao = 1"
            >
              ← Voltar / Reenviar
            </button>
            <button
              type="submit"
              :disabled="carregandoRecuperacao"
              class="btn-primary py-3 px-6 text-xs tracking-wider disabled:opacity-50"
            >
              <span v-if="carregandoRecuperacao" class="material-symbols-outlined animate-spin text-sm mr-1">refresh</span>
              REDEFINIR SENHA
            </button>
          </div>
        </form>
      </div>
    </div>

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

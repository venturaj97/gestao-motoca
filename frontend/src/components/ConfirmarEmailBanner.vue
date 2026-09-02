<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { solicitarConfirmacaoEmail, confirmarEmail } from '@/api/recuperacao'

const authStore = useAuthStore()

const mostrarModal = ref(false)
const etapa = ref(1) // 1: Pedir envio, 2: Digitar PIN
const pin = ref('')
const carregando = ref(false)
const erro = ref('')
const sucesso = ref('')

async function iniciarEnvio() {
  erro.value = ''
  sucesso.value = ''
  carregando.value = true
  try {
    const res = await solicitarConfirmacaoEmail()
    sucesso.value = res.mensagem || 'Código PIN de 6 dígitos enviado para seu e-mail!'
    etapa.value = 2
  } catch (e: any) {
    erro.value = e?.response?.data?.detail || 'Erro ao enviar código de confirmação.'
  } finally {
    carregando.value = false
  }
}

async function handleConfirmarPin() {
  if (!pin.value || pin.value.trim().length !== 6) {
    erro.value = 'Digite o código PIN completo de 6 dígitos.'
    return
  }
  erro.value = ''
  carregando.value = true
  try {
    await confirmarEmail(pin.value.trim())
    sucesso.value = '✓ E-mail confirmado com sucesso!'
    await authStore.carregarUsuario()
    setTimeout(() => {
      mostrarModal.value = false
      etapa.value = 1
      pin.value = ''
    }, 1500)
  } catch (e: any) {
    erro.value = e?.response?.data?.detail || 'Código PIN inválido ou expirado.'
  } finally {
    carregando.value = false
  }
}

function fecharModal() {
  mostrarModal.value = false
  etapa.value = 1
  pin.value = ''
  erro.value = ''
  sucesso.value = ''
}
</script>

<template>
  <!-- Exibe apenas se o usuário estiver logado e email_confirmado for false -->
  <div v-if="authStore.usuario && !authStore.usuario.email_confirmado" class="mb-6">
    <div
      class="bg-amber-500/10 dark:bg-amber-500/15 border border-amber-500/30 px-4 py-3 sm:px-6 sm:py-4
             flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 rounded-xl shadow-sm"
    >
      <div class="flex items-center gap-3">
        <span class="material-symbols-outlined text-amber-600 dark:text-amber-400 text-2xl flex-shrink-0" aria-hidden="true">mark_email_unread</span>
        <div>
          <p class="font-headline font-bold text-sm text-amber-900 dark:text-amber-300 uppercase tracking-wide">
            E-mail Não Confirmado
          </p>
          <p class="font-body text-xs text-amber-950 dark:text-amber-100 font-medium">
            Confirme seu e-mail para garantir a recuperação da sua conta se precisar trocar de celular ou senha.
          </p>
        </div>
      </div>

      <button
        aria-label="Abrir modal para confirmar e-mail"
        class="bg-amber-500 hover:bg-amber-400 text-amber-950 font-headline font-extrabold text-xs
               px-4 py-2.5 uppercase tracking-widest transition-colors flex items-center gap-1.5 flex-shrink-0 rounded-lg min-h-[44px]"
        @click="mostrarModal = true"
      >
        <span class="material-symbols-outlined text-base" aria-hidden="true">verified</span>
        CONFIRMAR AGORA
      </button>
    </div>

    <!-- Modal de Confirmação -->
    <div
      v-if="mostrarModal"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <div class="bg-surface-container-high border border-outline-variant/30 rounded-xl max-w-md w-full p-6 sm:p-8 space-y-6 shadow-2xl relative">
        <button
          class="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface transition-colors"
          @click="fecharModal"
        >
          <span class="material-symbols-outlined">close</span>
        </button>

        <div class="flex items-center gap-3 border-b border-outline-variant/20 pb-4">
          <span class="material-symbols-outlined text-primary-container text-3xl">verified_user</span>
          <div>
            <h3 class="font-headline font-bold text-lg text-on-surface uppercase tracking-tight">
              Confirmar E-mail
            </h3>
            <p class="font-label text-xs text-on-surface-variant">
              {{ authStore.usuario.email }}
            </p>
          </div>
        </div>

        <!-- Etapa 1: Enviar PIN -->
        <div v-if="etapa === 1" class="space-y-4">
          <p class="font-body text-sm text-on-surface-variant">
            Clique no botão abaixo para receber um código de verificação de 6 dígitos no seu e-mail.
          </p>

          <div v-if="erro" class="bg-error-container text-on-error-container text-xs font-label px-4 py-3">
            {{ erro }}
          </div>

          <button
            :disabled="carregando"
            class="w-full h-14 bg-tactical-gradient text-on-primary-fixed font-headline font-bold
                   text-sm tracking-widest uppercase flex items-center justify-center gap-2
                   disabled:opacity-50 transition-transform active:scale-95"
            @click="iniciarEnvio"
          >
            <span v-if="carregando" class="material-symbols-outlined animate-spin">refresh</span>
            <span v-else>ENVIAR CÓDIGO PIN</span>
          </button>
        </div>

        <!-- Etapa 2: Digitar PIN -->
        <form v-else novalidate class="space-y-4" @submit.prevent="handleConfirmarPin">
          <p class="font-body text-xs text-on-surface-variant">
            Insira abaixo o código de 6 dígitos enviado para <strong>{{ authStore.usuario.email }}</strong>:
          </p>

          <div v-if="sucesso" class="bg-primary-container text-on-primary-fixed text-xs font-label font-bold px-4 py-3">
            {{ sucesso }}
          </div>

          <div v-if="erro" class="bg-error-container text-on-error-container text-xs font-label px-4 py-3">
            {{ erro }}
          </div>

          <input
            v-model="pin"
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            maxlength="6"
            placeholder="000000"
            class="w-full h-14 bg-surface-container-lowest border-0 border-b-2 border-primary-container
                   text-center font-headline font-bold text-2xl tracking-[0.5em] text-on-surface focus:outline-none"
          />

          <div class="flex items-center gap-3 pt-2">
            <button
              type="button"
              class="w-1/3 h-12 border border-outline-variant text-on-surface-variant font-headline text-xs font-bold uppercase tracking-wider"
              @click="iniciarEnvio"
            >
              REENVIAR
            </button>
            <button
              type="submit"
              :disabled="carregando || pin.length !== 6"
              class="w-2/3 h-12 bg-tactical-gradient text-on-primary-fixed font-headline font-bold text-xs tracking-widest uppercase flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span v-if="carregando" class="material-symbols-outlined animate-spin">refresh</span>
              <span v-else>VALIDAR E-MAIL</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

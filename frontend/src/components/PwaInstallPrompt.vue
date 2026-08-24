<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

const deferredPrompt = ref<any>(null)
const mostrarPrompt = ref(false)
const isIos = ref(false)
const mostrarInstrucoesIos = ref(false)

const jaInstalado = computed(() => {
  if (typeof window === 'undefined') return false
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as any).standalone === true
  )
})

onMounted(() => {
  if (jaInstalado.value) return

  // Verificar se o usuário já dispensou nos últimos 3 dias
  const dispensadoEm = localStorage.getItem('gm_pwa_dispensado_em')
  if (dispensadoEm) {
    const dataDispensado = parseInt(dispensadoEm, 10)
    const tresDias = 3 * 24 * 60 * 60 * 1000
    if (Date.now() - dataDispensado < tresDias) {
      return
    }
  }

  // Detectar iOS Safari
  const ua = window.navigator.userAgent
  const isIphoneOrIpad = /iPhone|iPad|iPod/i.test(ua)
  const isSafari = /Safari/i.test(ua) && !/Chrome|CriOS|FxiOS/i.test(ua)
  if (isIphoneOrIpad && isSafari) {
    isIos.value = true
    // Exibe banner no iOS após 2 segundos
    setTimeout(() => {
      mostrarPrompt.value = true
    }, 2000)
    return
  }

  // Capturar evento de instalação nativa no Android / Chrome / Edge
  window.addEventListener('beforeinstallprompt', (e: Event) => {
    e.preventDefault()
    deferredPrompt.value = e
    mostrarPrompt.value = true
  })

  // Detectar quando for instalado com sucesso
  window.addEventListener('appinstalled', () => {
    deferredPrompt.value = null
    mostrarPrompt.value = false
    localStorage.removeItem('gm_pwa_dispensado_em')
  })
})

async function instalarApp() {
  if (isIos.value) {
    mostrarInstrucoesIos.value = !mostrarInstrucoesIos.value
    return
  }

  if (!deferredPrompt.value) return

  try {
    await deferredPrompt.value.prompt()
    const { outcome } = await deferredPrompt.value.userChoice
    if (outcome === 'accepted') {
      deferredPrompt.value = null
      mostrarPrompt.value = false
    }
  } catch (err) {
    console.error('Erro ao solicitar instalação do PWA:', err)
  }
}

function dispensar() {
  mostrarPrompt.value = false
  mostrarInstrucoesIos.value = false
  localStorage.setItem('gm_pwa_dispensado_em', Date.now().toString())
}
</script>

<template>
  <Transition
    enter-active-class="transition ease-out duration-300 transform"
    enter-from-class="translate-y-8 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition ease-in duration-200 transform"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-8 opacity-0"
  >
    <aside
      v-if="mostrarPrompt && !jaInstalado"
      class="fixed bottom-4 left-4 right-4 z-50 mx-auto max-w-lg overflow-hidden border border-primary/30 bg-slate-950/95 p-4 shadow-2xl backdrop-blur-md sm:bottom-6 sm:left-auto sm:right-6 sm:w-96 rounded-xl"
      role="dialog"
      aria-label="Instalação do Aplicativo Gestão Motoca"
    >
      <!-- Glow Decorativo -->
      <div class="pointer-events-none absolute -top-10 -right-10 h-28 w-28 rounded-full bg-primary/20 blur-2xl"></div>

      <div class="flex items-start gap-3">
        <!-- Ícone do App -->
        <div class="relative flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-slate-900 border border-primary/40 shadow-inner">
          <img src="/pwa-192x192.png" alt="Gestão Motoca" class="h-10 w-10 object-contain" />
        </div>

        <!-- Conteúdo do Banner -->
        <div class="min-w-0 flex-1">
          <div class="flex items-center justify-between">
            <h2 class="font-headline text-sm font-black uppercase tracking-wider text-slate-100">
              Gestão Motoca
            </h2>
            <button
              class="flex h-6 w-6 items-center justify-center rounded text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
              title="Dispensar por alguns dias"
              @click="dispensar"
            >
              <span class="material-symbols-outlined text-base">close</span>
            </button>
          </div>

          <p class="mt-0.5 text-xs text-slate-300 leading-snug">
            Instale o app na sua tela inicial para acesso rápido e economia de bateria na rua.
          </p>

          <!-- Instrução especial para iPhone / Safari -->
          <div
            v-if="mostrarInstrucoesIos"
            class="mt-2.5 rounded bg-slate-900/90 border border-primary/20 p-2 text-[11px] text-slate-300 space-y-1"
          >
            <div class="flex items-center gap-1.5 font-bold text-primary">
              <span class="material-symbols-outlined text-sm">ios_share</span>
              No Safari do iPhone:
            </div>
            <p>1. Toque no botão de <strong>Compartilhar</strong> na barra do navegador.</p>
            <p>2. Role e selecione <strong>"Adicionar à Tela de Início"</strong>.</p>
          </div>

          <!-- Botões de Ação -->
          <div class="mt-3 flex items-center gap-2">
            <button
              class="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-gradient-to-r from-primary via-indigo-500 to-cyan-500 px-3 py-2 text-xs font-black uppercase tracking-wider text-white shadow-lg hover:brightness-110 active:scale-95 transition-all"
              @click="instalarApp"
            >
              <span class="material-symbols-outlined text-sm">
                {{ isIos ? 'install_mobile' : 'download' }}
              </span>
              {{ isIos ? (mostrarInstrucoesIos ? 'Entendi' : 'Como Instalar') : 'Instalar App' }}
            </button>

            <button
              class="rounded-lg border border-slate-700 bg-slate-900/80 px-2.5 py-2 text-xs font-bold text-slate-300 hover:bg-slate-800 transition-colors"
              @click="dispensar"
            >
              Depois
            </button>
          </div>
        </div>
      </div>
    </aside>
  </Transition>
</template>

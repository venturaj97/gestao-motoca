<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  mostrarModal: boolean
}>()

const emit = defineEmits<{
  (e: 'fechar'): void
}>()

const rawPhone = import.meta.env.VITE_SUPPORT_WHATSAPP || '5521980115136'
const emailSuporte = import.meta.env.VITE_SUPPORT_EMAIL || 'joaom3ndes@gmail.com'

const copiadoEmail = ref(false)

// Formata o número para exibição visual humana (ex: (21) 98011-5136)
const telefoneFormatado = computed(() => {
  const digits = rawPhone.replace(/\D/g, '')
  if (digits.length === 13) { // 5521980115136
    const ddd = digits.slice(2, 4)
    const parte1 = digits.slice(4, 9)
    const parte2 = digits.slice(9)
    return `(${ddd}) ${parte1}-${parte2}`
  }
  if (digits.length === 11) { // 21980115136
    const ddd = digits.slice(0, 2)
    const parte1 = digits.slice(2, 7)
    const parte2 = digits.slice(7)
    return `(${ddd}) ${parte1}-${parte2}`
  }
  return rawPhone
})

// URL do WhatsApp com mensagem inicial
const linkWhatsapp = computed(() => {
  const digits = rawPhone.replace(/\D/g, '')
  const mensagem = encodeURIComponent('Olá! Preciso de ajuda no aplicativo Gestão Motoca.')
  return `https://wa.me/${digits}?text=${mensagem}`
})

async function copiarEmail() {
  try {
    await navigator.clipboard.writeText(emailSuporte)
    copiadoEmail.value = true
    setTimeout(() => {
      copiadoEmail.value = false
    }, 2500)
  } catch {
    // Fallback caso clipboard API falhe
    const input = document.createElement('input')
    input.value = emailSuporte
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    copiadoEmail.value = true
    setTimeout(() => {
      copiadoEmail.value = false
    }, 2500)
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="mostrarModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm"
        @click.self="emit('fechar')"
      >
        <div
          class="relative w-full max-w-md bg-surface-container-low border border-outline-variant/30 rounded-2xl p-6 shadow-2xl overflow-hidden transition-all transform scale-100"
        >
          <!-- Botão Fechar -->
          <button
            class="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface p-1 rounded-full hover:bg-surface-container transition-colors"
            title="Fechar"
            @click="emit('fechar')"
          >
            <span class="material-symbols-outlined text-2xl">close</span>
          </button>

          <!-- Cabeçalho -->
          <div class="flex items-center gap-3 mb-5">
            <div class="w-12 h-12 rounded-xl bg-primary-container/20 text-primary-container flex items-center justify-center border border-primary-container/30">
              <span class="material-symbols-outlined text-2xl">support_agent</span>
            </div>
            <div>
              <h2 class="text-lg font-headline font-black text-on-surface tracking-tight uppercase">
                Suporte & Ajuda
              </h2>
              <p class="text-xs text-on-surface-variant">
                Fale diretamente conosco para tirar dúvidas
              </p>
            </div>
          </div>

          <!-- Cards de Contato -->
          <div class="space-y-3.5">
            <!-- Opção WhatsApp -->
            <a
              :href="linkWhatsapp"
              target="_blank"
              rel="noopener noreferrer"
              class="group flex items-center justify-between p-4 rounded-xl bg-[#25D366]/10 border border-[#25D366]/30 hover:bg-[#25D366]/20 transition-all cursor-pointer active:scale-[0.98]"
            >
              <div class="flex items-center gap-3.5">
                <!-- SVG Ícone do WhatsApp -->
                <div class="w-10 h-10 rounded-lg bg-[#25D366] text-white flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
                  <svg
                    class="w-6 h-6 fill-current"
                    viewBox="0 0 24 24"
                  >
                    <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z" />
                  </svg>
                </div>
                <div>
                  <h3 class="font-bold text-[#25D366] text-sm flex items-center gap-1.5">
                    WhatsApp Directo
                    <span class="text-[10px] px-2 py-0.5 rounded-full bg-[#25D366]/20 font-semibold uppercase">Online</span>
                  </h3>
                  <p class="text-xs font-mono text-on-surface-variant font-medium">
                    {{ telefoneFormatado }}
                  </p>
                </div>
              </div>

              <span class="material-symbols-outlined text-xl text-[#25D366] group-hover:translate-x-1 transition-transform">
                open_in_new
              </span>
            </a>

            <!-- Opção E-mail -->
            <div class="p-4 rounded-xl bg-surface border border-outline-variant/30 flex flex-col gap-3">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-lg bg-surface-container-high text-primary-container flex items-center justify-center">
                    <span class="material-symbols-outlined text-xl">mail</span>
                  </div>
                  <div>
                    <h3 class="font-bold text-on-surface text-sm">
                      E-mail de Suporte
                    </h3>
                    <p class="text-xs font-mono text-on-surface-variant truncate">
                      {{ emailSuporte }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-2 pt-1 border-t border-outline-variant/15">
                <a
                  :href="`mailto:${emailSuporte}`"
                  class="flex-1 text-center py-2 px-3 rounded-lg bg-surface-container-high hover:bg-surface-container-highest text-on-surface text-xs font-bold transition-colors flex items-center justify-center gap-1.5"
                >
                  <span class="material-symbols-outlined text-sm">send</span>
                  Enviar E-mail
                </a>
                <button
                  class="py-2 px-3 rounded-lg border border-outline-variant/30 hover:bg-surface-container text-xs font-bold transition-colors flex items-center justify-center gap-1.5"
                  :class="{ 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10': copiadoEmail }"
                  @click="copiarEmail"
                >
                  <span class="material-symbols-outlined text-sm">
                    {{ copiadoEmail ? 'check' : 'content_copy' }}
                  </span>
                  {{ copiadoEmail ? 'Copiado!' : 'Copiar' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Rodapé informativo -->
          <div class="mt-5 pt-4 border-t border-outline-variant/20 flex items-center justify-between text-[11px] text-on-surface-variant">
            <span class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Atendimento disponível
            </span>
            <span>Gestão Motoca Suporte</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

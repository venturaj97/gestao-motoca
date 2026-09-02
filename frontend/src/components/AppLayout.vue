<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMotoStore } from '@/stores/moto'
import { useThemeStore } from '@/stores/theme'
import { computed } from 'vue'

const router    = useRouter()
const route     = useRoute()
const auth      = useAuthStore()
const motoStore = useMotoStore()
const theme     = useThemeStore()

const navItems = [
  { name: 'dashboard',     label: 'Início',     icon: 'dashboard'   },
  { name: 'historico',     label: 'Histórico',  icon: 'history'     },
  { name: 'lancar',        label: 'Lançar',     icon: 'add_box'     },
  { name: 'metas',         label: 'Metas',      icon: 'flag'        },
]

const primeiroNome = computed(() => {
  const nome = auth.usuario?.nome ?? ''
  return nome.split(' ')[0].toUpperCase()
})

const nomeMoto = computed(() => {
  const m = motoStore.motoAtiva
  if (!m) return null
  const marca  = m.marca_manual  ?? ''
  const modelo = m.modelo_manual ?? ''
  return [marca, modelo].filter(Boolean).join(' ') || null
})

function isActive(name: string) {
  return route.name === name
}

function navIconStyle(name: string): Record<string, string> {
  return isActive(name) ? { fontVariationSettings: '"FILL" 1' } : {}
}

function logout() {
  auth.logout()
  motoStore.limpar()
  router.push({ name: 'login' })
}
</script>

<template>
  <!-- ═══════════════════════════════════════════════════════════
       App Shell: Sidebar (desktop) + Bottom Nav (mobile)
  ════════════════════════════════════════════════════════════ -->
  <div class="app-layout">

    <!-- ══ SIDEBAR – visível apenas em desktop (≥1024px) ══ -->
    <aside class="sidebar">
      <!-- Logo / Marca -->
      <div class="sidebar-brand">
        <div class="flex items-center gap-3">
          <div class="sidebar-avatar">
            <span class="font-headline font-black text-sm">
              {{ primeiroNome.charAt(0) }}
            </span>
          </div>
          <div>
            <p class="sidebar-title">GESTÃO</p>
            <p class="sidebar-title sidebar-title--accent">MOTOCA</p>
          </div>
        </div>

        <div class="w-full pt-1">
          <button
            v-if="auth.ehPro"
            class="w-full rounded-lg bg-amber-500/20 px-2.5 py-1 text-[10px] font-black tracking-widest text-amber-300 border border-amber-400/40 uppercase whitespace-nowrap text-center flex items-center justify-center gap-1 cursor-pointer"
            title="Plano PRO Ativo"
            @click="router.push('/configuracoes')"
          >
            <span>PLANO PRO</span>
            <span>⭐</span>
          </button>
          <button
            v-else
            class="w-full rounded-lg bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 px-2.5 py-1 text-[10px] font-black tracking-widest text-slate-950 uppercase transition-all shadow-sm whitespace-nowrap text-center flex items-center justify-center gap-1 cursor-pointer active:scale-95"
            title="Assinar Gestão Motoca PRO"
            @click="router.push('/configuracoes')"
          >
            <span>SEJA PRO</span>
            <span>⭐</span>
          </button>
        </div>
      </div>

      <!-- Info Moto -->
      <div v-if="nomeMoto" class="sidebar-moto-badge">
        <span class="material-symbols-outlined text-sm">two_wheeler</span>
        <span class="font-label text-[10px] font-bold tracking-wider uppercase truncate">{{ nomeMoto }}</span>
      </div>

      <div class="sidebar-divider" />

      <!-- Nav links -->
      <nav class="sidebar-nav">
        <button
          v-for="item in navItems"
          :key="item.name"
          class="sidebar-nav-item"
          :class="{ 'sidebar-nav-item--active': isActive(item.name) }"
          @click="router.push({ name: item.name })"
        >
          <span
            class="material-symbols-outlined text-xl"
            :style="navIconStyle(item.name)"
          >{{ item.icon }}</span>
          <span class="font-label text-[11px] font-bold tracking-[0.12em] uppercase">{{ item.label }}</span>
        </button>
      </nav>

      <!-- Spacer -->
      <div class="flex-1" />

      <!-- Rodapé sidebar: config + tema + logout -->
      <div class="sidebar-footer">
        <button
          class="sidebar-footer-btn"
          :class="{ 'sidebar-footer-btn--active': isActive('configuracoes') }"
          title="Configurações"
          @click="router.push({ name: 'configuracoes' })"
        >
          <span
            class="material-symbols-outlined text-xl"
            :style="navIconStyle('configuracoes')"
          >settings</span>
          <span class="font-label text-[11px] font-bold tracking-widest uppercase">Config</span>
        </button>

        <button
          class="sidebar-footer-btn"
          :title="theme.escuro ? 'Ativar modo claro' : 'Ativar modo escuro'"
          @click="theme.alternarTema"
        >
          <span class="material-symbols-outlined text-xl">
            {{ theme.escuro ? 'light_mode' : 'dark_mode' }}
          </span>
          <span class="font-label text-[11px] font-bold tracking-widest uppercase">Tema</span>
        </button>

        <button
          class="sidebar-footer-btn sidebar-footer-btn--danger"
          title="Sair"
          @click="logout"
        >
          <span class="material-symbols-outlined text-xl">logout</span>
          <span class="font-label text-[11px] font-bold tracking-widest uppercase">Sair</span>
        </button>
      </div>
    </aside>

    <!-- ══ CONTEÚDO PRINCIPAL ══ -->
    <div class="main-area">
      <!-- Topbar mobile -->
      <header class="topbar-mobile">
        <div class="flex items-center gap-2">
          <button
            v-if="route.name !== 'dashboard'"
            class="topbar-icon-btn text-on-surface-variant hover:text-primary-container p-1"
            title="Voltar"
            @click="router.back()"
          >
            <span class="material-symbols-outlined text-2xl">arrow_back</span>
          </button>
          <div class="w-8 h-8 bg-surface-container-highest flex items-center justify-center">
            <span class="font-headline font-black text-primary-container text-sm">
              {{ primeiroNome.charAt(0) }}
            </span>
          </div>
          <h1 class="text-primary-container font-headline font-black text-base tracking-tight uppercase">
            GESTÃO MOTOCA
          </h1>
        </div>

        <div class="flex items-center gap-1.5">
          <button
            v-if="auth.ehPro"
            class="rounded-full bg-amber-500/20 px-2 py-0.5 text-[9px] font-black text-amber-300 border border-amber-400/40 uppercase whitespace-nowrap"
            title="Plano PRO Ativo"
            @click="router.push('/configuracoes')"
          >
            PRO ⭐
          </button>
          <button
            v-else
            class="rounded-full bg-amber-400 px-2.5 py-1 text-[9px] font-black text-amber-950 uppercase shadow-sm whitespace-nowrap min-h-[32px] flex items-center justify-center"
            title="Assinar Gestão Motoca PRO"
            @click="router.push('/configuracoes')"
          >
            SEJA PRO ⭐
          </button>
          <button
            class="topbar-icon-btn"
            :class="{ 'topbar-icon-btn--active': isActive('configuracoes') }"
            title="Configurações"
            @click="router.push({ name: 'configuracoes' })"
          >
            <span
              class="material-symbols-outlined text-xl"
              :style="navIconStyle('configuracoes')"
            >settings</span>
          </button>
          <button
            class="topbar-icon-btn"
            :title="theme.escuro ? 'Ativar modo claro' : 'Ativar modo escuro'"
            @click="theme.alternarTema"
          >
            <span class="material-symbols-outlined text-xl">
              {{ theme.escuro ? 'light_mode' : 'dark_mode' }}
            </span>
          </button>
          <button
            class="topbar-icon-btn topbar-icon-btn--danger"
            title="Sair"
            @click="logout"
          >
            <span class="material-symbols-outlined text-xl">logout</span>
          </button>
        </div>
      </header>

      <!-- Slot principal: cada view renderiza aqui -->
      <slot />
    </div>

    <!-- ══ BOTTOM NAV – visível apenas em mobile (<1024px) ══ -->
    <nav class="bottom-nav">
      <button
        v-for="item in navItems"
        :key="item.name"
        class="bottom-nav-item"
        :class="{ 'bottom-nav-item--active': isActive(item.name) }"
        @click="router.push({ name: item.name })"
      >
        <span
          class="material-symbols-outlined"
          :style="navIconStyle(item.name)"
        >{{ item.icon }}</span>
        <span class="font-label text-[9px] font-bold uppercase tracking-[0.08em] mt-0.5">
          {{ item.label }}
        </span>
      </button>
    </nav>
  </div>
</template>

<style scoped>
/* ─── Layout Shell ───────────────────────────────────────── */
.app-layout {
  display: flex;
  min-height: 100dvh;
  background: rgb(var(--color-background));
}

/* ─── Sidebar (desktop only) ─────────────────────────────── */
.sidebar {
  display: none;
}

@media (min-width: 1024px) {
  .sidebar {
    display: flex;
    flex-direction: column;
    width: 220px;
    min-height: 100dvh;
    position: sticky;
    top: 0;
    height: 100dvh;
    background: rgb(var(--color-surface-container-low));
    border-right: 1px solid rgb(var(--color-outline-variant));
    padding: 1.5rem 0 1rem 0;
    z-index: 40;
    flex-shrink: 0;
  }
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.75rem;
  padding: 0 1.25rem;
  margin-bottom: 1.25rem;
}

.sidebar-avatar {
  width: 2.25rem;
  height: 2.25rem;
  background: rgb(var(--color-primary-container) / 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: rgb(var(--color-primary-container));
}

.sidebar-title {
  font-family: var(--font-headline, 'Space Grotesk', sans-serif);
  font-weight: 900;
  font-size: 13px;
  letter-spacing: 0.12em;
  line-height: 1.1;
  text-transform: uppercase;
  color: rgb(var(--color-on-surface));
}

.sidebar-title--accent {
  color: rgb(var(--color-primary-container));
}

.sidebar-moto-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem 1rem;
  padding: 0.5rem 0.75rem;
  background: rgb(var(--color-primary-container) / 0.08);
  border-radius: 0.5rem;
  border: 1px solid rgb(var(--color-primary-container) / 0.3);
  color: rgb(var(--color-primary-container));
}

.sidebar-divider {
  height: 1px;
  background: rgb(var(--color-outline-variant));
  margin: 0 1rem 1rem;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0 0.75rem;
}

.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.75rem 0.875rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s ease;
  color: rgb(var(--color-on-surface-variant));
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
}

.sidebar-nav-item:hover {
  background: rgb(var(--color-surface-container));
  color: rgb(var(--color-on-surface));
}

.sidebar-nav-item--active {
  background: rgb(var(--color-primary-container) / 0.12);
  color: rgb(var(--color-primary-container));
  font-weight: 700;
}

.sidebar-footer {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-top: 1px solid rgb(var(--color-outline-variant));
  margin-top: 0.5rem;
}

.sidebar-footer-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
  color: rgb(var(--color-on-surface-variant));
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
}

.sidebar-footer-btn:hover {
  background: rgb(var(--color-surface-container));
  color: rgb(var(--color-on-surface));
}

.sidebar-footer-btn--active {
  background: rgb(var(--color-primary-container) / 0.12);
  color: rgb(var(--color-primary-container));
  font-weight: 700;
}

.sidebar-footer-btn--danger:hover {
  background: rgb(var(--color-error-container));
  color: rgb(var(--color-on-error-container));
}

/* ─── Main area ──────────────────────────────────────────── */
.main-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

/* ─── Topbar Mobile ──────────────────────────────────────── */
.topbar-mobile {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.25rem;
  height: 4rem;
  background: rgb(var(--color-background));
  border-bottom: 1px solid rgb(var(--color-outline-variant) / 0.3);
  position: sticky;
  top: 0;
  z-index: 50;
}

@media (min-width: 1024px) {
  .topbar-mobile {
    display: none;
  }
}

.topbar-icon-btn {
  color: rgb(var(--color-on-surface-variant));
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.375rem;
  display: flex;
  align-items: center;
  transition: color 0.15s;
}

.topbar-icon-btn:hover,
.topbar-icon-btn--active {
  color: rgb(var(--color-primary-container));
}

.topbar-icon-btn--danger:hover {
  color: rgb(var(--color-secondary));
}

/* ─── Bottom Nav (mobile only) ───────────────────────────── */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  height: 5rem;
  background: rgb(var(--color-surface));
  border-top: 1px solid rgb(var(--color-outline-variant));
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  box-shadow: 0 -2px 10px rgb(0 0 0 / 0.06);
}

@media (min-width: 1024px) {
  .bottom-nav {
    display: none;
  }
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: background 0.1s, color 0.1s;
  color: rgb(var(--color-on-surface-variant));
}

.bottom-nav-item:hover {
  background: rgb(var(--color-surface-container));
}

.bottom-nav-item--active {
  background: rgb(var(--color-primary-container));
  color: rgb(var(--color-on-primary-fixed));
}
</style>

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true,
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/usuarios': 'http://localhost:8000',
      '/motos': 'http://localhost:8000',
      '/categorias': 'http://localhost:8000',
      '/lancamentos': 'http://localhost:8000',
      '/abastecimentos': 'http://localhost:8000',
      '/manutencoes': 'http://localhost:8000',
      '/indicadores': 'http://localhost:8000',
      '/metas': 'http://localhost:8000',
      '/cofres': 'http://localhost:8000',
      '/visao-mes': 'http://localhost:8000',
      '/inteligencia': 'http://localhost:8000',
      '/assinaturas': 'http://localhost:8000',
      '/saude': 'http://localhost:8000',
      '/webhook': 'http://localhost:8000',
    },
  },
})

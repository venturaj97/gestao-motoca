import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.config.errorHandler = (err, _instance, info) => {
  console.error('Erro global capturado:', err, info)
  if (router.currentRoute.value.name !== 'erro') {
    router.push({ name: 'erro' })
  }
}

app.use(createPinia())
app.use(router)
app.mount('#app')

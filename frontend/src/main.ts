import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import { createHead } from '@vueuse/head'
import Toast, { type PluginOptions, POSITION } from 'vue-toastification'

// Import main App component
import App from './App.vue'

// Import global styles
import './assets/css/main.css'
import 'vue-toastification/dist/index.css'
import 'nprogress/nprogress.css'

// Import stores
import { setupStores } from '@/stores'

// Import router configuration
import { routes } from '@/router'

// Import plugins and utilities
import { setupChartJs } from '@/utils/chart'
import { registerServiceWorker } from '@/utils/pwa'

// Configure Vue app
const app = createApp(App)

// Configure router
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  }
})

// Configure head management
const head = createHead()

// Configure toast notifications
const toastOptions: PluginOptions = {
  position: POSITION.TOP_RIGHT,
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false,
  transition: 'Vue-Toastification__bounce',
  maxToasts: 5,
  newestOnTop: true
}

// Navigation guards
router.beforeEach((to, _from, next) => {
  // Start loading bar
  NProgress.start()
  
  // Set document title
  const title = to.meta?.title 
    ? `${to.meta.title} - MedLitBot`
    : 'MedLitBot - Medical Literature AI'
  document.title = title
  
  // Authentication check (if needed)
  if (to.meta?.requiresAuth) {
    const token = localStorage.getItem('auth_token')
    if (!token) {
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  next()
})

router.afterEach(() => {
  // Complete loading bar
  NProgress.done()
})

// Error handling
app.config.errorHandler = (error, _instance, info) => {
  console.error('Vue Error:', error, info)
  
  // Send to error tracking service in production
  if (import.meta.env.PROD) {
    // Example: Sentry.captureException(error)
  }
}

// Global properties
app.config.globalProperties.$appName = 'MedLitBot'
app.config.globalProperties.$appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0'

// Install plugins
app.use(router)
app.use(head)
app.use(Toast, toastOptions)
setupStores(app)

// Setup Chart.js
setupChartJs()

// Register service worker for PWA
if (import.meta.env.PROD) {
  registerServiceWorker()
}

// Mount app
app.mount('#app')

// Remove loading screen
const loadingElement = document.getElementById('app-loading')
if (loadingElement) {
  setTimeout(() => {
    loadingElement.style.opacity = '0'
    setTimeout(() => {
      loadingElement.remove()
    }, 300)
  }, 100)
}

// Development helpers
if (import.meta.env.DEV) {
  // Make app instance available in console
  ;(window as any).app = app
  
  console.log(`
🏥 MedLitBot Frontend Started
📊 Environment: ${import.meta.env.MODE}
🚀 Version: ${import.meta.env.VITE_APP_VERSION || '1.0.0'}
🔗 API: ${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}
  `)
}

// Global error handling for unhandled promises
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  event.preventDefault()
})

// Global keyboard shortcuts
document.addEventListener('keydown', (event) => {
  // Cmd/Ctrl + K for search
  if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
    event.preventDefault()
    // Emit search event or navigate to search
    router.push('/search')
  }
  
  // Escape key to close modals/dropdowns
  if (event.key === 'Escape') {
    // Emit global escape event
    window.dispatchEvent(new CustomEvent('global-escape'))
  }
})

export { app, router }

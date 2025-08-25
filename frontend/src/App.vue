<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Skip to main content link for accessibility -->
    <a 
      href="#main-content" 
      class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary-600 text-white px-4 py-2 rounded-lg z-50"
    >
      Skip to main content
    </a>
    
    <!-- Global loading bar -->
    <div 
      v-if="isGlobalLoading"
      class="fixed top-0 left-0 w-full h-1 bg-primary-600 z-50 animate-pulse"
    />
    
    <!-- App Layout -->
    <div class="flex h-screen overflow-hidden">
      <!-- Sidebar -->
      <AppSidebar 
        v-if="showSidebar"
        :collapsed="sidebarCollapsed"
        @toggle-collapse="toggleSidebar"
      />
      
      <!-- Main Content Area -->
      <div class="flex flex-col flex-1 overflow-hidden">
        <!-- Top Navigation -->
        <AppHeader 
          v-if="showHeader"
          :sidebar-collapsed="sidebarCollapsed"
          @toggle-sidebar="toggleSidebar"
        />
        
        <!-- Breadcrumbs -->
        <AppBreadcrumbs 
          v-if="showBreadcrumbs && breadcrumbs.length > 0"
          :items="breadcrumbs"
        />
        
        <!-- Page Content -->
        <main 
          id="main-content"
          class="flex-1 overflow-y-auto focus:outline-none"
          tabindex="-1"
        >
          <!-- Page Transition -->
          <Transition 
            name="page" 
            mode="out-in"
            @before-leave="onPageLeave"
            @after-enter="onPageEnter"
          >
            <RouterView v-slot="{ Component, route }">
              <component 
                :is="Component" 
                :key="route.path"
                class="animate-fade-in"
              />
            </RouterView>
          </Transition>
        </main>
        
        <!-- Footer -->
        <AppFooter v-if="showFooter" />
      </div>
    </div>
    
    <!-- Global Modals -->
    <GlobalModals />
    
    <!-- PWA Install Prompt -->
    <PwaInstallPrompt />
    
    <!-- Network Status Indicator -->
    <NetworkStatusIndicator />
    
    <!-- Debug Panel (development only) -->
    <DebugPanel v-if="isDevelopment" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useHead } from '@vueuse/head'
import { useEventListener, useLocalStorage, useOnline, usePreferredDark } from '@vueuse/core'

// Import components
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppBreadcrumbs from '@/components/layout/AppBreadcrumbs.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import GlobalModals from '@/components/modals/GlobalModals.vue'
import PwaInstallPrompt from '@/components/pwa/PwaInstallPrompt.vue'
import NetworkStatusIndicator from '@/components/ui/NetworkStatusIndicator.vue'
import DebugPanel from '@/components/dev/DebugPanel.vue'

// Import stores
import { useSystemStore } from '@/stores/system'
import { useNotificationStore } from '@/stores/notifications'

// Import types
import type { BreadcrumbItem } from '@/types'

// Environment
const isDevelopment = import.meta.env.DEV

// Router and route
const route = useRoute()

// Stores
const systemStore = useSystemStore()
const notificationStore = useNotificationStore()

// Reactive state
const isGlobalLoading = ref(false)
const sidebarCollapsed = useLocalStorage('sidebar-collapsed', false)

// Online status
const isOnline = useOnline()

// Theme management
const isDark = usePreferredDark()

// Computed properties
const showSidebar = computed(() => {
  return route.meta?.showSidebar !== false && route.name !== 'login'
})

const showHeader = computed(() => {
  return route.meta?.showHeader !== false && route.name !== 'login'
})

const showBreadcrumbs = computed(() => {
  return route.meta?.showBreadcrumbs !== false && route.name !== 'login'
})

const showFooter = computed(() => {
  return route.meta?.showFooter !== false
})

const breadcrumbs = computed((): BreadcrumbItem[] => {
  if (route.meta?.breadcrumb) {
    return Array.isArray(route.meta.breadcrumb) 
      ? route.meta.breadcrumb as BreadcrumbItem[]
      : [route.meta.breadcrumb as BreadcrumbItem]
  }
  
  // Auto-generate breadcrumbs from route path
  const pathSegments = route.path.split('/').filter(Boolean)
  const crumbs: BreadcrumbItem[] = [
    { label: 'Home', to: '/' }
  ]
  
  let currentPath = ''
  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`
    const isLast = index === pathSegments.length - 1
    
    const breadcrumb: BreadcrumbItem = {
      label: segment.charAt(0).toUpperCase() + segment.slice(1),
      active: isLast
    }
    if (!isLast) {
      breadcrumb.to = currentPath
    }
    crumbs.push(breadcrumb)
  })
  
  return crumbs
})

// Head management
useHead({
  titleTemplate: (title) => title ? `${title} - MedLitBot` : 'MedLitBot - Medical Literature AI',
  meta: [
    { name: 'description', content: 'AI-powered medical literature classification system' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1.0' },
    { name: 'theme-color', content: '#1e40af' }
  ],
  link: [
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
  ]
})

// Methods
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const onPageLeave = () => {
  isGlobalLoading.value = true
}

const onPageEnter = () => {
  isGlobalLoading.value = false
}

// Global keyboard shortcuts
useEventListener(document, 'keydown', (event: KeyboardEvent) => {
  // Cmd/Ctrl + Shift + D for debug panel
  if (isDevelopment && (event.metaKey || event.ctrlKey) && event.shiftKey && event.key === 'D') {
    event.preventDefault()
    // Toggle debug panel
    systemStore.toggleDebugPanel()
  }
  
  // Cmd/Ctrl + B to toggle sidebar
  if ((event.metaKey || event.ctrlKey) && event.key === 'b' && showSidebar.value) {
    event.preventDefault()
    toggleSidebar()
  }
})

// Global escape key handler
useEventListener(window, 'global-escape', () => {
  // Close any open modals, dropdowns, etc.
  systemStore.closeAllModals()
})

// Watch for route changes to update page title
watch(() => route.meta?.title, (title) => {
  if (title) {
    document.title = `${title} - MedLitBot`
  }
})

// Watch network status
watch(isOnline, (online) => {
  if (online) {
    notificationStore.addNotification({
      id: 'network-online',
      type: 'success',
      title: 'Back online',
      message: 'Internet connection restored',
      duration: 3000
    })
  } else {
    notificationStore.addNotification({
      id: 'network-offline', 
      type: 'warning',
      title: 'Offline',
      message: 'No internet connection',
      duration: 0
    })
  }
})

// Watch theme changes
watch(isDark, (dark) => {
  document.documentElement.classList.toggle('dark', dark)
})

// Lifecycle
onMounted(async () => {
  // Initialize system store
  await systemStore.initialize()
  
  // Load user preferences
  systemStore.loadUserPreferences()
  
  // Set initial theme
  document.documentElement.classList.toggle('dark', isDark.value)
  
  // Analytics or tracking initialization
  if (import.meta.env.PROD) {
    // Initialize analytics
  }
})

onUnmounted(() => {
  // Cleanup any subscriptions or timers
  systemStore.cleanup()
})

// Handle app errors
const handleError = (error: Error, errorInfo: string) => {
  console.error('App Error:', error, errorInfo)
  
  notificationStore.addNotification({
    id: `error-${Date.now()}`,
    type: 'error',
    title: 'Application Error',
    message: 'An unexpected error occurred. Please refresh the page.',
    duration: 10000
  })
}

// Provide error handler
import { provide } from 'vue'
provide('errorHandler', handleError)
</script>

<style scoped>
/* Page transitions */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* Loading bar styles */
.loading-bar {
  background: linear-gradient(
    90deg,
    transparent,
    rgba(59, 130, 246, 0.8),
    transparent
  );
  animation: loading-slide 1.5s ease-in-out infinite;
}

@keyframes loading-slide {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100vw);
  }
}
</style>

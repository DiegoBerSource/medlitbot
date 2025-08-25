// Central store configuration and exports
import { createPinia } from 'pinia'
import type { App } from 'vue'

// Create Pinia instance
export const pinia = createPinia()

// Plugin to install Pinia
export function setupStores(app: App) {
  app.use(pinia)
}

// Export all stores
export { useDatasetStore } from './datasets'
export { useModelStore } from './models' 
export { useClassificationStore } from './classification'
export { useTrainingStore } from './training'
export { useSystemStore } from './system'
export { useNotificationStore } from './notifications'
export { useWebSocketStore } from './websocket'

// Store utilities
export interface StoreState {
  loading: boolean
  error: string | null
  lastUpdated: Date | null
}

export const createInitialState = (): StoreState => ({
  loading: false,
  error: null,
  lastUpdated: null
})

// Store action helpers
export const withLoading = async <T>(
  state: StoreState,
  action: () => Promise<T>
): Promise<T> => {
  state.loading = true
  state.error = null
  
  try {
    const result = await action()
    state.lastUpdated = new Date()
    return result
  } catch (error) {
    state.error = error instanceof Error ? error.message : 'An error occurred'
    throw error
  } finally {
    state.loading = false
  }
}

// Local storage persistence helpers
export const persistStore = <T>(key: string, data: T): void => {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.warn(`Failed to persist store data for key ${key}:`, error)
  }
}

export const loadPersistedStore = <T>(key: string, defaultValue: T): T => {
  try {
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : defaultValue
  } catch (error) {
    console.warn(`Failed to load persisted store data for key ${key}:`, error)
    return defaultValue
  }
}

// Store subscription helpers
export const createStoreSubscription = (
  store: any,
  callback: (state: any) => void,
  immediate = false
) => {
  return store.$subscribe(callback, { immediate })
}

// Error handling for stores
export class StoreError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message)
    this.name = 'StoreError'
  }
}

export const handleStoreError = (error: unknown, context: string): StoreError => {
  if (error instanceof StoreError) {
    return error
  }
  
  const message = error instanceof Error ? error.message : 'Unknown error occurred'
  return new StoreError(`${context}: ${message}`, 'STORE_ERROR', error)
}

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSystemStore = defineStore('system', () => {
  // State
  const loading = ref(false)
  const stats = ref({
    total_datasets: 0,
    total_models: 0,
    total_predictions: 0,
    trained_models: 0,
    active_training_jobs: 0,
    validated_datasets: 0
  })

  // Actions
  const fetchStats = async () => {
    console.log('🔄 Fetching system stats...')
    loading.value = true
    try {
      // Use fetch directly instead of axios for now
      const response = await fetch('/api/system/stats')
      const responseData = await response.json()
      console.log('✅ API Response:', responseData)
      
      // Transform the nested API response to the flat structure expected by the frontend
      const newStats = {
        total_datasets: responseData.datasets?.total || 0,
        total_models: responseData.models?.total || 0,
        total_predictions: responseData.classifications?.total || 0,
        trained_models: responseData.models?.total || 0, // Assuming all models are trained for now
        active_training_jobs: responseData.models?.active_training || 0,
        validated_datasets: responseData.datasets?.validated || 0
      }
      
      console.log('🔄 Updating stats:', newStats)
      stats.value = newStats
      console.log('✅ Stats updated:', stats.value)
    } catch (error) {
      console.error('❌ Failed to fetch stats:', error)
    } finally {
      loading.value = false
    }
  }

  const initialize = async () => {
    await fetchStats()
  }

  const loadUserPreferences = () => {
    // Load user preferences from localStorage
  }

  const cleanup = () => {
    // Cleanup subscriptions
  }

  const toggleDebugPanel = () => {
    // Toggle debug panel
  }

  const closeAllModals = () => {
    // Close any open modals
  }

  return {
    loading,
    stats,
    fetchStats,
    initialize,
    loadUserPreferences,
    cleanup,
    toggleDebugPanel,
    closeAllModals
  }
})

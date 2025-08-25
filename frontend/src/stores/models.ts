import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { modelApi } from '@/utils/api'
import type { MLModel, MLModelCreateRequest, StartTrainingRequest } from '@/types'

export const useModelStore = defineStore('models', () => {
  // State
  const models = ref<MLModel[]>([])
  const currentModel = ref<MLModel | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const trainedModels = computed(() => 
    models.value.filter(m => m.is_trained)
  )
  
  const modelsByStatus = computed(() => ({
    trained: models.value.filter(m => m.status === 'trained'),
    training: models.value.filter(m => m.status === 'training'),
    created: models.value.filter(m => m.status === 'created'),
    failed: models.value.filter(m => m.status === 'failed')
  }))

  const modelCount = computed(() => models.value.length)

  // Actions
  const fetchModels = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await modelApi.getModels()
      models.value = response.items || response.results || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch models'
      console.error('Failed to fetch models:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchModel = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      currentModel.value = await modelApi.getModel(id)
      return currentModel.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch model'
      console.error('Failed to fetch model:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createModel = async (data: MLModelCreateRequest) => {
    loading.value = true
    error.value = null
    try {
      const newModel = await modelApi.createModel(data)
      models.value.push(newModel)
      return newModel
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create model'
      console.error('Failed to create model:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateModel = async (id: number, data: Partial<MLModelCreateRequest>) => {
    loading.value = true
    error.value = null
    try {
      const updatedModel = await modelApi.updateModel(id, data as any)
      const index = models.value.findIndex(m => m.id === id)
      if (index !== -1) {
        models.value[index] = updatedModel
      }
      if (currentModel.value?.id === id) {
        currentModel.value = updatedModel
      }
      return updatedModel
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update model'
      console.error('Failed to update model:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteModel = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await modelApi.deleteModel(id)
      models.value = models.value.filter(m => m.id !== id)
      if (currentModel.value?.id === id) {
        currentModel.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete model'
      console.error('Failed to delete model:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const startTraining = async (id: number, params: StartTrainingRequest) => {
    loading.value = true
    error.value = null
    try {
      const trainingJob = await modelApi.startTraining(id, params)
      // Update model status to training
      const index = models.value.findIndex(m => m.id === id)
      if (index !== -1) {
        models.value[index] = { ...models.value[index], status: 'training' } as any
      }
      return trainingJob
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to start training'
      console.error('Failed to start training:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const clearCurrentModel = () => {
    currentModel.value = null
  }

  return {
    // State
    models,
    currentModel,
    loading,
    error,
    
    // Computed
    trainedModels,
    modelsByStatus,
    modelCount,
    
    // Actions
    fetchModels,
    fetchModel,
    createModel,
    updateModel,
    deleteModel,
    startTraining,
    clearError,
    clearCurrentModel
  }
})

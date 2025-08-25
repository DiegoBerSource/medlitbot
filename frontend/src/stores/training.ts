import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { modelApi } from '@/utils/api'
import type { 
  TrainingJob, 
  HyperparameterOptimizationRequest,
  HyperparameterOptimizationResponse
} from '@/types'

export const useTrainingStore = defineStore('training', () => {
  // State
  const jobs = ref<TrainingJob[]>([])
  const activeJobs = ref<TrainingJob[]>([])
  const currentJob = ref<TrainingJob | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const jobsByStatus = computed(() => ({
    active: jobs.value.filter(j => j.status === 'running'),
    completed: jobs.value.filter(j => j.status === 'completed'),
    failed: jobs.value.filter(j => j.status === 'failed'),
    pending: jobs.value.filter(j => j.status === 'pending')
  }))

  const totalJobs = computed(() => jobs.value.length)
  const activeJobCount = computed(() => jobsByStatus.value.active.length)

  const recentJobs = computed(() => 
    jobs.value
      .slice()
      .sort((a, b) => {
        const timeA = a.started_at ? new Date(a.started_at).getTime() : 0
        const timeB = b.started_at ? new Date(b.started_at).getTime() : 0
        return timeB - timeA
      })
      .slice(0, 10)
  )

  // Actions
  const fetchJobs = async () => {
    loading.value = true
    error.value = null
    try {
      // Use modelApi to get models and derive training jobs from them
      const models = await modelApi.getModels()
      const trainingJobs: TrainingJob[] = []
      
      for (const model of models.items || []) {
        try {
          const trainingJob = await modelApi.getTrainingJob(model.id)
          trainingJobs.push(trainingJob)
        } catch {
          // Model might not have active training, skip
        }
      }
      
      jobs.value = trainingJobs
      activeJobs.value = jobs.value.filter(j => j.status === 'running')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch training jobs'
      console.error('Failed to fetch training jobs:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchActiveJobs = async () => {
    loading.value = true
    error.value = null
    try {
      // Get models and check which ones have active training
      const models = await modelApi.getModels()
      const activeTrainingJobs: TrainingJob[] = []
      
      for (const model of models.items || []) {
        if (model.status === 'training') {
          try {
            const trainingJob = await modelApi.getTrainingJob(model.id)
            activeTrainingJobs.push(trainingJob)
          } catch {
            // Training job might not exist, skip
          }
        }
      }
      
      activeJobs.value = activeTrainingJobs
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch active jobs'
      console.error('Failed to fetch active jobs:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchJob = async (modelId: number) => {
    loading.value = true
    error.value = null
    try {
      currentJob.value = await modelApi.getTrainingJob(modelId)
      return currentJob.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch training job'
      console.error('Failed to fetch training job:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const startTraining = async (modelId: number, params: any): Promise<TrainingJob> => {
    loading.value = true
    error.value = null
    try {
      const trainingJob = await modelApi.startTraining(modelId, params)
      
      jobs.value.unshift(trainingJob)
      activeJobs.value.unshift(trainingJob)
      currentJob.value = trainingJob
      
      return trainingJob
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to start training'
      console.error('Failed to start training:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const startHyperparameterOptimization = async (
    modelId: number, 
    request: HyperparameterOptimizationRequest
  ): Promise<HyperparameterOptimizationResponse> => {
    loading.value = true
    error.value = null
    try {
      const response = await modelApi.optimizeHyperparameters(modelId, request)
      
      // Create a training job record
      const newJob: TrainingJob = {
        id: (response as any).optimization_id || 0,
        model: modelId,
        status: 'running',
        progress_percentage: 0,
        current_epoch: 0,
        total_epochs: request.n_trials || 10,
        current_loss: null,
        current_accuracy: null,
        started_at: new Date().toISOString(),
        completed_at: null,
        error_message: null,
        celery_task_id: (response as any).task_id || '',
        model_id: modelId,
        updated_at: new Date().toISOString()
      }
      
      jobs.value.unshift(newJob)
      activeJobs.value.unshift(newJob)
      currentJob.value = newJob
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to start hyperparameter optimization'
      console.error('Failed to start hyperparameter optimization:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const stopJob = async (modelId: number) => {
    loading.value = true
    error.value = null
    try {
      await modelApi.stopTraining(modelId)
      
      // Update job status
      const jobIndex = jobs.value.findIndex(j => j.model_id === modelId)
      if (jobIndex !== -1) {
        jobs.value[jobIndex] = { ...jobs.value[jobIndex], status: 'cancelled' } as any
      }
      
      const activeIndex = activeJobs.value.findIndex(j => j.model_id === modelId)
      if (activeIndex !== -1) {
        activeJobs.value.splice(activeIndex, 1)
      }
      
      if (currentJob.value?.model_id === modelId) {
        currentJob.value = { ...currentJob.value, status: 'cancelled' }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to stop training job'
      console.error('Failed to stop training job:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteJob = async (modelId: number) => {
    loading.value = true
    error.value = null
    try {
      // In this case, deleting a training job means deleting the model
      await modelApi.deleteModel(modelId)
      
      jobs.value = jobs.value.filter(j => j.model_id !== modelId)
      activeJobs.value = activeJobs.value.filter(j => j.model_id !== modelId)
      
      if (currentJob.value?.model_id === modelId) {
        currentJob.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete training job'
      console.error('Failed to delete training job:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateJobProgress = (jobId: number, progress: Partial<TrainingJob>) => {
    const jobIndex = jobs.value.findIndex(j => j.id === jobId)
    if (jobIndex !== -1) {
      jobs.value[jobIndex] = { ...jobs.value[jobIndex], ...progress } as any
    }
    
    const activeIndex = activeJobs.value.findIndex(j => j.id === jobId)
    if (activeIndex !== -1) {
      activeJobs.value[activeIndex] = { ...activeJobs.value[activeIndex], ...progress } as any
    }
    
    if (currentJob.value?.id === jobId) {
      currentJob.value = { ...currentJob.value, ...progress }
    }
  }

  const clearError = () => {
    error.value = null
  }

  const clearCurrentJob = () => {
    currentJob.value = null
  }

  const clearJobs = () => {
    jobs.value = []
    activeJobs.value = []
  }

  return {
    // State
    jobs,
    activeJobs,
    currentJob,
    loading,
    error,
    
    // Computed
    jobsByStatus,
    totalJobs,
    activeJobCount,
    recentJobs,
    
    // Actions
    fetchJobs,
    fetchActiveJobs,
    fetchJob,
    startTraining,
    startHyperparameterOptimization,
    stopJob,
    deleteJob,
    updateJobProgress,
    clearError,
    clearCurrentJob,
    clearJobs
  }
})

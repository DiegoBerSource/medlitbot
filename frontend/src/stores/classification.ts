import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { classificationApi } from '@/utils/api'
import type { 
  ClassificationResult, 
  ClassificationRequest,
  ClassificationResponse,
  BatchClassificationRequest,
  BatchClassificationResponse
} from '@/types'

export const useClassificationStore = defineStore('classification', () => {
  // State
  const predictions = ref<ClassificationResult[]>([])
  const currentPrediction = ref<ClassificationResult | null>(null)
  const loading = ref(false)
  const batchLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const totalPredictions = computed(() => predictions.value.length)
  
  const predictionsByDomain = computed(() => {
    const domains: Record<string, ClassificationResult[]> = {}
    predictions.value.forEach(pred => {
      pred.predicted_domains?.forEach(domain => {
        if (!domains[domain]) {
          domains[domain] = []
        }
        domains[domain]!.push(pred)
      })
    })
    return domains
  })

  const recentPredictions = computed(() => 
    predictions.value
      .slice()
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10)
  )

  const predictionStats = computed(() => ({
    total: totalPredictions.value,
    domains: Object.keys(predictionsByDomain.value).length,
    recentCount: recentPredictions.value.length
  }))

  // Actions
  const fetchPredictions = async (page = 1, pageSize = 20) => {
    loading.value = true
    error.value = null
    try {
      const response = await classificationApi.getPredictions(page, pageSize)
      if (page === 1) {
        predictions.value = response.items || response.results || []
      } else {
        predictions.value.push(...(response.items || response.results || []))
      }
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch predictions'
      console.error('Failed to fetch predictions:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchPrediction = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      // Note: This endpoint might not exist in the current API, but we'll implement it for completeness
      const prediction = predictions.value.find(p => p.id === id)
      if (prediction) {
        currentPrediction.value = prediction
        return prediction
      }
      // If not found locally, you might want to implement a specific API call
      throw new Error('Prediction not found')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch prediction'
      console.error('Failed to fetch prediction:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const classify = async (modelId: number, data: ClassificationRequest): Promise<ClassificationResponse> => {
    loading.value = true
    error.value = null
    try {
      // Add model_id to the request data
      const requestData = {
        ...data,
        model_id: modelId
      }
      
      const result = await classificationApi.predict(modelId, requestData)
      
      // Create a classification result record
      const predictionRecord: ClassificationResult = {
        id: Date.now(), // Temporary ID
        model: modelId,
        title: data.title,
        abstract: data.abstract,
        predicted_domains: result.predicted_domains,
        confidence_scores: result.confidence_scores,
        all_domain_scores: result.all_domain_scores || result.confidence_scores,
        prediction_threshold: data.threshold || 0.5,
        inference_time_ms: result.inference_time_ms || 0,
        created_at: new Date().toISOString()
      }
      
      predictions.value.unshift(predictionRecord)
      currentPrediction.value = predictionRecord
      
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to classify article'
      console.error('Failed to classify article:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const batchClassify = async (modelId: number, data: BatchClassificationRequest): Promise<BatchClassificationResponse> => {
    batchLoading.value = true
    error.value = null
    try {
      const results = await classificationApi.batchPredict(modelId, data)
      
      // Create classification result records for each article
      const predictionRecords: ClassificationResult[] = results.results.map((pred, index) => ({
        id: Date.now() + index, // Temporary ID
        model: modelId,
        title: data.articles?.[index]?.title || '',
        abstract: data.articles?.[index]?.abstract || '',
        predicted_domains: pred.predicted_domains,
        confidence_scores: pred.confidence_scores,
        all_domain_scores: pred.confidence_scores, // Use confidence_scores as fallback
        prediction_threshold: data.threshold || 0.5,
        inference_time_ms: pred.inference_time_ms || 0,
        created_at: new Date().toISOString()
      }))
      
      predictions.value.unshift(...predictionRecords)
      
      return results
    } catch (err: any) {
      const errorMessage = extractErrorMessage(err)
      error.value = errorMessage
      console.error('Failed to perform batch classification:', err)
      throw new Error(errorMessage)
    } finally {
      batchLoading.value = false
    }
  }

  const clearPredictions = () => {
    predictions.value = []
  }

  const clearError = () => {
    error.value = null
  }

  const clearCurrentPrediction = () => {
    currentPrediction.value = null
  }

  // Helper function to extract meaningful error messages from API responses
  const extractErrorMessage = (err: any): string => {
    const defaultMessage = 'Failed to perform batch classification'
    
    const details = err.response?.data?.detail
    if (!details) {
      return err.response?.data?.error || err.message || defaultMessage
    }
    
    if (typeof details === 'string') {
      return details
    }
    
    if (Array.isArray(details) && details.length > 0) {
      const firstError = details[0]
      if (firstError.type === 'too_long' && firstError.loc?.includes('articles')) {
        const maxLength = firstError.ctx?.max_length || 1000
        const actualLength = firstError.ctx?.actual_length || 'unknown'
        return `Too many articles: Maximum ${maxLength} articles allowed, but you provided ${actualLength}`
      }
      return firstError.msg || defaultMessage
    }
    
    return defaultMessage
  }

  return {
    // State
    predictions,
    currentPrediction,
    loading,
    batchLoading,
    error,
    
    // Computed
    totalPredictions,
    predictionsByDomain,
    recentPredictions,
    predictionStats,
    
    // Actions
    fetchPredictions,
    fetchPrediction,
    classify,
    batchClassify,
    clearPredictions,
    clearError,
    clearCurrentPrediction
  }
})

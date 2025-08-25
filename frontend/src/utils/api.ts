import axios from 'axios'
// @ts-ignore - Axios type issues
import { useToast } from 'vue-toastification'
import type { 
  ApiResponse, 
  PaginatedResponse, 
  ErrorResponse,
  Dataset,
  DatasetSample,
  MLModel,
  MLModelCreateRequest,
  TrainingJob,
  StartTrainingRequest,
  ClassificationRequest,
  ClassificationResponse,
  BatchClassificationRequest,
  BatchClassificationResponse,
  HyperparameterOptimizationRequest,
  HyperparameterOptimizationResponse,
  ModelComparison,
  ModelComparisonCreateRequest,
  SystemStats
} from '@/types'

// API Configuration
// When served by Django, use relative URLs. When in development, use full URL.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')
const API_TIMEOUT = 30000 // 30 seconds

// Create Axios instance
// @ts-ignore - Axios type issues
export const apiClient = (axios as any).create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Request interceptor for auth tokens, loading states, etc.
apiClient.interceptors.request.use(
  (config: any) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add request timestamp
    config.metadata = { startTime: Date.now() }
    
    return config
  },
  (error: any) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and logging
// @ts-ignore - Axios type issues
apiClient.interceptors.response.use(
  (response: any) => {
    // Log response time in development
    if (import.meta.env.DEV && response.config.metadata) {
      const duration = Date.now() - response.config.metadata.startTime
      console.log(`API ${response.config.method?.toUpperCase()} ${response.config.url}: ${duration}ms`)
    }
    
    return response
  },
  (error: any) => {
    const toast = useToast()
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const data = error.response.data as ErrorResponse
      
      switch (status) {
        case 401:
          toast.error('Authentication required. Please log in.')
          // Redirect to login or clear auth token
          localStorage.removeItem('auth_token')
          break
        case 403:
          toast.error('Access forbidden. You don\'t have permission.')
          break
        case 404:
          toast.error('Resource not found.')
          break
        case 422:
          // Validation errors - don't show toast, let component handle
          break
        case 500:
          toast.error('Server error. Please try again later.')
          break
        default:
          toast.error(data.error || `Request failed with status ${status}`)
      }
    } else if (error.request) {
      // Network error
      toast.error('Network error. Please check your connection.')
    } else {
      // Request setup error
      toast.error('Request failed. Please try again.')
    }
    
    return Promise.reject(error)
  }
)

// Generic API methods
class ApiService {
  async get<T>(url: string, config?: any): Promise<T> {
    // @ts-ignore - Axios type issues
    const response = await apiClient.get(url, config)
    return response.data
  }
  
  async post<T, D = unknown>(url: string, data?: D, config?: any): Promise<T> {
    // @ts-ignore - Axios type issues
    const response = await apiClient.post(url, data, config)
    return response.data
  }
  
  async put<T, D = unknown>(url: string, data?: D, config?: any): Promise<T> {
    // @ts-ignore - Axios type issues
    const response = await apiClient.put(url, data, config)
    return response.data
  }
  
  async patch<T, D = unknown>(url: string, data?: D, config?: any): Promise<T> {
    // @ts-ignore - Axios type issues
    const response = await apiClient.patch(url, data, config)
    return response.data
  }
  
  async delete<T>(url: string, config?: any): Promise<T> {
    // @ts-ignore - Axios type issues
    const response = await apiClient.delete(url, config)
    return response.data
  }
  
  // File upload with progress
  async upload<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData()
    formData.append('file', file)
    
    // @ts-ignore - Axios type issues
    const response = await apiClient.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent: any) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    })
    
    return response.data
  }
}

// Create service instance
const api = new ApiService()

// Dataset API
export const datasetApi = {
  // Get all datasets with pagination
  getDatasets: (page = 1, pageSize = 20): Promise<PaginatedResponse<Dataset>> =>
    api.get(`/api/datasets/?page=${page}&page_size=${pageSize}`),
  
  // Get single dataset
  getDataset: (id: number): Promise<Dataset> =>
    api.get(`/api/datasets/${id}/`),
  
  // Create new dataset (Step 1: Create empty dataset)
  createDataset: (data: { name: string; description?: string }): Promise<Dataset> => {
    return api.post('/api/datasets/', {
      name: data.name,
      description: data.description || ''
    })
  },

  // Upload file to dataset (Step 2: Upload file)
  uploadDatasetFile: (datasetId: number, file: File): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post(`/api/datasets/${datasetId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // Update dataset
  updateDataset: (id: number, data: Partial<Dataset>): Promise<Dataset> =>
    api.patch(`/api/datasets/${id}/`, data),
  
  // Delete dataset
  deleteDataset: (id: number): Promise<void> =>
    api.delete(`/api/datasets/${id}/`),
  
  // Get dataset samples
  getDatasetSamples: (datasetId: number, page = 1, pageSize = 20): Promise<PaginatedResponse<DatasetSample>> =>
    api.get(`/api/datasets/${datasetId}/samples/?page=${page}&page_size=${pageSize}`),
  
  // Validate dataset
  validateDataset: (id: number): Promise<ApiResponse> =>
    api.post(`/api/datasets/${id}/validate`),
  
  // Get dataset statistics
  getDatasetStats: (id: number): Promise<any> =>
    api.get(`/api/datasets/${id}/statistics/`)
}

// ML Model API
export const modelApi = {
  // Get all models
  getModels: (page = 1, pageSize = 20): Promise<PaginatedResponse<MLModel>> =>
    api.get(`/api/classification/models?page=${page}&page_size=${pageSize}`),
  
  // Get single model
  getModel: (id: number): Promise<MLModel> =>
    api.get(`/api/classification/models/${id}`),
  
  // Create new model
  createModel: (data: MLModelCreateRequest): Promise<MLModel> =>
    api.post('/api/classification/models', data),
  
  // Update model
  updateModel: (id: number, data: Partial<MLModel>): Promise<MLModel> =>
    api.patch(`/api/classification/models/${id}`, data),
  
  // Delete model
  deleteModel: (id: number): Promise<void> =>
    api.delete(`/api/classification/models/${id}`),
  
  // Start training
  startTraining: (modelId: number, params: StartTrainingRequest): Promise<TrainingJob> =>
    api.post(`/api/classification/models/${modelId}/train`, params),
  
  // Get training job
  getTrainingJob: (modelId: number): Promise<TrainingJob> =>
    api.get(`/api/classification/models/${modelId}/training-job`),
  
  // Stop training
  stopTraining: (modelId: number): Promise<ApiResponse> =>
    api.post(`/api/classification/models/${modelId}/stop-training`),
  
  // Optimize hyperparameters
  optimizeHyperparameters: (modelId: number, params: HyperparameterOptimizationRequest): Promise<HyperparameterOptimizationResponse> =>
    api.post(`/api/classification/models/${modelId}/optimize`, params)
}

// Classification API
export const classificationApi = {
  // Single prediction
  predict: (modelId: number, data: ClassificationRequest): Promise<ClassificationResponse> =>
    api.post(`/api/classification/predict`, { ...data, model_id: modelId }),
  
  // Batch predictions
  batchPredict: (modelId: number, data: BatchClassificationRequest): Promise<BatchClassificationResponse> =>
    api.post(`/api/classification/predict-batch`, { ...data, model_id: modelId }),
  
  // Get prediction history
  getPredictions: (page = 1, pageSize = 20): Promise<PaginatedResponse<any>> =>
    api.get(`/api/classification/predictions?page=${page}&page_size=${pageSize}`),
  
  // Get model predictions
  getModelPredictions: (modelId: number, page = 1, pageSize = 20): Promise<PaginatedResponse<any>> =>
    api.get(`/api/classification/predictions?model_id=${modelId}&page=${page}&page_size=${pageSize}`)
}

// Model Comparison API
export const comparisonApi = {
  // Get comparisons
  getComparisons: (): Promise<ModelComparison[]> =>
    api.get('/api/classification/comparisons'),
  
  // Create comparison
  createComparison: (data: ModelComparisonCreateRequest): Promise<ModelComparison> =>
    api.post('/api/classification/comparisons', data),
  
  // Get comparison details
  getComparison: (id: number): Promise<ModelComparison> =>
    api.get(`/api/classification/comparisons/${id}`),
  
  // Delete comparison
  deleteComparison: (id: number): Promise<void> =>
    api.delete(`/api/classification/comparisons/${id}`)
}

// System API
export const systemApi = {
  // Get system statistics
  getStats: (): Promise<SystemStats> =>
    api.get('/api/system/stats'),
  
  // Health check
  healthCheck: (): Promise<ApiResponse> =>
    api.get('/api/health/'),
  
  // Get medical domains
  getMedicalDomains: (): Promise<string[]> =>
    api.get('/api/medical-domains')
}

// Dashboard API
export const dashboardApi = {
  // Get chart data
  getChartData: (type: string): Promise<any> =>
    api.get(`/dashboard/api/chart-data/?type=${type}`)
}

// Export all APIs
export {
  api,
  apiClient as axiosClient
}

// Error handling utilities
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

export function handleApiError(error: unknown): string {
  if (isApiError(error)) {
    return error.message
  }
  
  if ((axios as any).isAxiosError?.(error)) {
    if ((error as any).response?.data?.error) {
      return (error as any).response.data.error
    }
    return (error as any).message
  }
  
  return 'An unexpected error occurred'
}

// Request cancellation utilities
export const cancelTokenSource = () => (axios as any).CancelToken?.source()

export function isRequestCancelled(error: unknown): boolean {
  return (axios as any).isCancel?.(error) || false
}

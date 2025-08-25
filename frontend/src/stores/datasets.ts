import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { datasetApi } from '@/utils/api'
import { withLoading, createInitialState, persistStore, loadPersistedStore } from './index'
import type { 
  Dataset, 
  DatasetSample, 
  DatasetCreateRequest
} from '@/types'

export const useDatasetStore = defineStore('datasets', () => {
  // State
  const state = ref(createInitialState())
  const datasets = ref<Dataset[]>([])
  const currentDataset = ref<Dataset | null>(null)
  const samples = ref<DatasetSample[]>([])
  const pagination = ref({
    count: 0,
    next: null as string | null,
    previous: null as string | null,
    currentPage: 1,
    pageSize: 20,
    totalPages: 0
  })
  const samplesPagination = ref({
    count: 0,
    next: null as string | null,
    previous: null as string | null,
    currentPage: 1,
    pageSize: 20,
    totalPages: 0
  })
  
  // Filters and search
  const filters = ref({
    search: '',
    isValidated: null as boolean | null,
    medicalDomains: [] as string[],
    sortBy: 'uploaded_at',
    sortOrder: 'desc' as 'asc' | 'desc'
  })
  
  // Upload state
  const uploadState = ref({
    isUploading: false,
    progress: 0,
    error: null as string | null
  })

  // Computed
  const totalDatasets = computed(() => pagination.value.count)
  const hasDatasets = computed(() => datasets.value.length > 0)
  const isLoading = computed(() => state.value.loading)
  const error = computed(() => state.value.error)
  
  const validatedDatasets = computed(() => 
    datasets.value.filter(d => d.is_validated)
  )
  
  const pendingDatasets = computed(() => 
    datasets.value.filter(d => !d.is_validated)
  )
  
  const filteredDatasets = computed(() => {
    let result = datasets.value
    
    // Search filter
    if (filters.value.search) {
      const query = filters.value.search.toLowerCase()
      result = result.filter(d => 
        d.name.toLowerCase().includes(query) ||
        d.description.toLowerCase().includes(query)
      )
    }
    
    // Validation filter
    if (filters.value.isValidated !== null) {
      result = result.filter(d => d.is_validated === filters.value.isValidated)
    }
    
    // Medical domains filter
    if (filters.value.medicalDomains.length > 0) {
      result = result.filter(d => 
        filters.value.medicalDomains.some(domain => 
          d.medical_domains.includes(domain)
        )
      )
    }
    
    // Sort
    result = [...result].sort((a, b) => {
      const aVal = a[filters.value.sortBy as keyof Dataset]
      const bVal = b[filters.value.sortBy as keyof Dataset]
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return filters.value.sortOrder === 'asc' 
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal)
      }
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return filters.value.sortOrder === 'asc' 
          ? aVal - bVal
          : bVal - aVal
      }
      
      return 0
    })
    
    return result
  })
  
  // Dataset statistics
  const statistics = computed(() => ({
    total: datasets.value.length,
    validated: validatedDatasets.value.length,
    pending: pendingDatasets.value.length,
    totalSamples: datasets.value.reduce((sum, d) => sum + d.total_samples, 0),
    averageSamples: datasets.value.length > 0 
      ? Math.round(datasets.value.reduce((sum, d) => sum + d.total_samples, 0) / datasets.value.length)
      : 0,
    totalSize: datasets.value.reduce((sum, d) => sum + d.file_size_mb, 0),
    uniqueDomains: [...new Set(datasets.value.flatMap(d => d.medical_domains))].length
  }))

  // Actions
  const fetchDatasets = async (page = 1, pageSize = 20) => {
    return await withLoading(state.value, async () => {
      const response = await datasetApi.getDatasets(page, pageSize)
      
      datasets.value = response.items || response.results || []
      pagination.value = {
        count: response.count || 0,
        next: response.next,
        previous: response.previous,
        currentPage: page,
        pageSize,
        totalPages: Math.ceil((response.count || 0) / pageSize)
      }
      
      // Persist to localStorage for offline access
      persistStore('datasets', datasets.value)
      
      return response
    })
  }
  
  const fetchDataset = async (id: number) => {
    return await withLoading(state.value, async () => {
      const dataset = await datasetApi.getDataset(id)
      
      currentDataset.value = dataset
      
      // Update in datasets array if exists
      const index = datasets.value.findIndex(d => d.id === id)
      if (index !== -1) {
        datasets.value[index] = dataset
      }
      
      return dataset
    })
  }
  
  const createDataset = async (data: DatasetCreateRequest, onProgress?: (progress: number) => void) => {
    uploadState.value.isUploading = true
    uploadState.value.progress = 0
    uploadState.value.error = null
    
    try {
      // Step 1: Create empty dataset
      uploadState.value.progress = 10
      onProgress?.(10)
      
      const createData: { name: string; description?: string } = {
        name: data.name
      }
      if (data.description) {
        createData.description = data.description
      }
      const dataset = await datasetApi.createDataset(createData)
      
      // Step 2: Upload file if provided
      if (data.file) {
        uploadState.value.progress = 30
        onProgress?.(30)
        
        // Simulate progress for file upload
        const progressInterval = setInterval(() => {
          if (uploadState.value.progress < 90) {
            uploadState.value.progress += 10
            onProgress?.(uploadState.value.progress)
          }
        }, 200)
        
        await datasetApi.uploadDatasetFile(dataset.id, data.file)
        
        clearInterval(progressInterval)
      }
      
      uploadState.value.progress = 100
      onProgress?.(100)
      
      // Add to datasets array
      datasets.value.unshift(dataset)
      pagination.value.count++
      
      return dataset
    } catch (error) {
      uploadState.value.error = error instanceof Error ? error.message : 'Upload failed'
      throw error
    } finally {
      uploadState.value.isUploading = false
      setTimeout(() => {
        uploadState.value.progress = 0
        uploadState.value.error = null
      }, 2000)
    }
  }
  
  const updateDataset = async (id: number, data: Partial<Dataset>) => {
    return await withLoading(state.value, async () => {
      const updatedDataset = await datasetApi.updateDataset(id, data)
      
      // Update in datasets array
      const index = datasets.value.findIndex(d => d.id === id)
      if (index !== -1) {
        datasets.value[index] = updatedDataset
      }
      
      // Update current dataset if it's the same
      if (currentDataset.value?.id === id) {
        currentDataset.value = updatedDataset
      }
      
      return updatedDataset
    })
  }
  
  const deleteDataset = async (id: number) => {
    return await withLoading(state.value, async () => {
      await datasetApi.deleteDataset(id)
      
      // Remove from datasets array
      datasets.value = datasets.value.filter(d => d.id !== id)
      pagination.value.count--
      
      // Clear current dataset if it was deleted
      if (currentDataset.value?.id === id) {
        currentDataset.value = null
      }
    })
  }
  
  const validateDataset = async (id: number) => {
    return await withLoading(state.value, async () => {
      const response = await datasetApi.validateDataset(id)
      
      // Refresh dataset data after validation
      await fetchDataset(id)
      
      return response
    })
  }
  
  const fetchDatasetSamples = async (datasetId: number, page = 1, pageSize = 20) => {
    return await withLoading(state.value, async () => {
      const response = await datasetApi.getDatasetSamples(datasetId, page, pageSize)
      
      samples.value = response.items || response.results || []
      samplesPagination.value = {
        count: response.count || 0,
        next: response.next,
        previous: response.previous,
        currentPage: page,
        pageSize,
        totalPages: Math.ceil((response.count || 0) / pageSize)
      }
      
      return response
    })
  }
  
  const getDatasetStats = async (id: number) => {
    return await withLoading(state.value, async () => {
      return await datasetApi.getDatasetStats(id)
    })
  }
  
  // Filter actions
  const setSearch = (query: string) => {
    filters.value.search = query
  }
  
  const setValidationFilter = (validated: boolean | null) => {
    filters.value.isValidated = validated
  }
  
  const setMedicalDomainsFilter = (domains: string[]) => {
    filters.value.medicalDomains = domains
  }
  
  const setSorting = (sortBy: string, sortOrder: 'asc' | 'desc') => {
    filters.value.sortBy = sortBy
    filters.value.sortOrder = sortOrder
  }
  
  const clearFilters = () => {
    filters.value = {
      search: '',
      isValidated: null,
      medicalDomains: [],
      sortBy: 'uploaded_at',
      sortOrder: 'desc'
    }
  }
  
  // Utility actions
  const getDatasetById = (id: number): Dataset | undefined => {
    return datasets.value.find(d => d.id === id)
  }
  
  const refreshDatasets = async () => {
    await fetchDatasets(pagination.value.currentPage, pagination.value.pageSize)
  }
  
  const resetState = () => {
    datasets.value = []
    currentDataset.value = null
    samples.value = []
    pagination.value = {
      count: 0,
      next: null,
      previous: null,
      currentPage: 1,
      pageSize: 20,
      totalPages: 0
    }
    samplesPagination.value = {
      count: 0,
      next: null,
      previous: null,
      currentPage: 1,
      pageSize: 20,
      totalPages: 0
    }
    clearFilters()
    state.value = createInitialState()
  }
  
  // Load persisted data on initialization
  const loadPersistedData = () => {
    const persistedDatasets = loadPersistedStore('datasets', [])
    if (persistedDatasets.length > 0) {
      datasets.value = persistedDatasets
    }
  }

  return {
    // State
    datasets,
    currentDataset,
    samples,
    pagination,
    samplesPagination,
    filters,
    uploadState,
    
    // Computed
    totalDatasets,
    hasDatasets,
    isLoading,
    error,
    validatedDatasets,
    pendingDatasets,
    filteredDatasets,
    statistics,
    
    // Actions
    fetchDatasets,
    fetchDataset,
    createDataset,
    updateDataset,
    deleteDataset,
    validateDataset,
    fetchDatasetSamples,
    getDatasetStats,
    
    // Filter actions
    setSearch,
    setValidationFilter,
    setMedicalDomainsFilter,
    setSorting,
    clearFilters,
    
    // Utility actions
    getDatasetById,
    refreshDatasets,
    resetState,
    loadPersistedData
  }
})

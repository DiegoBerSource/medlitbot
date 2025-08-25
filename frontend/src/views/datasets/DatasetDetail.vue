<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="text-center">
        <Icon name="clock" class="w-8 h-8 text-blue-500 mx-auto mb-2 animate-spin" />
        <p class="text-gray-600">Loading dataset details...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-center">
        <Icon name="warning" class="w-5 h-5 text-red-600 mr-2" />
        <h3 class="text-red-800 font-medium">Error Loading Dataset</h3>
      </div>
      <p class="text-red-700 mt-1">{{ error }}</p>
      <button @click="loadDataset" class="mt-3 text-red-600 hover:text-red-800 text-sm underline">
        Try Again
      </button>
    </div>

    <!-- Dataset Details -->
    <div v-else-if="dataset" class="space-y-8">
      <!-- Header Section -->
      <div class="medical-card">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center space-x-4">
            <div class="p-3 bg-purple-100 rounded-lg">
              <Icon name="database" class="w-8 h-8 text-purple-600" />
            </div>
            <div>
              <h1 class="text-3xl font-bold text-gray-900 flex items-center">
                {{ dataset.name }}
                <span v-if="dataset.is_validated" class="ml-3 px-2 py-1 bg-green-100 text-green-800 text-sm rounded-full">✓ Validated</span>
                <span v-else class="ml-3 px-2 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full">⚠ Not Validated</span>
              </h1>
              <p class="text-gray-600 mt-1">{{ dataset.description || 'No description provided' }}</p>
              <div class="flex items-center space-x-4 mt-2">
                <span class="text-sm text-gray-500">{{ dataset.total_samples || 0 }} samples</span>
                <span class="text-sm text-gray-500">{{ formatFileSize(dataset.file_size_mb) }}</span>
                <span class="text-sm text-gray-500">{{ dataset.file_extension?.toUpperCase() || 'Unknown' }} format</span>
                <span class="text-sm text-gray-500">Uploaded {{ formatDate(dataset.uploaded_at) }}</span>
              </div>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex space-x-3">
            <button class="btn-secondary" @click="downloadDataset" :disabled="!dataset.file_size_mb">
              <Icon name="document" class="w-4 h-4 mr-2" />
              Download
            </button>
            <button class="btn-secondary" @click="validateDataset" :disabled="loading">
              <Icon name="success" class="w-4 h-4 mr-2" />
              Validate
            </button>
            <button class="btn-primary" @click="trainModel" :disabled="!dataset.is_validated">
              <Icon name="brain" class="w-4 h-4 mr-2" />
              Train Model
            </button>
          </div>
        </div>
      </div>

      <!-- Statistics Overview -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          label="Total Samples"
          :value="dataset.total_samples || 0"
          icon="list"
          color="blue"
        />
        <StatCard
          label="Medical Domains"
          :value="dataset.medical_domains?.length || 0"
          icon="chart-bar"
          color="purple"
        />
        <StatCard
          label="Avg Title Length"
          :value="dataset.avg_title_length ? `${Math.round(dataset.avg_title_length)} chars` : 'N/A'"
          icon="document"
          color="green"
        />
        <StatCard
          label="Avg Abstract Length"
          :value="dataset.avg_abstract_length ? `${Math.round(dataset.avg_abstract_length)} chars` : 'N/A'"
          icon="document"
          color="yellow"
        />
      </div>

      <!-- Charts and Analysis -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Domain Distribution Chart -->
        <ChartCard title="Medical Domain Distribution" :loading="false">
          <DoughnutChart 
            v-if="domainChartData?.datasets?.[0]?.data?.length"
            :data="domainChartData" 
            :options="doughnutOptions"
            :height="300"
          />
          <div v-else class="p-8 text-center">
            <Icon name="chart-bar" class="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p class="text-gray-500">No domain distribution data available</p>
          </div>
        </ChartCard>

        <!-- Validation Status -->
        <ChartCard title="Data Quality Status" :loading="false">
          <div class="p-4">
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700">Validation Status</span>
                <span class="text-sm font-medium" :class="dataset.is_validated ? 'text-green-600' : 'text-yellow-600'">
                  {{ dataset.is_validated ? 'Validated' : 'Pending Validation' }}
                </span>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700">File Format</span>
                <span class="text-sm text-gray-900">{{ dataset.file_extension?.toUpperCase() || 'Unknown' }}</span>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700">File Size</span>
                <span class="text-sm text-gray-900">{{ formatFileSize(dataset.file_size_mb) }}</span>
              </div>

              <!-- Validation Errors -->
              <div v-if="dataset.validation_errors && (dataset.validation_errors as any)?.length > 0" class="mt-6 pt-4 border-t border-gray-200">
                <h4 class="text-sm font-medium text-gray-700 mb-3">Validation Issues</h4>
                <div class="space-y-2">
                  <div 
                    v-for="(error, index) in dataset.validation_errors" 
                    :key="index"
                    class="flex items-center text-sm"
                  >
                    <div class="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
                    <span class="text-gray-700">{{ error }}</span>
                  </div>
                </div>
              </div>

              <!-- Quality Metrics -->
              <div class="mt-6 pt-4 border-t border-gray-200">
                <h4 class="text-sm font-medium text-gray-700 mb-3">Quality Metrics</h4>
                <div class="space-y-2">
                  <div class="flex items-center text-sm">
                    <Icon name="success" class="w-4 h-4 text-green-500 mr-2" />
                    <span class="text-gray-700">{{ dataset.total_samples || 0 }} valid samples</span>
                  </div>
                  <div class="flex items-center text-sm">
                    <Icon name="chart-bar" class="w-4 h-4 text-blue-500 mr-2" />
                    <span class="text-gray-700">{{ dataset.medical_domains?.length || 0 }} unique domains</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </ChartCard>
      </div>

      <!-- Medical Domains Breakdown -->
      <div v-if="dataset.medical_domains && dataset.medical_domains.length > 0" class="medical-card">
        <div class="medical-card-header">
          <h2 class="text-xl font-semibold text-gray-900">Medical Domains</h2>
          <p class="text-sm text-gray-600">Distribution of medical domains in this dataset</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="domain in dataset.medical_domains" 
            :key="domain"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center justify-between">
              <h3 class="font-medium text-gray-900">{{ formatDomain(domain) }}</h3>
              <span class="text-sm text-gray-500">
                {{ getDomainCount(domain) }} samples
              </span>
            </div>
            <div class="mt-2">
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full bg-purple-500"
                  :style="`width: ${getDomainPercentage(domain)}%`"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="medical-card">
        <div class="medical-card-header">
          <h2 class="text-xl font-semibold text-gray-900">Quick Actions</h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button 
            @click="trainModel"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            :disabled="!dataset.is_validated"
          >
            <Icon name="brain" class="w-6 h-6 text-blue-500 mb-2" />
            <h3 class="font-medium text-gray-900">Train AI Model</h3>
            <p class="text-sm text-gray-600 mt-1">Create a new classification model</p>
          </button>
          
          <button 
            @click="validateDataset"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <Icon name="success" class="w-6 h-6 text-green-500 mb-2" />
            <h3 class="font-medium text-gray-900">Validate Dataset</h3>
            <p class="text-sm text-gray-600 mt-1">Check data quality and structure</p>
          </button>
          
          <button 
            @click="exportDataset"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <Icon name="document" class="w-6 h-6 text-purple-500 mb-2" />
            <h3 class="font-medium text-gray-900">Export Dataset</h3>
            <p class="text-sm text-gray-600 mt-1">Download in various formats</p>
          </button>
        </div>
      </div>

      <!-- Dataset Samples Preview -->
      <div class="medical-card">
        <div class="medical-card-header">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Dataset Samples</h2>
              <p class="text-sm text-gray-600">Preview of articles in this dataset</p>
            </div>
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-500">
                Showing {{ Math.min(displayCount, samples.length) }} of {{ dataset.total_samples || 0 }}
              </span>
              <button 
                v-if="samples.length > displayCount"
                @click="loadMoreSamples"
                class="btn-outline text-sm"
              >
                Load More
              </button>
            </div>
          </div>
        </div>

        <!-- Samples Loading -->
        <div v-if="samplesLoading" class="flex items-center justify-center h-32">
          <Icon name="clock" class="w-6 h-6 text-blue-500 animate-spin" />
        </div>

        <!-- Samples Table -->
        <div v-else-if="samples.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Domains</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Journal</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Year</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="sample in displayedSamples" :key="sample.id" class="hover:bg-gray-50">
                <td class="px-6 py-4">
                  <div class="max-w-md">
                    <p class="text-sm font-medium text-gray-900 line-clamp-2">{{ sample.title }}</p>
                    <p class="text-sm text-gray-500 line-clamp-2 mt-1">{{ sample.abstract }}</p>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap gap-1">
                    <span 
                      v-for="domain in sample.medical_domains?.slice(0, 2)" 
                      :key="domain"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800"
                    >
                      {{ formatDomain(domain) }}
                    </span>
                    <span 
                      v-if="sample.medical_domains && sample.medical_domains.length > 2"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600"
                    >
                      +{{ sample.medical_domains.length - 2 }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-900">
                  {{ sample.journal || 'N/A' }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-900">
                  {{ sample.publication_year || 'N/A' }}
                </td>
                <td class="px-6 py-4 text-sm font-medium">
                  <button 
                    @click="viewSample(sample)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty Samples State -->
        <div v-else class="text-center py-8">
          <Icon name="document" class="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p class="text-gray-500">No samples available</p>
          <p class="text-sm text-gray-400 mt-1">Upload a file to see dataset samples</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useDatasetStore } from '@/stores/datasets'
import { storeToRefs } from 'pinia'
import Icon from '@/components/ui/Icon.vue'
import StatCard from '@/components/ui/StatCard.vue'
import ChartCard from '@/components/charts/ChartCard.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'
import { datasetApi } from '@/utils/api'
import type { Dataset, DatasetSample } from '@/types'

interface Props {
  id: number
}

const props = defineProps<Props>()
const router = useRouter()
const toast = useToast()
const datasetStore = useDatasetStore()
const { datasets } = storeToRefs(datasetStore)

// State
const dataset = ref<Dataset | null>(null)
const samples = ref<DatasetSample[]>([])
const loading = ref(true)
const samplesLoading = ref(false)
const error = ref<string | null>(null)
const displayCount = ref(10)

// Computed
const displayedSamples = computed(() => 
  samples.value.slice(0, displayCount.value)
)

const domainChartData = computed(() => {
  if (!dataset.value?.domain_distribution) return { labels: [], datasets: [{ data: [] }] }
  
  const distribution = dataset.value.domain_distribution
  const labels = Object.keys(distribution)
  const data = Object.values(distribution)
  
  if (labels.length === 0) return { labels: [], datasets: [{ data: [] }] }
  
  return {
    labels: labels.map(formatDomain),
    datasets: [
      {
        data: data,
        backgroundColor: [
          '#8B5CF6', '#EF4444', '#10B981', '#F59E0B', '#3B82F6',
          '#EC4899', '#84CC16', '#F97316', '#06B6D4', '#6366F1'
        ],
        borderWidth: 1,
        borderColor: '#fff'
      }
    ]
  }
})

const doughnutOptions = computed(() => ({
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        padding: 20,
        usePointStyle: true
      }
    }
  },
  responsive: true,
  maintainAspectRatio: false
}))

// Methods
const loadDataset = async () => {
  loading.value = true
  error.value = null
  
  try {
    // First check if dataset is in store
    let foundDataset = datasets.value.find(d => d.id === props.id)
    
    if (!foundDataset) {
      // Fetch from API
      foundDataset = await datasetApi.getDataset(props.id)
    }
    
    dataset.value = foundDataset
    
    // Load samples
    await loadSamples()
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load dataset'
    console.error('Failed to load dataset:', err)
  } finally {
    loading.value = false
  }
}

const loadSamples = async () => {
  if (!dataset.value) return
  
  samplesLoading.value = true
  try {
    const response = await datasetApi.getDatasetSamples(dataset.value.id, 1, 50)
    samples.value = response.results || response.items || []
  } catch (err) {
    console.error('Failed to load samples:', err)
  } finally {
    samplesLoading.value = false
  }
}

const loadMoreSamples = () => {
  displayCount.value = Math.min(displayCount.value + 10, samples.value.length)
}

// Helper functions
const formatFileSize = (sizeMb: number | null) => {
  if (!sizeMb) return 'Unknown'
  if (sizeMb < 1) return `${Math.round(sizeMb * 1024)} KB`
  if (sizeMb < 1024) return `${sizeMb.toFixed(1)} MB`
  return `${(sizeMb / 1024).toFixed(1)} GB`
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

const formatDomain = (domain: string) => {
  return domain.charAt(0).toUpperCase() + domain.slice(1).replace(/_/g, ' ')
}

const getDomainCount = (domain: string) => {
  if (!dataset.value?.domain_distribution) return 0
  return dataset.value.domain_distribution[domain] || 0
}

const getDomainPercentage = (domain: string) => {
  if (!dataset.value?.domain_distribution || !dataset.value.total_samples) return 0
  const count = dataset.value.domain_distribution[domain] || 0
  return Math.round((count / dataset.value.total_samples) * 100)
}

// Action handlers
const validateDataset = async () => {
  if (!dataset.value) return
  
  loading.value = true
  try {
    await datasetApi.validateDataset(dataset.value.id)
    toast.success('Dataset validation started')
    
    // Reload dataset to get updated validation status
    setTimeout(() => loadDataset(), 2000)
    
  } catch (error) {
    toast.error('Failed to start validation')
    console.error('Validation error:', error)
  } finally {
    loading.value = false
  }
}

const trainModel = () => {
  router.push(`/models/create?dataset=${props.id}`)
}

const downloadDataset = () => {
  toast.info('Download functionality coming soon')
}

const exportDataset = () => {
  toast.info('Export functionality coming soon')
}

const viewSample = (sample: DatasetSample) => {
  toast.info(`Viewing sample: ${sample.title}`)
  // Could open a modal or navigate to sample detail
}

// Lifecycle
onMounted(loadDataset)
</script>

<style scoped>
.medical-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 p-6;
}

.medical-card-header {
  @apply mb-6 pb-4 border-b border-gray-200;
}

.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-outline {
  @apply border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

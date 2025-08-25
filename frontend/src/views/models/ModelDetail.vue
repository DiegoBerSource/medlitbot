<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="text-center">
        <Icon name="clock" class="w-8 h-8 text-blue-500 mx-auto mb-2 animate-spin" />
        <p class="text-gray-600">Loading model details...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-center">
        <Icon name="warning" class="w-5 h-5 text-red-600 mr-2" />
        <h3 class="text-red-800 font-medium">Error Loading Model</h3>
      </div>
      <p class="text-red-700 mt-1">{{ error }}</p>
      <button @click="loadModel" class="mt-3 text-red-600 hover:text-red-800 text-sm underline">
        Try Again
      </button>
    </div>

    <!-- Model Details -->
    <div v-else-if="model" class="space-y-8">
      <!-- Header Section -->
      <div class="medical-card">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center space-x-4">
            <div class="p-3 bg-blue-100 rounded-lg">
              <Icon name="cpu" class="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 class="text-3xl font-bold text-gray-900 flex items-center">
                {{ model.name }}
                <span v-if="isBestModel" class="ml-3 px-2 py-1 bg-green-100 text-green-800 text-sm rounded-full">⭐ Best Model</span>
              </h1>
              <p class="text-gray-600 mt-1">{{ model.description || 'No description provided' }}</p>
              <div class="flex items-center space-x-4 mt-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium" :class="getStatusClass(model.status)">
                  <Icon :name="getStatusIcon(model.status)" class="w-4 h-4 mr-1" />
                  {{ formatStatus(model.status) }}
                </span>
                <span class="text-sm text-gray-500">{{ formatModelType(model.model_type) }}</span>
                <span class="text-sm text-gray-500">Created {{ formatDate(model.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex space-x-3">
            <button class="btn-secondary" @click="exportModel" :disabled="model.status !== 'trained'">
              <Icon name="document" class="w-4 h-4 mr-2" />
              Export
            </button>
            <button class="btn-secondary" @click="retrainModel" :disabled="model.status === 'training'">
              <Icon name="brain" class="w-4 h-4 mr-2" />
              Retrain
            </button>
            <button class="btn-primary" @click="testModel" :disabled="model.status !== 'trained'">
              <Icon name="view" class="w-4 h-4 mr-2" />
              Test Model
            </button>
          </div>
        </div>
      </div>

      <!-- Performance Metrics Overview -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          label="Accuracy"
          :value="model.accuracy ? `${(model.accuracy * 100).toFixed(1)}%` : 'N/A'"
          icon="chart-bar"
          :color="getScoreColor(model.accuracy)"
        />
        <StatCard
          label="F1 Score"
          :value="model.f1_score ? `${(model.f1_score * 100).toFixed(1)}%` : 'N/A'"
          icon="chart-bar"
          :color="getScoreColor(model.f1_score)"
        />
        <StatCard
          label="Precision"
          :value="model.precision ? `${(model.precision * 100).toFixed(1)}%` : 'N/A'"
          icon="chart-bar"
          :color="getScoreColor(model.precision)"
        />
        <StatCard
          label="Recall"
          :value="model.recall ? `${(model.recall * 100).toFixed(1)}%` : 'N/A'"
          icon="chart-bar"
          :color="getScoreColor(model.recall)"
        />
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Performance Radar Chart -->
        <ChartCard title="Performance Metrics" :loading="false">
          <RadarChart 
            :data="performanceChartData" 
            :options="radarOptions"
            :height="300"
          />
        </ChartCard>

        <!-- Training Details -->
        <ChartCard title="Training Details" :loading="false">
          <div v-if="model.status === 'trained'" class="p-4">
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <span class="text-sm font-medium text-gray-700">Training Duration</span>
                <span class="text-sm text-gray-900">{{ formatTrainingTime(model.training_time_minutes) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm font-medium text-gray-700">Total Epochs</span>
                <span class="text-sm text-gray-900">{{ model.num_epochs || 'N/A' }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm font-medium text-gray-700">Best Epoch</span>
                <span class="text-sm text-gray-900">{{ model.best_epoch || 'N/A' }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm font-medium text-gray-700">Learning Rate</span>
                <span class="text-sm text-gray-900">{{ model.learning_rate || 'N/A' }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm font-medium text-gray-700">Batch Size</span>
                <span class="text-sm text-gray-900">{{ model.batch_size || 'N/A' }}</span>
              </div>
            </div>

            <!-- Training Timeline -->
            <div class="mt-6 pt-4 border-t border-gray-200">
              <h4 class="text-sm font-medium text-gray-700 mb-3">Training Timeline</h4>
              <div class="space-y-2">
                <div class="flex items-center text-sm">
                  <div class="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                  <span class="text-gray-600">Started:</span>
                  <span class="ml-2 text-gray-900">{{ formatDateTime(model.training_started_at) }}</span>
                </div>
                <div class="flex items-center text-sm">
                  <div class="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  <span class="text-gray-600">Completed:</span>
                  <span class="ml-2 text-gray-900">{{ formatDateTime(model.training_completed_at) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="p-8 text-center">
            <Icon name="clock" class="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p class="text-gray-500">Training details will appear after model training</p>
          </div>
        </ChartCard>
      </div>

      <!-- Model Configuration & Dataset Information -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Model Configuration -->
        <div class="medical-card">
          <div class="medical-card-header">
            <h2 class="text-xl font-semibold text-gray-900">Configuration</h2>
          </div>
          
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="text-sm font-medium text-gray-700">Model Type</span>
                <p class="text-sm text-gray-900 mt-1">{{ formatModelType(model.model_type) }}</p>
              </div>
              <div>
                <span class="text-sm font-medium text-gray-700">Model Size</span>
                <p class="text-sm text-gray-900 mt-1">{{ model.model_size_mb ? `${model.model_size_mb.toFixed(1)} MB` : 'N/A' }}</p>
              </div>
            </div>

            <!-- Hyperparameters -->
            <div v-if="model.hyperparameters && Object.keys(model.hyperparameters).length > 0">
              <span class="text-sm font-medium text-gray-700">Hyperparameters</span>
              <div class="mt-2 space-y-1">
                <div 
                  v-for="[key, value] in Object.entries(model.hyperparameters)"
                  :key="key"
                  class="flex justify-between text-sm"
                >
                  <span class="text-gray-600">{{ formatHyperparamName(key) }}:</span>
                  <span class="text-gray-900 font-mono">{{ value }}</span>
                </div>
              </div>
            </div>

            <!-- Technical Details -->
            <div class="pt-4 border-t border-gray-200">
              <div class="grid grid-cols-1 gap-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Training Complete:</span>
                  <span class="text-gray-900">{{ model.is_training_complete ? 'Yes' : 'No' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Deployed:</span>
                  <span class="text-gray-900">{{ model.is_deployed ? 'Yes' : 'No' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Last Updated:</span>
                  <span class="text-gray-900">{{ formatDate(model.updated_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dataset Information -->
        <div class="medical-card">
          <div class="medical-card-header">
            <h2 class="text-xl font-semibold text-gray-900">Training Dataset</h2>
          </div>
          
          <div class="space-y-4">
            <div>
              <span class="text-sm font-medium text-gray-700">Dataset Name</span>
              <p class="text-sm text-gray-900 mt-1">{{ model.dataset_name || `Dataset ${model.dataset}` }}</p>
            </div>

            <!-- Domain Performance -->
            <div v-if="model.domain_performance && Object.keys(model.domain_performance).length > 0">
              <span class="text-sm font-medium text-gray-700">Domain Performance</span>
              <div class="mt-2 space-y-2">
                <div 
                  v-for="[domain, metrics] in Object.entries(model.domain_performance)"
                  :key="domain"
                  class="p-3 bg-gray-50 rounded-lg"
                >
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-sm font-medium text-gray-900">{{ formatDomain(domain) }}</span>
                    <span class="text-xs text-gray-500">{{ metrics.support }} samples</span>
                  </div>
                  <div class="grid grid-cols-3 gap-2 text-xs">
                    <div class="text-center">
                      <div class="text-gray-600">F1</div>
                      <div class="font-medium">{{ (metrics.f1_score * 100).toFixed(0) }}%</div>
                    </div>
                    <div class="text-center">
                      <div class="text-gray-600">Precision</div>
                      <div class="font-medium">{{ (metrics.precision * 100).toFixed(0) }}%</div>
                    </div>
                    <div class="text-center">
                      <div class="text-gray-600">Recall</div>
                      <div class="font-medium">{{ (metrics.recall * 100).toFixed(0) }}%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Dataset Actions -->
            <div class="pt-4 border-t border-gray-200">
              <RouterLink 
                :to="`/datasets/${model.dataset}`"
                class="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
              >
                <Icon name="view" class="w-4 h-4 mr-1" />
                View Dataset Details
              </RouterLink>
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
            @click="goToClassification"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            :disabled="model.status !== 'trained'"
          >
            <Icon name="brain" class="w-6 h-6 text-blue-500 mb-2" />
            <h3 class="font-medium text-gray-900">Test Classification</h3>
            <p class="text-sm text-gray-600 mt-1">Try single article classification</p>
          </button>
          
          <button 
            @click="goToBatchClassification"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            :disabled="model.status !== 'trained'"
          >
            <Icon name="document" class="w-6 h-6 text-purple-500 mb-2" />
            <h3 class="font-medium text-gray-900">Batch Processing</h3>
            <p class="text-sm text-gray-600 mt-1">Classify multiple articles</p>
          </button>
          
          <button 
            @click="goToComparison"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <Icon name="chart-bar" class="w-6 h-6 text-green-500 mb-2" />
            <h3 class="font-medium text-gray-900">Model Comparison</h3>
            <p class="text-sm text-gray-600 mt-1">Compare with other models</p>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useModelStore } from '@/stores/models'
import { storeToRefs } from 'pinia'
import Icon from '@/components/ui/Icon.vue'
import StatCard from '@/components/ui/StatCard.vue'
import ChartCard from '@/components/charts/ChartCard.vue'
import RadarChart from '@/components/charts/RadarChart.vue'
import type { MLModel } from '@/types'

interface Props {
  id: number
}

const props = defineProps<Props>()
const router = useRouter()
const toast = useToast()
const modelStore = useModelStore()
const { models } = storeToRefs(modelStore)

// State
const model = ref<MLModel | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Computed
const isBestModel = computed(() => {
  if (!model.value || models.value.length === 0) return false
  
  const trainedModels = models.value.filter(m => m.status === 'trained' || m.is_trained)
  if (trainedModels.length === 0) return false
  
  const bestModel = trainedModels.reduce((best, current) => {
    if (current.f1_score && best.f1_score) {
      return current.f1_score > best.f1_score ? current : best
    }
    if (current.accuracy && best.accuracy) {
      return current.accuracy > best.accuracy ? current : best
    }
    return new Date(current.updated_at) > new Date(best.updated_at) ? current : best
  })
  
  return bestModel.id === model.value.id
})

const performanceChartData = computed(() => {
  if (!model.value) return { labels: [], datasets: [] }
  
  return {
    labels: ['Accuracy', 'F1 Score', 'Precision', 'Recall'],
    datasets: [
      {
        label: 'Performance',
        data: [
          (model.value.accuracy || 0) * 100,
          (model.value.f1_score || 0) * 100,
          (model.value.precision || 0) * 100,
          (model.value.recall || 0) * 100
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderColor: 'rgb(59, 130, 246)',
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(59, 130, 246)'
      }
    ]
  }
})

const radarOptions = computed(() => ({
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      max: 100,
      ticks: {
        display: false
      }
    }
  }
}))

// Methods
const loadModel = async () => {
  loading.value = true
  error.value = null
  
  try {
    // First ensure we have all models loaded
    if (models.value.length === 0) {
      await modelStore.fetchModels()
    }
    
    // Find the specific model
    const foundModel = models.value.find(m => m.id === props.id)
    if (foundModel) {
      model.value = foundModel
    } else {
      // Try to fetch the specific model
      model.value = await modelStore.fetchModel(props.id)
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load model'
    console.error('Failed to load model:', err)
  } finally {
    loading.value = false
  }
}

// Helper functions
const formatModelType = (modelType: string) => {
  const typeMap: Record<string, string> = {
    'biobert': 'BioBERT',
    'clinicalbert': 'ClinicalBERT', 
    'scibert': 'SciBERT',
    'pubmedbert': 'PubMedBERT',
    'bert': 'BERT',
    'hybrid': 'Hybrid Ensemble',
    'traditional': 'Traditional ML'
  }
  return typeMap[modelType] || modelType.charAt(0).toUpperCase() + modelType.slice(1)
}

const formatStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    'trained': 'bg-green-100 text-green-800',
    'training': 'bg-yellow-100 text-yellow-800',
    'created': 'bg-gray-100 text-gray-800',
    'failed': 'bg-red-100 text-red-800'
  }
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}

const getStatusIcon = (status: string) => {
  const statusMap: Record<string, string> = {
    'trained': 'success',
    'training': 'clock',
    'created': 'clock',
    'failed': 'warning'
  }
  return statusMap[status] || 'clock'
}

const getScoreColor = (score: number | null) => {
  if (!score) return 'gray'
  if (score >= 0.8) return 'green'
  if (score >= 0.7) return 'blue'
  if (score >= 0.6) return 'yellow'
  return 'red'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

const formatDateTime = (dateString: string | null) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const formatTrainingTime = (minutes: number | null) => {
  if (!minutes) return 'N/A'
  if (minutes < 60) return `${minutes.toFixed(0)}m`
  if (minutes < 1440) return `${(minutes / 60).toFixed(1)}h`
  return `${(minutes / 1440).toFixed(1)}d`
}

const formatDomain = (domain: string) => {
  return domain.charAt(0).toUpperCase() + domain.slice(1).replace(/_/g, ' ')
}

const formatHyperparamName = (key: string) => {
  return key.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

// Action handlers
const exportModel = () => {
  toast.info('Model export functionality coming soon')
}

const retrainModel = () => {
  router.push(`/models/${props.id}/training`)
}

const testModel = () => {
  goToClassification()
}

const goToClassification = () => {
  router.push(`/classification?model=${props.id}`)
}

const goToBatchClassification = () => {
  router.push(`/classification/batch?model=${props.id}`)
}

const goToComparison = () => {
  router.push(`/analytics/comparison?models=${props.id}`)
}

// Lifecycle
onMounted(loadModel)
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
</style>

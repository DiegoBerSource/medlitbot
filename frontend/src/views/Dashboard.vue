<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            Welcome to MedLitBot
          </h1>
          <p class="mt-2 text-gray-600">
            AI-powered medical literature classification dashboard
          </p>
        </div>
        
        <div class="flex items-center space-x-4">
          <!-- Quick Actions -->
          <div class="flex space-x-2">
            <button
              v-for="action in quickActions"
              :key="action.name"
              @click="router.push(action.route)"
              class="btn-primary flex items-center space-x-2"
              :title="action.description"
            >
              <Icon :name="action.icon" class="w-4 h-4" />
              <span class="hidden sm:inline">{{ action.name }}</span>
            </button>
          </div>
          
          <!-- Refresh Button -->
          <button
            @click="refreshData"
            :disabled="isLoading"
            class="btn-secondary flex items-center space-x-2"
          >
            <Icon 
              name="refresh" 
              class="w-4 h-4"
              :class="{ 'animate-spin': isLoading }"
            />
            <span class="hidden sm:inline">Refresh</span>
          </button>
        </div>
      </div>
      
      <!-- System Status -->
      <div class="mt-4 flex items-center space-x-4">
        <div class="flex items-center space-x-2">
          <div 
            class="w-3 h-3 rounded-full"
            :class="isOnline ? 'bg-green-400' : 'bg-red-400'"
          />
          <span class="text-sm text-gray-600">
            {{ isOnline ? 'Online' : 'Offline' }}
          </span>
        </div>
        
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-green-400" />
          <span class="text-sm text-gray-600">
            API Connected
          </span>
        </div>
        
        <div class="text-sm text-gray-500">
          Last updated: {{ lastUpdatedFormatted }}
        </div>
      </div>
    </div>
    
    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard
        v-for="stat in statistics"
        :key="stat.label"
        :label="stat.label"
        :value="stat.value"
        :icon="stat.icon"
        :color="stat.color"
        :trend="stat.trend"
        :loading="isLoading"
      />
    </div>
    
    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <!-- Dataset Overview Chart -->
      <ChartCard
        title="Dataset Overview"
        :loading="isLoading"
      >
        <DoughnutChart
          :data="datasetChartData"
          :options="chartOptions.dataset"
          :height="300"
        />
      </ChartCard>
      
      <!-- Model Performance Chart -->
      <ChartCard
        title="Model Performance"
        :loading="isLoading"
      >
        <RadarChart
          :data="modelPerformanceData"
          :options="chartOptions.performance"
          :height="300"
        />
      </ChartCard>
    </div>
    
    <!-- Recent Activity and Data Tables -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <!-- Recent Datasets -->
      <div class="medical-card">
        <div class="medical-card-header">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              Recent Datasets
            </h3>
            <RouterLink
              to="/datasets"
              class="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              View all →
            </RouterLink>
          </div>
        </div>
        
        <div class="space-y-3">
          <div
            v-for="dataset in recentDatasets"
            :key="dataset.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex-1">
              <h4 class="font-medium text-gray-900 truncate">
                {{ dataset.name }}
              </h4>
              <p class="text-sm text-gray-500">
                {{ dataset.total_samples }} samples
              </p>
            </div>
            
            <div class="flex items-center space-x-2">
              <span
                class="status-badge"
                :class="dataset.is_validated ? 'status-badge-success' : 'status-badge-warning'"
              >
                {{ dataset.is_validated ? 'Validated' : 'Pending' }}
              </span>
            </div>
          </div>
          
          <div
            v-if="recentDatasets.length === 0 && !isLoading"
            class="text-center py-8 text-gray-500"
          >
            <Icon name="database" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No datasets yet</p>
            <RouterLink to="/datasets/create" class="text-primary-600 hover:text-primary-700 text-sm">
              Create your first dataset →
            </RouterLink>
          </div>
        </div>
      </div>
      
      <!-- Recent Models -->
      <div class="medical-card">
        <div class="medical-card-header">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              ML Models
            </h3>
            <RouterLink
              to="/models"
              class="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              View all →
            </RouterLink>
          </div>
        </div>
        
        <div class="space-y-3">
          <div
            v-for="model in recentModels"
            :key="model.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex-1">
              <h4 class="font-medium text-gray-900 truncate">
                {{ model.name }}
              </h4>
              <p class="text-sm text-gray-500">
                {{ formatModelType(model.model_type) }}
                {{ model.f1_score ? `• F1: ${(model.f1_score * 100).toFixed(1)}%` : '' }}
              </p>
            </div>
            
            <div class="flex items-center space-x-2">
              <span
                class="status-badge"
                :class="{
                  'status-badge-success': model.status === 'trained',
                  'status-badge-warning': model.status === 'training',
                  'status-badge-error': model.status === 'failed',
                  'status-badge-info': model.status === 'created'
                }"
              >
                {{ model.status }}
              </span>
            </div>
          </div>
          
          <div
            v-if="recentModels.length === 0 && !isLoading"
            class="text-center py-8 text-gray-500"
          >
            <Icon name="cpu" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No models yet</p>
            <RouterLink to="/models/create" class="text-primary-600 hover:text-primary-700 text-sm">
              Create your first model →
            </RouterLink>
          </div>
        </div>
      </div>
      
      <!-- Recent Classifications -->
      <div class="medical-card">
        <div class="medical-card-header">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              Recent Classifications
            </h3>
            <RouterLink
              to="/classification/history"
              class="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              View all →
            </RouterLink>
          </div>
        </div>
        
        <div class="space-y-3">
          <div
            v-for="prediction in recentPredictions"
            :key="prediction.id"
            class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex-1">
              <h4 class="font-medium text-gray-900 text-sm line-clamp-2">
                {{ prediction.title }}
              </h4>
              <div class="mt-2 flex flex-wrap gap-1">
                <span
                  v-for="domain in prediction.predicted_domains.slice(0, 2)"
                  :key="domain"
                  class="domain-badge"
                >
                  {{ domain }}
                </span>
                <span
                  v-if="prediction.predicted_domains.length > 2"
                  class="text-xs text-gray-500"
                >
                  +{{ prediction.predicted_domains.length - 2 }} more
                </span>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                {{ formatRelativeTime(prediction.created_at) }}
              </p>
            </div>
          </div>
          
          <div
            v-if="recentPredictions.length === 0 && !isLoading"
            class="text-center py-8 text-gray-500"
          >
            <Icon name="brain" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No classifications yet</p>
            <RouterLink to="/classification" class="text-primary-600 hover:text-primary-700 text-sm">
              Start classifying →
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Training Progress (if any active) -->
    <div
      v-if="activeTrainingJobs.length > 0"
      class="mt-8"
    >
      <div class="medical-card">
        <div class="medical-card-header">
          <h3 class="text-lg font-semibold text-gray-900">
            Active Training Jobs
          </h3>
        </div>
        
        <div class="space-y-4">
          <TrainingProgressCard
            v-for="job in activeTrainingJobs"
            :key="job.id"
            :training-job="job"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useOnline } from '@vueuse/core'
import { formatDistanceToNow } from 'date-fns'

// Import components
import StatCard from '@/components/ui/StatCard.vue'
import ChartCard from '@/components/charts/ChartCard.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'
import RadarChart from '@/components/charts/RadarChart.vue'
import TrainingProgressCard from '@/components/training/TrainingProgressCard.vue'
import Icon from '@/components/ui/Icon.vue'

// Import stores
import { useDatasetStore } from '@/stores/datasets'
import { useModelStore } from '@/stores/models'
import { useClassificationStore } from '@/stores/classification'
import { useTrainingStore } from '@/stores/training'
import { useSystemStore } from '@/stores/system'

// Import types (not needed as we use stores directly)

// Setup
const router = useRouter()

// Stores
const datasetStore = useDatasetStore()
const modelStore = useModelStore()
const classificationStore = useClassificationStore()
const trainingStore = useTrainingStore()
const systemStore = useSystemStore()

// Reactive state
const isLoading = ref(false)
const lastUpdated = ref<Date>(new Date())

// Online status
const isOnline = useOnline()

// Quick actions
const quickActions = [
  {
    name: 'New Dataset',
    route: '/datasets/create',
    icon: 'plus',
    description: 'Upload medical literature dataset'
  },
  {
    name: 'Train Model',
    route: '/models/create',
    icon: 'academic-cap',
    description: 'Create and train AI model'
  },
  {
    name: 'Classify',
    route: '/classification',
    icon: 'document-text',
    description: 'Classify medical articles'
  }
]

// Computed properties
const lastUpdatedFormatted = computed(() => {
  return formatDistanceToNow(lastUpdated.value, { addSuffix: true })
})

const recentDatasets = computed(() => {
  return datasetStore.datasets ? datasetStore.datasets.slice(0, 5) : []
})

const recentModels = computed(() => {
  return modelStore.models ? modelStore.models.slice(0, 5) : []
})

const recentPredictions = computed(() => {
  return classificationStore.predictions ? classificationStore.predictions.slice(0, 5) : []
})

const activeTrainingJobs = computed(() => {
  return trainingStore.activeJobs || []
})

const statistics = computed(() => [
  {
    label: 'Total Datasets',
    value: systemStore.stats.total_datasets,
    icon: 'database',
    color: 'primary',
    trend: (systemStore.stats.total_datasets > 0 ? 'up' : null) as 'up' | 'down' | null
  },
  {
    label: 'Trained Models',
    value: systemStore.stats.total_models,
    icon: 'cpu',
    color: 'medical',
    trend: (systemStore.stats.total_models > 0 ? 'up' : null) as 'up' | 'down' | null
  },
  {
    label: 'Classifications',
    value: systemStore.stats.total_predictions,
    icon: 'brain',
    color: 'success',
    trend: (systemStore.stats.total_predictions > 0 ? 'up' : null) as 'up' | 'down' | null
  },
  {
    label: 'Active Training',
    value: systemStore.stats.active_training_jobs,
    icon: 'clock',
    color: systemStore.stats.active_training_jobs > 0 ? 'warning' : 'info',
    trend: (systemStore.stats.active_training_jobs > 0 ? 'up' : null) as 'up' | 'down' | null
  }
])

const datasetChartData = computed(() => ({
  labels: ['Validated', 'Pending', 'In Review'],
  datasets: [{
    data: [
      systemStore.stats.validated_datasets || 0,
      (systemStore.stats.total_datasets || 0) - (systemStore.stats.validated_datasets || 0),
      0
    ],
    backgroundColor: [
      '#10B981', // success-500
      '#F59E0B', // warning-500
      '#6B7280'  // gray-500
    ]
  }]
}))

const modelPerformanceData = computed(() => {
  const trainedModels = modelStore.models?.filter(m => m.status === 'trained' && m.is_trained) || []
  
  if (trainedModels.length === 0) {
    return {
      labels: ['Accuracy', 'F1 Score', 'Precision', 'Recall'],
      datasets: [{
        label: 'No trained models',
        data: [0, 0, 0, 0],
        backgroundColor: 'rgba(156, 163, 175, 0.2)',
        borderColor: 'rgba(156, 163, 175, 1)',
        pointBackgroundColor: 'rgba(156, 163, 175, 1)'
      }]
    }
  }

  // Calculate averages of all trained models
  const avgAccuracy = trainedModels.reduce((sum, m) => sum + (m.accuracy || 0), 0) / trainedModels.length * 100
  const avgF1Score = trainedModels.reduce((sum, m) => sum + (m.f1_score || 0), 0) / trainedModels.length * 100
  const avgPrecision = trainedModels.reduce((sum, m) => sum + (m.precision || 0), 0) / trainedModels.length * 100
  const avgRecall = trainedModels.reduce((sum, m) => sum + (m.recall || 0), 0) / trainedModels.length * 100

  return {
    labels: ['Accuracy', 'F1 Score', 'Precision', 'Recall'],
    datasets: [{
      label: `Average Performance (${trainedModels.length} models)`,
      data: [avgAccuracy, avgF1Score, avgPrecision, avgRecall],
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      borderColor: 'rgba(59, 130, 246, 1)',
      pointBackgroundColor: 'rgba(59, 130, 246, 1)'
    }]
  }
})

const chartOptions = {
  dataset: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const
      }
    }
  },
  performance: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: {
          stepSize: 20
        }
      }
    },
    plugins: {
      legend: {
        position: 'bottom' as const
      }
    }
  }
}

// Methods
const refreshData = async () => {
  isLoading.value = true
  
  try {
    await Promise.all([
      datasetStore.fetchDatasets(),
      modelStore.fetchModels(),
      classificationStore.fetchPredictions(),
      trainingStore.fetchActiveJobs(),
      systemStore.fetchStats()
    ])
    
    lastUpdated.value = new Date()
  } catch (error) {
    console.error('Failed to refresh data:', error)
  } finally {
    isLoading.value = false
  }
}

const formatRelativeTime = (dateString: string) => {
  return formatDistanceToNow(new Date(dateString), { addSuffix: true })
}

const formatModelType = (type: string): string => {
  const typeMap: Record<string, string> = {
    bert: 'BERT',
    biobert: 'BioBERT',
    clinicalbert: 'ClinicalBERT',
    scibert: 'SciBERT',
    pubmedbert: 'PubMedBERT',
    'gemma2-2b': 'Gemma 2B',
    traditional: 'Traditional ML',
    hybrid: 'Hybrid',
    custom: 'Custom'
  }
  return typeMap[type] || type.toUpperCase()
}

// Lifecycle
onMounted(async () => {
  await refreshData()
  
  // Set up auto-refresh every 30 seconds
  setInterval(() => {
    if (isOnline.value) {
      refreshData()
    }
  }, 30000)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

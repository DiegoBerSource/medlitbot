<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Model Training</h1>
          <p v-if="model" class="text-gray-600 mt-1">{{ model.name }}</p>
        </div>
        <div class="flex space-x-3">
          <button 
            v-if="!currentJob || currentJob.status !== 'running'"
            @click="startTraining"
            :disabled="loading || !model || model.status === 'training'"
            class="btn-primary"
          >
            <Icon name="play" class="w-4 h-4 mr-2" />
            Start Training
          </button>
          <button 
            v-if="currentJob && currentJob.status === 'running'"
            @click="stopTraining"
            :disabled="loading"
            class="btn-secondary"
          >
            <Icon name="stop" class="w-4 h-4 mr-2" />
            Stop Training
          </button>
          <button 
            @click="refreshData"
            :disabled="loading"
            class="btn-outline"
          >
            <Icon name="refresh" class="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="initialLoading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-2 text-gray-600">Loading training data...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
      <div class="flex items-center">
        <Icon name="alert" class="w-5 h-5 text-red-500 mr-2" />
        <h3 class="text-sm font-medium text-red-800">Error</h3>
      </div>
      <p class="mt-1 text-sm text-red-700">{{ error }}</p>
      <button @click="refreshData" class="mt-3 btn-outline text-red-700 border-red-300 hover:bg-red-50">
        Try Again
      </button>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- Current Training Status -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Training Progress Card -->
        <div class="lg:col-span-2">
          <div v-if="currentJob" class="medical-card">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-semibold text-gray-900">Training Progress</h3>
              <span 
                class="status-badge text-sm"
                :class="{
                  'status-badge-success': currentJob.status === 'completed',
                  'status-badge-warning': currentJob.status === 'running',
                  'status-badge-error': currentJob.status === 'failed',
                  'status-badge-info': currentJob.status === 'pending'
                }"
              >
                {{ formatStatus(currentJob.status) }}
              </span>
            </div>

            <!-- Progress Bar -->
            <div class="mb-6">
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>Overall Progress</span>
                <span>{{ Math.round(currentJob.progress_percentage) }}%</span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-bar-fill transition-all duration-300"
                  :style="{ width: currentJob.progress_percentage + '%' }"
                  :class="{
                    'bg-green-500': currentJob.status === 'completed',
                    'bg-blue-500': currentJob.status === 'running',
                    'bg-red-500': currentJob.status === 'failed'
                  }"
                />
              </div>
            </div>

            <!-- Training Metrics -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ currentJob.current_epoch }}</div>
                <div class="text-sm text-gray-500">Current Epoch</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ currentJob.total_epochs }}</div>
                <div class="text-sm text-gray-500">Total Epochs</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">
                  {{ currentJob.current_loss ? currentJob.current_loss.toFixed(4) : '--' }}
                </div>
                <div class="text-sm text-gray-500">Current Loss</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">
                  {{ currentJob.current_accuracy ? (currentJob.current_accuracy * 100).toFixed(1) + '%' : '--' }}
                </div>
                <div class="text-sm text-gray-500">Current Accuracy</div>
              </div>
            </div>

            <!-- Time Information -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span class="text-gray-500">Started:</span>
                <span class="ml-1 font-medium">{{ formatDate(currentJob.started_at) }}</span>
              </div>
              <div v-if="currentJob.completed_at">
                <span class="text-gray-500">Completed:</span>
                <span class="ml-1 font-medium">{{ formatDate(currentJob.completed_at) }}</span>
              </div>
              <div v-else-if="currentJob.status === 'running'">
                <span class="text-gray-500">Estimated:</span>
                <span class="ml-1 font-medium">{{ getEstimatedCompletion() }}</span>
              </div>
              <div v-if="currentJob.started_at && currentJob.status === 'running'">
                <span class="text-gray-500">Duration:</span>
                <span class="ml-1 font-medium">{{ getTrainingDuration() }}</span>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="currentJob.error_message" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <div class="flex items-start">
                <Icon name="alert" class="w-4 h-4 text-red-500 mt-0.5 mr-2 flex-shrink-0" />
                <div>
                  <h4 class="text-sm font-medium text-red-800">Training Error</h4>
                  <p class="mt-1 text-sm text-red-700">{{ currentJob.error_message }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- No Training Job State -->
          <div v-else class="medical-card text-center py-12">
            <Icon name="brain" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900 mb-2">No Active Training</h3>
            <p class="text-gray-600 mb-6">This model is not currently being trained. Start training to monitor progress here.</p>
            <button 
              @click="startTraining"
              :disabled="loading || !model"
              class="btn-primary"
            >
              <Icon name="play" class="w-4 h-4 mr-2" />
              Start Training
            </button>
          </div>
        </div>

        <!-- Model Information -->
        <div class="space-y-6">
          <!-- Model Details -->
          <div v-if="model" class="medical-card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Model Details</h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">Type:</span>
                <span class="font-medium">{{ formatModelType(model.model_type) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Status:</span>
                <span class="font-medium" :class="getStatusColor(model.status)">{{ formatStatus(model.status) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Dataset:</span>
                <span class="font-medium">{{ model.dataset_name || 'Unknown' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Created:</span>
                <span class="font-medium">{{ formatDate(model.created_at) }}</span>
              </div>
              <div v-if="model.accuracy" class="flex justify-between">
                <span class="text-gray-500">Best Accuracy:</span>
                <span class="font-medium text-green-600">{{ (model.accuracy * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <!-- Quick Stats -->
          <div class="medical-card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Training History</h3>
            <div class="space-y-3">
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Total Runs:</span>
                <span class="font-medium">{{ trainingHistory.length }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Successful:</span>
                <span class="font-medium text-green-600">{{ trainingHistory.filter(j => j.status === 'completed').length }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Failed:</span>
                <span class="font-medium text-red-600">{{ trainingHistory.filter(j => j.status === 'failed').length }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Training History -->
      <div v-if="trainingHistory.length > 0" class="medical-card">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-gray-900">Training History</h3>
          <button @click="loadTrainingHistory" :disabled="loading" class="btn-outline text-sm">
            <Icon name="refresh" class="w-4 h-4 mr-1" />
            Refresh
          </button>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Epochs</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Best Accuracy</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Started</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="job in trainingHistory.slice(0, 10)" :key="job.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="status-badge text-xs"
                    :class="{
                      'status-badge-success': job.status === 'completed',
                      'status-badge-warning': job.status === 'running',
                      'status-badge-error': job.status === 'failed',
                      'status-badge-info': job.status === 'pending'
                    }"
                  >
                    {{ formatStatus(job.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        class="bg-blue-600 h-2 rounded-full"
                        :style="{ width: job.progress_percentage + '%' }"
                      ></div>
                    </div>
                    <span class="text-sm text-gray-900">{{ Math.round(job.progress_percentage) }}%</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ job.current_epoch }}/{{ job.total_epochs }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ job.current_accuracy ? (job.current_accuracy * 100).toFixed(1) + '%' : '--' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ getJobDuration(job) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(job.started_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="medical-card text-center py-12">
        <Icon name="chart" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Training History</h3>
        <p class="text-gray-600">Training history will appear here once you start training this model.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
// import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import Icon from '@/components/ui/Icon.vue'
import { useModelStore } from '@/stores/models'
import { useTrainingStore } from '@/stores/training'
import { useWebSocketStore } from '@/stores/websocket'
import type { MLModel, TrainingJob, StartTrainingRequest } from '@/types'

interface Props {
  id: number
}

const props = defineProps<Props>()
const toast = useToast()
const modelStore = useModelStore()
const trainingStore = useTrainingStore()
const websocketStore = useWebSocketStore()

// Reactive state
const model = ref<MLModel | null>(null)
const currentJob = ref<TrainingJob | null>(null)
const trainingHistory = ref<TrainingJob[]>([])
const initialLoading = ref(true)
const loading = ref(false)
const error = ref<string | null>(null)
const refreshInterval = ref<number | null>(null)

// Auto-refresh when training is active
const shouldAutoRefresh = computed(() => {
  return currentJob.value?.status === 'running'
})

// Watch for training status changes to control auto-refresh
watch(shouldAutoRefresh, (newVal) => {
  if (newVal) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

// Lifecycle hooks
onMounted(async () => {
  await loadData()
  
  // Connect to WebSocket for real-time updates
  websocketStore.connect(props.id)
  
  if (shouldAutoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
  websocketStore.disconnect()
})

// Data loading methods
const loadData = async () => {
  initialLoading.value = true
  error.value = null
  
  try {
    await Promise.all([
      loadModel(),
      loadCurrentJob(),
      loadTrainingHistory()
    ])
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load training data'
    console.error('Failed to load data:', err)
  } finally {
    initialLoading.value = false
  }
}

const loadModel = async () => {
  try {
    model.value = await modelStore.fetchModel(props.id)
  } catch (err) {
    console.error('Failed to load model:', err)
    throw new Error('Failed to load model details')
  }
}

const loadCurrentJob = async () => {
  try {
    currentJob.value = await trainingStore.fetchJob(props.id)
  } catch (err) {
    // It's normal for models to not have active training jobs
    currentJob.value = null
    console.log('No active training job found:', err instanceof Error ? err.message : err)
  }
}

const loadTrainingHistory = async () => {
  try {
    await trainingStore.fetchJobs()
    // Filter jobs for this specific model
    trainingHistory.value = trainingStore.jobs.filter(job => job.model === props.id)
      .sort((a, b) => new Date(b.started_at || 0).getTime() - new Date(a.started_at || 0).getTime())
  } catch (err) {
    console.error('Failed to load training history:', err)
    trainingHistory.value = []
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadCurrentJob(),
      loadTrainingHistory()
    ])
  } catch (err) {
    console.error('Failed to refresh training data:', err)
    toast.error('Failed to refresh training data')
  } finally {
    loading.value = false
  }
}

// Auto-refresh functionality
const startAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  
  refreshInterval.value = setInterval(async () => {
    await refreshData()
  }, 5000) // Refresh every 5 seconds
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// Training control methods
const startTraining = async () => {
  if (!model.value) return
  
  loading.value = true
  
  try {
    // Create a basic training request with default parameters
    const trainingParams: StartTrainingRequest = {
      total_epochs: (model.value.parameters?.hyperparameters as any)?.epochs || 3,
      batch_size: (model.value.parameters?.hyperparameters as any)?.batch_size || 16,
      learning_rate: parseFloat((model.value.parameters?.hyperparameters as any)?.learning_rate || '2e-5'),
      validation_split: (model.value.parameters as any)?.validation_split || 0.2
    }
    
    const newJob = await trainingStore.startTraining(props.id, trainingParams)
    currentJob.value = newJob
    
    toast.success('Training started successfully!')
    
    // Start auto-refresh
    startAutoRefresh()
    
  } catch (err) {
    console.error('Failed to start training:', err)
    toast.error('Failed to start training. Please try again.')
  } finally {
    loading.value = false
  }
}

const stopTraining = async () => {
  loading.value = true
  
  try {
    await trainingStore.stopJob(props.id)
    toast.success('Training stopped successfully!')
    
    // Refresh to get updated status
    await refreshData()
    
    // Stop auto-refresh
    stopAutoRefresh()
    
  } catch (err) {
    console.error('Failed to stop training:', err)
    toast.error('Failed to stop training. Please try again.')
  } finally {
    loading.value = false
  }
}

// Formatting utilities
const formatStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    'pending': 'Pending',
    'running': 'Running', 
    'completed': 'Completed',
    'failed': 'Failed',
    'created': 'Created',
    'training': 'Training'
  }
  return statusMap[status] || status.charAt(0).toUpperCase() + status.slice(1)
}

const formatModelType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'bert': 'BERT',
    'biobert': 'BioBERT',
    'clinicalbert': 'ClinicalBERT',
    'scibert': 'SciBERT',
    'traditional': 'Traditional ML',
    'hybrid': 'Hybrid',
    'custom': 'Custom'
  }
  return typeMap[type] || type.toUpperCase()
}

const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    'created': 'text-gray-600',
    'training': 'text-blue-600',
    'completed': 'text-green-600',
    'failed': 'text-red-600'
  }
  return colorMap[status] || 'text-gray-600'
}

const formatDate = (dateString: string | null): string => {
  if (!dateString) return '--'
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return '--'
  }
}

const getTrainingDuration = (): string => {
  if (!currentJob.value?.started_at) return '--'
  
  const start = new Date(currentJob.value.started_at)
  const now = new Date()
  const diff = now.getTime() - start.getTime()
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

const getJobDuration = (job: TrainingJob): string => {
  if (!job.started_at) return '--'
  
  const start = new Date(job.started_at)
  const end = job.completed_at ? new Date(job.completed_at) : new Date()
  const diff = end.getTime() - start.getTime()
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

const getEstimatedCompletion = (): string => {
  if (!currentJob.value?.started_at || !currentJob.value.progress_percentage) return '--'
  
  const start = new Date(currentJob.value.started_at)
  const now = new Date()
  const elapsed = now.getTime() - start.getTime()
  
  if (currentJob.value.progress_percentage > 0) {
    const estimated = (elapsed / currentJob.value.progress_percentage) * 100
    const remaining = estimated - elapsed
    
    if (remaining > 0) {
      const remainingMinutes = Math.floor(remaining / (1000 * 60))
      const remainingHours = Math.floor(remainingMinutes / 60)
      
      if (remainingHours > 0) {
        return `~${remainingHours}h ${remainingMinutes % 60}m`
      }
      return `~${remainingMinutes}m`
    }
  }
  
  return '--'
}
</script>

<style scoped>
.medical-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 p-6;
}

.status-badge {
  @apply px-2 py-1 rounded-full text-xs font-medium;
}

.status-badge-success {
  @apply bg-green-100 text-green-800;
}

.status-badge-warning {
  @apply bg-yellow-100 text-yellow-800;
}

.status-badge-error {
  @apply bg-red-100 text-red-800;
}

.status-badge-info {
  @apply bg-blue-100 text-blue-800;
}

.progress-bar {
  @apply w-full bg-gray-200 rounded-full h-2;
}

.progress-bar-fill {
  @apply h-2 rounded-full;
}

.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors inline-flex items-center;
}

.btn-secondary {
  @apply bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors inline-flex items-center;
}

.btn-outline {
  @apply border border-gray-300 hover:bg-gray-50 disabled:bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors inline-flex items-center;
}
</style>

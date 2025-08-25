<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Loading State -->
    <div v-if="loading && !model" class="bg-white rounded-lg shadow p-6">
      <div class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-500">Loading model details...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-center">
        <Icon name="alert-circle" class="w-5 h-5 text-red-600 mr-2" />
        <h3 class="text-red-800 font-medium">Error loading model</h3>
      </div>
      <p class="text-red-700 mt-1">{{ error }}</p>
      <div class="mt-4 space-x-3">
        <button @click="fetchModel" class="btn-secondary">Try Again</button>
        <RouterLink to="/models" class="btn-outline">Back to Models</RouterLink>
      </div>
    </div>

    <!-- Edit Form -->
    <div v-else-if="model">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Edit Model</h1>
            <p class="mt-2 text-gray-600">{{ model.name }}</p>
            <div class="mt-2 flex items-center space-x-4">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getStatusClass(model.status)">
                <Icon :name="getStatusIcon(model.status)" class="w-3 h-3 mr-1" />
                {{ formatStatus(model.status) }}
              </span>
              <span class="text-sm text-gray-500">{{ formatModelType(model.model_type) }}</span>
            </div>
          </div>
          
          <!-- Delete Button -->
          <button
            @click="showDeleteModal = true"
            class="btn-danger"
            :disabled="loading || model.status === 'training'"
          >
            <Icon name="trash" class="w-4 h-4 mr-2" />
            Delete Model
          </button>
        </div>
      </div>

      <!-- Training Status Warning -->
      <div v-if="model.status === 'training'" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div class="flex items-center">
          <Icon name="alert-triangle" class="w-5 h-5 text-yellow-600 mr-2" />
          <p class="text-yellow-800">
            <strong>Model is currently training.</strong> 
            Some settings cannot be modified while training is in progress.
          </p>
        </div>
      </div>

      <!-- Main Form -->
      <form @submit.prevent="handleSubmit" class="space-y-8">
        <!-- Basic Information -->
        <div class="medical-card">
          <div class="medical-card-header">
            <h2 class="text-xl font-semibold text-gray-900">Basic Information</h2>
            <p class="text-sm text-gray-600">Update model name and description</p>
          </div>

          <div class="space-y-6">
            <!-- Model Name -->
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
                Model Name *
              </label>
              <input
                id="name"
                v-model="form.name"
                type="text"
                required
                class="input-field"
                :class="{ 'border-red-500': errors.name }"
                :disabled="loading"
              />
              <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
            </div>

            <!-- Description -->
            <div>
              <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                id="description"
                v-model="form.description"
                rows="3"
                class="input-field"
                :disabled="loading"
                placeholder="Describe the model's purpose and expected use cases..."
              />
            </div>
          </div>
        </div>

        <!-- Model Information (Read-only) -->
        <div class="medical-card">
          <div class="medical-card-header">
            <h2 class="text-xl font-semibold text-gray-900">Model Configuration</h2>
            <p class="text-sm text-gray-600">Current model settings (read-only)</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Model Type</label>
              <div class="p-3 bg-gray-50 rounded-md border">
                <span class="font-medium">{{ formatModelType(model.model_type) }}</span>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Dataset</label>
              <div class="p-3 bg-gray-50 rounded-md border">
                <span class="font-medium">{{ model.dataset_name || `Dataset ${model.dataset}` }}</span>
              </div>
            </div>

            <div v-if="model.created_at">
              <label class="block text-sm font-medium text-gray-700 mb-2">Created</label>
              <div class="p-3 bg-gray-50 rounded-md border">
                <span>{{ formatDate(model.created_at) }}</span>
              </div>
            </div>

            <div v-if="model.training_completed_at">
              <label class="block text-sm font-medium text-gray-700 mb-2">Training Completed</label>
              <div class="p-3 bg-gray-50 rounded-md border">
                <span>{{ formatDate(model.training_completed_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Metrics (if trained) -->
        <div v-if="model.is_trained && hasMetrics" class="medical-card">
          <div class="medical-card-header">
            <h2 class="text-xl font-semibold text-gray-900">Performance Metrics</h2>
            <p class="text-sm text-gray-600">Current model performance</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div v-if="model.accuracy">
              <label class="block text-sm font-medium text-gray-700 mb-2">Accuracy</label>
              <div class="p-3 bg-green-50 rounded-md border border-green-200">
                <span class="text-lg font-bold text-green-800">{{ (model.accuracy * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <div v-if="model.f1_score">
              <label class="block text-sm font-medium text-gray-700 mb-2">F1 Score</label>
              <div class="p-3 bg-blue-50 rounded-md border border-blue-200">
                <span class="text-lg font-bold text-blue-800">{{ (model.f1_score * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <div v-if="model.precision">
              <label class="block text-sm font-medium text-gray-700 mb-2">Precision</label>
              <div class="p-3 bg-purple-50 rounded-md border border-purple-200">
                <span class="text-lg font-bold text-purple-800">{{ (model.precision * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <div v-if="model.recall">
              <label class="block text-sm font-medium text-gray-700 mb-2">Recall</label>
              <div class="p-3 bg-orange-50 rounded-md border border-orange-200">
                <span class="text-lg font-bold text-orange-800">{{ (model.recall * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-between items-center pt-6 border-t border-gray-200">
          <RouterLink to="/models" class="btn-outline">
            <Icon name="arrow-left" class="w-4 h-4 mr-2" />
            Back to Models
          </RouterLink>

          <div class="flex space-x-3">
            <RouterLink :to="`/models/${model.id}`" class="btn-secondary">
              <Icon name="eye" class="w-4 h-4 mr-2" />
              View Details
            </RouterLink>
            
            <button
              type="submit"
              class="btn-primary"
              :disabled="loading || !hasChanges"
            >
              <Icon v-if="loading" name="clock" class="w-4 h-4 mr-2 animate-spin" />
              <Icon v-else name="save" class="w-4 h-4 mr-2" />
              {{ loading ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="p-6">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
              <Icon name="alert-triangle" class="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h3 class="text-lg font-medium text-gray-900">Delete Model</h3>
              <p class="text-sm text-gray-500">This action cannot be undone</p>
            </div>
          </div>

          <div class="mb-6">
            <p class="text-gray-700">
              Are you sure you want to delete <strong>"{{ model?.name }}"</strong>?
            </p>
            <div class="mt-3 p-3 bg-red-50 rounded-md border border-red-200">
              <p class="text-sm text-red-800">
                <Icon name="alert-circle" class="w-4 h-4 inline mr-1" />
                This will permanently delete:
              </p>
              <ul class="text-sm text-red-700 mt-2 ml-5 list-disc">
                <li>The model configuration</li>
                <li>All training data and checkpoints</li>
                <li>Performance metrics and history</li>
                <li v-if="model?.status === 'training'">The current training job</li>
              </ul>
            </div>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              @click="showDeleteModal = false"
              class="btn-outline"
              :disabled="deleting"
            >
              Cancel
            </button>
            <button
              @click="handleDelete"
              class="btn-danger"
              :disabled="deleting"
            >
              <Icon v-if="deleting" name="clock" class="w-4 h-4 mr-2 animate-spin" />
              <Icon v-else name="trash" class="w-4 h-4 mr-2" />
              {{ deleting ? 'Deleting...' : 'Delete Model' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import Icon from '@/components/ui/Icon.vue'
import { useModelStore } from '@/stores/models'
import type { MLModel, ModelType, ModelStatus } from '@/types'

// Props
interface Props {
  id: number
}
const props = defineProps<Props>()

// Composables
const router = useRouter()
const toast = useToast()
const modelStore = useModelStore()

// Reactive state
const model = ref<MLModel | null>(null)
const loading = ref(false)
const deleting = ref(false)
const error = ref<string | null>(null)
const errors = ref<Record<string, string>>({})
const showDeleteModal = ref(false)

// Form data
const form = ref({
  name: '',
  description: ''
})

// Computed
const hasChanges = computed(() => {
  if (!model.value) return false
  return form.value.name !== model.value.name || 
         form.value.description !== model.value.description
})

const hasMetrics = computed(() => {
  if (!model.value) return false
  return model.value.accuracy || model.value.f1_score || model.value.precision || model.value.recall
})

// Methods
const fetchModel = async () => {
  loading.value = true
  error.value = null
  try {
    model.value = await modelStore.fetchModel(props.id)
    
    // Populate form with current values
    if (model.value) {
      form.value.name = model.value.name
      form.value.description = model.value.description
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load model'
    console.error('Failed to fetch model:', err)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!model.value || !hasChanges.value) return

  loading.value = true
  errors.value = {}
  
  try {
    // Validate
    if (!form.value.name.trim()) {
      errors.value.name = 'Model name is required'
      return
    }

    // Update model
    await modelStore.updateModel(props.id, {
      name: form.value.name.trim(),
      description: form.value.description.trim()
    })

    toast.success('Model updated successfully!')
    
    // Refresh model data
    await fetchModel()
    
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to update model'
    error.value = errorMessage
    toast.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const handleDelete = async () => {
  if (!model.value) return

  deleting.value = true
  
  try {
    await modelStore.deleteModel(props.id)
    toast.success(`Model "${model.value.name}" deleted successfully!`)
    router.push('/models')
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to delete model'
    toast.error(errorMessage)
    console.error('Failed to delete model:', err)
  } finally {
    deleting.value = false
    showDeleteModal.value = false
  }
}

// Helper functions
const formatModelType = (type: ModelType): string => {
  const typeMap: Record<ModelType, string> = {
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

const formatStatus = (status: ModelStatus): string => {
  const statusMap: Record<ModelStatus, string> = {
    created: 'Created',
    training: 'Training',
    trained: 'Trained',
    failed: 'Failed',
    optimizing: 'Optimizing'
  }
  return statusMap[status] || status
}

const getStatusClass = (status: ModelStatus): string => {
  const classMap: Record<ModelStatus, string> = {
    created: 'bg-gray-100 text-gray-800',
    training: 'bg-yellow-100 text-yellow-800',
    trained: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    optimizing: 'bg-blue-100 text-blue-800'
  }
  return classMap[status] || 'bg-gray-100 text-gray-800'
}

const getStatusIcon = (status: ModelStatus): string => {
  const iconMap: Record<ModelStatus, string> = {
    created: 'plus-circle',
    training: 'clock',
    trained: 'check-circle',
    failed: 'x-circle',
    optimizing: 'zap'
  }
  return iconMap[status] || 'circle'
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  fetchModel()
})
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Create AI Model</h1>
      <p class="mt-2 text-gray-600">Configure and train a new medical literature classification model</p>
    </div>

    <!-- Main Form -->
    <form @submit.prevent="handleSubmit" class="space-y-8">
      <!-- Basic Model Information -->
      <div class="medical-card">
        <div class="medical-card-header">
          <h2 class="text-xl font-semibold text-gray-900">Basic Configuration</h2>
          <p class="text-sm text-gray-600">Define the core model parameters</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
              placeholder="e.g., BioBERT Cardiology Classifier"
              :class="{ 'border-red-500': errors.name }"
            />
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>

          <!-- Model Type -->
          <div>
            <label for="model_type" class="block text-sm font-medium text-gray-700 mb-2">
              Model Type *
            </label>
            <select
              id="model_type"
              v-model="form.model_type"
              required
              class="input-field"
              :class="{ 'border-red-500': errors.model_type }"
            >
              <option value="">Select model type</option>
              <option value="bert">BERT - Transformer-based model</option>
              <option value="gemma2-2b">Google Gemma 2B - Advanced generative model</option>
              <option value="traditional">Traditional ML - Classical algorithms</option>
              <option value="hybrid">Hybrid - Combined approach</option>
              <option value="custom">Custom - User-defined architecture</option>
            </select>
            <p v-if="errors.model_type" class="mt-1 text-sm text-red-600">{{ errors.model_type }}</p>
          </div>

          <!-- Base Model (when BERT is selected) -->
          <div v-if="form.model_type === 'bert'">
            <label for="base_model" class="block text-sm font-medium text-gray-700 mb-2">
              Base Model *
            </label>
            <select
              id="base_model"
              v-model="form.parameters.base_model"
              required
              class="input-field"
              :class="{ 'border-red-500': errors.base_model }"
            >
              <option value="">Select base model</option>
              <option
                v-for="model in baseModels"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }} - {{ model.description }}
              </option>
            </select>
            <p v-if="errors.base_model" class="mt-1 text-sm text-red-600">{{ errors.base_model }}</p>
          </div>
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
            placeholder="Describe the model's purpose, training objectives, and expected use cases..."
          />
        </div>
      </div>

      <!-- Dataset Selection -->
      <div class="medical-card">
        <div class="medical-card-header">
          <h2 class="text-xl font-semibold text-gray-900">Training Dataset</h2>
          <p class="text-sm text-gray-600">Select the dataset for training your model</p>
        </div>

        <div class="space-y-4">
          <!-- Dataset Selection -->
          <div>
            <label for="dataset" class="block text-sm font-medium text-gray-700 mb-2">
              Training Dataset *
            </label>
            <select
              id="dataset"
              v-model="form.dataset_id"
              required
              class="input-field"
              :class="{ 'border-red-500': errors.dataset_id }"
              @change="onDatasetChange"
            >
              <option value="0">Select training dataset</option>
              <option
                v-for="dataset in availableDatasets"
                :key="dataset.id"
                :value="dataset.id"
              >
                {{ dataset.name }} ({{ dataset.total_samples }} samples)
              </option>
            </select>
            <p v-if="errors.dataset_id" class="mt-1 text-sm text-red-600">{{ errors.dataset_id }}</p>
          </div>

          <!-- Dataset Info -->
          <div v-if="selectedDataset" class="p-4 bg-gray-50 rounded-lg border">
            <h4 class="font-medium text-gray-900 mb-2">Dataset Information</h4>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-600">Samples:</span>
                <span class="ml-2 font-medium">{{ selectedDataset.total_samples }}</span>
              </div>
              <div>
                <span class="text-gray-600">Status:</span>
                <span class="ml-2 font-medium text-green-600" v-if="selectedDataset.is_validated">Validated</span>
                <span class="ml-2 font-medium text-yellow-600" v-else>Pending Validation</span>
              </div>
              <div>
                <span class="text-gray-600">Domains:</span>
                <span class="ml-2 font-medium">{{ selectedDataset.medical_domains?.length || 0 }}</span>
              </div>
              <div>
                <span class="text-gray-600">Created:</span>
                <span class="ml-2 font-medium">{{ formatDate(selectedDataset.uploaded_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Data Split Configuration -->
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label for="train_split" class="block text-sm font-medium text-gray-700 mb-2">
                Training Split (%)
              </label>
              <input
                id="train_split"
                v-model.number="form.parameters.training_split"
                type="number"
                min="50"
                max="90"
                class="input-field"
              />
            </div>
            <div>
              <label for="val_split" class="block text-sm font-medium text-gray-700 mb-2">
                Validation Split (%)
              </label>
              <input
                id="val_split"
                v-model.number="form.parameters.validation_split"
                type="number"
                min="5"
                max="30"
                class="input-field"
                readonly
              />
            </div>
            <div>
              <label for="test_split" class="block text-sm font-medium text-gray-700 mb-2">
                Test Split (%)
              </label>
              <input
                id="test_split"
                v-model.number="form.parameters.test_split"
                type="number"
                min="5"
                max="30"
                class="input-field"
                readonly
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Training Configuration -->
      <div class="medical-card">
        <div class="medical-card-header">
          <h2 class="text-xl font-semibold text-gray-900">Training Parameters</h2>
          <p class="text-sm text-gray-600">Configure hyperparameters and training settings</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Learning Rate -->
          <div>
            <label for="learning_rate" class="block text-sm font-medium text-gray-700 mb-2">
              Learning Rate
            </label>
            <select
              id="learning_rate"
              v-model="form.parameters.hyperparameters.learning_rate"
              class="input-field"
            >
              <option value="1e-5">1e-5 (Conservative)</option>
              <option value="2e-5" selected>2e-5 (Recommended)</option>
              <option value="3e-5">3e-5 (Aggressive)</option>
              <option value="5e-5">5e-5 (Very Aggressive)</option>
            </select>
          </div>

          <!-- Batch Size -->
          <div>
            <label for="batch_size" class="block text-sm font-medium text-gray-700 mb-2">
              Batch Size
            </label>
            <select
              id="batch_size"
              v-model="form.parameters.hyperparameters.batch_size"
              class="input-field"
            >
              <option value="8">8 (Low Memory)</option>
              <option value="16" selected>16 (Recommended)</option>
              <option value="32">32 (High Memory)</option>
              <option value="64">64 (Very High Memory)</option>
            </select>
          </div>

          <!-- Epochs -->
          <div>
            <label for="epochs" class="block text-sm font-medium text-gray-700 mb-2">
              Training Epochs
            </label>
            <input
              id="epochs"
              v-model.number="form.parameters.hyperparameters.epochs"
              type="number"
              min="1"
              max="50"
              class="input-field"
            />
          </div>

          <!-- Max Sequence Length -->
          <div>
            <label for="max_length" class="block text-sm font-medium text-gray-700 mb-2">
              Max Sequence Length
            </label>
            <select
              id="max_length"
              v-model="form.parameters.hyperparameters.max_sequence_length"
              class="input-field"
            >
              <option value="128">128 tokens (Fast)</option>
              <option value="256">256 tokens (Balanced)</option>
              <option value="512" selected>512 tokens (Recommended)</option>
              <option value="1024">1024 tokens (Slow)</option>
            </select>
          </div>
        </div>

        <!-- Advanced Options -->
        <div class="mt-6">
          <h4 class="text-sm font-medium text-gray-900 mb-3">Advanced Options</h4>
          <div class="space-y-3">
            <label class="flex items-center">
              <input
                v-model="form.parameters.use_early_stopping"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">
                Enable early stopping (stop training when validation loss plateaus)
              </span>
            </label>
            <label class="flex items-center">
              <input
                v-model="form.parameters.use_class_weights"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">
                Use class weights to handle imbalanced datasets
              </span>
            </label>
            <label class="flex items-center">
              <input
                v-model="form.parameters.enable_gradient_checkpointing"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">
                Enable gradient checkpointing (reduces memory usage)
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- Hyperparameter Optimization -->
      <div class="medical-card">
        <div class="medical-card-header">
          <h2 class="text-xl font-semibold text-gray-900">Hyperparameter Optimization</h2>
          <p class="text-sm text-gray-600">Automatically find the best hyperparameters</p>
        </div>

        <div class="space-y-4">
          <label class="flex items-start">
            <input
              v-model="form.parameters.enable_hyperparameter_optimization"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mt-1"
            />
            <div class="ml-2">
              <span class="text-sm font-medium text-gray-700">
                Enable Hyperparameter Optimization
              </span>
              <p class="text-xs text-gray-500 mt-1">
                Use Optuna to automatically search for optimal hyperparameters. This will override manual settings above.
              </p>
            </div>
          </label>

          <div v-if="form.parameters.enable_hyperparameter_optimization" class="ml-6 space-y-4 border-l-2 border-blue-200 pl-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="optimization_trials" class="block text-sm font-medium text-gray-700 mb-2">
                  Number of Trials
                </label>
                <input
                  id="optimization_trials"
                  v-model.number="form.parameters.optimization_params.n_trials"
                  type="number"
                  min="5"
                  max="100"
                  class="input-field"
                />
              </div>
              <div>
                <label for="optimization_timeout" class="block text-sm font-medium text-gray-700 mb-2">
                  Timeout (minutes)
                </label>
                <input
                  id="optimization_timeout"
                  v-model.number="form.parameters.optimization_params.timeout"
                  type="number"
                  min="30"
                  max="1440"
                  class="input-field"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-between pt-6 border-t border-gray-200">
        <button
          type="button"
          @click="$router.push('/models')"
          class="btn-secondary"
        >
          Cancel
        </button>

        <div class="flex space-x-3">
          <button
            type="button"
            @click="saveDraft"
            class="btn-outline"
            :disabled="loading || !form.name"
          >
            Save Draft
          </button>
          <button
            type="submit"
            class="btn-primary"
            :disabled="loading || !isFormValid"
          >
            <Icon v-if="loading" name="clock" class="w-4 h-4 mr-2 animate-spin" />
            <Icon v-else name="brain" class="w-4 h-4 mr-2" />
            {{ loading ? 'Creating...' : 'Create Model' }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import Icon from '@/components/ui/Icon.vue'
import { useModelStore } from '@/stores/models'
import { useDatasetStore } from '@/stores/datasets'
import type { Dataset, ModelType } from '@/types'

// Composables
const router = useRouter()
const route = useRoute()
const toast = useToast()
const modelStore = useModelStore()
const datasetStore = useDatasetStore()

// Reactive state
const loading = ref(false)
const availableDatasets = ref<Dataset[]>([])
const selectedDataset = ref<Dataset | null>(null)

// Base models configuration
const baseModels = ref([
  {
    id: 'biobert',
    name: 'BioBERT',
    description: 'Biomedical domain pre-trained BERT'
  },
  {
    id: 'clinicalbert',
    name: 'ClinicalBERT',
    description: 'Clinical notes pre-trained BERT'
  },
  {
    id: 'scibert',
    name: 'SciBERT',
    description: 'Scientific literature pre-trained BERT'
  },
  {
    id: 'bert-base',
    name: 'BERT Base',
    description: 'Standard BERT base model'
  }
])

// Form data with non-null parameters
const form = ref({
  name: '',
  description: '',
  model_type: 'bert' as ModelType,
  dataset_id: 0,
  parameters: {
    base_model: 'biobert',
    training_split: 70,
    validation_split: 20,
    test_split: 10,
    hyperparameters: {
      learning_rate: '2e-5',
      batch_size: 16,
      epochs: 3,
      max_sequence_length: 512
    },
    use_early_stopping: true,
    use_class_weights: false,
    enable_gradient_checkpointing: false,
    enable_hyperparameter_optimization: false,
    optimization_params: {
      n_trials: 20,
      timeout: 120
    }
  }
})

// Clean parameters based on model type before submission
const cleanParametersForModelType = (modelType: string, params: any) => {
  const cleanParams = { ...params }
  
  // Remove BERT-specific parameters for non-BERT models
  if (modelType !== 'bert') {
    delete cleanParams.base_model
  }
  
  // For Gemma models, we might want to keep only relevant parameters
  if (modelType === 'gemma2-2b') {
    // Keep only parameters relevant to Gemma models
    return {
      training_split: cleanParams.training_split,
      validation_split: cleanParams.validation_split, 
      test_split: cleanParams.test_split,
      hyperparameters: {
        max_sequence_length: cleanParams.hyperparameters?.max_sequence_length || 512
      }
    }
  }
  
  return cleanParams
}

// Form validation
const errors = ref<Record<string, string>>({})

// Computed
const isFormValid = computed(() => {
  return (
    form.value.name.trim() &&
    form.value.model_type &&
    form.value.dataset_id > 0 &&
    !Object.keys(errors.value).length
  )
})

// Watchers
watch(() => form.value.parameters?.training_split, (newVal) => {
  if (newVal && form.value.parameters) {
    form.value.parameters.validation_split = Math.round((100 - newVal) / 2)
    form.value.parameters.test_split = 100 - newVal - form.value.parameters.validation_split
  }
})

watch(() => form.value.dataset_id, (newId) => {
  if (newId) {
    selectedDataset.value = availableDatasets.value.find(d => d.id === newId) || null
  } else {
    selectedDataset.value = null
  }
})

// Methods
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.name.trim()) {
    errors.value.name = 'Model name is required'
  } else if (form.value.name.length < 3) {
    errors.value.name = 'Model name must be at least 3 characters'
  }
  
  if (!form.value.model_type) {
    errors.value.model_type = 'Model type is required'
  }
  
  if (form.value.model_type === 'bert' && (!form.value.parameters?.base_model)) {
    errors.value.base_model = 'Base model is required for BERT type'
  }
  
  if (!form.value.dataset_id || form.value.dataset_id === 0) {
    errors.value.dataset_id = 'Training dataset is required'
  } else if (selectedDataset.value && !selectedDataset.value.is_validated) {
    toast.warning('Warning: Selected dataset is not validated. This may affect training quality.')
  }
  
  if (form.value.parameters && 
      form.value.parameters.training_split + form.value.parameters.validation_split + form.value.parameters.test_split !== 100) {
    errors.value.splits = 'Data splits must sum to 100%'
  }
}

const onDatasetChange = () => {
  validateForm()
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString()
}

const handleSubmit = async () => {
  validateForm()
  
  if (!isFormValid.value) {
    toast.error('Please fix the form errors before submitting')
    return
  }
  
  loading.value = true
  
  try {
    // Clean parameters based on model type before submission
    const cleanedFormData = {
      ...form.value,
      parameters: cleanParametersForModelType(form.value.model_type, form.value.parameters)
    }
    
    const newModel = await modelStore.createModel(cleanedFormData)
    toast.success('Model created successfully!')
    
    // Ask if user wants to start training immediately
    const startTraining = confirm('Model created successfully! Would you like to start training now?')
    if (startTraining) {
      router.push(`/models/${newModel.id}/training`)
    } else {
      router.push(`/models/${newModel.id}`)
    }
    
  } catch (error) {
    console.error('Failed to create model:', error)
    toast.error('Failed to create model. Please try again.')
  } finally {
    loading.value = false
  }
}

const saveDraft = async () => {
  // Implement draft saving functionality
  toast.info('Draft saving functionality will be implemented soon')
}

// Lifecycle
onMounted(async () => {
  try {
    await datasetStore.fetchDatasets()
    availableDatasets.value = datasetStore.datasets.filter(d => d.total_samples > 0)
    
    // Check for dataset query parameter and preselect it
    const datasetParam = route.query.dataset
    if (datasetParam) {
      const datasetId = parseInt(datasetParam as string)
      if (datasetId && availableDatasets.value.some(d => d.id === datasetId)) {
        form.value.dataset_id = datasetId
        toast.success(`Dataset preselected from URL`, { timeout: 2000 })
      }
    }
  } catch (error) {
    console.error('Failed to load datasets:', error)
    toast.error('Failed to load datasets')
  }
})
</script>

<style scoped>
.input-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.medical-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 p-6;
}

.medical-card-header {
  @apply mb-6 pb-4 border-b border-gray-200;
}

.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors inline-flex items-center;
}

.btn-secondary {
  @apply bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors;
}

.btn-outline {
  @apply border border-gray-300 hover:bg-gray-50 text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors;
}
</style>

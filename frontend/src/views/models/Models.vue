<template>
  <div class="p-6">
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">ML Models</h1>
        <p class="text-gray-600">Train and manage your AI models</p>
      </div>
      <RouterLink to="/models/create" class="btn-primary">
        Create Model
      </RouterLink>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-6">
      <div class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-500">Loading models...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
      <div class="flex items-center">
        <Icon name="alert-circle" class="w-5 h-5 text-red-600 mr-2" />
        <h3 class="text-red-800 font-medium">Error loading models</h3>
      </div>
      <p class="text-red-700 mt-1">{{ error }}</p>
      <button @click="fetchModels" class="mt-3 btn-secondary">
        Try Again
      </button>
    </div>

    <!-- Models List -->
    <div v-else-if="models.length > 0" class="space-y-6">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <Icon name="cpu" class="w-8 h-8 text-blue-600 mr-3" />
            <div>
              <p class="text-sm text-gray-500">Total Models</p>
              <p class="text-2xl font-bold text-gray-900">{{ modelCount }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <Icon name="check-circle" class="w-8 h-8 text-green-600 mr-3" />
            <div>
              <p class="text-sm text-gray-500">Trained</p>
              <p class="text-2xl font-bold text-gray-900">{{ modelsByStatus.trained.length }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <Icon name="clock" class="w-8 h-8 text-yellow-600 mr-3" />
            <div>
              <p class="text-sm text-gray-500">Training</p>
              <p class="text-2xl font-bold text-gray-900">{{ modelsByStatus.training.length }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <Icon name="x-circle" class="w-8 h-8 text-red-600 mr-3" />
            <div>
              <p class="text-sm text-gray-500">Failed</p>
              <p class="text-2xl font-bold text-gray-900">{{ modelsByStatus.failed.length }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Models Table -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Your Models</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Model
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Dataset
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Performance
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="model in models" :key="model.id" 
                  class="hover:bg-gray-50 cursor-pointer"
                  @click="router.push(['training', 'optimizing'].includes(model.status) ? `/models/${model.id}/training` : `/models/${model.id}`)">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-1">
                      <div class="text-sm font-medium text-gray-900">{{ model.name }}</div>
                      <div class="text-sm text-gray-500">{{ model.description }}</div>
                    </div>
                    <div v-if="['training', 'optimizing'].includes(model.status)" 
                         class="ml-2 text-xs text-blue-600 font-medium">
                      Click to monitor →
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getModelTypeClass(model.model_type)">
                    {{ formatModelType(model.model_type) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ model.dataset_name || `Dataset ${model.dataset}` }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getStatusClass(model.status)">
                    <Icon :name="getStatusIcon(model.status)" class="w-3 h-3 mr-1" />
                    {{ formatStatus(model.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div v-if="model.is_trained && model.accuracy">
                    <div>Accuracy: {{ (model.accuracy * 100).toFixed(1) }}%</div>
                    <div v-if="model.f1_score" class="text-xs text-gray-500">
                      F1: {{ (model.f1_score * 100).toFixed(1) }}%
                    </div>
                  </div>
                  <span v-else class="text-gray-400">-</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(model.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2" @click.stop>
                  <!-- Conditional routing based on training status -->
                  <RouterLink 
                    :to="['training', 'optimizing'].includes(model.status) ? `/models/${model.id}/training` : `/models/${model.id}`" 
                    class="text-blue-600 hover:text-blue-900">
                    {{ ['training', 'optimizing'].includes(model.status) ? 'Monitor' : 'View' }}
                  </RouterLink>
                  <button v-if="model.status === 'created'" 
                          @click="handleStartTraining(model.id)"
                          class="text-green-600 hover:text-green-900">
                    Train
                  </button>
                  <RouterLink :to="`/models/${model.id}/edit`" class="text-gray-600 hover:text-gray-900">
                    Edit
                  </RouterLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-lg shadow p-6">
      <div class="text-center py-12">
        <Icon name="cpu" class="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No models yet</h3>
        <p class="text-gray-500 mb-4">Create your first BioBERT, ClinicalBERT, Gemma or other medical AI model</p>
        <RouterLink to="/models/create" class="btn-primary">
          Create Your First Model
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useModelStore } from '@/stores/models'
import { storeToRefs } from 'pinia'
import Icon from '@/components/ui/Icon.vue'
import type { ModelType, ModelStatus } from '@/types'

const router = useRouter()

const modelStore = useModelStore()
const { models, loading, error, modelCount, modelsByStatus } = storeToRefs(modelStore)
const { fetchModels, startTraining } = modelStore

// Fetch models on component mount
onMounted(() => {
  fetchModels()
})

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

const getModelTypeClass = (type: ModelType): string => {
  const classMap: Record<ModelType, string> = {
    bert: 'bg-blue-100 text-blue-800',
    biobert: 'bg-green-100 text-green-800',
    clinicalbert: 'bg-purple-100 text-purple-800',
    scibert: 'bg-indigo-100 text-indigo-800',
    pubmedbert: 'bg-teal-100 text-teal-800',
    'gemma2-2b': 'bg-red-100 text-red-800',
    traditional: 'bg-gray-100 text-gray-800',
    hybrid: 'bg-orange-100 text-orange-800',
    custom: 'bg-pink-100 text-pink-800'
  }
  return classMap[type] || 'bg-gray-100 text-gray-800'
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
  return new Date(dateString).toLocaleDateString()
}

const handleStartTraining = async (modelId: number) => {
  try {
    // Use default training parameters
    await startTraining(modelId, {
      total_epochs: 10,
      learning_rate: 2e-5,
      batch_size: 16,
      validation_split: 0.2
    })
  } catch (error) {
    console.error('Failed to start training:', error)
  }
}
</script>

<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Medical Literature Classification</h1>
      <p class="text-gray-600">Classify articles into medical domains using trained AI models</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Classification Form -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-medium text-gray-900">Single Article Classification</h2>
            <div class="flex space-x-2">
              <RouterLink to="/classification/batch" class="btn-secondary text-sm">
                Batch Classification
              </RouterLink>
              <RouterLink to="/classification/history" class="btn-secondary text-sm">
                View History
              </RouterLink>
            </div>
          </div>

          <form @submit.prevent="handleClassify" class="space-y-6">
            <!-- Model Selection -->
            <div>
              <label for="model-select" class="block text-sm font-medium text-gray-700 mb-2">
                Select Model
              </label>
              <select 
                id="model-select"
                v-model="form.selectedModelId"
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                :disabled="modelsLoading"
              >
                <option value="">Best Available Model (Auto-select)</option>
                <option 
                  v-for="model in trainedModels" 
                  :key="model.id" 
                  :value="model.id"
                >
                  {{ model.name }} ({{ formatModelType(model.model_type) }}) - {{ model.accuracy ? (model.accuracy * 100).toFixed(1) : '0.0' }}% accuracy
                </option>
              </select>
            </div>

            <!-- Article Title -->
            <div>
              <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
                Article Title *
              </label>
              <input
                id="title"
                v-model="form.title"
                type="text"
                required
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="Enter the article title..."
              />
            </div>

            <!-- Article Abstract -->
            <div>
              <label for="abstract" class="block text-sm font-medium text-gray-700 mb-2">
                Article Abstract *
              </label>
              <textarea
                id="abstract"
                v-model="form.abstract"
                required
                rows="8"
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="Enter the article abstract..."
              ></textarea>
            </div>

            <!-- Threshold -->
            <div>
              <label for="threshold" class="block text-sm font-medium text-gray-700 mb-2">
                Classification Threshold: {{ form.threshold }}
              </label>
              <input
                id="threshold"
                v-model.number="form.threshold"
                type="range"
                min="0.1"
                max="0.9"
                step="0.1"
                class="block w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>Less Confident (0.1)</span>
                <span>More Confident (0.9)</span>
              </div>
            </div>

            <!-- Submit Button -->
            <div>
              <button
                type="submit"
                :disabled="loading || !form.title.trim() || !form.abstract.trim()"
                class="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Icon 
                  v-if="loading" 
                  name="loader" 
                  class="animate-spin w-4 h-4 mr-2"
                />
                {{ loading ? 'Classifying...' : 'Classify Article' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Results & Info Panel -->
      <div class="space-y-6">
        <!-- Current Result -->
        <div v-if="currentResult" class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Classification Result</h3>
          
          <div class="space-y-4">
            <!-- Model Used -->
            <div>
              <h4 class="text-sm font-medium text-gray-700">Model Used</h4>
              <p class="text-sm text-gray-900">{{ (currentResult as any).model_used || 'Unknown Model' }}</p>
            </div>

            <!-- Predicted Domains -->
            <div v-if="currentResult.predicted_domains && currentResult.predicted_domains.length > 0">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Predicted Medical Domains</h4>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="domain in currentResult.predicted_domains" 
                  :key="domain"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                >
                  {{ formatDomain(domain) }}
                </span>
              </div>
            </div>

            <!-- Confidence Scores -->
            <div v-if="currentResult.confidence_scores">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Confidence Scores</h4>
              <div class="space-y-2">
                <div 
                  v-for="[domain, score] in sortedConfidenceScores" 
                  :key="domain"
                  class="flex items-center justify-between text-xs"
                >
                  <span class="text-gray-700">{{ formatDomain(domain) }}</span>
                  <div class="flex items-center space-x-2">
                    <div class="w-20 bg-gray-200 rounded-full h-1.5">
                      <div 
                        class="h-1.5 rounded-full"
                        :class="score >= form.threshold ? 'bg-green-500' : 'bg-gray-400'"
                        :style="`width: ${score * 100}%`"
                      ></div>
                    </div>
                    <span class="font-mono text-gray-900 w-10 text-right">{{ (score * 100).toFixed(0) }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Processing Time -->
            <div v-if="currentResult.inference_time_ms">
              <h4 class="text-sm font-medium text-gray-700">Processing Time</h4>
              <p class="text-sm text-gray-900">{{ currentResult.inference_time_ms }}ms</p>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="flex items-center">
            <Icon name="alert-circle" class="w-5 h-5 text-red-600 mr-2" />
            <h3 class="text-red-800 font-medium">Classification Error</h3>
          </div>
          <p class="text-red-700 mt-1 text-sm">{{ error }}</p>
          <button 
            @click="clearError" 
            class="mt-3 text-red-600 hover:text-red-800 text-sm underline"
          >
            Dismiss
          </button>
        </div>

        <!-- Available Models Info -->
        <div class="bg-blue-50 rounded-lg p-4">
          <h3 class="text-lg font-medium text-blue-900 mb-3">Available Models</h3>
          <div v-if="modelsLoading" class="text-center py-4">
            <Icon name="loader" class="animate-spin w-6 h-6 mx-auto mb-2 text-blue-600" />
            <p class="text-blue-700">Loading models...</p>
          </div>
          <div v-else-if="trainedModels.length === 0" class="text-center py-4">
            <Icon name="alert-triangle" class="w-6 h-6 mx-auto mb-2 text-yellow-600" />
            <p class="text-gray-700">No trained models available</p>
            <RouterLink to="/models/create" class="text-blue-600 hover:text-blue-800 text-sm">
              Create a model
            </RouterLink>
          </div>
          <div v-else class="space-y-2">
            <div 
              v-for="model in trainedModels.slice(0, 3)" 
              :key="model.id"
              class="flex items-center justify-between text-sm"
            >
              <div>
                <p class="font-medium text-gray-900">{{ model.name }}</p>
                <p class="text-gray-500">{{ formatModelType(model.model_type) }}</p>
              </div>
              <div class="text-right">
                <p class="font-medium text-blue-900">{{ model.accuracy ? (model.accuracy * 100).toFixed(1) : '0.0' }}%</p>
                <p class="text-gray-500 text-xs">accuracy</p>
              </div>
            </div>
            <div v-if="trainedModels.length > 3" class="text-center pt-2">
              <RouterLink to="/models" class="text-blue-600 hover:text-blue-800 text-sm">
                View all {{ trainedModels.length }} models
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useModelStore } from '@/stores/models'
import { useClassificationStore } from '@/stores/classification'
import { storeToRefs } from 'pinia'
import Icon from '@/components/ui/Icon.vue'
import type { ModelType, ClassificationResponse } from '@/types'

const modelStore = useModelStore()
const classificationStore = useClassificationStore()

const { models: allModels, loading: modelsLoading } = storeToRefs(modelStore)
const { loading, error } = storeToRefs(classificationStore)

const currentResult = ref<ClassificationResponse | null>(null)

const form = ref({
  selectedModelId: '' as string | number,
  title: '',
  abstract: '',
  threshold: 0.5
})

// Computed properties
const trainedModels = computed(() => 
  allModels.value.filter(model => model.is_trained && model.status === 'trained')
)

const sortedConfidenceScores = computed(() => {
  if (!currentResult.value?.confidence_scores) return []
  return Object.entries(currentResult.value.confidence_scores)
    .sort(([, a], [, b]) => b - a)
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

const formatDomain = (domain: string): string => {
  return domain.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const clearError = () => {
  classificationStore.clearError()
}

// Form handling
const handleClassify = async () => {
  try {
    const modelId = form.value.selectedModelId ? 
      Number(form.value.selectedModelId) : 
      trainedModels.value[0]?.id // Use best model if none selected

    if (!modelId) {
      throw new Error('No trained models available for classification')
    }

    currentResult.value = await classificationStore.classify(modelId, {
      title: form.value.title.trim(),
      abstract: form.value.abstract.trim(),
      threshold: form.value.threshold
    })

  } catch (error) {
    console.error('Classification failed:', error)
    currentResult.value = null
  }
}

// Initialize
onMounted(() => {
  modelStore.fetchModels()
})
</script>

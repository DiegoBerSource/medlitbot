<template>
  <div class="p-6 max-w-6xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Batch Classification</h1>
      <p class="mt-2 text-gray-600">Classify multiple medical literature articles at once</p>
    </div>

    <!-- Model Selection -->
    <div class="medical-card mb-8">
      <div class="medical-card-header">
        <h2 class="text-xl font-semibold text-gray-900">Select Classification Model</h2>
        <p class="text-sm text-gray-600">Choose a trained model for batch processing</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label for="model" class="block text-sm font-medium text-gray-700 mb-2">
            Trained Model *
          </label>
          <select
            id="model"
            v-model="selectedModelId"
            required
            class="input-field"
            :class="{ 'border-red-500': !selectedModelId && attempted }"
            @change="onModelChange"
          >
            <option value="">Select a trained model</option>
            <option
              v-for="model in trainedModels"
              :key="model.id"
              :value="model.id"
            >
              {{ model.name }}{{ bestModel && model.id === bestModel.id ? ' ⭐ (Best)' : '' }} - 
              {{ model.f1_score ? `F1: ${(model.f1_score * 100).toFixed(1)}%` : model.accuracy ? `Acc: ${(model.accuracy * 100).toFixed(1)}%` : 'Training' }}
            </option>
          </select>
          <p v-if="!selectedModelId && attempted" class="mt-1 text-sm text-red-600">
            Please select a model for classification
          </p>
        </div>

        <!-- Enhanced Model Info -->
        <div v-if="selectedModel" class="p-4 bg-gradient-from-blue-50 to-gray-50 rounded-lg border border-blue-200">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-900 flex items-center">
              <Icon name="check-circle" class="w-4 h-4 text-green-500 mr-2" v-if="bestModel && selectedModel.id === bestModel.id" />
              {{ selectedModel.name }}
              <span v-if="bestModel && selectedModel.id === bestModel.id" class="ml-2 px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded-full">Best</span>
            </h3>
            <div class="text-xs text-gray-500">
              {{ formatModelType(selectedModel.model_type) }}
            </div>
          </div>
          
          <!-- Performance Metrics -->
          <div class="grid grid-cols-2 gap-4 mb-3">
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">F1 Score:</span>
                <span class="font-medium" :class="getScoreColor(selectedModel.f1_score)">
                  {{ selectedModel.f1_score ? `${(selectedModel.f1_score * 100).toFixed(1)}%` : 'N/A' }}
                </span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Accuracy:</span>
                <span class="font-medium" :class="getScoreColor(selectedModel.accuracy)">
                  {{ selectedModel.accuracy ? `${(selectedModel.accuracy * 100).toFixed(1)}%` : 'N/A' }}
                </span>
              </div>
            </div>
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Precision:</span>
                <span class="font-medium" :class="getScoreColor(selectedModel.precision)">
                  {{ selectedModel.precision ? `${(selectedModel.precision * 100).toFixed(1)}%` : 'N/A' }}
                </span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Recall:</span>
                <span class="font-medium" :class="getScoreColor(selectedModel.recall)">
                  {{ selectedModel.recall ? `${(selectedModel.recall * 100).toFixed(1)}%` : 'N/A' }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Additional Info -->
          <div class="pt-3 border-t border-gray-200">
            <div class="grid grid-cols-2 gap-4 text-xs text-gray-600">
              <div>
                <span class="font-medium">Dataset:</span>
                <span class="ml-1">{{ selectedModel.dataset_name || `Dataset ${selectedModel.dataset}` }}</span>
              </div>
              <div>
                <span class="font-medium">Training Time:</span>
                <span class="ml-1">{{ formatTrainingTime(selectedModel.training_time_minutes) }}</span>
              </div>
              <div>
                <span class="font-medium">Epochs:</span>
                <span class="ml-1">{{ selectedModel.best_epoch || selectedModel.num_epochs || 'N/A' }}</span>
              </div>
              <div>
                <span class="font-medium">Created:</span>
                <span class="ml-1">{{ formatDate(selectedModel.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Methods -->
    <div class="medical-card mb-8">
      <div class="medical-card-header">
        <h2 class="text-xl font-semibold text-gray-900">Input Articles</h2>
        <p class="text-sm text-gray-600">Choose how to provide articles for classification</p>
      </div>

      <!-- Method Selection -->
      <div class="flex space-x-4 mb-6">
        <button
          @click="inputMethod = 'file'"
          class="method-btn"
          :class="{ 'method-btn-active': inputMethod === 'file' }"
        >
          <Icon name="document" class="w-5 h-5 mr-2" />
          Upload File
        </button>
        <button
          @click="inputMethod = 'manual'"
          class="method-btn"
          :class="{ 'method-btn-active': inputMethod === 'manual' }"
        >
          <Icon name="edit" class="w-5 h-5 mr-2" />
          Manual Entry
        </button>
      </div>

      <!-- File Upload Method -->
      <div v-if="inputMethod === 'file'" class="space-y-4">
        <!-- File Upload Area -->
        <div
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleFileDrop"
          class="border-2 border-dashed rounded-lg p-8 text-center transition-colors"
          :class="{
            'border-blue-400 bg-blue-50': isDragging,
            'border-gray-300': !isDragging && !uploadedFile,
            'border-green-400 bg-green-50': uploadedFile
          }"
        >
          <Icon 
            :name="uploadedFile ? 'document' : 'plus'" 
            class="w-12 h-12 mx-auto text-gray-400 mb-4"
          />
          
          <div v-if="!uploadedFile">
            <p class="text-lg font-medium text-gray-900 mb-2">
              Drop your article file here
            </p>
            <p class="text-gray-600 mb-4">CSV or JSON file with title and abstract columns</p>
            <button
              type="button"
              @click="triggerFileInput"
              class="btn-primary"
            >
              <Icon name="plus" class="w-4 h-4 mr-2" />
              Choose File
            </button>
            <input
              ref="fileInputRef"
              type="file"
              accept=".csv,.json"
              class="hidden"
              @change="handleFileSelect"
            />
          </div>

          <!-- File Info -->
          <div v-else class="text-left max-w-md mx-auto">
            <div class="flex items-start space-x-3">
              <Icon name="document" class="w-6 h-6 text-green-600 mt-1" />
              <div class="flex-1">
                <p class="font-medium text-gray-900">{{ uploadedFile.name }}</p>
                <p v-if="parsedArticles.length" class="text-sm text-green-600 mt-1">
                  {{ parsedArticles.length }} articles found
                </p>
                <div class="mt-2">
                  <button
                    @click="removeFile"
                    class="text-sm text-red-600 hover:text-red-700"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Manual Entry Method -->
      <div v-if="inputMethod === 'manual'" class="space-y-4">
        <div class="flex justify-between items-center">
          <h4 class="text-lg font-medium text-gray-900">Articles</h4>
          <button @click="addManualArticle" class="btn-outline">
            <Icon name="plus" class="w-4 h-4 mr-2" />
            Add Article
          </button>
        </div>

        <div class="space-y-6">
          <div
            v-for="(article, index) in manualArticles"
            :key="index"
            class="p-4 border border-gray-200 rounded-lg"
          >
            <div class="flex justify-between items-start mb-4">
              <h5 class="font-medium text-gray-900">Article {{ index + 1 }}</h5>
              <button
                @click="removeManualArticle(index)"
                class="text-red-600 hover:text-red-700"
              >
                <Icon name="delete" class="w-4 h-4" />
              </button>
            </div>

            <div class="space-y-4">
              <div>
                <label :for="`title-${index}`" class="block text-sm font-medium text-gray-700 mb-2">
                  Title *
                </label>
                <input
                  :id="`title-${index}`"
                  v-model="article.title"
                  type="text"
                  required
                  class="input-field"
                  placeholder="Enter article title..."
                />
              </div>

              <div>
                <label :for="`abstract-${index}`" class="block text-sm font-medium text-gray-700 mb-2">
                  Abstract *
                </label>
                <textarea
                  :id="`abstract-${index}`"
                  v-model="article.abstract"
                  rows="4"
                  required
                  class="input-field"
                  placeholder="Enter article abstract..."
                />
              </div>
            </div>
          </div>
        </div>

        <div v-if="manualArticles.length === 0" class="text-center py-8 text-gray-500">
          <Icon name="document" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No articles added yet. Click "Add Article" to get started.</p>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-between">
      <div class="text-sm" :class="canClassify ? 'text-green-600' : 'text-gray-500'">
        <Icon v-if="canClassify" name="check-circle" class="w-4 h-4 inline mr-1 text-green-500" />
        {{ getArticleCount() }} articles ready for classification
        {{ selectedModelId && selectedModelId !== '' ? `• Model: ${selectedModel?.name || 'Selected'}` : '' }}
      </div>

      <div class="flex space-x-4">
        <button
          @click="clearAll"
          class="btn-secondary"
          :disabled="loading"
        >
          Clear All
        </button>
        
        <button
          @click="classifyBatch"
          class="btn-primary"
          :disabled="!canClassify || loading"
        >
          <Icon v-if="loading" name="clock" class="w-4 h-4 mr-2 animate-spin" />
          <Icon v-else name="brain" class="w-4 h-4 mr-2" />
          {{ loading ? 'Classifying...' : 'Classify Articles' }}
        </button>
      </div>
    </div>

    <!-- Results Display -->
    <div v-if="batchResults && batchResults.results && batchResults.results.length > 0" class="mt-8">
      <div class="medical-card">
        <div class="medical-card-header">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Classification Results</h2>
              <p class="text-sm text-gray-600">
                Successfully classified {{ (batchResults as any).total_processed || batchResults.results.length }} articles in {{ ((batchResults as any).processing_time_seconds * 1000 || batchResults.total_inference_time_ms).toFixed(0) }}ms
              </p>
            </div>
            <div class="text-sm text-gray-500">
              <span class="font-medium">Model:</span> {{ (batchResults as any).model_used || 'Unknown' }}
            </div>
          </div>
        </div>

        <!-- Results Grid -->
        <div class="space-y-4">
          <div 
            v-for="(result, index) in batchResults.results" 
            :key="index"
            class="border border-gray-200 rounded-lg p-4 bg-gray-50"
          >
            <!-- Article Title -->
            <div class="flex items-start justify-between mb-3">
              <h3 class="font-medium text-gray-900 text-sm">
                {{ (result as any).title || `Article ${result.article_index}` }}
              </h3>
              <div class="text-xs text-gray-500 ml-4">
                {{ result.inference_time_ms ? result.inference_time_ms.toFixed(1) + 'ms' : 'N/A' }}
              </div>
            </div>

            <!-- Predicted Domains -->
            <div v-if="result.predicted_domains && result.predicted_domains.length > 0" class="mb-3">
              <h4 class="text-xs font-medium text-gray-700 mb-2">Predicted Medical Domains</h4>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="domain in result.predicted_domains" 
                  :key="domain"
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                >
                  {{ formatDomain(domain) }}
                </span>
              </div>
            </div>

            <!-- Confidence Scores -->
            <div v-if="result.confidence_scores && Object.keys(result.confidence_scores).length > 0" class="mb-2">
              <h4 class="text-xs font-medium text-gray-700 mb-2">Confidence Scores</h4>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
                <div 
                  v-for="[domain, score] in getSortedConfidenceScores(result.confidence_scores)" 
                  :key="domain"
                  class="flex items-center justify-between text-xs bg-white rounded px-2 py-1"
                >
                  <span class="text-gray-700 truncate mr-2">{{ formatDomain(domain) }}</span>
                  <div class="flex items-center space-x-1">
                    <div class="w-10 bg-gray-200 rounded-full h-1">
                      <div 
                        class="h-1 rounded-full"
                        :class="score >= ((result as any).prediction_threshold || 0.5) ? 'bg-green-500' : 'bg-gray-400'"
                        :style="`width: ${score * 100}%`"
                      ></div>
                    </div>
                    <span class="font-mono text-gray-900 text-xs w-8 text-right">{{ (score * 100).toFixed(0) }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="(!result.predicted_domains || result.predicted_domains.length === 0)" class="text-center py-4">
              <Icon name="alert-circle" class="w-5 h-5 text-yellow-500 mx-auto mb-2" />
              <p class="text-sm text-gray-600">No domains predicted for this article</p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="mt-6 pt-4 border-t border-gray-200 flex justify-between items-center">
          <button 
            @click="clearResults"
            class="btn-secondary text-sm"
          >
            Clear Results
          </button>
          <button 
            @click="goToHistory"
            class="btn-outline text-sm"
          >
            View Full History →
          </button>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="classificationStore.error" class="mt-8">
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <div class="flex items-center">
          <Icon name="alert-circle" class="w-5 h-5 text-red-600 mr-2" />
          <h3 class="text-red-800 font-medium">Classification Error</h3>
        </div>
        <p class="text-red-700 mt-1 text-sm">{{ classificationStore.error }}</p>
        <button 
          @click="classificationStore.clearError" 
          class="mt-3 text-red-600 hover:text-red-800 text-sm underline"
        >
          Dismiss
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'
import Icon from '@/components/ui/Icon.vue'
import { useModelStore } from '@/stores/models'
import { useClassificationStore } from '@/stores/classification'
import type { BatchClassificationResponse } from '@/types'

// Composables
const toast = useToast()
const router = useRouter()
const modelStore = useModelStore()
const classificationStore = useClassificationStore()

// Reactive state
const loading = ref(false)
const attempted = ref(false)
const selectedModelId = ref<string>('') // HTML select returns strings
const inputMethod = ref<'file' | 'manual'>('file')
const isDragging = ref(false)
const uploadedFile = ref<File | null>(null)
const fileInputRef = ref<HTMLInputElement>()
const parsedArticles = ref<Array<{ title: string; abstract: string }>>([])
const manualArticles = ref<Array<{ title: string; abstract: string }>>([])
const batchResults = ref<BatchClassificationResponse | null>(null)

// Computed
const trainedModels = computed(() => 
  modelStore.models.filter(m => m.status === 'trained' || m.is_trained)
)

const bestModel = computed(() => {
  if (trainedModels.value.length === 0) return null
  
  // Helper function to get model score priority
  const getModelScore = (model: any) => {
    // Prioritize F1 score, then accuracy
    if (model.f1_score) return { primary: model.f1_score, secondary: model.accuracy || 0 }
    if (model.accuracy) return { primary: model.accuracy, secondary: 0 }
    return { primary: 0, secondary: 0 }
  }
  
  // Sort models by performance metrics and recency
  return trainedModels.value
    .slice()
    .sort((a, b) => {
      const aScore = getModelScore(a)
      const bScore = getModelScore(b)
      
      // Compare primary scores (F1 or accuracy)
      if (aScore.primary !== bScore.primary) {
        return bScore.primary - aScore.primary
      }
      
      // If primary scores equal, compare secondary
      if (aScore.secondary !== bScore.secondary) {
        return bScore.secondary - aScore.secondary
      }
      
      // If all scores equal, prefer most recent
      return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    })[0]
})

const selectedModel = computed(() => 
  trainedModels.value.find(m => m.id === Number(selectedModelId.value)) || null
)

const canClassify = computed(() => {
  const hasModel = selectedModelId.value && selectedModelId.value !== ''
  const hasArticles = getArticleCount() > 0
  return hasModel && hasArticles
})

// Methods
const getArticleCount = () => {
  switch (inputMethod.value) {
    case 'file': return parsedArticles.value.length
    case 'manual': return manualArticles.value.filter(a => a.title.trim() && a.abstract.trim()).length
    default: return 0
  }
}

const getArticles = () => {
  switch (inputMethod.value) {
    case 'file': return parsedArticles.value
    case 'manual': return manualArticles.value.filter(a => a.title.trim() && a.abstract.trim())
    default: return []
  }
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    uploadedFile.value = target.files[0]
    parseFile(target.files[0])
  }
}

const handleFileDrop = (event: DragEvent) => {
  isDragging.value = false
  
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    uploadedFile.value = event.dataTransfer.files[0]
    parseFile(event.dataTransfer.files[0])
  }
}

const parseFile = async (file: File) => {
  try {
    console.log('Parsing file:', file.name, 'size:', file.size)
    const text = await file.text()
    const extension = file.name.split('.').pop()?.toLowerCase()
    
    if (extension === 'csv') {
      parsedArticles.value = parseCSV(text)
    } else if (extension === 'json') {
      parsedArticles.value = parseJSON(text)
    } else {
      toast.error('Unsupported file format. Please use CSV or JSON.')
      return
    }
    
    console.log('Parsed articles:', parsedArticles.value.length)
    
    const MAX_ARTICLES = 1000
    if (parsedArticles.value.length > MAX_ARTICLES) {
      toast.warning(`⚠️ Large file detected: ${parsedArticles.value.length} articles found. The system can only process up to ${MAX_ARTICLES} articles at once. You may need to split this file into smaller batches.`)
    } else {
      toast.success(`Parsed ${parsedArticles.value.length} articles from file`)
    }
  } catch (error) {
    console.error('Error parsing file:', error)
    toast.error('Error parsing file. Please check the format.')
    parsedArticles.value = [] // Clear any partial parsing
  }
}

const parseCSV = (text: string) => {
  const lines = text.split('\n').filter(line => line.trim())
  
  if (lines.length < 2) {
    throw new Error('CSV file must have at least a header row and one data row')
  }
  
  const headers = lines[0]?.split(',').map(h => h.trim().replace(/"/g, '')) || []
  console.log('CSV headers found:', headers)
  
  const titleIndex = headers.findIndex(h => 
    h.toLowerCase().includes('title') || 
    h.toLowerCase() === 'title' ||
    h.toLowerCase() === 'name'
  )
  const abstractIndex = headers.findIndex(h => 
    h.toLowerCase().includes('abstract') || 
    h.toLowerCase().includes('summary') ||
    h.toLowerCase().includes('description')
  )
  
  console.log('Title index:', titleIndex, 'Abstract index:', abstractIndex)
  
  if (titleIndex === -1 || abstractIndex === -1) {
    throw new Error(`CSV must contain title and abstract columns. Found headers: ${headers.join(', ')}`)
  }
  
  const articles = lines.slice(1).map((line, index) => {
    const values = line.split(',').map(v => v.trim().replace(/"/g, ''))
    const article = {
      title: values[titleIndex] || '',
      abstract: values[abstractIndex] || ''
    }
    console.log(`Article ${index + 1}:`, article.title.substring(0, 50), '...', article.abstract.substring(0, 50))
    return article
  }).filter(article => article.title.trim() && article.abstract.trim())
  
  console.log('Valid articles parsed:', articles.length)
  return articles
}

const parseJSON = (text: string) => {
  const data = JSON.parse(text)
  if (!Array.isArray(data)) {
    throw new Error('JSON must be an array of articles')
  }
  
  return data.map((item: any) => ({
    title: item.title || item.Title || '',
    abstract: item.abstract || item.Abstract || item.summary || ''
  })).filter(article => article.title && article.abstract)
}

const addManualArticle = () => {
  manualArticles.value.push({ title: '', abstract: '' })
}

const removeManualArticle = (index: number) => {
  manualArticles.value.splice(index, 1)
}

const removeFile = () => {
  uploadedFile.value = null
  parsedArticles.value = []
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const onModelChange = () => {
  // Model changed, ready for new classification
}

const classifyBatch = async () => {
  if (!selectedModelId.value || selectedModelId.value === '') {
    attempted.value = true
    toast.error('Please select a model for classification')
    return
  }
  
  const articles = getArticles()
  if (articles.length === 0) {
    toast.error('Please add articles to classify')
    return
  }
  
  // Check article limit before submitting
  const MAX_ARTICLES = 1000
  if (articles.length > MAX_ARTICLES) {
    toast.error(`Too many articles: Maximum ${MAX_ARTICLES} articles allowed, but you have ${articles.length}. Please reduce the number of articles or split into smaller batches.`)
    return
  }
  
  loading.value = true
  batchResults.value = null // Clear previous results
  
  try {
    // Use the classification store for batch processing
    const results = await classificationStore.batchClassify(Number(selectedModelId.value), {
      articles: articles
    })
    
    // Store results for display
    batchResults.value = results
    
    toast.success(`Successfully classified ${articles.length} articles!`)
    
    // Scroll to results
    setTimeout(() => {
      const resultsElement = document.querySelector('.medical-card:last-of-type')
      if (resultsElement) {
        resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 100)
    
  } catch (error: any) {
    console.error('Batch classification error:', error)
    // Show the specific error message from the store
    const errorMessage = error.message || classificationStore.error || 'Error during batch classification. Please try again.'
    toast.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const clearAll = () => {
  uploadedFile.value = null
  parsedArticles.value = []
  manualArticles.value = []
  batchResults.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
  toast.info('All data cleared')
}

const clearResults = () => {
  batchResults.value = null
  toast.info('Results cleared')
}

const goToHistory = () => {
  router.push('/classification/history')
}

// Helper functions
const formatDomain = (domain: string) => {
  return domain.charAt(0).toUpperCase() + domain.slice(1).replace(/_/g, ' ')
}

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

const getScoreColor = (score: number | null) => {
  if (!score) return 'text-gray-500'
  if (score >= 0.8) return 'text-green-600'
  if (score >= 0.7) return 'text-blue-600'
  if (score >= 0.6) return 'text-yellow-600'
  return 'text-red-600'
}

const formatTrainingTime = (minutes: number | null) => {
  if (!minutes) return 'N/A'
  if (minutes < 60) return `${minutes.toFixed(0)}m`
  if (minutes < 1440) return `${(minutes / 60).toFixed(1)}h`
  return `${(minutes / 1440).toFixed(1)}d`
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

const getSortedConfidenceScores = (confidenceScores: Record<string, number>) => {
  return Object.entries(confidenceScores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 6) // Show top 6 scores
}

// Lifecycle
onMounted(async () => {
  try {
    await modelStore.fetchModels()
    
    // Set the best model as default after models are loaded
    if (bestModel.value && !selectedModelId.value) {
      selectedModelId.value = String(bestModel.value.id)
      toast.success(`Best model "${bestModel.value.name}" selected automatically`, {
        timeout: 3000
      })
    }
  } catch (error) {
    console.error('Failed to load models:', error)
    toast.error('Failed to load models')
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

.method-btn {
  @apply px-4 py-2 border border-gray-300 rounded-lg font-medium transition-colors inline-flex items-center;
}

.method-btn-active {
  @apply bg-blue-600 text-white border-blue-600;
}

.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-outline {
  @apply border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed;
}

.bg-gradient-from-blue-50 {
  background: linear-gradient(135deg, rgb(239 246 255) 0%, rgb(249 250 251) 100%);
}
</style>

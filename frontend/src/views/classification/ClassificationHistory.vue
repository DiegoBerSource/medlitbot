<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Classification History</h1>
        <p class="text-gray-600">View your past medical literature classification results</p>
      </div>
      <RouterLink to="/classification" class="btn-primary">
        New Classification
      </RouterLink>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Search -->
        <div>
          <label for="search" class="block text-sm font-medium text-gray-700 mb-2">
            Search by title or abstract
          </label>
          <input
            id="search"
            v-model="searchQuery"
            type="text"
            placeholder="Search classifications..."
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>

        <!-- Model Filter -->
        <div>
          <label for="model-filter" class="block text-sm font-medium text-gray-700 mb-2">
            Filter by model
          </label>
          <select 
            id="model-filter"
            v-model="selectedModelId"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="">All Models</option>
            <option v-for="model in availableModels" :key="model.id" :value="model.id">
              {{ model.name }}
            </option>
          </select>
        </div>

        <!-- Domain Filter -->
        <div>
          <label for="domain-filter" class="block text-sm font-medium text-gray-700 mb-2">
            Filter by domain
          </label>
          <select 
            id="domain-filter"
            v-model="selectedDomain"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="">All Domains</option>
            <option v-for="domain in uniqueDomains" :key="domain" :value="domain">
              {{ formatDomain(domain) }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-500">Loading classification history...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
      <div class="flex items-center">
        <Icon name="alert-circle" class="w-5 h-5 text-red-600 mr-2" />
        <h3 class="text-red-800 font-medium">Error loading history</h3>
      </div>
      <p class="text-red-700 mt-1">{{ error }}</p>
      <button @click="loadPredictions" class="mt-3 btn-secondary">
        Try Again
      </button>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredPredictions.length === 0 && !loading" class="bg-white rounded-lg shadow p-12">
      <div class="text-center">
        <Icon name="document-text" class="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          {{ predictions.length === 0 ? 'No classifications yet' : 'No results found' }}
        </h3>
        <p class="text-gray-500 mb-4">
          {{ predictions.length === 0 
            ? 'Start classifying medical literature to see results here' 
            : 'Try adjusting your search or filter criteria' }}
        </p>
        <RouterLink to="/classification" class="btn-primary">
          {{ predictions.length === 0 ? 'Create Your First Classification' : 'New Classification' }}
        </RouterLink>
      </div>
    </div>

    <!-- Results -->
    <div v-else class="space-y-6">
      <!-- Summary Stats -->
      <div class="bg-blue-50 rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium text-blue-900">
              {{ filteredPredictions.length }} classification{{ filteredPredictions.length !== 1 ? 's' : '' }}
              {{ searchQuery || selectedModelId || selectedDomain ? 'found' : 'total' }}
            </h3>
            <p class="text-blue-700 text-sm">
              Showing {{ Math.min(displayCount, filteredPredictions.length) }} results
            </p>
          </div>
          <button 
            v-if="filteredPredictions.length > displayCount"
            @click="loadMore"
            class="btn-secondary text-sm"
          >
            Load More
          </button>
        </div>
      </div>

      <!-- Classification Cards -->
      <div class="grid grid-cols-1 gap-6">
        <div 
          v-for="prediction in displayedPredictions" 
          :key="prediction.id"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200"
        >
          <div class="p-6">
            <!-- Header -->
            <div class="flex justify-between items-start mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-medium text-gray-900 mb-1">{{ prediction.title }}</h3>
                <p class="text-sm text-gray-500">
                  {{ formatDate(prediction.created_at) }} • 
                  Model: {{ prediction.model_name || 'Unknown' }}
                </p>
              </div>
              <div class="flex items-center space-x-2">
                <span v-if="prediction.inference_time_ms" class="text-xs text-gray-400">
                  {{ prediction.inference_time_ms.toFixed(1) }}ms
                </span>
                <button 
                  @click="toggleExpanded(prediction.id)"
                  class="text-gray-400 hover:text-gray-600"
                >
                  <Icon 
                    :name="expandedCards.has(prediction.id) ? 'chevron-up' : 'chevron-down'" 
                    class="w-5 h-5" 
                  />
                </button>
              </div>
            </div>

            <!-- Predicted Domains -->
            <div class="mb-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Predicted Domains</h4>
              <div v-if="prediction.predicted_domains && prediction.predicted_domains.length > 0" class="flex flex-wrap gap-2">
                <span 
                  v-for="domain in prediction.predicted_domains" 
                  :key="domain"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                >
                  {{ formatDomain(domain) }}
                  <span v-if="prediction.confidence_scores && prediction.confidence_scores[domain]" class="ml-1 text-green-600">
                    ({{ ((prediction.confidence_scores?.[domain] || 0) * 100).toFixed(0) }}%)
                  </span>
                </span>
              </div>
              <p v-else class="text-sm text-gray-400">No domains predicted</p>
            </div>

            <!-- Expanded Content -->
            <div v-if="expandedCards.has(prediction.id)" class="border-t pt-4 mt-4 space-y-4">
              <!-- Abstract -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Abstract</h4>
                <p class="text-sm text-gray-600 bg-gray-50 rounded p-3">
                  {{ prediction.abstract || 'No abstract available' }}
                </p>
              </div>

              <!-- Confidence Scores -->
              <div v-if="prediction.confidence_scores && Object.keys(prediction.confidence_scores).length > 0">
                <h4 class="text-sm font-medium text-gray-700 mb-2">Confidence Scores</h4>
                <div class="space-y-2">
                  <div 
                    v-for="[domain, score] in sortedConfidenceScores(prediction.confidence_scores)" 
                    :key="domain"
                    class="flex items-center justify-between text-xs"
                  >
                    <span class="text-gray-700 min-w-0 flex-1">{{ formatDomain(domain) }}</span>
                    <div class="flex items-center space-x-2 ml-4">
                      <div class="w-20 bg-gray-200 rounded-full h-1.5">
                        <div 
                          class="h-1.5 rounded-full"
                          :class="score >= (prediction.prediction_threshold || 0.5) ? 'bg-green-500' : 'bg-gray-400'"
                          :style="`width: ${score * 100}%`"
                        ></div>
                      </div>
                      <span class="font-mono text-gray-900 w-10 text-right">{{ (score * 100).toFixed(0) }}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Classification Details -->
              <div class="grid grid-cols-2 gap-4 text-xs text-gray-500">
                <div>
                  <span class="font-medium">Threshold:</span> 
                  {{ ((prediction.prediction_threshold || 0.5) * 100).toFixed(0) }}%
                </div>
                <div v-if="prediction.inference_time_ms">
                  <span class="font-medium">Processing Time:</span> 
                  {{ prediction.inference_time_ms.toFixed(1) }}ms
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="filteredPredictions.length > displayCount" class="text-center">
        <button @click="loadMore" class="btn-secondary">
          Load More Results ({{ filteredPredictions.length - displayCount }} remaining)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useClassificationStore } from '@/stores/classification'
import { useModelStore } from '@/stores/models'
import { storeToRefs } from 'pinia'
import Icon from '@/components/ui/Icon.vue'


const classificationStore = useClassificationStore()
const modelStore = useModelStore()

const { predictions, loading, error } = storeToRefs(classificationStore)
const { models } = storeToRefs(modelStore)

// Local state
const searchQuery = ref('')
const selectedModelId = ref('')
const selectedDomain = ref('')
const displayCount = ref(10)
const expandedCards = ref(new Set<number>())

// Computed
const availableModels = computed(() => 
  models.value.filter(model => model.is_trained)
)

const uniqueDomains = computed(() => {
  const domains = new Set<string>()
  predictions.value.forEach(pred => {
    pred.predicted_domains?.forEach(domain => domains.add(domain))
  })
  return Array.from(domains).sort()
})

const filteredPredictions = computed(() => {
  let filtered = [...predictions.value]

  // Search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(pred => 
      pred.title?.toLowerCase().includes(query) || 
      pred.abstract?.toLowerCase().includes(query)
    )
  }

  // Model filter
  if (selectedModelId.value) {
    filtered = filtered.filter(pred => pred.model === Number(selectedModelId.value))
  }

  // Domain filter
  if (selectedDomain.value) {
    filtered = filtered.filter(pred => 
      pred.predicted_domains?.includes(selectedDomain.value)
    )
  }

  return filtered
})

const displayedPredictions = computed(() => 
  filteredPredictions.value.slice(0, displayCount.value)
)

// Methods
const loadPredictions = async () => {
  try {
    await classificationStore.fetchPredictions()
  } catch (err) {
    console.error('Failed to load predictions:', err)
  }
}

const loadMore = () => {
  displayCount.value += 10
}

const toggleExpanded = (id: number) => {
  if (expandedCards.value.has(id)) {
    expandedCards.value.delete(id)
  } else {
    expandedCards.value.add(id)
  }
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' at ' + date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const formatDomain = (domain: string): string => {
  return domain.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const sortedConfidenceScores = (confidenceScores: Record<string, number>): [string, number][] => {
  return Object.entries(confidenceScores).sort(([, a], [, b]) => b - a)
}

// Watchers
watch([searchQuery, selectedModelId, selectedDomain], () => {
  displayCount.value = 10 // Reset display count when filters change
})

// Lifecycle
onMounted(() => {
  loadPredictions()
  modelStore.fetchModels() // Load models for filter
})
</script>

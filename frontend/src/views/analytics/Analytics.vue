<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Analytics</h1>
      <p class="text-gray-600">System performance and model insights</p>
    </div>

    <!-- Performance Metrics Overview -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard
        label="Average Accuracy"
        :value="averageAccuracy"
        icon="chart-bar"
        :color="getScoreColor(averageAccuracyValue)"
        :loading="isLoading"
      />
      <StatCard
        label="Average F1-Score"
        :value="averageF1Score"
        icon="chart-bar"
        :color="getScoreColor(averageF1ScoreValue)"
        :loading="isLoading"
      />
      <StatCard
        label="Best Model Accuracy"
        :value="bestAccuracy"
        icon="trophy"
        color="success"
        :loading="isLoading"
      />
      <StatCard
        label="Total Trained Models"
        :value="trainedModelsCount.toString()"
        icon="cpu"
        color="primary"
        :loading="isLoading"
      />
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
      <!-- Model Performance Comparison -->
      <ChartCard
        title="Model Performance Comparison"
        :loading="isLoading"
      >
        <RadarChart
          :data="performanceComparisonData"
          :options="radarOptions"
          :height="400"
        />
      </ChartCard>

      <!-- Accuracy vs F1-Score Scatter -->
      <ChartCard
        title="Accuracy vs F1-Score"
        :loading="isLoading"
      >
        <canvas ref="scatterChart" height="400"></canvas>
      </ChartCard>
    </div>

    <!-- Confusion Matrix Section -->
    <div class="mb-8">
      <div class="medical-card">
        <div class="medical-card-header mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Confusion Matrix Analysis</h3>
          <p class="text-sm text-gray-600 mt-1">
            Select a model to view its confusion matrix
          </p>
        </div>

        <!-- Model Selector -->
        <div class="mb-6">
          <label for="model-select" class="block text-sm font-medium text-gray-700 mb-2">
            Select Model:
          </label>
          <select
            id="model-select"
            v-model="selectedModelId"
            class="form-select w-full max-w-md"
            :disabled="trainedModels.length === 0"
          >
            <option value="">
              {{ trainedModels.length === 0 ? 'No trained models available' : 'Select a model...' }}
            </option>
            <option
              v-for="model in trainedModels"
              :key="model.id"
              :value="model.id"
            >
              {{ model.name }} ({{ model.f1_score ? (model.f1_score * 100).toFixed(1) : '0.0' }}% F1)
            </option>
          </select>
        </div>

        <!-- Confusion Matrix -->
        <div v-if="selectedModel && selectedModel.confusion_matrix">
          <ConfusionMatrix
            :matrix="selectedModel.confusion_matrix"
            :labels="confusionMatrixLabels"
            :title="`${selectedModel.name} - Confusion Matrix`"
          />
        </div>
        
        <div v-else-if="selectedModelId && selectedModel" class="text-center py-8 text-gray-500">
          <Icon name="chart-bar" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No confusion matrix data available for this model</p>
        </div>
        
        <div v-else-if="trainedModels.length === 0" class="text-center py-8 text-gray-500">
          <Icon name="cpu" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No trained models available</p>
          <RouterLink to="/models/create" class="text-primary-600 hover:text-primary-700 text-sm">
            Create your first model →
          </RouterLink>
        </div>
        
        <div v-else class="text-center py-8 text-gray-500">
          <Icon name="chart-bar" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Select a model above to view its confusion matrix</p>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="flex justify-center space-x-4">
      <RouterLink to="/analytics/comparison" class="btn-primary">
        <Icon name="chart-bar" class="w-4 h-4 mr-2" />
        Model Comparison
      </RouterLink>
      <RouterLink to="/models" class="btn-secondary">
        <Icon name="cpu" class="w-4 h-4 mr-2" />
        View All Models
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import Icon from '@/components/ui/Icon.vue'
import StatCard from '@/components/ui/StatCard.vue'
import ChartCard from '@/components/charts/ChartCard.vue'
import RadarChart from '@/components/charts/RadarChart.vue'
import ConfusionMatrix from '@/components/charts/ConfusionMatrix.vue'
import { useModelStore } from '@/stores/models'
// Types imported through stores

// Store
const modelStore = useModelStore()
const { models } = storeToRefs(modelStore)

// State
const isLoading = ref(false)
const selectedModelId = ref<string>('')

// Computed
const trainedModels = computed(() => {
  return models.value?.filter(m => m.status === 'trained' && m.is_trained) || []
})

const selectedModel = computed(() => {
  if (!selectedModelId.value) return null
  return trainedModels.value.find(m => m.id.toString() === selectedModelId.value) || null
})

const trainedModelsCount = computed(() => trainedModels.value.length)

const averageAccuracyValue = computed(() => {
  if (trainedModels.value.length === 0) return 0
  return trainedModels.value.reduce((sum, m) => sum + (m.accuracy || 0), 0) / trainedModels.value.length
})

const averageAccuracy = computed(() => {
  if (trainedModels.value.length === 0) return 'N/A'
  return `${(averageAccuracyValue.value * 100).toFixed(1)}%`
})

const averageF1ScoreValue = computed(() => {
  if (trainedModels.value.length === 0) return 0
  return trainedModels.value.reduce((sum, m) => sum + (m.f1_score || 0), 0) / trainedModels.value.length
})

const averageF1Score = computed(() => {
  if (trainedModels.value.length === 0) return 'N/A'
  return `${(averageF1ScoreValue.value * 100).toFixed(1)}%`
})

const bestAccuracy = computed(() => {
  if (trainedModels.value.length === 0) return 'N/A'
  const best = Math.max(...trainedModels.value.map(m => m.accuracy || 0))
  return `${(best * 100).toFixed(1)}%`
})

const performanceComparisonData = computed(() => {
  if (trainedModels.value.length === 0) {
    return {
      labels: ['Accuracy', 'F1 Score', 'Precision', 'Recall'],
      datasets: []
    }
  }

  const colors = [
    'rgba(59, 130, 246, 0.2)', // blue
    'rgba(16, 185, 129, 0.2)', // green
    'rgba(245, 158, 11, 0.2)', // yellow
    'rgba(239, 68, 68, 0.2)', // red
    'rgba(139, 92, 246, 0.2)'  // purple
  ]

  const borderColors = [
    'rgba(59, 130, 246, 1)',
    'rgba(16, 185, 129, 1)',
    'rgba(245, 158, 11, 1)',
    'rgba(239, 68, 68, 1)',
    'rgba(139, 92, 246, 1)'
  ]

  return {
    labels: ['Accuracy', 'F1 Score', 'Precision', 'Recall'],
    datasets: trainedModels.value.slice(0, 5).map((model, index) => ({
      label: model.name,
      data: [
        (model.accuracy || 0) * 100,
        (model.f1_score || 0) * 100,
        (model.precision || 0) * 100,
        (model.recall || 0) * 100
      ],
      backgroundColor: colors[index % colors.length],
      borderColor: borderColors[index % borderColors.length],
      pointBackgroundColor: borderColors[index % borderColors.length]
    }))
  }
})

const confusionMatrixLabels = computed(() => {
  // For medical domain classification, these would typically be the domain names
  // For now, we'll use generic labels that can be customized based on the actual domains
  if (!selectedModel.value || !selectedModel.value.confusion_matrix) return []
  
  const matrixSize = selectedModel.value.confusion_matrix.length
  return Array.from({ length: matrixSize }, (_, i) => `Class ${i + 1}`)
})

const radarOptions = {
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

// Methods
const getScoreColor = (score: number) => {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'error'
}

const refreshData = async () => {
  isLoading.value = true
  try {
    await modelStore.fetchModels()
  } catch (error) {
    console.error('Failed to fetch models:', error)
  } finally {
    isLoading.value = false
  }
}

// Auto-select best model when models are loaded
watch(trainedModels, (newModels) => {
  if (newModels.length > 0 && !selectedModelId.value) {
    // Select the model with highest F1 score
    const bestModel = newModels.reduce((best, current) => {
      const bestScore = best.f1_score || best.accuracy || 0
      const currentScore = current.f1_score || current.accuracy || 0
      return currentScore > bestScore ? current : best
    })
    selectedModelId.value = bestModel.id.toString()
  }
}, { immediate: true })

// Lifecycle
onMounted(async () => {
  await refreshData()
})
</script>

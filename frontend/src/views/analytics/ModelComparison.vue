<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Model Comparison</h1>
      <p class="text-gray-600">Compare performance metrics across different models</p>
    </div>

    <!-- Model Selection -->
    <div class="mb-8">
      <div class="medical-card">
        <div class="medical-card-header">
          <h3 class="text-lg font-semibold text-gray-900">Select Models to Compare</h3>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label for="model1-select" class="block text-sm font-medium text-gray-700 mb-2">
              Model 1:
            </label>
            <select id="model1-select" v-model="selectedModel1" class="form-select w-full">
              <option value="">Select first model...</option>
              <option
                v-for="model in trainedModels"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }} (F1: {{ model.f1_score ? (model.f1_score * 100).toFixed(1) : '0.0' }}%)
              </option>
            </select>
          </div>
          
          <div>
            <label for="model2-select" class="block text-sm font-medium text-gray-700 mb-2">
              Model 2:
            </label>
            <select id="model2-select" v-model="selectedModel2" class="form-select w-full">
              <option value="">Select second model...</option>
              <option
                v-for="model in trainedModels"
                :key="model.id"
                :value="model.id"
                :disabled="model.id === selectedModel1"
              >
                {{ model.name }} (F1: {{ model.f1_score ? (model.f1_score * 100).toFixed(1) : '0.0' }}%)
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison Results -->
    <div v-if="model1 && model2" class="space-y-8">
      <!-- Metrics Comparison Table -->
      <div class="medical-card">
        <div class="medical-card-header">
          <h3 class="text-lg font-semibold text-gray-900">Performance Metrics</h3>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metric
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {{ model1.name }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {{ model2.name }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Difference
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Winner
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="metric in comparisonMetrics" :key="metric.name">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ metric.name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ metric.value1 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ metric.value2 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm"
                    :class="metric.difference > 0 ? 'text-green-600' : metric.difference < 0 ? 'text-red-600' : 'text-gray-500'">
                  {{ metric.differenceText }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span v-if="metric.winner" 
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="metric.winner === model1.name ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'">
                    {{ metric.winner }}
                  </span>
                  <span v-else class="text-sm text-gray-500">Tie</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Performance Chart -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ChartCard title="Performance Comparison" :loading="isLoading">
          <RadarChart
            :data="comparisonChartData"
            :options="radarOptions"
            :height="350"
          />
        </ChartCard>

        <!-- Training Details -->
        <div class="medical-card">
          <div class="medical-card-header">
            <h3 class="text-lg font-semibold text-gray-900">Training Details</h3>
          </div>
          
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-2">{{ model1.name }}</h4>
                <div class="space-y-1 text-sm text-gray-600">
                  <div><strong>Type:</strong> {{ model1.model_type.toUpperCase() }}</div>
                  <div><strong>Training Time:</strong> {{ model1.training_time_minutes || 'N/A' }} min</div>
                  <div><strong>Epochs:</strong> {{ model1.num_epochs || 'N/A' }}</div>
                  <div><strong>Learning Rate:</strong> {{ model1.learning_rate || 'N/A' }}</div>
                  <div><strong>Batch Size:</strong> {{ model1.batch_size || 'N/A' }}</div>
                </div>
              </div>
              
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-2">{{ model2.name }}</h4>
                <div class="space-y-1 text-sm text-gray-600">
                  <div><strong>Type:</strong> {{ model2.model_type.toUpperCase() }}</div>
                  <div><strong>Training Time:</strong> {{ model2.training_time_minutes || 'N/A' }} min</div>
                  <div><strong>Epochs:</strong> {{ model2.num_epochs || 'N/A' }}</div>
                  <div><strong>Learning Rate:</strong> {{ model2.learning_rate || 'N/A' }}</div>
                  <div><strong>Batch Size:</strong> {{ model2.batch_size || 'N/A' }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Confusion Matrices Side by Side -->
      <div v-if="model1.confusion_matrix && model2.confusion_matrix">
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
          <div class="medical-card">
            <div class="medical-card-header">
              <h3 class="text-lg font-semibold text-gray-900">{{ model1.name }} - Confusion Matrix</h3>
            </div>
            <ConfusionMatrix
              :matrix="model1.confusion_matrix"
              :labels="getConfusionMatrixLabels(model1.confusion_matrix)"
            />
          </div>
          
          <div class="medical-card">
            <div class="medical-card-header">
              <h3 class="text-lg font-semibold text-gray-900">{{ model2.name }} - Confusion Matrix</h3>
            </div>
            <ConfusionMatrix
              :matrix="model2.confusion_matrix"
              :labels="getConfusionMatrixLabels(model2.confusion_matrix)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- No Models Selected State -->
    <div v-else class="text-center py-12">
      <Icon name="chart-bar" class="w-16 h-16 mx-auto mb-4 text-gray-300" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">Select Models to Compare</h3>
      <p class="text-gray-500 mb-4">Choose two trained models above to see a detailed comparison</p>
      <div v-if="trainedModels.length < 2" class="text-sm text-gray-500">
        <p>You need at least 2 trained models to make comparisons.</p>
        <RouterLink to="/models/create" class="text-primary-600 hover:text-primary-700">
          Train more models →
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import Icon from '@/components/ui/Icon.vue'
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
const selectedModel1 = ref<number | string>('')
const selectedModel2 = ref<number | string>('')

// Computed
const trainedModels = computed(() => {
  return models.value?.filter(m => m.status === 'trained' && m.is_trained) || []
})

const model1 = computed(() => {
  return trainedModels.value.find(m => m.id === selectedModel1.value) || null
})

const model2 = computed(() => {
  return trainedModels.value.find(m => m.id === selectedModel2.value) || null
})

const comparisonMetrics = computed(() => {
  if (!model1.value || !model2.value) return []

  const metrics = [
    {
      name: 'Accuracy',
      value1: `${((model1.value.accuracy || 0) * 100).toFixed(1)}%`,
      value2: `${((model2.value.accuracy || 0) * 100).toFixed(1)}%`,
      raw1: model1.value.accuracy || 0,
      raw2: model2.value.accuracy || 0
    },
    {
      name: 'F1 Score',
      value1: `${((model1.value.f1_score || 0) * 100).toFixed(1)}%`,
      value2: `${((model2.value.f1_score || 0) * 100).toFixed(1)}%`,
      raw1: model1.value.f1_score || 0,
      raw2: model2.value.f1_score || 0
    },
    {
      name: 'Precision',
      value1: `${((model1.value.precision || 0) * 100).toFixed(1)}%`,
      value2: `${((model2.value.precision || 0) * 100).toFixed(1)}%`,
      raw1: model1.value.precision || 0,
      raw2: model2.value.precision || 0
    },
    {
      name: 'Recall',
      value1: `${((model1.value.recall || 0) * 100).toFixed(1)}%`,
      value2: `${((model2.value.recall || 0) * 100).toFixed(1)}%`,
      raw1: model1.value.recall || 0,
      raw2: model2.value.recall || 0
    }
  ]

  return metrics.map(metric => {
    const difference = metric.raw1 - metric.raw2
    const absDiff = Math.abs(difference)
    const differencePercent = (absDiff * 100).toFixed(1)
    
    return {
      ...metric,
      difference,
      differenceText: (() => {
        if (difference === 0) return '0.0%'
        const sign = difference > 0 ? '+' : '-'
        return `${sign}${differencePercent}%`
      })(),
      winner: (() => {
        if (difference > 0.001) return model1.value!.name
        if (difference < -0.001) return model2.value!.name
        return null
      })()
    }
  })
})

const comparisonChartData = computed(() => {
  if (!model1.value || !model2.value) return { labels: [], datasets: [] }

  return {
    labels: ['Accuracy', 'F1 Score', 'Precision', 'Recall'],
    datasets: [
      {
        label: model1.value.name,
        data: [
          (model1.value.accuracy || 0) * 100,
          (model1.value.f1_score || 0) * 100,
          (model1.value.precision || 0) * 100,
          (model1.value.recall || 0) * 100
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 1)',
        pointBackgroundColor: 'rgba(59, 130, 246, 1)'
      },
      {
        label: model2.value.name,
        data: [
          (model2.value.accuracy || 0) * 100,
          (model2.value.f1_score || 0) * 100,
          (model2.value.precision || 0) * 100,
          (model2.value.recall || 0) * 100
        ],
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderColor: 'rgba(16, 185, 129, 1)',
        pointBackgroundColor: 'rgba(16, 185, 129, 1)'
      }
    ]
  }
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
const getConfusionMatrixLabels = (matrix: number[][]) => {
  const size = matrix.length
  return Array.from({ length: size }, (_, i) => `Class ${i + 1}`)
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

// Lifecycle
onMounted(async () => {
  await refreshData()
})
</script>

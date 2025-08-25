<template>
  <div class="confusion-matrix-container">
    <div class="mb-4">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">
        Confusion Matrix
      </h3>
      <p class="text-sm text-gray-600" v-if="!matrix || matrix.length === 0">
        No confusion matrix data available
      </p>
    </div>
    
    <div v-if="matrix && matrix.length > 0" class="confusion-matrix">
      <!-- Labels Row -->
      <div class="matrix-labels-row">
        <div class="label-corner"></div>
        <div class="predicted-label">
          <span>Predicted</span>
        </div>
      </div>
      
      <!-- Column Headers -->
      <div class="matrix-headers">
        <div class="actual-label">
          <span>Actual</span>
        </div>
        <div class="matrix-header-row">
          <div
            v-for="(label, index) in labels"
            :key="`col-${index}`"
            class="matrix-header"
            :title="label"
          >
            {{ truncateLabel(label) }}
          </div>
        </div>
      </div>
      
      <!-- Matrix Grid -->
      <div class="matrix-grid">
        <div
          v-for="(row, rowIndex) in matrix"
          :key="`row-${rowIndex}`"
          class="matrix-row"
        >
          <!-- Row Label -->
          <div 
            class="matrix-row-label"
            :title="labels?.[rowIndex] || ''"
          >
            {{ truncateLabel(labels?.[rowIndex] || '') }}
          </div>
          
          <!-- Matrix Cells -->
          <div
            v-for="(value, colIndex) in row"
            :key="`cell-${rowIndex}-${colIndex}`"
            class="matrix-cell"
            :class="{
              'diagonal': rowIndex === colIndex,
              'correct': rowIndex === colIndex && value > 0,
              'incorrect': rowIndex !== colIndex && value > 0
            }"
            :style="getCellStyle(value)"
            @click="selectCell(rowIndex, colIndex, value)"
            :title="`${labels[rowIndex]} → ${labels[colIndex]}: ${value}`"
          >
            <span class="cell-value">{{ value }}</span>
            <div v-if="showPercentages" class="cell-percentage">
              {{ getPercentage(value, rowIndex) }}%
            </div>
          </div>
        </div>
      </div>
      
      <!-- Legend -->
      <div class="matrix-legend">
        <div class="legend-item">
          <div class="legend-color correct-prediction"></div>
          <span>Correct Predictions</span>
        </div>
        <div class="legend-item">
          <div class="legend-color incorrect-prediction"></div>
          <span>Incorrect Predictions</span>
        </div>
        <div class="legend-controls">
          <label class="legend-control">
            <input
              type="checkbox"
              v-model="showPercentages"
            />
            <span class="ml-2">Show percentages</span>
          </label>
        </div>
      </div>
      
      <!-- Selected Cell Details -->
      <div v-if="selectedCell" class="selected-cell-details">
        <h4 class="font-medium text-gray-900">Selected Cell Details</h4>
        <p class="text-sm text-gray-600">
          <strong>Actual:</strong> {{ labels[selectedCell.row] }}<br>
          <strong>Predicted:</strong> {{ labels[selectedCell.col] }}<br>
          <strong>Count:</strong> {{ selectedCell.value }}<br>
          <strong>Percentage of Row:</strong> {{ getPercentage(selectedCell.value, selectedCell.row) }}%
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  matrix: number[][]
  labels: string[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confusion Matrix'
})

// State
const showPercentages = ref(false)
const selectedCell = ref<{ row: number, col: number, value: number } | null>(null)

// Computed
const maxValue = computed(() => {
  if (!props.matrix || props.matrix.length === 0) return 1
  return Math.max(...props.matrix.flat())
})

// Methods
const getCellStyle = (value: number) => {
  if (maxValue.value === 0) return { opacity: '0.1' }
  
  const intensity = value / maxValue.value
  return {
    opacity: Math.max(0.1, intensity).toString()
  }
}

const getPercentage = (value: number, rowIndex: number) => {
  if (!props.matrix || !props.matrix[rowIndex]) return 0
  
  const rowSum = props.matrix[rowIndex]!.reduce((sum, val) => sum + val, 0)
  if (rowSum === 0) return 0
  
  return Math.round((value / rowSum) * 100)
}

const selectCell = (row: number, col: number, value: number) => {
  selectedCell.value = { row, col, value }
}

const truncateLabel = (label: string, maxLength: number = 12) => {
  if (label.length <= maxLength) return label
  return label.substring(0, maxLength - 3) + '...'
}
</script>

<style scoped>
.confusion-matrix-container {
  @apply w-full max-w-4xl mx-auto;
}

.confusion-matrix {
  @apply bg-white border border-gray-200 rounded-lg overflow-hidden;
}

.matrix-labels-row {
  @apply flex;
}

.label-corner {
  @apply w-24 h-8;
}

.predicted-label {
  @apply flex-1 flex items-center justify-center bg-blue-50 border-b border-gray-200;
}

.predicted-label span {
  @apply text-sm font-medium text-blue-700;
}

.matrix-headers {
  @apply flex;
}

.actual-label {
  @apply w-24 flex items-center justify-center bg-blue-50 border-r border-gray-200;
  writing-mode: vertical-rl;
  text-orientation: mixed;
}

.actual-label span {
  @apply text-sm font-medium text-blue-700;
}

.matrix-header-row {
  @apply flex flex-1;
}

.matrix-header {
  @apply flex-1 min-w-16 max-w-20 p-2 text-xs font-medium text-gray-700 bg-gray-50 border-r border-gray-200 text-center truncate;
}

.matrix-grid {
  @apply border-t border-gray-200;
}

.matrix-row {
  @apply flex border-b border-gray-200 last:border-b-0;
}

.matrix-row-label {
  @apply w-24 p-2 text-xs font-medium text-gray-700 bg-gray-50 border-r border-gray-200 flex items-center justify-center text-center truncate;
}

.matrix-cell {
  @apply flex-1 min-w-16 max-w-20 p-2 text-center cursor-pointer border-r border-gray-200 last:border-r-0 transition-all hover:ring-2 hover:ring-blue-500 hover:ring-inset relative;
}

.matrix-cell.diagonal {
  @apply bg-green-50;
}

.matrix-cell.correct {
  @apply bg-green-100;
}

.matrix-cell.incorrect {
  @apply bg-red-50;
}

.cell-value {
  @apply text-sm font-medium text-gray-900 block;
}

.cell-percentage {
  @apply text-xs text-gray-500;
}

.matrix-legend {
  @apply flex items-center justify-between p-4 bg-gray-50 border-t border-gray-200;
}

.legend-item {
  @apply flex items-center space-x-2;
}

.legend-color {
  @apply w-4 h-4 rounded border border-gray-300;
}

.legend-color.correct-prediction {
  @apply bg-green-100;
}

.legend-color.incorrect-prediction {
  @apply bg-red-50;
}

.legend-controls {
  @apply flex items-center space-x-4;
}

.legend-control {
  @apply flex items-center text-sm text-gray-700 cursor-pointer;
}

.legend-control input[type="checkbox"] {
  @apply rounded border-gray-300 text-blue-600 focus:ring-blue-500;
}

.selected-cell-details {
  @apply mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg;
}
</style>

<template>
  <div class="medical-card">
    <div class="flex items-center justify-between mb-4">
      <h4 class="font-medium text-gray-900">Model Training #{{ trainingJob.model }}</h4>
      <span 
        class="status-badge"
        :class="{
          'status-badge-success': trainingJob.status === 'completed',
          'status-badge-warning': trainingJob.status === 'running',
          'status-badge-error': trainingJob.status === 'failed'
        }"
      >
        {{ trainingJob.status }}
      </span>
    </div>
    
    <div class="space-y-3">
      <div class="flex justify-between text-sm">
        <span>Progress</span>
        <span>{{ Math.round(trainingJob.progress_percentage) }}%</span>
      </div>
      
      <div class="progress-bar">
        <div 
          class="progress-bar-fill"
          :style="{ width: trainingJob.progress_percentage + '%' }"
        />
      </div>
      
      <div class="grid grid-cols-2 gap-4 text-sm text-gray-600">
        <div>Epoch: {{ trainingJob.current_epoch }}/{{ trainingJob.total_epochs }}</div>
        <div v-if="trainingJob.current_loss">Loss: {{ trainingJob.current_loss.toFixed(4) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TrainingJob } from '@/types'

interface Props {
  trainingJob: TrainingJob
}

defineProps<Props>()
</script>

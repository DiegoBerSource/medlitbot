<template>
  <div class="chart-container">
    <div class="medical-card-header">
      <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
    </div>
    <div class="relative">
      <div v-if="loading" class="flex items-center justify-center h-64">
        <div class="loading-spinner-lg"></div>
      </div>
      <slot v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  loading: false
})
</script>

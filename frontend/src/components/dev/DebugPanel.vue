<template>
  <div class="fixed bottom-4 left-4 bg-gray-900 text-white p-4 rounded-lg shadow-lg max-w-sm">
    <h3 class="font-medium mb-2">Debug Panel</h3>
          <div class="text-xs space-y-1">
        <div>Environment: {{ environment }}</div>
        <div>Node: {{ nodeVersion }}</div>
        <div>Build: {{ buildTime }}</div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const environment = ref(import.meta.env.MODE || 'development')
const nodeVersion = ref('24.1.0')
const buildTime = ref(new Date().toISOString())
</script>

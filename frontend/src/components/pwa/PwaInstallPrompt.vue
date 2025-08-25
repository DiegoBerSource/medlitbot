<template>
  <div v-if="showPrompt" class="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 max-w-sm">
    <h3 class="font-medium text-gray-900">Install MedLitBot</h3>
    <p class="text-sm text-gray-600 mt-1">
      Install our app for the best experience.
    </p>
    <div class="flex mt-3 space-x-2">
      <button @click="install" class="btn-primary text-sm px-3 py-1">
        Install
      </button>
      <button @click="dismiss" class="btn-secondary text-sm px-3 py-1">
        Dismiss
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showPrompt = ref(false)

const install = () => {
  showPrompt.value = false
}

const dismiss = () => {
  showPrompt.value = false
}
</script>

<template>
  <header class="bg-white shadow-sm border-b border-gray-200">
    <div class="px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center">
          <button
            @click="$emit('toggleSidebar')"
            class="p-2 rounded-md text-gray-400 hover:text-gray-500"
          >
            <Icon name="menu" class="w-6 h-6" />
          </button>
          
          <h1 class="ml-4 text-xl font-semibold text-gray-900">
            MedLitBot
          </h1>
        </div>
        
        <div class="flex items-center space-x-4">
          <button class="p-2 rounded-md text-gray-400 hover:text-gray-500">
            <Icon name="bell" class="w-6 h-6" />
          </button>
          
          <div class="w-8 h-8 bg-gray-300 rounded-full"></div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import Icon from '../ui/Icon.vue'

interface Props {
  sidebarCollapsed?: boolean
}

defineProps<Props>()

defineEmits<{
  toggleSidebar: []
}>()
</script>

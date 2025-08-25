<template>
  <div class="bg-white shadow-lg h-full">
    <div class="p-4">
      <h2 class="text-xl font-bold text-gray-900">MedLitBot</h2>
    </div>
    
    <nav class="mt-8 px-4">
      <div class="space-y-2">
        <RouterLink
          to="/"
          class="nav-link-inactive hover:nav-link-active"
        >
          <Icon name="home" class="w-5 h-5 mr-3" />
          Dashboard
        </RouterLink>
        
        <RouterLink
          to="/datasets"
          class="nav-link-inactive hover:nav-link-active"
        >
          <Icon name="database" class="w-5 h-5 mr-3" />
          Datasets
        </RouterLink>
        
        <RouterLink
          to="/models"
          class="nav-link-inactive hover:nav-link-active"
        >
          <Icon name="cpu" class="w-5 h-5 mr-3" />
          Models
        </RouterLink>
        
        <RouterLink
          to="/classification"
          class="nav-link-inactive hover:nav-link-active"
        >
          <Icon name="brain" class="w-5 h-5 mr-3" />
          Classification
        </RouterLink>
        
        <RouterLink
          to="/analytics"
          class="nav-link-inactive hover:nav-link-active"
        >
          <Icon name="chart-bar" class="w-5 h-5 mr-3" />
          Analytics
        </RouterLink>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import Icon from '../ui/Icon.vue'

interface Props {
  collapsed?: boolean
}

withDefaults(defineProps<Props>(), {
  collapsed: false
})

const emit = defineEmits<{
  toggleCollapse: []
}>()
</script>

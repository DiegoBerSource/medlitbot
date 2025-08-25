<template>
  <nav class="bg-gray-50 px-4 py-3" aria-label="Breadcrumb">
    <ol class="flex items-center space-x-2">
      <li v-for="(item, index) in items" :key="index" class="flex items-center">
        <RouterLink
          v-if="item.to && !item.active"
          :to="item.to"
          class="text-gray-500 hover:text-gray-700"
        >
          {{ item.label }}
        </RouterLink>
        
        <span
          v-else
          class="text-gray-900 font-medium"
          :class="{ 'text-gray-500': !item.active }"
        >
          {{ item.label }}
        </span>
        
        <Icon
          v-if="index < items.length - 1"
          name="chevron-right"
          class="w-4 h-4 mx-2 text-gray-400"
        />
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
import type { BreadcrumbItem } from '@/types'
import Icon from '../ui/Icon.vue'

interface Props {
  items: BreadcrumbItem[]
}

defineProps<Props>()
</script>

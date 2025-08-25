<template>
  <div class="medical-card">
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <Icon :name="icon" class="w-8 h-8" :class="`text-${color}-500`" />
      </div>
      <div class="ml-5 w-0 flex-1">
        <dl>
          <dt class="text-sm font-medium text-gray-500 truncate">
            {{ label }}
          </dt>
          <dd>
            <div class="text-lg font-medium text-gray-900">
              <span v-if="loading">-</span>
              <span v-else>{{ value }}</span>
            </div>
          </dd>
        </dl>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Icon from './Icon.vue'

interface Props {
  label: string
  value: string | number
  icon: string
  color?: string
  trend?: 'up' | 'down' | null
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  color: 'primary',
  trend: null,
  loading: false
})
</script>

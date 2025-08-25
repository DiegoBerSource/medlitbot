<template>
  <div
    v-if="!isOnline"
    class="fixed top-0 left-0 right-0 bg-red-600 text-white text-center py-2 text-sm z-50"
  >
    <Icon name="wifi-off" class="w-4 h-4 inline mr-2" />
    You are currently offline
  </div>
</template>

<script setup lang="ts">
import { useOnline } from '@vueuse/core'
import Icon from './Icon.vue'

const isOnline = useOnline()
</script>

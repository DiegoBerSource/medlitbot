<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
      <p class="text-gray-600">Configure your MedLitBot preferences</p>
    </div>
    
    <div class="bg-white rounded-lg shadow p-6">
      <div class="text-center py-12">
        <Icon name="cog" class="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">System Settings</h3>
        <p class="text-gray-500 mb-4">Configure system preferences and user profile</p>
        <RouterLink to="/settings/profile" class="btn-primary">
          Edit Profile
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Icon from '@/components/ui/Icon.vue'
</script>

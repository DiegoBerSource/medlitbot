<template>
  <component :is="iconComponent" :class="[classes, 'flex-shrink-0']" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  HomeIcon,
  CircleStackIcon,
  CpuChipIcon,
  ChartBarIcon,
  CogIcon,
  BeakerIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  ClockIcon,
  UserIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

interface Props {
  name: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

// Map icon names to Heroicon components
const iconMap = {
  home: HomeIcon,
  database: CircleStackIcon,
  cpu: CpuChipIcon,
  'chart-bar': ChartBarIcon,
  cog: CogIcon,
  brain: BeakerIcon, // Using BeakerIcon for brain/science
  document: DocumentTextIcon,
  list: ClipboardDocumentListIcon,
  clock: ClockIcon,
  user: UserIcon,
  warning: ExclamationTriangleIcon,
  success: CheckCircleIcon,
  close: XMarkIcon,
  plus: PlusIcon,
  view: EyeIcon,
  edit: PencilIcon,
  delete: TrashIcon
}

const iconComponent = computed(() => {
  return iconMap[props.name as keyof typeof iconMap] || HomeIcon
})

const classes = computed(() => {
  const sizeMap: Record<typeof props.size, string> = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-8 h-8'
  }
  return sizeMap[props.size]
})
</script>

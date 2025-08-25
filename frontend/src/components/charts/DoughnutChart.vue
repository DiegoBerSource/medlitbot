<template>
  <div :style="{ height: height + 'px' }">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart } from 'chart.js'

interface Props {
  data: any
  options?: any
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  height: 400
})

const chartRef = ref<HTMLCanvasElement>()
let chart: Chart | null = null

const createChart = () => {
  if (!chartRef.value) return
  
  chart = new Chart(chartRef.value, {
    type: 'doughnut',
    data: props.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      ...props.options
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => props.data, () => {
  if (chart) {
    chart.data = props.data
    chart.update()
  }
}, { deep: true })
</script>

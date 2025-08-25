import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useTrainingStore } from './training'

interface WebSocketMessage {
  type: string
  data: any
}

export const useWebSocketStore = defineStore('websocket', () => {
  // State
  const connected = ref(false)
  const socket = ref<WebSocket | null>(null)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5

  // Get training store for updates
  const trainingStore = useTrainingStore()

  // Actions
  const connect = (modelId?: number) => {
    if (socket.value?.readyState === WebSocket.OPEN) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = modelId 
      ? `${protocol}//${window.location.host}/ws/training/${modelId}/`
      : `${protocol}//${window.location.host}/ws/training/`

    socket.value = new WebSocket(wsUrl)

    socket.value.onopen = () => {
      connected.value = true
      reconnectAttempts.value = 0
      console.log('WebSocket connected')
    }

    socket.value.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data)
      handleMessage(message)
    }

    socket.value.onclose = () => {
      connected.value = false
      console.log('WebSocket disconnected')
      
      // Auto-reconnect for training updates
      if (reconnectAttempts.value < maxReconnectAttempts) {
        setTimeout(() => {
          reconnectAttempts.value++
          connect(modelId)
        }, 1000 * Math.pow(2, reconnectAttempts.value))
      }
    }

    socket.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
      connected.value = false
      reconnectAttempts.value = 0
    }
  }

  const handleMessage = (message: WebSocketMessage) => {
    if (message.type === 'training_progress') {
      // Update training store with real-time data
      const data = message.data
      trainingStore.updateJobProgress(data.model_id, {
        progress_percentage: data.progress_percentage,
        current_epoch: data.current_epoch,
        total_epochs: data.total_epochs,
        current_loss: data.current_loss,
        current_accuracy: data.current_accuracy,
        status: data.status,
        updated_at: data.timestamp
      })
    }
  }

  return {
    connected,
    connect,
    disconnect,
    reconnectAttempts
  }
})

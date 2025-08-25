<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Datasets</h1>
        <p class="text-gray-600">Manage your medical literature datasets</p>
      </div>
      <RouterLink to="/datasets/create" class="btn-primary">
        <Icon name="plus" class="w-4 h-4 mr-2" />
        Create Dataset
      </RouterLink>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-8">
      <div class="flex items-center justify-center">
        <Icon name="clock" class="w-6 h-6 animate-spin text-blue-600 mr-3" />
        <span class="text-gray-600">Loading datasets...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-white rounded-lg shadow p-6">
      <div class="text-center py-8">
        <Icon name="warning" class="w-16 h-16 mx-auto mb-4 text-red-400" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Failed to Load Datasets</h3>
        <p class="text-gray-500 mb-4">{{ error }}</p>
        <button @click="() => fetchDatasets()" class="btn-primary">
          <Icon name="clock" class="w-4 h-4 mr-2" />
          Retry
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="datasets.length === 0" class="bg-white rounded-lg shadow p-6">
      <div class="text-center py-12">
        <Icon name="database" class="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Datasets Found</h3>
        <p class="text-gray-500 mb-4">Get started by creating your first medical literature dataset</p>
        <RouterLink to="/datasets/create" class="btn-primary">
          <Icon name="plus" class="w-4 h-4 mr-2" />
          Create Your First Dataset
        </RouterLink>
      </div>
    </div>

    <!-- Datasets Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="dataset in datasets"
        :key="dataset.id"
        class="bg-white rounded-lg shadow hover:shadow-md transition-shadow border border-gray-200"
      >
        <!-- Dataset Header -->
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 mb-1 truncate">
                {{ dataset.name }}
              </h3>
              <p class="text-sm text-gray-600 mb-3 line-clamp-2">
                {{ dataset.description || 'No description provided' }}
              </p>
              
              <!-- Status Badge -->
              <div class="flex items-center mb-2">
                <span
                  :class="{
                    'bg-green-100 text-green-800': dataset.is_validated,
                    'bg-yellow-100 text-yellow-800': !dataset.is_validated
                  }"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  <Icon 
                    :name="dataset.is_validated ? 'success' : 'warning'" 
                    class="w-3 h-3 mr-1" 
                  />
                  {{ dataset.is_validated ? 'Validated' : 'Pending' }}
                </span>
              </div>
            </div>
            
            <!-- Actions Dropdown -->
            <div class="ml-2">
              <button
                @click="toggleMenu(dataset.id)"
                class="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
              >
                <Icon name="cog" class="w-5 h-5" />
              </button>
              
              <!-- Dropdown Menu -->
              <div 
                v-if="activeMenu === dataset.id"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10"
              >
                <div class="py-1">
                  <RouterLink
                    :to="`/datasets/${dataset.id}`"
                    class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    @click="activeMenu = null"
                  >
                    <Icon name="view" class="w-4 h-4 mr-3" />
                    View Details
                  </RouterLink>
                  <button
                    @click="validateDataset(dataset.id)"
                    :disabled="dataset.is_validated"
                    class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50"
                  >
                    <Icon name="success" class="w-4 h-4 mr-3" />
                    Validate Dataset
                  </button>
                  <button
                    @click="confirmDelete(dataset)"
                    class="flex items-center w-full px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                  >
                    <Icon name="delete" class="w-4 h-4 mr-3" />
                    Delete Dataset
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Dataset Stats -->
        <div class="p-6">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">
                {{ dataset.total_samples.toLocaleString() }}
              </div>
              <div class="text-xs text-gray-500">Samples</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">
                {{ dataset.medical_domains?.length || 0 }}
              </div>
              <div class="text-xs text-gray-500">Domains</div>
            </div>
          </div>
          
          <!-- Medical Domains -->
          <div v-if="dataset.medical_domains && dataset.medical_domains.length > 0" class="mb-4">
            <div class="text-xs text-gray-500 mb-2">Medical Domains:</div>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="domain in dataset.medical_domains.slice(0, 3)"
                :key="domain"
                class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
              >
                {{ formatDomain(domain) }}
              </span>
              <span
                v-if="dataset.medical_domains.length > 3"
                class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-600"
              >
                +{{ dataset.medical_domains.length - 3 }} more
              </span>
            </div>
          </div>
          
          <!-- Dataset Info -->
          <div class="text-xs text-gray-500 space-y-1">
            <div class="flex justify-between">
              <span>Created:</span>
              <span>{{ formatDate(dataset.uploaded_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span>Size:</span>
              <span>{{ dataset.file_size_mb }} MB</span>
            </div>
            <div class="flex justify-between">
              <span>Format:</span>
              <span>{{ dataset.file_extension?.toUpperCase() || 'Unknown' }}</span>
            </div>
          </div>
        </div>
        
        <!-- Dataset Actions -->
        <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
          <RouterLink
            :to="`/datasets/${dataset.id}`"
            class="text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            View Details
          </RouterLink>
          <button
            @click="useForTraining(dataset)"
            :disabled="!dataset.is_validated"
            class="text-sm font-medium text-green-600 hover:text-green-700 disabled:opacity-50"
          >
            Use for Training
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination (if needed) -->
    <div v-if="totalPages > 1" class="mt-8 flex justify-center">
      <nav class="flex items-center space-x-2">
        <button
          @click="changePage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          Previous
        </button>
        
        <span class="px-3 py-2 text-sm font-medium text-gray-700">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        
        <button
          @click="changePage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          Next
        </button>
      </nav>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deleteModal.show"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Delete Dataset</h3>
        <p class="text-gray-600 mb-6">
          Are you sure you want to delete "{{ deleteModal.dataset?.name }}"? 
          This action cannot be undone and will remove all associated data.
        </p>
        
        <div class="flex justify-end space-x-3">
          <button
            @click="deleteModal.show = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="deleteDataset"
            :disabled="deleteModal.loading"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            <Icon v-if="deleteModal.loading" name="clock" class="w-4 h-4 mr-2 animate-spin" />
            Delete Dataset
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import Icon from '@/components/ui/Icon.vue'
import { useDatasetStore } from '@/stores/datasets'
import type { Dataset } from '@/types'

// Composables
const router = useRouter()
const toast = useToast()
const datasetStore = useDatasetStore()

// Reactive state
const activeMenu = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const deleteModal = ref({
  show: false,
  dataset: null as Dataset | null,
  loading: false
})

// Computed
const datasets = computed(() => datasetStore.datasets || [])
const loading = computed(() => datasetStore.isLoading)
const error = computed(() => datasetStore.error)
const totalDatasets = computed(() => datasetStore.totalDatasets)
const totalPages = computed(() => Math.ceil(totalDatasets.value / pageSize.value))

// Methods
const fetchDatasets = async (page = 1) => {
  currentPage.value = page
  await datasetStore.fetchDatasets(page, pageSize.value)
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchDatasets(page)
  }
}

const toggleMenu = (datasetId: number) => {
  activeMenu.value = activeMenu.value === datasetId ? null : datasetId
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDomain = (domain: string): string => {
  return domain.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const validateDataset = async (id: number) => {
  try {
    await datasetStore.validateDataset(id)
    toast.success('Dataset validation started')
    activeMenu.value = null
  } catch (error) {
    toast.error('Failed to start dataset validation')
  }
}

const confirmDelete = (dataset: Dataset) => {
  deleteModal.value = {
    show: true,
    dataset,
    loading: false
  }
  activeMenu.value = null
}

const deleteDataset = async () => {
  if (!deleteModal.value.dataset) return
  
  deleteModal.value.loading = true
  try {
    await datasetStore.deleteDataset(deleteModal.value.dataset.id)
    toast.success('Dataset deleted successfully')
    deleteModal.value.show = false
    
    // Refresh the datasets list
    await fetchDatasets(currentPage.value)
  } catch (error) {
    toast.error('Failed to delete dataset')
  } finally {
    deleteModal.value.loading = false
  }
}

const useForTraining = (dataset: Dataset) => {
  router.push(`/models/create?dataset=${dataset.id}`)
}

// Close menu when clicking outside
const handleClickOutside = (event: Event) => {
  if (activeMenu.value && !(event.target as Element).closest('.relative')) {
    activeMenu.value = null
  }
}

// Lifecycle
onMounted(async () => {
  await fetchDatasets()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors inline-flex items-center;
}
</style>

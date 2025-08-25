<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Create New Dataset</h1>
      <p class="mt-2 text-gray-600">Upload medical literature data for AI model training</p>
    </div>

    <!-- Main Form -->
    <form @submit.prevent="handleSubmit" class="space-y-8">
      <!-- Basic Information -->
      <div class="medical-card">
        <div class="medical-card-header">
          <h2 class="text-xl font-semibold text-gray-900">Basic Information</h2>
          <p class="text-sm text-gray-600">Provide basic details about your dataset</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Dataset Name -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
              Dataset Name *
            </label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="input-field"
              placeholder="e.g., Medical Literature Collection 2024"
              :class="{ 'border-red-500': errors.name }"
            />
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>

          <!-- Medical Domains -->
          <div>
            <label for="domains" class="block text-sm font-medium text-gray-700 mb-2">
              Primary Medical Domains
            </label>
            <select
              id="domains"
              v-model="form.medical_domains"
              multiple
              class="input-field min-h-[120px]"
            >
              <option
                v-for="domain in medicalDomains"
                :key="domain"
                :value="domain"
                class="py-1"
              >
                {{ formatDomain(domain) }}
              </option>
            </select>
            <p class="mt-1 text-sm text-gray-500">Hold Ctrl/Cmd to select multiple domains</p>
          </div>
        </div>

        <!-- Description -->
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            id="description"
            :value="form.description || ''"
            @input="form.description = ($event.target as HTMLTextAreaElement).value"
            rows="3"
            class="input-field"
            placeholder="Describe the dataset contents, sources, and intended use cases..."
          />
        </div>
      </div>

      <!-- File Upload -->
      <div class="medical-card">
        <div class="medical-card-header">
          <h2 class="text-xl font-semibold text-gray-900">Data Upload</h2>
          <p class="text-sm text-gray-600">Upload your medical literature data file</p>
        </div>

        <!-- Supported Formats -->
        <div class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 class="text-sm font-medium text-blue-900 mb-1">Supported Formats</h4>
          <p class="text-sm text-blue-700">
            CSV, JSON, Excel (XLS, XLSX) • Max size: 100MB
          </p>
          <p class="text-xs text-blue-600 mt-1">
            Required columns: title, abstract, medical_domains (optional)
          </p>
        </div>

        <!-- File Upload Area -->
        <div
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleFileDrop"
          class="border-2 border-dashed rounded-lg p-8 text-center transition-colors"
          :class="{
            'border-blue-400 bg-blue-50': isDragging,
            'border-gray-300': !isDragging && !selectedFile,
            'border-green-400 bg-green-50': selectedFile && !errors.file
          }"
        >
          <Icon 
            :name="selectedFile ? 'document' : 'plus'" 
            class="w-12 h-12 mx-auto text-gray-400 mb-4"
          />
          
          <div v-if="!selectedFile">
            <p class="text-lg font-medium text-gray-900 mb-2">
              Drop your dataset file here
            </p>
            <p class="text-gray-600 mb-4">or</p>
            <button
              type="button"
              @click="triggerFileInput"
              class="btn-primary inline-flex items-center"
            >
              <Icon name="plus" class="w-4 h-4 mr-2" />
              Choose File
            </button>
            <input
              ref="fileInputRef"
              type="file"
              accept=".csv,.json,.xlsx,.xls"
              class="hidden"
              @change="handleFileSelect"
            />
          </div>

          <!-- Selected File Info -->
          <div v-else class="text-left max-w-md mx-auto">
            <div class="flex items-start space-x-3">
              <Icon name="document" class="w-6 h-6 text-green-600 mt-1" />
              <div class="flex-1">
                <p class="font-medium text-gray-900">{{ selectedFile.name }}</p>
                <p class="text-sm text-gray-600">
                  {{ formatFileSize(selectedFile.size) }} • {{ getFileType(selectedFile.name) }}
                </p>
                <div class="mt-2 flex space-x-2">
                  <button
                    type="button"
                    @click="removeFile"
                    class="text-sm text-red-600 hover:text-red-700"
                  >
                    Remove
                  </button>
                  <button
                    type="button"
                    @click="triggerFileInput"
                    class="text-sm text-blue-600 hover:text-blue-700"
                  >
                    Replace
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <p v-if="errors.file" class="mt-2 text-sm text-red-600">{{ errors.file }}</p>

        <!-- Upload Progress -->
        <div v-if="uploadProgress > 0 && uploadProgress < 100" class="mt-4">
          <div class="flex justify-between text-sm text-gray-700 mb-1">
            <span>Uploading...</span>
            <span>{{ uploadProgress }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${uploadProgress}%` }"
            />
          </div>
        </div>
      </div>

      <!-- Advanced Options -->
      <div class="medical-card">
        <div class="medical-card-header">
          <h2 class="text-xl font-semibold text-gray-900">Advanced Options</h2>
          <p class="text-sm text-gray-600">Configure data processing and validation</p>
        </div>

        <div class="space-y-4">
          <!-- Validation Options -->
          <div>
            <h4 class="text-sm font-medium text-gray-900 mb-3">Data Validation</h4>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="(form as any).validate_structure"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700">
                  Validate data structure and format
                </span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="(form as any).check_duplicates"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700">
                  Check for duplicate entries
                </span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="(form as any).extract_domains"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700">
                  Auto-extract medical domains from text
                </span>
              </label>
            </div>
          </div>

          <!-- Processing Options -->
          <div>
            <h4 class="text-sm font-medium text-gray-900 mb-3">Text Processing</h4>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="(form as any).preprocess_text"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700">
                  Clean and preprocess text (remove special characters, normalize)
                </span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="(form as any).extract_keywords"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700">
                  Extract medical keywords and entities
                </span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-between pt-6 border-t border-gray-200">
        <button
          type="button"
          @click="$router.push('/datasets')"
          class="btn-secondary"
        >
          Cancel
        </button>

        <div class="flex space-x-3">
          <button
            type="button"
            @click="saveDraft"
            class="btn-outline"
            :disabled="loading || !form.name"
          >
            Save Draft
          </button>
          <button
            type="submit"
            class="btn-primary"
            :disabled="loading || !isFormValid"
          >
            <Icon v-if="loading" name="clock" class="w-4 h-4 mr-2 animate-spin" />
            <Icon v-else name="plus" class="w-4 h-4 mr-2" />
            {{ loading ? 'Creating...' : 'Create Dataset' }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import Icon from '@/components/ui/Icon.vue'
import { useDatasetStore } from '@/stores/datasets'
import { systemApi } from '@/utils/api'
// import type { DatasetCreateRequest } from '@/types'

// Composables
const router = useRouter()
const toast = useToast()
const datasetStore = useDatasetStore()

// Reactive state
const loading = ref(false)
const uploadProgress = ref(0)
const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const fileInputRef = ref<HTMLInputElement>()
const medicalDomains = ref<string[]>([])

// Form data
const form = ref({
  name: '',
  description: '',
  medical_domains: [],
  // validate_structure: true,  // Not in API type
  // check_duplicates: true,  // Not in API type
  // extract_domains: false,   // Not in API type
  // preprocess_text: true,    // Not in API type
  // extract_keywords: false   // Not in API type
})

// Form validation
const errors = ref<Record<string, string>>({})

// Computed
const isFormValid = computed(() => {
  return form.value.name.trim() && selectedFile.value && !Object.keys(errors.value).length
})

// Methods
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.name.trim()) {
    errors.value.name = 'Dataset name is required'
  } else if (form.value.name.length < 3) {
    errors.value.name = 'Dataset name must be at least 3 characters'
  }
  
  if (!selectedFile.value) {
    errors.value.file = 'Please select a data file'
  } else {
    const maxSize = 100 * 1024 * 1024 // 100MB
    if (selectedFile.value.size > maxSize) {
      errors.value.file = 'File size must be less than 100MB'
    }
    
    const allowedTypes = ['.csv', '.json', '.xlsx', '.xls']
    const fileExtension = '.' + selectedFile.value.name.split('.').pop()?.toLowerCase()
    if (!allowedTypes.includes(fileExtension)) {
      errors.value.file = 'File must be CSV, JSON, or Excel format'
    }
  }
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    validateForm()
  }
}

const handleFileDrop = (event: DragEvent) => {
  isDragging.value = false
  
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedFile.value = event.dataTransfer.files[0]
    validateForm()
  }
}

const removeFile = () => {
  selectedFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
  delete errors.value.file
}

const formatFileSize = (bytes: number): string => {
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(1)} MB`
}

const getFileType = (filename: string): string => {
  const extension = filename.split('.').pop()?.toUpperCase()
  return extension || 'Unknown'
}

const formatDomain = (domain: string): string => {
  return domain.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const handleSubmit = async () => {
  validateForm()
  
  if (!isFormValid.value) {
    toast.error('Please fix the form errors before submitting')
    return
  }
  
  loading.value = true
  uploadProgress.value = 0
  
  try {
    // Create dataset with file upload
    const datasetData = {
      name: form.value.name,
      description: form.value.description || '',
      file: selectedFile.value!,
      medical_domains: form.value.medical_domains
    }
    
    const newDataset = await datasetStore.createDataset(datasetData as any, (progress) => {
      uploadProgress.value = progress
    })
    
    toast.success('Dataset created and file uploaded successfully!')
    
    // Redirect to dataset detail or list
    router.push(`/datasets/${newDataset.id}`)
    
  } catch (error: any) {
    console.error('Failed to create dataset:', error)
    const errorMessage = error.message || error.response?.data?.message || 'Failed to create dataset. Please try again.'
    toast.error(errorMessage)
    uploadProgress.value = 0
  } finally {
    loading.value = false
  }
}

const saveDraft = async () => {
  // Implement draft saving functionality
  toast.info('Draft saving functionality will be implemented soon')
}

// Lifecycle
onMounted(async () => {
  try {
    medicalDomains.value = await systemApi.getMedicalDomains()
  } catch (error) {
    console.error('Failed to load medical domains:', error)
    // Fallback domains
    medicalDomains.value = [
      'cardiology', 'neurology', 'oncology', 'gastroenterology',
      'endocrinology', 'respiratory', 'infectious_disease', 'dermatology',
      'psychiatry', 'orthopedics', 'radiology', 'pathology'
    ]
  }
})
</script>

<style scoped>
.input-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.medical-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 p-6;
}

.medical-card-header {
  @apply mb-6 pb-4 border-b border-gray-200;
}

.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors inline-flex items-center;
}

.btn-secondary {
  @apply bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors;
}

.btn-outline {
  @apply border border-gray-300 hover:bg-gray-50 text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors;
}
</style>

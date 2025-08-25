// API Response Types for MedLitBot Django Backend

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  message?: string
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results?: T[]  // Django REST framework standard
  items?: T[]    // Django Ninja pagination format
}

// Dataset Types
export interface Dataset {
  id: number
  name: string
  description: string
  file_path: string
  uploaded_at: string
  updated_at: string
  total_samples: number
  is_validated: boolean
  validation_errors: Record<string, unknown> | null
  medical_domains: string[]
  file_size_mb: number
  file_extension: string | null
  unique_domains_count: number
  avg_title_length: number
  avg_abstract_length: number
  domain_distribution?: Record<string, number>
}

export interface DatasetSample {
  id: number
  dataset: number
  title: string
  abstract: string
  authors: string
  publication_year: number
  doi: string
  journal?: string
  medical_domains: string[]
  created_at: string
}

export interface DatasetCreateRequest {
  name: string
  description?: string
  file: File
  medical_domains?: string[]
}

// ML Model Types
export interface MLModel {
  id: number
  name: string
  model_type: ModelType
  dataset: number
  dataset_name?: string
  description: string
  status: ModelStatus
  is_trained: boolean
  created_at: string
  updated_at: string
  
  // Training parameters
  num_epochs: number | null
  best_epoch: number | null
  learning_rate: number | null
  batch_size: number | null
  
  // Performance metrics
  accuracy: number | null
  f1_score: number | null
  precision: number | null
  recall: number | null
  
  // Training details
  training_time_minutes: number | null
  training_started_at: string | null
  training_completed_at: string | null
  
  // Additional metrics
  domain_performance: Record<string, DomainMetrics> | null
  confusion_matrix: number[][] | null
  hyperparameters: Record<string, unknown>
  
  // Backend computed properties
  model_size_mb: number
  is_training_complete: boolean
  is_deployed: boolean
  
  // Model parameters and configuration
  parameters: Record<string, unknown>
}

export type ModelType = 
  | 'bert'
  | 'biobert'
  | 'clinicalbert'
  | 'scibert'
  | 'pubmedbert'
  | 'gemma2-2b'
  | 'traditional'
  | 'hybrid'
  | 'custom'

export type ModelStatus = 
  | 'created'
  | 'training'
  | 'trained'
  | 'failed'
  | 'optimizing'

export interface DomainMetrics {
  f1_score: number
  precision: number
  recall: number
  support: number
}

export interface ModelParameters {
  base_model?: string
  training_split?: number
  validation_split?: number
  test_split?: number
  hyperparameters?: {
    learning_rate?: string
    batch_size?: number
    epochs?: number
    max_sequence_length?: number
  }
  use_early_stopping?: boolean
  use_class_weights?: boolean
  enable_gradient_checkpointing?: boolean
  enable_hyperparameter_optimization?: boolean
  optimization_params?: {
    n_trials?: number
    timeout?: number
  }
}

export interface MLModelCreateRequest {
  name: string
  model_type: ModelType
  dataset_id: number
  description?: string
  parameters?: ModelParameters
}

// Training Job Types
export interface TrainingJob {
  id: number
  model: number
  status: TrainingStatus
  progress_percentage: number
  current_epoch: number
  total_epochs: number
  current_loss: number | null
  current_accuracy: number | null
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  celery_task_id: string
  model_id?: number
  updated_at?: string
}

export type TrainingStatus = 
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'

export interface StartTrainingRequest {
  total_epochs?: number
  learning_rate?: number
  batch_size?: number
  validation_split?: number
}

// Classification Types
export interface ClassificationResult {
  id: number
  model: number
  model_name?: string
  title: string
  abstract: string
  predicted_domains: string[]
  confidence_scores: Record<string, number>
  all_domain_scores: Record<string, number>
  prediction_threshold: number
  inference_time_ms: number
  created_at: string
}

export interface ClassificationRequest {
  title: string
  abstract: string
  threshold?: number
}

export interface BatchClassificationRequest {
  articles: Array<{
    title: string
    abstract: string
  }>
  threshold?: number
}

export interface ClassificationResponse {
  predicted_domains: string[]
  confidence_scores: Record<string, number>
  all_domain_scores: Record<string, number>
  inference_time_ms: number
}

export interface BatchClassificationResponse {
  results: Array<{
    article_index: number
    predicted_domains: string[]
    confidence_scores: Record<string, number>
    inference_time_ms: number
  }>
  total_inference_time_ms: number
}

// Hyperparameter Optimization Types
export interface HyperparameterOptimizationRequest {
  n_trials?: number
  timeout?: number
  metric?: OptimizationMetric
}

export type OptimizationMetric = 
  | 'f1_macro'
  | 'f1_micro'
  | 'accuracy'
  | 'precision'
  | 'recall'

export interface HyperparameterOptimizationResponse {
  status: string
  model_id: number | null
  best_params: Record<string, unknown> | null
  best_value: number | null
  optimization_metric: string | null
  n_trials: number | null
  message: string
}

// Model Comparison Types
export interface ModelComparison {
  id: number
  name: string
  description: string
  ml_models: number[]
  comparison_metrics: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface ModelComparisonCreateRequest {
  name: string
  description?: string
  model_ids: number[]
}

// Error Response Types
export interface ErrorResponse {
  error: string
  details?: Record<string, unknown>
  field_errors?: Record<string, string[]>
}

// Statistics Types
export interface SystemStats {
  total_datasets: number
  total_models: number
  total_predictions: number
  trained_models: number
  active_training_jobs: number
  validated_datasets: number
  recent_activity: ActivityItem[]
}

export interface ActivityItem {
  type: 'dataset_created' | 'model_trained' | 'prediction_made' | 'training_started'
  title: string
  description: string
  timestamp: string
  metadata?: Record<string, unknown>
}

// Chart Data Types
export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor: string | string[]
  borderColor?: string | string[]
  fill?: boolean
}

export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: string
  data: unknown
  timestamp: string
}

export interface TrainingProgressMessage extends WebSocketMessage {
  type: 'training_progress'
  data: {
    model_id: number
    progress: number
    current_epoch: number
    total_epochs: number
    current_loss: number | null
    current_accuracy: number | null
    status: TrainingStatus
  }
}

export interface ModelStatusMessage extends WebSocketMessage {
  type: 'model_status'
  data: {
    model_id: number
    status: ModelStatus
    message?: string
  }
}

// Medical Domain Types
export const MEDICAL_DOMAINS = [
  'cardiology',
  'neurology', 
  'oncology',
  'respiratory',
  'endocrinology',
  'infectious_disease',
  'gastroenterology',
  'rheumatology',
  'dermatology',
  'psychiatry',
  'pediatrics',
  'radiology',
  'surgery',
  'emergency_medicine',
  'anesthesiology'
] as const

export type MedicalDomain = typeof MEDICAL_DOMAINS[number]

export interface DomainInfo {
  key: MedicalDomain
  label: string
  color: string
  description: string
  icon?: string
}

// File Upload Types
export interface FileUploadResponse {
  file_path: string
  file_size: number
  file_name: string
  upload_url?: string
}

// Notification Types
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
  actions?: Array<{
    label: string
    action: () => void
  }>
}

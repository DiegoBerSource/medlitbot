// Re-export all API types
export * from './api'

// Vue Router module augmentation
declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    roles?: string[]
    breadcrumb?: BreadcrumbItem[]
    showInSidebar?: boolean
    icon?: string
    order?: number
  }
}

// Vue-specific types
export interface RouteMetaData {
  title?: string
  requiresAuth?: boolean
  roles?: string[]
  breadcrumb?: BreadcrumbItem[]
  showInSidebar?: boolean
  icon?: string
  order?: number
}

export interface BreadcrumbItem {
  label: string
  to?: string
  active?: boolean
}

// Form types
export interface FormField<T = string> {
  value: T
  error: string | null
  touched: boolean
  required?: boolean
  validator?: (value: T) => string | null
}

export interface FormState {
  [key: string]: FormField
}

// Table types
export interface TableColumn<T = unknown> {
  key: keyof T | string
  label: string
  sortable?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
  formatter?: (value: unknown, row: T) => string | number
  render?: (value: unknown, row: T) => string
}

export interface TableOptions {
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  page?: number
  pageSize?: number
  search?: string
  filters?: Record<string, unknown>
}

// Component prop types
export interface LoadingState {
  isLoading: boolean
  error: string | null
  data: unknown
}

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'medical'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  icon?: string
  iconPosition?: 'left' | 'right'
}

export interface ModalProps {
  isOpen: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  closeable?: boolean
  persistent?: boolean
}

// Chart types
export interface ChartOptions {
  responsive?: boolean
  maintainAspectRatio?: boolean
  plugins?: {
    legend?: {
      display?: boolean
      position?: 'top' | 'bottom' | 'left' | 'right'
    }
    tooltip?: {
      enabled?: boolean
      mode?: string
    }
  }
  scales?: {
    x?: {
      display?: boolean
      title?: {
        display?: boolean
        text?: string
      }
    }
    y?: {
      display?: boolean
      beginAtZero?: boolean
      title?: {
        display?: boolean
        text?: string
      }
    }
  }
}

// Theme types
export interface ThemeConfig {
  primaryColor: string
  secondaryColor: string
  backgroundColor: string
  textColor: string
  borderColor: string
  borderRadius: string
  fontSize: {
    xs: string
    sm: string
    base: string
    lg: string
    xl: string
  }
  spacing: {
    xs: string
    sm: string
    md: string
    lg: string
    xl: string
  }
}

// Environment types
export interface AppConfig {
  apiBaseUrl: string
  wsUrl: string
  appTitle: string
  appVersion: string
  environment: 'development' | 'production' | 'staging'
  features: {
    realTimeUpdates: boolean
    notifications: boolean
    analytics: boolean
    offlineMode: boolean
  }
}

// Store types
export interface BaseState {
  loading: boolean
  error: string | null
  lastUpdated: Date | null
}

// Filter types
export interface FilterOption<T = string> {
  label: string
  value: T
  count?: number
  selected?: boolean
}

export interface DateRange {
  start: Date | null
  end: Date | null
}

export interface NumericRange {
  min: number | null
  max: number | null
}

// Medical AI specific types
export interface PredictionSettings {
  threshold: number
  modelId: number | null
  includeDomainScores: boolean
  maxResults: number
}

export interface TrainingSettings {
  epochs: number
  learningRate: number
  batchSize: number
  validationSplit: number
  optimizer: 'adam' | 'sgd' | 'adamw'
  scheduler: 'linear' | 'cosine' | 'constant'
}

export interface ModelMetrics {
  accuracy: number
  f1Score: number
  precision: number
  recall: number
  trainingTime: number
  inferenceTime: number
}

export interface ComparisonResult {
  modelId: number
  modelName: string
  metrics: ModelMetrics
  rank: number
  improvement: number
}

// Utility types
export type Nullable<T> = T | null
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// Event types
export interface CustomEvent<T = unknown> {
  type: string
  payload: T
  timestamp: Date
}

// Validation types
export interface ValidationRule<T = unknown> {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: T) => string | null
  min?: number
  max?: number
}

export interface ValidationResult {
  isValid: boolean
  errors: Record<string, string[]>
  warnings?: Record<string, string[]>
}

// Toast/Notification types
export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastOptions {
  title?: string
  description?: string
  duration?: number
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
  persistent?: boolean
  actions?: Array<{
    label: string
    action: () => void
  }>
}

// Layout types
export interface SidebarItem {
  id: string
  label: string
  icon?: string
  route?: string
  children?: SidebarItem[]
  expanded?: boolean
  badge?: {
    text: string
    variant: 'primary' | 'success' | 'warning' | 'error'
  }
  permissions?: string[]
}

export interface LayoutConfig {
  sidebarCollapsed: boolean
  showBreadcrumbs: boolean
  theme: 'light' | 'dark' | 'auto'
  density: 'compact' | 'comfortable' | 'spacious'
}

// Search types
export interface SearchResult<T = unknown> {
  id: string
  title: string
  description?: string
  category?: string
  score: number
  data: T
  highlighted?: {
    title?: string
    description?: string
  }
}

export interface SearchOptions {
  query: string
  category?: string
  limit?: number
  offset?: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  filters?: Record<string, unknown>
}

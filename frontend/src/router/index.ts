import type { RouteRecordRaw } from 'vue-router'

// Import views (lazy-loaded for better performance)
const Dashboard = () => import('@/views/Dashboard.vue')
const Datasets = () => import('@/views/datasets/Datasets.vue')
const DatasetDetail = () => import('@/views/datasets/DatasetDetail.vue')
const DatasetCreate = () => import('@/views/datasets/DatasetCreate.vue')
const Models = () => import('@/views/models/Models.vue')
const ModelDetail = () => import('@/views/models/ModelDetail.vue')
const ModelCreate = () => import('@/views/models/ModelCreate.vue')
const ModelEdit = () => import('@/views/models/ModelEdit.vue')
const ModelTraining = () => import('@/views/models/ModelTraining.vue')
const Classification = () => import('@/views/classification/Classification.vue')
const ClassificationBatch = () => import('@/views/classification/ClassificationBatch.vue')
const ClassificationHistory = () => import('@/views/classification/ClassificationHistory.vue')
const Analytics = () => import('@/views/analytics/Analytics.vue')
const ModelComparison = () => import('@/views/analytics/ModelComparison.vue')
const Settings = () => import('@/views/settings/Settings.vue')
const Profile = () => import('@/views/settings/Profile.vue')
const Login = () => import('@/views/auth/Login.vue')
const NotFound = () => import('@/views/errors/NotFound.vue')

// Route definitions with enhanced metadata
export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard',
      showInSidebar: true,
      icon: 'home',
      order: 1,
      breadcrumb: [
        { label: 'Dashboard', active: true }
      ]
    }
  },
  
  // Dataset routes
  {
    path: '/datasets',
    name: 'datasets',
    component: Datasets,
    meta: {
      title: 'Datasets',
      showInSidebar: true,
      icon: 'database',
      order: 2,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Datasets', active: true }
      ]
    }
  },
  {
    path: '/datasets/create',
    name: 'dataset-create',
    component: DatasetCreate,
    meta: {
      title: 'Create Dataset',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Datasets', to: '/datasets' },
        { label: 'Create', active: true }
      ]
    }
  },
  {
    path: '/datasets/:id',
    name: 'dataset-detail',
    component: DatasetDetail,
    meta: {
      title: 'Dataset Details',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Datasets', to: '/datasets' },
        { label: 'Details', active: true }
      ]
    },
    props: route => ({ id: Number(route.params.id) })
  },
  
  // Model routes
  {
    path: '/models',
    name: 'models',
    component: Models,
    meta: {
      title: 'ML Models',
      showInSidebar: true,
      icon: 'cpu',
      order: 3,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Models', active: true }
      ]
    }
  },
  {
    path: '/models/create',
    name: 'model-create',
    component: ModelCreate,
    meta: {
      title: 'Create Model',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Models', to: '/models' },
        { label: 'Create', active: true }
      ]
    }
  },
  {
    path: '/models/:id',
    name: 'model-detail',
    component: ModelDetail,
    meta: {
      title: 'Model Details',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Models', to: '/models' },
        { label: 'Details', active: true }
      ]
    },
    props: route => ({ id: Number(route.params.id) })
  },
  {
    path: '/models/:id/edit',
    name: 'model-edit',
    component: ModelEdit,
    meta: {
      title: 'Edit Model',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Models', to: '/models' },
        { label: 'Edit', active: true }
      ]
    },
    props: route => ({ id: Number(route.params.id) })
  },
  {
    path: '/models/:id/training',
    name: 'model-training',
    component: ModelTraining,
    meta: {
      title: 'Model Training',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Models', to: '/models' },
        { label: 'Training', active: true }
      ]
    },
    props: route => ({ id: Number(route.params.id) })
  },
  
  // Classification routes
  {
    path: '/classification',
    name: 'classification',
    component: Classification,
    meta: {
      title: 'Classification',
      showInSidebar: true,
      icon: 'brain',
      order: 4,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Classification', active: true }
      ]
    }
  },
  {
    path: '/classification/batch',
    name: 'classification-batch',
    component: ClassificationBatch,
    meta: {
      title: 'Batch Classification',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Classification', to: '/classification' },
        { label: 'Batch', active: true }
      ]
    }
  },
  {
    path: '/classification/history',
    name: 'classification-history',
    component: ClassificationHistory,
    meta: {
      title: 'Classification History',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Classification', to: '/classification' },
        { label: 'History', active: true }
      ]
    }
  },
  
  // Analytics routes
  {
    path: '/analytics',
    name: 'analytics',
    component: Analytics,
    meta: {
      title: 'Analytics',
      showInSidebar: true,
      icon: 'chart-bar',
      order: 5,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Analytics', active: true }
      ]
    }
  },
  {
    path: '/analytics/comparison',
    name: 'model-comparison',
    component: ModelComparison,
    meta: {
      title: 'Model Comparison',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Analytics', to: '/analytics' },
        { label: 'Model Comparison', active: true }
      ]
    }
  },
  
  // Settings routes
  {
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: {
      title: 'Settings',
      showInSidebar: true,
      icon: 'cog',
      order: 10,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Settings', active: true }
      ]
    }
  },
  {
    path: '/settings/profile',
    name: 'profile',
    component: Profile,
    meta: {
      title: 'Profile',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: 'Settings', to: '/settings' },
        { label: 'Profile', active: true }
      ]
    }
  },
  
  // Auth routes
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: {
      title: 'Login',
      showInSidebar: false,
      showHeader: false,
      showFooter: false,
      showBreadcrumbs: false
    }
  },
  
  // Error routes
  {
    path: '/404',
    name: 'not-found',
    component: NotFound,
    meta: {
      title: 'Page Not Found',
      showInSidebar: false,
      breadcrumb: [
        { label: 'Home', to: '/' },
        { label: '404', active: true }
      ]
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

// Helper functions for route management
export const getSidebarRoutes = () => {
  return routes
    .filter(route => route.meta?.showInSidebar)
    .sort((a, b) => {
      const aOrder = typeof a.meta?.order === 'number' ? a.meta.order : 999
      const bOrder = typeof b.meta?.order === 'number' ? b.meta.order : 999
      return aOrder - bOrder
    })
}

export const getRouteByName = (name: string) => {
  return routes.find(route => route.name === name)
}

export const getBreadcrumbsForRoute = (routeName: string) => {
  const route = getRouteByName(routeName)
  return route?.meta?.breadcrumb || []
}

// Route guards and utilities
export const requiresAuth = (to: any, _from: any, next: any) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    next()
  } else {
    next({ name: 'login', query: { redirect: to.fullPath } })
  }
}

export const redirectIfAuthenticated = (_to: any, _from: any, next: any) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
}

// Medical domain route helpers
export const MEDICAL_DOMAIN_ROUTES = {
  cardiology: '/classification?domain=cardiology',
  neurology: '/classification?domain=neurology',
  oncology: '/classification?domain=oncology',
  respiratory: '/classification?domain=respiratory',
  endocrinology: '/classification?domain=endocrinology',
  infectious_disease: '/classification?domain=infectious_disease',
  gastroenterology: '/classification?domain=gastroenterology',
  rheumatology: '/classification?domain=rheumatology',
  dermatology: '/classification?domain=dermatology',
  psychiatry: '/classification?domain=psychiatry'
} as const

// Model type route helpers
export const MODEL_TYPE_ROUTES = {
  biobert: '/models?type=biobert',
  clinicalbert: '/models?type=clinicalbert',
  scibert: '/models?type=scibert',
  traditional: '/models?type=traditional',
  hybrid: '/models?type=hybrid'
} as const

// Quick navigation helpers
export const QUICK_ACTIONS = [
  {
    name: 'Create Dataset',
    route: '/datasets/create',
    icon: 'plus',
    description: 'Upload and create a new medical literature dataset'
  },
  {
    name: 'Train Model',
    route: '/models/create',
    icon: 'academic-cap',
    description: 'Create and train a new AI classification model'
  },
  {
    name: 'Classify Article',
    route: '/classification',
    icon: 'document-text',
    description: 'Classify medical literature using trained models'
  },
  {
    name: 'View Analytics',
    route: '/analytics',
    icon: 'chart-bar',
    description: 'Analyze model performance and system metrics'
  }
] as const

// Export for use in components
export default routes

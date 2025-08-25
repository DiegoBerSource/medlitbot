# 🏥 MedLitBot Frontend

**Vue 3 + TypeScript + Vite - Modern Medical AI Interface**

A cutting-edge Vue 3 frontend application for MedLitBot's medical literature AI classification system, built with modern edge technologies and best practices.

## 🚀 **Technology Stack**

### **Core Framework**
- **Vue 3.4+** with Composition API
- **TypeScript 5.3+** for type safety
- **Vite 5.0+** for lightning-fast development

### **State Management & Routing**
- **Pinia 2.1+** for reactive state management
- **Vue Router 4.2+** for SPA navigation
- **@vueuse/core** for composition utilities

### **UI & Styling**
- **Tailwind CSS 3.4+** with custom medical theme
- **HeadlessUI** for accessible components
- **@heroicons/vue** for consistent iconography
- **Custom medical-grade color palette**

### **Data Visualization**
- **Chart.js 4.4+** for interactive charts
- **Vue-ChartJS 5.3+** for Vue integration
- **Medical domain-specific visualizations**

### **API & Real-time**
- **Axios 1.6+** with interceptors and error handling
- **Socket.io Client 4.7+** for WebSocket connections
- **@tanstack/vue-query** for server state management

### **Developer Experience**
- **ESLint + Prettier** for code quality
- **TypeScript strict mode** with comprehensive types
- **Vite PWA Plugin** for offline capabilities
- **Hot Module Replacement** for instant updates

## 📁 **Project Structure**

```
frontend/
├── public/                 # Static assets
│   ├── favicon.ico
│   ├── manifest.json      # PWA manifest
│   └── pwa-*.png         # PWA icons
├── src/
│   ├── assets/           # Application assets
│   │   ├── css/         # Tailwind styles
│   │   ├── images/      # Image assets
│   │   └── icons/       # Custom icons
│   ├── components/      # Vue components
│   │   ├── ui/         # Reusable UI components
│   │   ├── layout/     # Layout components
│   │   ├── charts/     # Chart components
│   │   ├── forms/      # Form components
│   │   └── modals/     # Modal components
│   ├── composables/    # Vue 3 composables
│   ├── stores/         # Pinia stores
│   │   ├── datasets.ts
│   │   ├── models.ts
│   │   ├── classification.ts
│   │   └── system.ts
│   ├── types/          # TypeScript definitions
│   │   ├── api.ts      # API types
│   │   └── index.ts    # Global types
│   ├── utils/          # Utility functions
│   │   ├── api.ts      # API client
│   │   ├── chart.ts    # Chart utilities
│   │   └── validation.ts
│   ├── views/          # Page components
│   │   ├── Dashboard.vue
│   │   ├── datasets/
│   │   ├── models/
│   │   └── classification/
│   ├── router/         # Vue Router config
│   ├── App.vue         # Root component
│   └── main.ts         # Application entry
├── index.html          # HTML template
├── vite.config.ts      # Vite configuration
├── tailwind.config.js  # Tailwind configuration
├── tsconfig.json       # TypeScript configuration
└── package.json        # Dependencies
```

## 🛠️ **Quick Start**

### **Prerequisites**
- Node.js 18+ 
- npm, yarn, or pnpm
- MedLitBot Django backend running on port 8000

### **Installation**

```bash
# Clone and navigate to frontend
cd frontend

# Install dependencies (choose one)
npm install
# or
yarn install
# or  
pnpm install

# Start development server
npm run dev
```

### **Automated Setup**

```bash
# Run the automated setup script
./frontend_setup.sh
```

The app will be available at **http://localhost:3000**

## 📜 **Available Scripts**

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Build optimized production bundle |
| `npm run preview` | Preview production build locally |
| `npm run type-check` | Run TypeScript type checking |
| `npm run lint` | Run ESLint with auto-fix |
| `npm run format` | Format code with Prettier |

## 🎨 **UI Components & Features**

### **Medical-Specific Components**
- **DatasetCard** - Display medical literature datasets
- **ModelCard** - Show AI model information and metrics  
- **ClassificationResult** - Display prediction results
- **TrainingProgress** - Real-time training visualization
- **DomainBadges** - Medical specialty indicators
- **ConfidenceMeter** - Visual confidence scores

### **Chart Components**
- **ModelPerformanceRadar** - Multi-metric model comparison
- **DatasetDistribution** - Sample distribution visualization  
- **TrainingHistory** - Loss and accuracy curves
- **DomainAnalytics** - Medical domain statistics

### **Interactive Features**
- **Real-time Updates** via WebSocket
- **Progressive Web App** with offline support
- **Responsive Design** for all devices
- **Keyboard Shortcuts** for power users
- **Dark/Light Theme** support

## 🔌 **API Integration**

### **Django Backend Integration**

The frontend seamlessly integrates with the Django backend:

```typescript
// API endpoints automatically configured
const API_ENDPOINTS = {
  datasets: '/api/datasets/',
  models: '/api/classification/models/',
  predictions: '/api/classification/predictions/',
  training: '/api/training/',
  analytics: '/dashboard/api/chart-data/'
}
```

### **Type-Safe API Client**

```typescript
// Fully typed API calls
import { datasetApi } from '@/utils/api'

// Create dataset with type safety
const dataset = await datasetApi.createDataset({
  name: 'Medical Research Papers',
  description: 'Latest cardiovascular research',
  file: selectedFile,
  medical_domains: ['cardiology', 'surgery']
})
```

### **Real-time Features**

```typescript
// WebSocket integration for live updates
import { useWebSocketStore } from '@/stores/websocket'

const wsStore = useWebSocketStore()

// Listen for training progress
wsStore.subscribe('training_progress', (data) => {
  updateTrainingProgress(data.model_id, data.progress)
})
```

## 🎯 **Key Features**

### **📊 Dashboard**
- **System Overview** with real-time statistics
- **Recent Activity** feed
- **Quick Actions** for common tasks
- **Performance Metrics** visualization

### **📚 Dataset Management**
- **Upload & Validation** of medical literature
- **Sample Preview** with pagination
- **Domain Classification** statistics
- **Batch Processing** capabilities

### **🤖 AI Model Management** 
- **Model Creation** with various architectures
- **Training Progress** monitoring
- **Hyperparameter Optimization** with Optuna
- **Model Comparison** and benchmarking

### **🧠 Classification Interface**
- **Single Article** classification
- **Batch Processing** for multiple articles
- **Confidence Scoring** visualization
- **Results Export** functionality

### **📈 Analytics & Insights**
- **Performance Dashboards** with interactive charts
- **Training History** analysis
- **Model Comparison** tools
- **Medical Domain** analytics

## 🔧 **Configuration**

### **Environment Variables**

Create `.env` file in the frontend directory:

```bash
# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000/ws

# App Configuration  
VITE_APP_TITLE=MedLitBot - Medical Literature AI
VITE_APP_VERSION=1.0.0

# Features
VITE_ENABLE_PWA=true
VITE_ENABLE_REAL_TIME=true
VITE_ENABLE_ANALYTICS=false
```

### **Tailwind Theme Customization**

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        medical: {
          50: '#f0f9ff',
          500: '#0ea5e9', 
          600: '#0284c7'
        }
      }
    }
  }
}
```

## 🔐 **Authentication & Security**

```typescript
// JWT token handling
const authStore = useAuthStore()

// Auto-attach tokens to requests
apiClient.interceptors.request.use(config => {
  const token = authStore.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

## 📱 **Progressive Web App**

The frontend includes full PWA support:

- **Offline Functionality** with service worker
- **Install Prompts** for mobile/desktop
- **Push Notifications** for training completion
- **Background Sync** for pending requests

## 🧪 **Development & Testing**

### **Type Checking**
```bash
# Continuous type checking
npm run type-check -- --watch
```

### **Linting & Formatting** 
```bash
# Fix linting issues
npm run lint

# Format all files
npm run format
```

### **Component Development**
```bash
# Hot reload during development
npm run dev
```

## 🚀 **Deployment**

### **Production Build**
```bash
# Create optimized build
npm run build

# The dist/ folder contains the built application
```

### **Preview Production Build**
```bash
# Test production build locally
npm run preview
```

### **Docker Deployment**
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🎨 **Customization**

### **Adding New Medical Domains**
```typescript
// types/api.ts
export const MEDICAL_DOMAINS = [
  'cardiology',
  'neurology', 
  'oncology',
  'your_new_domain' // Add here
] as const
```

### **Custom Chart Types**
```vue
<!-- Create new chart component -->
<template>
  <canvas ref="chartRef"></canvas>
</template>

<script setup lang="ts">
import { Chart } from 'chart.js'
// Implement custom medical visualization
</script>
```

## 🤝 **Contributing**

1. **Follow TypeScript strict mode**
2. **Use Composition API** for all components
3. **Implement proper error handling**
4. **Add loading states** for async operations
5. **Include accessibility features**
6. **Write comprehensive types**

## 📋 **Browser Support**

- **Chrome/Edge** 90+
- **Firefox** 88+
- **Safari** 14+
- **Mobile browsers** with ES2020 support

## 🔗 **Related Documentation**

- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [TypeScript Vue Guide](https://vuejs.org/guide/typescript/overview.html)
- [Pinia Store Guide](https://pinia.vuejs.org/getting-started.html)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)

## 🆘 **Troubleshooting**

### **Common Issues**

**Node.js Version Issues:**
```bash
# Use Node Version Manager
nvm install 18
nvm use 18
```

**Type Errors:**
```bash
# Clear TypeScript cache
rm -rf node_modules/.cache
npm run type-check
```

**Build Failures:**
```bash
# Clear dependencies and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 🎉 **Success!**

You now have a **modern, type-safe, performant** Vue 3 frontend for your medical AI system! 

**Features Ready:**
- ✅ Real-time dashboards
- ✅ Medical domain visualization  
- ✅ AI model management
- ✅ Classification interface
- ✅ PWA capabilities
- ✅ TypeScript safety
- ✅ Responsive design

**Happy coding with MedLitBot! 🏥🚀**

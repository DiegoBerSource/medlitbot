#!/bin/bash

# MedLitBot Frontend Setup Script
# Vue 3 + TypeScript + Vite + Modern Edge Technologies

set -e

echo "🏥 MedLitBot Frontend Setup Starting..."
echo "========================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2)
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)

if [ "$NODE_MAJOR" -lt 18 ]; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version $NODE_VERSION detected"

# Change to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
if command -v pnpm &> /dev/null; then
    echo "Using pnpm for faster installation..."
    pnpm install
elif command -v yarn &> /dev/null; then
    echo "Using yarn for installation..."
    yarn install
else
    echo "Using npm for installation..."
    npm install
fi

echo "✅ Dependencies installed successfully"

# Create environment file
echo "🔧 Setting up environment configuration..."

if [ ! -f .env ]; then
    cat > .env << EOL
# MedLitBot Frontend Environment Configuration

# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000/ws

# App Configuration
VITE_APP_TITLE=MedLitBot - Medical Literature AI
VITE_APP_VERSION=1.0.0

# Feature Flags
VITE_ENABLE_PWA=true
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_REAL_TIME=true

# Development
VITE_DEV_TOOLS=true
VITE_API_TIMEOUT=30000
EOL
    echo "✅ Environment file created (.env)"
else
    echo "⚠️  Environment file already exists"
fi

# Create development environment file
if [ ! -f .env.development ]; then
    cat > .env.development << EOL
# Development Environment
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000/ws
VITE_DEV_TOOLS=true
VITE_API_TIMEOUT=10000
EOL
    echo "✅ Development environment file created"
fi

# Create production environment file
if [ ! -f .env.production ]; then
    cat > .env.production << EOL
# Production Environment
VITE_API_BASE_URL=https://api.medlitbot.com
VITE_WS_URL=wss://api.medlitbot.com/ws
VITE_DEV_TOOLS=false
VITE_API_TIMEOUT=30000
VITE_ENABLE_ANALYTICS=true
EOL
    echo "✅ Production environment file created"
fi

# Create public directory and assets
echo "🖼️  Setting up public assets..."

mkdir -p public

# Create basic favicon and PWA icons (placeholders)
if [ ! -f public/favicon.ico ]; then
    # Create a simple SVG favicon
    cat > public/favicon.svg << 'EOL'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#1e40af"/>
  <text x="50" y="60" font-family="Arial, sans-serif" font-size="40" fill="white" text-anchor="middle">🏥</text>
</svg>
EOL
    echo "✅ Favicon created"
fi

# Create manifest.json for PWA
if [ ! -f public/manifest.json ]; then
    cat > public/manifest.json << EOL
{
  "name": "MedLitBot - Medical Literature AI",
  "short_name": "MedLitBot",
  "description": "AI-powered medical literature classification system",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1e40af",
  "icons": [
    {
      "src": "/pwa-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/pwa-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
EOL
    echo "✅ PWA manifest created"
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    cat > .gitignore << EOL
# Dependencies
node_modules/
.pnpm-debug.log*
.yarn-debug.log*
.yarn-error.log*

# Build outputs
dist/
dist-ssr/
*.local

# Environment files
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# Stores VSCode versions used for testing VSCode extensions
.vscode-test

# yarn v2
.yarn/cache
.yarn/unplugged
.yarn/build-state.yml
.yarn/install-state.gz
.pnp.*

# Editor directories and files
.idea
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# PWA
sw.js
workbox-*.js
EOL
    echo "✅ .gitignore created"
fi

# Create basic TypeScript declaration files if missing
mkdir -p src/components/ui src/components/layout src/components/charts src/components/forms
mkdir -p src/composables src/utils

# Create placeholder components to prevent import errors
echo "🧩 Creating placeholder components..."

# Icon component
if [ ! -f src/components/ui/Icon.vue ]; then
    cat > src/components/ui/Icon.vue << 'EOL'
<template>
  <span class="inline-block" :class="classes">
    <!-- Heroicons placeholder - replace with actual icon library -->
    <svg v-if="name === 'home'" class="w-full h-full" fill="currentColor" viewBox="0 0 20 20">
      <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
    </svg>
    <!-- Add more icons as needed -->
    <span v-else>{{ name }}</span>
  </span>
</template>

<script setup lang="ts">
interface Props {
  name: string
  size?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const classes = computed(() => {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5', 
    lg: 'w-6 h-6',
    xl: 'w-8 h-8'
  }
  return sizeMap[props.size] || sizeMap.md
})
</script>
EOL
    echo "✅ Icon component created"
fi

# Type check
echo "🔍 Running type check..."
if command -v pnpm &> /dev/null; then
    pnpm type-check
elif command -v yarn &> /dev/null; then
    yarn type-check
else
    npm run type-check
fi

echo ""
echo "🎉 Frontend Setup Complete!"
echo "=========================="
echo ""
echo "📁 Project Structure:"
echo "   frontend/"
echo "   ├── src/"
echo "   │   ├── components/     # Vue 3 components"
echo "   │   ├── views/          # Page components"
echo "   │   ├── stores/         # Pinia state management"
echo "   │   ├── composables/    # Vue 3 composition functions"
echo "   │   ├── utils/          # Utility functions"
echo "   │   ├── types/          # TypeScript definitions"
echo "   │   └── assets/         # Static assets"
echo "   ├── public/             # Static files"
echo "   └── dist/               # Built application"
echo ""
echo "🚀 Available Commands:"
echo "   npm run dev          # Start development server"
echo "   npm run build        # Build for production"
echo "   npm run preview      # Preview production build"
echo "   npm run type-check   # TypeScript type checking"
echo "   npm run lint         # ESLint code linting"
echo ""
echo "🔧 Technology Stack:"
echo "   ✅ Vue 3 (Composition API)"
echo "   ✅ TypeScript"
echo "   ✅ Vite (Build tool)"
echo "   ✅ Pinia (State management)"
echo "   ✅ Vue Router 4"
echo "   ✅ Tailwind CSS"
echo "   ✅ HeadlessUI"
echo "   ✅ Chart.js"
echo "   ✅ Axios (API client)"
echo "   ✅ Socket.io (WebSocket)"
echo "   ✅ PWA support"
echo ""
echo "🌐 Next Steps:"
echo "   1. cd frontend"
echo "   2. npm run dev"
echo "   3. Open http://localhost:3000"
echo "   4. Start building your medical AI frontend!"
echo ""
echo "📚 Documentation:"
echo "   - Vue 3: https://vuejs.org/"
echo "   - TypeScript: https://www.typescriptlang.org/"
echo "   - Tailwind CSS: https://tailwindcss.com/"
echo "   - Pinia: https://pinia.vuejs.org/"
echo ""
echo "🏥 Happy coding with MedLitBot! 🚀"

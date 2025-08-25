#!/bin/bash
# MedLitBot Frontend Build Script
# Usage: ./build-frontend.sh [options]
#   --fast        : Skip TypeScript checking
#   --watch       : Watch mode (rebuild on changes)
#   --preview     : Build and preview
#   --analyze     : Build with bundle analyzer
#   --check-only  : Only run type checking and linting

set -e

echo "🏗️  MedLitBot Frontend Build System"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the project root
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Must be run from the project root directory${NC}"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    npm install
    echo ""
fi

# Check-only mode
if [[ "$*" == *"--check-only"* ]]; then
    echo -e "${BLUE}🔍 Running full checks (TypeScript + Linting + Formatting)...${NC}"
    npm run full-check
    echo -e "${GREEN}✅ All checks passed!${NC}"
    exit 0
fi

# Different build modes
if [[ "$*" == *"--fast"* ]]; then
    echo -e "${YELLOW}⚡ Fast build (skipping TypeScript checking)...${NC}"
    npm run build:fast
    echo -e "${GREEN}✅ Fast build completed!${NC}"
    
elif [[ "$*" == *"--watch"* ]]; then
    echo -e "${BLUE}👀 Watch mode - rebuilding on changes...${NC}"
    npm run build:watch
    
elif [[ "$*" == *"--analyze"* ]]; then
    echo -e "${BLUE}📊 Building with bundle analysis...${NC}"
    npm run build:analyze
    echo -e "${GREEN}✅ Build with analysis completed!${NC}"
    
elif [[ "$*" == *"--preview"* ]]; then
    echo -e "${BLUE}🏗️  Building for production...${NC}"
    npm run build
    echo ""
    echo -e "${GREEN}🌐 Starting preview server...${NC}"
    npm run preview
    
else
    echo -e "${BLUE}🏗️  Building for production...${NC}"
    echo -e "${YELLOW}📝 Running TypeScript checking...${NC}"
    npm run build
    echo ""
    echo -e "${GREEN}✅ Build completed successfully!${NC}"
    echo -e "${BLUE}💡 Tip: Use --preview to test the build, or --fast for quicker builds${NC}"
fi

# Show build size info
if [ -d "dist" ] && [[ "$*" != *"--watch"* ]]; then
    echo ""
    echo -e "${BLUE}📦 Build output:${NC}"
    du -sh dist/
    if command -v tree >/dev/null 2>&1; then
        echo ""
        tree dist/ -L 2
    else
        echo ""
        ls -la dist/
    fi
fi

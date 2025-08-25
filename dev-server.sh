#!/bin/bash
# MedLitBot Frontend Development Server
# Usage: ./dev-server.sh [options]
#   --host    : Expose to network
#   --open    : Auto-open browser
#   --clean   : Clean cache before starting

set -e

echo "🚀 Starting MedLitBot Frontend Development Server..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the project root
if [ ! -d "frontend" ]; then
    echo "❌ Error: Must be run from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Clean cache if requested
if [[ "$*" == *"--clean"* ]]; then
    echo -e "${YELLOW}🧹 Cleaning cache...${NC}"
    npm run clean
    echo ""
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    npm install
    echo ""
fi

# Determine which dev command to run
if [[ "$*" == *"--host"* ]] && [[ "$*" == *"--open"* ]]; then
    echo -e "${GREEN}🌐 Starting dev server (network accessible, auto-open browser)...${NC}"
    npm run dev -- --host --open
elif [[ "$*" == *"--host"* ]]; then
    echo -e "${GREEN}🌐 Starting dev server (network accessible)...${NC}"
    npm run dev:host
elif [[ "$*" == *"--open"* ]]; then
    echo -e "${GREEN}🌐 Starting dev server (auto-open browser)...${NC}"
    npm run dev:open
else
    echo -e "${GREEN}🌐 Starting dev server...${NC}"
    npm run dev
fi

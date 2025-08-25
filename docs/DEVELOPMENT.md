# MedLitBot Development Commands

This guide provides quick commands for developing MedLitBot efficiently.

## 🚀 Quick Start

### Most Common Commands

```bash
# Start development server
make dev
# or
npm run dev

# Build for production  
make build
# or
npm run build

# Fast build (no type checking)
make build-fast
# or
npm run build:fast
```

## 📋 All Available Commands

### Using Make (Recommended)

```bash
make help                 # Show all available commands
make dev                  # Start development server
make dev-open            # Start dev server + open browser
make dev-host            # Start dev server (network accessible)
make dev-clean           # Clean cache + start dev server

make build               # Full production build (with type checking)
make build-fast          # Fast build (skip type checking) 
make build-watch         # Build in watch mode
make preview             # Build + preview production version

make check               # Run all quality checks (TypeScript + linting + formatting)
make lint                # Run and fix linting
make format              # Format code with Prettier
make type-check          # TypeScript type checking

make install             # Install frontend dependencies
make clean               # Clean build artifacts

# Backend commands
make backend             # Start Django server
make migrate             # Run Django migrations

# Full stack (requires tmux)
make fullstack           # Start both backend + frontend
make stop-fullstack      # Stop fullstack sessions
```

### Using npm (Alternative)

```bash
# From project root
npm run dev              # Start frontend dev server
npm run build            # Production build
npm run build:fast       # Fast build
npm run preview          # Build + preview
npm run check            # Quality checks
npm run backend          # Start Django backend
npm run install:all      # Install all dependencies

# Show help
npm run help
```

### From Frontend Directory

```bash
cd frontend

# Development
npm run dev              # Start dev server
npm run dev:host         # Network accessible
npm run dev:open         # Auto-open browser

# Building  
npm run build            # Full build (TypeScript + Vite)
npm run build:fast       # Skip TypeScript checking
npm run build:watch      # Watch mode
npm run preview          # Preview production build

# Quality
npm run type-check       # TypeScript checking
npm run type-check:watch # TypeScript checking (watch mode)
npm run lint             # Fix linting issues
npm run lint:check       # Check linting (no fixes)
npm run format           # Format with Prettier
npm run format:check     # Check formatting
npm run full-check       # All quality checks

# Utilities
npm run clean            # Clean cache + dist
```

## 🔧 Development Workflow

### Daily Development
```bash
# Start working
make dev-clean          # Clean start
# or just
make dev               # Normal start

# Before committing
make check             # Run all checks
```

### Building for Production
```bash
# Full build with all checks
make build

# Fast build for testing
make build-fast

# Test production build
make preview
```

### Full Stack Development
```bash
# Option 1: Separate terminals
Terminal 1: make backend
Terminal 2: make dev

# Option 2: Using tmux (if available)
make fullstack         # Starts both in background
# Use tmux commands to attach to sessions
```

## 🌐 Development URLs

- **Frontend Dev**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Admin**: http://localhost:8000/admin

## 🎯 Tips

1. **Use `make dev-clean`** if you encounter caching issues
2. **Use `make build-fast`** for quicker iteration during development
3. **Always run `make check`** before committing code
4. **Use `make preview`** to test production builds locally
5. **Use network mode (`make dev-host`)** to test on mobile devices

## 🛠️ Troubleshooting

### Build Errors
```bash
make clean             # Clean cache
make install           # Reinstall dependencies
make check             # Check for issues
```

### TypeScript Errors
```bash
make type-check        # Check types
cd frontend && npm run type-check:watch  # Watch mode
```

### Port Already in Use
```bash
# Kill processes on ports 3000/8000
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

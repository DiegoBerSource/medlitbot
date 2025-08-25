# MedLitBot Development Commands
# Colors
GREEN  := \033[0;32m
BLUE   := \033[0;34m
YELLOW := \033[1;33m
NC     := \033[0m # No Color

.PHONY: help dev build dev-clean build-fast preview install check clean

# Default target
help: ## Show this help message
	@echo "🤖 MedLitBot Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make dev          # Start development server"
	@echo "  make build        # Production build with type checking"  
	@echo "  make build-fast   # Fast build without type checking"
	@echo "  make preview      # Build and preview production version"

# Development
dev: ## Start the development server
	@echo "$(GREEN)🚀 Starting development server...$(NC)"
	@./dev-server.sh

dev-open: ## Start dev server and open browser
	@echo "$(GREEN)🚀 Starting development server (auto-open)...$(NC)"
	@./dev-server.sh --open

dev-host: ## Start dev server accessible on network
	@echo "$(GREEN)🌐 Starting development server (network accessible)...$(NC)"
	@./dev-server.sh --host

dev-clean: ## Clean cache and start dev server
	@echo "$(GREEN)🧹 Cleaning and starting development server...$(NC)"
	@./dev-server.sh --clean

# Building
build: ## Full production build with type checking
	@echo "$(BLUE)🏗️  Building for production...$(NC)"
	@./build-frontend.sh

build-fast: ## Fast production build (skip type checking)
	@echo "$(YELLOW)⚡ Fast build...$(NC)"
	@./build-frontend.sh --fast

build-watch: ## Build in watch mode
	@echo "$(BLUE)👀 Build in watch mode...$(NC)"
	@./build-frontend.sh --watch

preview: ## Build and preview production version
	@echo "$(BLUE)🌐 Build and preview...$(NC)"
	@./build-frontend.sh --preview

# Quality checks
check: ## Run type checking, linting, and formatting checks
	@echo "$(BLUE)🔍 Running quality checks...$(NC)"
	@./build-frontend.sh --check-only

type-check: ## Run TypeScript type checking
	@echo "$(BLUE)📝 Type checking...$(NC)"
	@cd frontend && npm run type-check

lint: ## Run and fix linting issues
	@echo "$(BLUE)🔧 Linting and fixing...$(NC)"
	@cd frontend && npm run lint

format: ## Format code with Prettier
	@echo "$(BLUE)💅 Formatting code...$(NC)"
	@cd frontend && npm run format

# Installation and maintenance
install: ## Install frontend dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@cd frontend && npm install

install-ci: ## Clean install for CI environments
	@echo "$(BLUE)🏭 CI installation...$(NC)"
	@cd frontend && npm ci

clean: ## Clean build artifacts and cache
	@echo "$(YELLOW)🧹 Cleaning build artifacts...$(NC)"
	@cd frontend && npm run clean
	@rm -rf frontend/dist

# Django backend commands (bonus)
backend: ## Start Django development server
	@echo "$(GREEN)🐍 Starting Django backend...$(NC)"
	@source .venv/bin/activate && python manage.py runserver

migrate: ## Run Django migrations
	@echo "$(BLUE)📊 Running migrations...$(NC)"
	@source .venv/bin/activate && python manage.py migrate

# Combined commands
fullstack: ## Start both backend and frontend (requires tmux)
	@echo "$(GREEN)🚀 Starting full stack development...$(NC)"
	@tmux new-session -d -s medlitbot-backend 'source .venv/bin/activate && python manage.py runserver'
	@tmux new-session -d -s medlitbot-frontend 'make dev'
	@echo "$(GREEN)✅ Backend and frontend started in tmux sessions$(NC)"
	@echo "  Backend:  tmux attach -t medlitbot-backend"
	@echo "  Frontend: tmux attach -t medlitbot-frontend"

stop-fullstack: ## Stop fullstack tmux sessions
	@tmux kill-session -t medlitbot-backend 2>/dev/null || true
	@tmux kill-session -t medlitbot-frontend 2>/dev/null || true
	@echo "$(YELLOW)🛑 Stopped fullstack sessions$(NC)"

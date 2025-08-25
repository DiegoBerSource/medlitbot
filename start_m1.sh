#!/bin/bash
# MedLitBot M1 Mac Startup Script
# Optimized for Apple Silicon training stability

echo "🍎 Starting MedLitBot with M1 optimizations..."

# Set M1 environment variables
export PYTORCH_ENABLE_MPS_FALLBACK=0
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export TOKENIZERS_PARALLELISM=false
export PYTORCH_NO_CUDA_MEMORY_CACHING=1
export CUDA_VISIBLE_DEVICES=""
export CELERY_POOL=solo
export USE_SQLITE=True
# Set your Hugging Face token (get from https://huggingface.co/settings/tokens)
export HF_TOKEN="your_hugging_face_token_here"

# Ensure logs directory exists
mkdir -p logs

# Function to start Django
start_django() {
    echo "🌐 Starting Django server..."
    python manage.py runserver 127.0.0.1:8000 &
    DJANGO_PID=$!
    echo "   Django PID: $DJANGO_PID"
}

# Function to start Celery
start_celery() {
    echo "⚡ Starting Celery worker (M1 optimized)..."
    USE_SQLITE=True celery -A medlitbot_project worker \
        --loglevel=info \
        --concurrency=1 \
        --pool=solo \
        --without-gossip \
        --without-mingle \
        --optimization=fair \
        --logfile=logs/celery_m1.log &
    CELERY_PID=$!
    echo "   Celery PID: $CELERY_PID"
}

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up processes..."
    if [ ! -z "$DJANGO_PID" ]; then
        kill $DJANGO_PID 2>/dev/null
    fi
    if [ ! -z "$CELERY_PID" ]; then
        kill $CELERY_PID 2>/dev/null
    fi
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Start services
start_django
start_celery

echo "✅ MedLitBot started with M1 optimizations"
echo "   Web interface: http://127.0.0.1:8000"
echo "   Admin panel: http://127.0.0.1:8000/admin/"
echo "   API docs: http://127.0.0.1:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait

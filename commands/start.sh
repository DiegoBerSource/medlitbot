#!/bin/bash
# MedLitBot Standard Startup Script
# For Intel/AMD systems and Linux

echo "🚀 Starting MedLitBot (Standard Configuration)..."

# Set standard environment variables
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4
export TOKENIZERS_PARALLELISM=true
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
    echo "⚡ Starting Celery worker..."
    USE_SQLITE=True celery -A medlitbot_project worker \
        --loglevel=info \
        --concurrency=4 \
        --logfile=logs/celery.log &
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

echo "✅ MedLitBot started successfully"
echo "   🌐 Backend API: http://127.0.0.1:8000"
echo "   📊 Admin panel: http://127.0.0.1:8000/admin/"
echo "   📚 API docs: http://127.0.0.1:8000/api/docs"
echo ""
echo "🎨 To start the frontend (Vue.js), run in another terminal:"
echo "   ./commands/dev-server.sh"
echo "   Then visit: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait

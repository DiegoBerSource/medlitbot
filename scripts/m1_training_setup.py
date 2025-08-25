#!/usr/bin/env python3
"""
M1 Mac Training Environment Setup Script
Configures optimal settings for running MedLitBot on Apple Silicon
"""

import os
import sys
import platform
import logging

logger = logging.getLogger(__name__)


def configure_m1_environment():
    """Configure environment variables for M1 Mac compatibility"""
    
    # Check if we're on Apple Silicon
    is_apple_silicon = platform.machine() == 'arm64' and platform.system() == 'Darwin'
    
    if not is_apple_silicon:
        print("ℹ️  Not running on Apple Silicon, skipping M1 optimizations")
        return False
    
    print("🍎 Apple Silicon detected - Configuring M1 optimizations...")
    
    # PyTorch and MPS settings
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '0'  # Disable MPS completely
    os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'  # Disable MPS memory
    
    # Threading optimizations for M1
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1' 
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
    
    # Python multiprocessing settings
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Disable tokenizer parallelism
    os.environ['HF_DATASETS_CACHE'] = os.path.expanduser('~/Library/Caches/huggingface/datasets')
    os.environ['TRANSFORMERS_CACHE'] = os.path.expanduser('~/Library/Caches/huggingface/transformers')
    
    # Memory and performance settings
    os.environ['PYTORCH_NO_CUDA_MEMORY_CACHING'] = '1'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Completely disable CUDA
    
    # Celery settings for M1
    os.environ['CELERY_OPTIMIZATION'] = 'fair'
    os.environ['CELERY_POOL'] = 'solo'  # Use single-threaded pool
    
    # Django settings for M1
    os.environ['DJANGO_SETTINGS_MODULE'] = 'medlitbot_project.settings'
    
    print("✅ M1 environment configuration complete")
    
    return True


def check_dependencies():
    """Check if required dependencies are M1 compatible"""
    
    print("🔍 Checking M1 compatibility...")
    
    try:
        import torch
        print(f"   PyTorch: {torch.__version__}")
        
        if torch.backends.mps.is_available():
            print("   ⚠️  MPS backend available but will be disabled for training stability")
        
        if hasattr(torch.backends, 'mps'):
            torch.backends.mps.enabled = False
            print("   ✅ MPS backend disabled")
    
    except ImportError:
        print("   ❌ PyTorch not installed")
        return False
        
    try:
        import transformers
        print(f"   Transformers: {transformers.__version__}")
    except ImportError:
        print("   ❌ Transformers not installed")
        return False
        
    try:
        import datasets
        print(f"   Datasets: {datasets.__version__}")
    except ImportError:
        print("   ❌ Datasets not installed")
        return False
    
    print("✅ All dependencies are available")
    return True


def optimize_celery_for_m1():
    """Configure Celery worker settings for M1"""
    
    # Create optimized Celery command
    celery_cmd = [
        "celery", "-A", "medlitbot_project", "worker",
        "--loglevel=info",
        "--concurrency=1",  # Single worker process
        "--pool=solo",      # Single-threaded execution
        "--without-gossip", # Disable gossip
        "--without-mingle", # Disable mingle
        "--without-heartbeat", # Disable heartbeat
        "--optimization=fair",
        f"--logfile=logs/celery_m1.log"
    ]
    
    print("🚀 Optimized Celery command for M1:")
    print(f"   {' '.join(celery_cmd)}")
    
    return celery_cmd


def create_m1_startup_script():
    """Create a startup script with M1 optimizations"""
    
    script_content = '''#!/bin/bash
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
    USE_SQLITE=True celery -A medlitbot_project worker \\
        --loglevel=info \\
        --concurrency=1 \\
        --pool=solo \\
        --without-gossip \\
        --without-mingle \\
        --optimization=fair \\
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
'''
    
    with open('start_m1.sh', 'w') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod('start_m1.sh', 0o755)
    
    print("✅ Created M1 startup script: start_m1.sh")


def main():
    """Main setup function"""
    
    print("🏥 MedLitBot M1 Mac Setup")
    print("=" * 40)
    
    # Configure environment
    is_m1 = configure_m1_environment()
    
    if not is_m1:
        print("⏭️  Skipping M1-specific setup")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Please install missing dependencies first")
        sys.exit(1)
    
    # Show optimized Celery command
    optimize_celery_for_m1()
    
    # Create startup script
    create_m1_startup_script()
    
    print("\n🎉 M1 setup complete!")
    print("\n📋 Next steps:")
    print("   1. Run './start_m1.sh' to start with M1 optimizations")
    print("   2. Or manually set environment variables and run services")
    print("   3. Test BERT training with smaller datasets first")
    
    print("\n💡 M1 Training Tips:")
    print("   • Use smaller batch sizes (4-8)")
    print("   • Limit training epochs (1-3 for testing)")
    print("   • Monitor memory usage closely")
    print("   • Use CPU-only mode for stability")


if __name__ == "__main__":
    main()

"""
Main Django Ninja API configuration and routing
"""
from django.http import HttpRequest
from ninja import NinjaAPI
from ninja.security import HttpBearer
from typing import Optional

# Import API routers from each app
from dataset_management.api import router as datasets_router
from classification.api import router as classification_router


class AuthBearer(HttpBearer):
    """
    Optional authentication for API endpoints
    Can be extended to use JWT, session auth, etc.
    """
    def authenticate(self, request: HttpRequest, token: str) -> Optional[str]:
        # For now, we'll make API endpoints publicly accessible
        # In production, implement proper authentication here
        return token


# Initialize the main API
api = NinjaAPI(
    title="MedLitBot API",
    version="1.0.0",
    description="""
    Medical Literature AI Classification System API
    
    This API provides endpoints for:
    - Dataset management and upload
    - AI model training and management  
    - Medical literature classification
    - Performance analytics and monitoring
    
    Built with Django Ninja for fast, type-safe API development.
    """,
    docs_url="/docs",  # Swagger UI documentation
)


# Add routers from different apps
api.add_router("datasets/", datasets_router, tags=["Datasets"])
api.add_router("classification/", classification_router, tags=["Classification"])


# Health check endpoint
@api.get("/health", tags=["System"])
def health_check(request):
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "message": "MedLitBot API is running",
        "version": "1.0.0"
    }


# System info endpoint  
@api.get("/info", tags=["System"])
def system_info(request):
    """Get system information and API details"""
    return {
        "api_name": "MedLitBot API", 
        "version": "1.0.0",
        "description": "Medical Literature AI Classification System",
        "features": [
            "Dataset Upload & Management",
            "AI Model Training",
            "Medical Literature Classification", 
            "Performance Analytics",
            "Real-time Training Monitoring"
        ],
        "supported_formats": ["CSV", "JSON", "XLSX", "XLS"],
        "ai_models": ["BioBERT", "ClinicalBERT", "SciBERT", "Traditional ML"],
        "documentation": {
            "swagger": request.build_absolute_uri("/api/docs"),
            "redoc": request.build_absolute_uri("/api/redoc")
        }
    }


# System statistics endpoint
@api.get("/system/stats", tags=["System"])
def system_stats(request):
    """Get system statistics and dashboard data"""
    from dataset_management.models import Dataset
    from classification.models import MLModel, ClassificationResult
    from django.db.models import Count
    
    # Get basic counts
    dataset_count = Dataset.objects.count()
    model_count = MLModel.objects.count()
    classification_count = ClassificationResult.objects.count()
    
    # Get validated datasets count
    validated_datasets = Dataset.objects.filter(is_validated=True).count()
    
    # Get active training jobs (models with 'training' status)
    active_training = MLModel.objects.filter(status='training').count()
    
    # Get total samples across all datasets
    total_samples = sum(Dataset.objects.values_list('total_samples', flat=True)) or 0
    
    return {
        "datasets": {
            "total": dataset_count,
            "validated": validated_datasets,
            "total_samples": total_samples
        },
        "models": {
            "total": model_count,
            "active_training": active_training
        },
        "classifications": {
            "total": classification_count
        },
        "system": {
            "status": "operational",
            "uptime": "running",
            "last_updated": "2024-01-01T00:00:00Z"
        }
    }


# Medical domains endpoint
@api.get("/medical-domains", tags=["System"])
def medical_domains(request):
    """Get list of supported medical domains"""
    return [
        "cardiology",
        "neurology", 
        "oncology",
        "gastroenterology",
        "endocrinology",
        "respiratory",
        "infectious_disease",
        "dermatology",
        "psychiatry",
        "orthopedics",
        "radiology",
        "pathology",
        "pharmacology",
        "surgery",
        "pediatrics",
        "geriatrics",
        "emergency_medicine",
        "anesthesiology",
        "obstetrics_gynecology",
        "ophthalmology"
    ]

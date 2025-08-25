"""
Pydantic schemas for API request/response validation
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from ninja import ModelSchema

from dataset_management.models import Dataset, DatasetSample
from classification.models import MLModel, ClassificationResult, TrainingJob, ModelComparison


# Base response schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None
    success: bool = False


# Dataset schemas
class DatasetOut(ModelSchema):
    """Schema for dataset output"""
    class Config:
        model = Dataset
        model_fields = [
            'id', 'name', 'description', 'uploaded_at', 'updated_at',
            'total_samples', 'medical_domains', 'is_validated',
            'avg_title_length', 'avg_abstract_length', 'domain_distribution'
        ]
    
    file_size_mb: float
    file_extension: Optional[str]


class DatasetCreateIn(BaseModel):
    """Schema for dataset creation"""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the dataset")
    description: Optional[str] = Field(None, description="Dataset description")


class DatasetSampleOut(ModelSchema):
    """Schema for dataset sample output"""
    class Config:
        model = DatasetSample
        model_fields = [
            'id', 'title', 'abstract', 'medical_domains', 'authors', 
            'journal', 'publication_year', 'doi', 'is_preprocessed', 'created_at'
        ]
    
    domain_count: int


# ML Model schemas
class MLModelOut(ModelSchema):
    """Schema for ML model output"""
    class Config:
        model = MLModel
        model_fields = [
            'id', 'name', 'description', 'model_type', 'status',
            'is_trained', 'accuracy', 'f1_score', 'precision', 'recall',
            'training_time_minutes', 'num_epochs', 'best_epoch',
            'is_deployed', 'created_at', 'updated_at', 'confusion_matrix',
            'domain_performance', 'parameters'
        ]
    
    dataset_name: str
    model_size_mb: float
    is_training_complete: bool


class MLModelCreateIn(BaseModel):
    """Schema for ML model creation"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    model_type: str = Field(..., pattern="^(bert|gemma2-2b|traditional|hybrid|custom)$")
    dataset_id: int = Field(..., gt=0)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TrainingJobOut(BaseModel):
    """Schema for training job output"""
    id: int
    status: str
    progress_percentage: float
    current_epoch: int
    total_epochs: int
    current_loss: Optional[float] = None
    current_accuracy: Optional[float] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: str = ""
    celery_task_id: str = ""
    created_at: str
    model_name: str
    
    @classmethod
    def from_training_job(cls, training_job):
        """Create TrainingJobOut from TrainingJob instance"""
        return cls(
            id=training_job.id,
            status=training_job.status,
            progress_percentage=training_job.progress_percentage,
            current_epoch=training_job.current_epoch,
            total_epochs=training_job.total_epochs,
            current_loss=training_job.current_loss,
            current_accuracy=training_job.current_accuracy,
            started_at=training_job.started_at.isoformat() if training_job.started_at else None,
            completed_at=training_job.completed_at.isoformat() if training_job.completed_at else None,
            error_message=training_job.error_message or "",
            celery_task_id=training_job.celery_task_id or "",
            created_at=training_job.created_at.isoformat(),
            model_name=training_job.model.name
        )


class StartTrainingIn(BaseModel):
    """Schema for starting model training"""
    total_epochs: int = Field(default=10, ge=1, le=100)
    learning_rate: float = Field(default=2e-5, gt=0, le=1)
    batch_size: int = Field(default=16, ge=1, le=128)
    validation_split: float = Field(default=0.2, ge=0.1, le=0.5)


class HyperparameterOptimizationIn(BaseModel):
    """Schema for hyperparameter optimization"""
    n_trials: int = Field(default=20, ge=5, le=100, description="Number of optimization trials")
    timeout: Optional[int] = Field(default=3600, ge=300, le=7200, description="Timeout in seconds")
    metric: str = Field(default="f1_macro", description="Metric to optimize for")
    
    @field_validator('metric')
    @classmethod
    def validate_metric(cls, v):
        valid_metrics = ['f1_macro', 'f1_micro', 'accuracy', 'precision', 'recall']
        if v not in valid_metrics:
            raise ValueError(f'Metric must be one of: {valid_metrics}')
        return v


class HyperparameterOptimizationOut(BaseModel):
    """Schema for hyperparameter optimization results"""
    status: str
    model_id: Optional[int]
    best_params: Optional[Dict[str, Any]]
    best_value: Optional[float]
    optimization_metric: Optional[str]
    n_trials: Optional[int]
    message: str


# Classification schemas
class ClassificationIn(BaseModel):
    """Schema for classification input"""
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    abstract: str = Field(..., min_length=1, description="Article abstract")
    model_id: Optional[int] = Field(None, description="Specific model ID to use (optional)")
    threshold: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Prediction threshold")


class ClassificationOut(BaseModel):
    """Schema for classification output"""
    title: str
    predicted_domains: List[str]
    confidence_scores: Dict[str, float]
    prediction_threshold: float
    inference_time_ms: Optional[float]
    model_used: str
    created_at: datetime


class ClassificationResultOut(ModelSchema):
    """Schema for classification result from database"""
    class Config:
        model = ClassificationResult
        model_fields = [
            'id', 'title', 'predicted_domains', 'confidence_scores',
            'prediction_threshold', 'inference_time_ms', 'created_at'
        ]
    
    model_name: str


class BatchClassificationIn(BaseModel):
    """Schema for batch classification input"""
    articles: List[ClassificationIn] = Field(..., min_items=1, max_items=1000, description="Articles to classify (max 1000 per batch)")
    model_id: Optional[int] = None
    threshold: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)


class BatchClassificationOut(BaseModel):
    """Schema for batch classification output"""
    results: List[ClassificationOut]
    total_processed: int
    processing_time_seconds: float
    model_used: str


# Analytics schemas
class DatasetStatsOut(BaseModel):
    """Schema for dataset statistics"""
    total_datasets: int
    total_samples: int
    unique_domains: List[str]
    domain_distribution: Dict[str, int]
    avg_samples_per_dataset: float
    recent_uploads: int  # Last 7 days


class ModelStatsOut(BaseModel):
    """Schema for model statistics"""
    total_models: int
    trained_models: int
    deployed_models: int
    avg_accuracy: Optional[float]
    best_model: Optional[MLModelOut]
    recent_predictions: int  # Last 24 hours


class SystemStatsOut(BaseModel):
    """Schema for system statistics"""
    dataset_stats: DatasetStatsOut
    model_stats: ModelStatsOut
    uptime_hours: float
    api_version: str


# Model comparison schemas
class ModelComparisonOut(ModelSchema):
    """Schema for model comparison output"""
    class Config:
        model = ModelComparison
        model_fields = ['id', 'name', 'description', 'comparison_results', 'created_at']
    
    models_count: int
    test_dataset_name: Optional[str]


class ModelComparisonCreateIn(BaseModel):
    """Schema for creating model comparison"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    model_ids: List[int] = Field(..., min_items=2, max_items=10)
    test_dataset_id: Optional[int] = None


# Pagination schemas
class PaginatedResponse(BaseModel):
    """Generic paginated response schema"""
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[Any]


# File upload schemas
class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    filename: str
    size_mb: float
    status: str
    message: str

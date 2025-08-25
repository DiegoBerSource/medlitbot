"""
Django Ninja API router for ML model training and classification
"""
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.utils import timezone
from ninja import Router
from ninja.pagination import paginate, PageNumberPagination

from .models import MLModel, ClassificationResult, TrainingJob, ModelComparison
from dataset_management.models import Dataset
from api.schemas import (
    MLModelOut, MLModelCreateIn, ClassificationIn, ClassificationOut,
    ClassificationResultOut, BatchClassificationIn, BatchClassificationOut, 
    TrainingJobOut, StartTrainingIn, HyperparameterOptimizationIn,
    HyperparameterOptimizationOut, ModelComparisonOut, ModelComparisonCreateIn,
    MessageResponse, ErrorResponse
)
from .tasks import start_model_training, predict_domains, optimize_hyperparameters

router = Router()


# Model Management Endpoints
@router.get("/models", response=List[MLModelOut], tags=["Model Management"])
@paginate(PageNumberPagination)
def list_models(request: HttpRequest):
    """
    List all ML models
    
    Returns a paginated list of all models in the system.
    """
    return MLModel.objects.select_related('dataset').all()


@router.get("/models/{model_id}", response=MLModelOut, tags=["Model Management"])
def get_model(request: HttpRequest, model_id: int):
    """
    Get a specific model by ID
    
    Returns detailed information about a specific ML model.
    """
    model = get_object_or_404(MLModel.objects.select_related('dataset'), id=model_id)
    return model


@router.post("/models", response=MLModelOut, tags=["Model Management"])
def create_model(request: HttpRequest, payload: MLModelCreateIn):
    """
    Create a new ML model configuration
    
    Creates a new model configuration that can be trained later.
    The model will be in 'created' status until training is started.
    """
    try:
        dataset = get_object_or_404(Dataset, id=payload.dataset_id)
        
        # Ensure dataset is validated
        if not dataset.is_validated:
            return ErrorResponse(
                error="Dataset must be validated before creating models",
                details={"dataset_id": payload.dataset_id, "dataset_name": dataset.name}
            )
        
        model = MLModel.objects.create(
            name=payload.name,
            description=payload.description or "",
            model_type=payload.model_type,
            dataset=dataset,
            parameters=payload.parameters,
            created_by=request.user if request.user.is_authenticated else None
        )
        
        return model
        
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "creation_error"})


@router.post("/models/{model_id}/train", response=TrainingJobOut, tags=["Model Training"])
def start_training(request: HttpRequest, model_id: int, training_config: StartTrainingIn):
    """
    Start training a model
    
    Initiates the training process for a model. This is an asynchronous operation
    that will run in the background. Use the training job endpoints to monitor progress.
    """
    try:
        model = get_object_or_404(MLModel, id=model_id)
        
        if model.status == 'training':
            return ErrorResponse(
                error="Model is already training",
                details={"model_id": model_id, "current_status": model.status}
            )
        
        if model.is_trained and model.status != 'failed':
            return ErrorResponse(
                error="Model is already trained. Create a new model to train again.",
                details={"model_id": model_id, "current_status": model.status}
            )
        
        # Update model parameters with training config
        model.parameters.update({
            "total_epochs": training_config.total_epochs,
            "learning_rate": training_config.learning_rate,
            "batch_size": training_config.batch_size,
            "validation_split": training_config.validation_split
        })
        model.save()
        
        # Start training task
        task_result = start_model_training.delay(model.id, training_config.dict())
        
        # Create training job record
        training_job = TrainingJob.objects.create(
            model=model,
            celery_task_id=task_result.id,
            total_epochs=training_config.total_epochs
        )
        
        # Update model status
        model.status = 'training'
        model.save()
        
        return TrainingJobOut.from_training_job(training_job)
        
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "training_error"})


@router.post("/models/{model_id}/optimize", response=HyperparameterOptimizationOut, tags=["Model Training"])
def optimize_model_hyperparameters(request: HttpRequest, model_id: int, optimization_config: HyperparameterOptimizationIn):
    """
    Optimize hyperparameters for a model
    
    Runs hyperparameter optimization using Optuna to find the best parameters
    for the specified model. The model will be updated with the optimized parameters
    and can then be trained using the optimized configuration.
    """
    try:
        model = get_object_or_404(MLModel, id=model_id)
        
        if model.status == 'training':
            return ErrorResponse(
                error="Model is currently training or being optimized",
                details={"model_id": model_id, "current_status": model.status}
            )
        
        # Ensure dataset is validated
        if not model.dataset.is_validated:
            return ErrorResponse(
                error="Dataset must be validated before optimization",
                details={"dataset_id": model.dataset.id}
            )
        
        # Start hyperparameter optimization task
        task_result = optimize_hyperparameters.delay(model.id, optimization_config.dict())
        
        # Update model status
        model.status = 'training'  # Use training status during optimization
        model.save()
        
        return HyperparameterOptimizationOut(
            status="started",
            model_id=model.id,
            best_params=None,
            best_value=None,
            optimization_metric=optimization_config.metric,
            n_trials=optimization_config.n_trials,
            message=f"Hyperparameter optimization started with {optimization_config.n_trials} trials"
        )
        
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "optimization_error"})


@router.get("/training-jobs/{job_id}", response=TrainingJobOut, tags=["Model Training"])
def get_training_job(request: HttpRequest, job_id: int):
    """
    Get training job status and progress
    
    Returns current status and progress information for a training job.
    """
    job = get_object_or_404(TrainingJob.objects.select_related('model'), id=job_id)
    return TrainingJobOut.from_training_job(job)


@router.get("/models/{model_id}/training-job", response=TrainingJobOut, tags=["Model Training"])
def get_model_training_job(request: HttpRequest, model_id: int):
    """
    Get the training job for a specific model
    
    Returns the training job information for the specified model.
    If no training job exists, returns 404.
    """
    model = get_object_or_404(MLModel, id=model_id)
    
    try:
        # Try to get the training job for this model
        training_job = TrainingJob.objects.get(model=model)
        return TrainingJobOut.from_training_job(training_job)
    except TrainingJob.DoesNotExist:
        from django.http import Http404
        raise Http404("No training job found for this model")





@router.post("/models/{model_id}/stop-training", response=MessageResponse, tags=["Model Training"])
def stop_model_training(request: HttpRequest, model_id: int):
    """
    Stop training for a specific model
    
    Cancels the training job if it's currently running.
    """
    model = get_object_or_404(MLModel, id=model_id)
    
    try:
        training_job = TrainingJob.objects.get(model=model, status__in=['pending', 'running'])
        training_job.status = 'cancelled'
        training_job.completed_at = timezone.now()
        training_job.save()
        
        # Update model status
        model.status = 'created'
        model.save()
        
        # Cancel Celery task
        if training_job.celery_task_id:
            from celery import current_app
            current_app.control.revoke(training_job.celery_task_id, terminate=True)
        
        return MessageResponse(
            message="Training stopped successfully",
            success=True
        )
    except TrainingJob.DoesNotExist:
        from django.http import JsonResponse
        return JsonResponse(
            {"error": "No active training job found for this model", "model_id": model_id}, 
            status=404
        )


# Classification Endpoints
@router.post("/predict", response=ClassificationOut, tags=["Classification"])
def classify_single(request: HttpRequest, payload: ClassificationIn):
    """
    Classify a single medical article
    
    Predicts medical domains for a single article based on title and abstract.
    If no model_id is provided, uses the best available trained model.
    """
    try:
        # Get model to use
        if payload.model_id:
            model = get_object_or_404(MLModel, id=payload.model_id, is_trained=True)
        else:
            # Use best available model (highest F1 score) that has a model file
            model = MLModel.objects.filter(
                is_trained=True,
                model_path__isnull=False  # Only models with actual files
            ).exclude(model_path='').order_by('-f1_score').first()
            
            if not model:
                return ErrorResponse(
                    error="No trained models available for classification",
                    details={"suggestion": "Train a model first"}
                )
        
        # Perform classification synchronously for immediate results
        # In production, you might want to use Celery for async processing
        prediction_result = predict_domains(
            model.id, 
            payload.title, 
            payload.abstract, 
            payload.threshold
        )
        
        # Check if prediction was successful
        if prediction_result.get("status") == "error":
            return ErrorResponse(
                error=prediction_result.get("message", "Prediction failed"),
                details={"model_id": model.id}
            )
        
        # Return the actual prediction results
        return ClassificationOut(
            title=prediction_result.get("title", payload.title),
            predicted_domains=prediction_result.get("predicted_domains", []),
            confidence_scores=prediction_result.get("confidence_scores", {}),
            prediction_threshold=payload.threshold,
            inference_time_ms=prediction_result.get("inference_time_ms", 0.0),
            model_used=prediction_result.get("model_used", model.name),
            created_at=timezone.now()
        )
        
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "classification_error"})


@router.post("/predict-batch", response=BatchClassificationOut, tags=["Classification"])
def classify_batch(request: HttpRequest, payload: BatchClassificationIn):
    """
    Classify multiple medical articles at once
    
    Performs batch classification on multiple articles. More efficient than
    individual requests for processing multiple articles.
    """
    try:
        # Get model to use
        if payload.model_id:
            model = get_object_or_404(MLModel, id=payload.model_id, is_trained=True)
        else:
            model = MLModel.objects.filter(
                is_trained=True
            ).order_by('-f1_score').first()
            
            if not model:
                return ErrorResponse(
                    error="No trained models available for classification"
                )
        
        # Process each article using actual prediction
        results = []
        processing_start = timezone.now()
        
        for article in payload.articles:
            # Call the actual prediction function
            prediction_result = predict_domains(
                model.id,
                article.title,
                article.abstract,
                payload.threshold or 0.5
            )
            
            # Check if prediction was successful
            if prediction_result.get("status") == "success":
                results.append(ClassificationOut(
                    title=article.title,
                    predicted_domains=prediction_result.get("predicted_domains", []),
                    confidence_scores=prediction_result.get("confidence_scores", {}),
                    prediction_threshold=payload.threshold or 0.5,
                    inference_time_ms=prediction_result.get("inference_time_ms", 0.0),
                    model_used=model.name,
                    created_at=timezone.now()
                ))
            else:
                # Add failed prediction with empty results but proper structure
                results.append(ClassificationOut(
                    title=article.title,
                    predicted_domains=[],
                    confidence_scores={},
                    prediction_threshold=payload.threshold or 0.5,
                    inference_time_ms=0.0,
                    model_used=model.name,
                    created_at=timezone.now()
                ))
        
        processing_end = timezone.now()
        processing_time = (processing_end - processing_start).total_seconds()
        
        return BatchClassificationOut(
            results=results,
            total_processed=len(results),
            processing_time_seconds=processing_time,
            model_used=model.name
        )
        
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "batch_classification_error"})


@router.get("/predictions", response=List[ClassificationResultOut], tags=["Classification"])
@paginate(PageNumberPagination)
def list_predictions(request: HttpRequest, model_id: Optional[int] = None):
    """
    List previous classification results
    
    Returns a paginated list of previous classification results.
    Can be filtered by model_id.
    """
    queryset = ClassificationResult.objects.select_related('model')
    
    if model_id:
        queryset = queryset.filter(model_id=model_id)
    
    return queryset.order_by('-created_at')


# Model Comparison Endpoints
@router.get("/comparisons", response=List[ModelComparisonOut], tags=["Model Comparison"])
@paginate(PageNumberPagination)  
def list_comparisons(request: HttpRequest):
    """
    List model comparisons
    
    Returns a paginated list of model comparison experiments.
    """
    return ModelComparison.objects.all()


@router.post("/comparisons", response=ModelComparisonOut, tags=["Model Comparison"])
def create_comparison(request: HttpRequest, payload: ModelComparisonCreateIn):
    """
    Create a new model comparison
    
    Sets up a comparison experiment between multiple models.
    All models must be trained before comparison.
    """
    try:
        # Validate that all models exist and are trained
        models = MLModel.objects.filter(id__in=payload.model_ids, is_trained=True)
        
        if models.count() != len(payload.model_ids):
            return ErrorResponse(
                error="Some models not found or not trained",
                details={"requested_ids": payload.model_ids}
            )
        
        # Get test dataset if specified
        test_dataset = None
        if payload.test_dataset_id:
            test_dataset = get_object_or_404(Dataset, id=payload.test_dataset_id)
        
        # Create comparison
        comparison = ModelComparison.objects.create(
            name=payload.name,
            description=payload.description or "",
            test_dataset=test_dataset
        )
        
        comparison.ml_models.set(models)
        
        # Trigger comparison task (to be implemented)
        # run_model_comparison.delay(comparison.id)
        
        return comparison
        
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "comparison_error"})


@router.delete("/models/{model_id}", response=MessageResponse, tags=["Model Management"])
def delete_model(request: HttpRequest, model_id: int):
    """
    Delete a model
    
    Permanently removes a model and all associated training jobs and predictions.
    This action cannot be undone.
    """
    try:
        model = get_object_or_404(MLModel, id=model_id)
        model_name = model.name
        model.delete()
        
        return MessageResponse(
            message=f"Model '{model_name}' has been deleted successfully",
            success=True
        )
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "deletion_error"})

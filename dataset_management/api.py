"""
Django Ninja API router for dataset management
"""
from typing import List
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from ninja import Router, File, Form, UploadedFile
from ninja.pagination import paginate, PageNumberPagination

from .models import Dataset, DatasetSample
from api.schemas import (
    DatasetOut, DatasetCreateIn, DatasetSampleOut, 
    MessageResponse, ErrorResponse, FileUploadResponse
)
from .tasks import process_dataset_file, validate_dataset_task

router = Router()


@router.get("/", response=List[DatasetOut], tags=["Dataset Management"])
@paginate(PageNumberPagination)
def list_datasets(request: HttpRequest):
    """
    List all datasets with pagination
    
    Returns a paginated list of all datasets in the system.
    """
    return Dataset.objects.all()


@router.get("/{dataset_id}", response=DatasetOut, tags=["Dataset Management"])
def get_dataset(request: HttpRequest, dataset_id: int):
    """
    Get a specific dataset by ID
    
    Returns detailed information about a specific dataset.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    return dataset


@router.post("/", response=DatasetOut, tags=["Dataset Management"])
def create_dataset(request: HttpRequest, payload: DatasetCreateIn):
    """
    Create a new empty dataset
    
    Creates a new dataset entry without uploading files.
    Files can be uploaded separately using the upload endpoint.
    """
    try:
        dataset = Dataset.objects.create(
            name=payload.name,
            description=payload.description or ""
        )
        return dataset
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "creation_error"})


@router.post("/{dataset_id}/upload", response=FileUploadResponse, tags=["Dataset Management"])
def upload_dataset_file(
    request: HttpRequest, 
    dataset_id: int,
    file: UploadedFile = File(...)
):
    """
    Upload a dataset file (CSV, JSON, Excel)
    
    Uploads and processes a dataset file. The file will be validated
    and parsed asynchronously. Supported formats: CSV, JSON, XLSX, XLS.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    
    try:
        # Validate file extension
        filename = file.name
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        
        if extension not in Dataset.SUPPORTED_FORMATS:
            return ErrorResponse(
                error=f"Unsupported file format: {extension}",
                details={
                    "supported_formats": Dataset.SUPPORTED_FORMATS,
                    "filename": filename
                }
            )
        
        # Save file to dataset
        dataset.file_path = file
        dataset.save()
        
        # Trigger async processing
        process_dataset_file.delay(dataset.id)
        
        return FileUploadResponse(
            filename=filename,
            size_mb=round(file.size / (1024 * 1024), 2),
            status="processing",
            message="File uploaded successfully and processing started"
        )
        
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "upload_error"})


@router.get("/{dataset_id}/samples", response=List[DatasetSampleOut], tags=["Dataset Samples"])
@paginate(PageNumberPagination)
def list_dataset_samples(request: HttpRequest, dataset_id: int):
    """
    List samples within a dataset
    
    Returns a paginated list of all samples in the specified dataset.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    return DatasetSample.objects.filter(dataset=dataset)


@router.get("/{dataset_id}/samples/", response=List[DatasetSampleOut], tags=["Dataset Samples"])
@paginate(PageNumberPagination)
def list_dataset_samples_with_slash(request: HttpRequest, dataset_id: int):
    """
    List samples within a dataset (with trailing slash)
    
    Returns a paginated list of all samples in the specified dataset.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    return DatasetSample.objects.filter(dataset=dataset)


@router.get("/{dataset_id}/samples/{sample_id}", response=DatasetSampleOut, tags=["Dataset Samples"])
def get_dataset_sample(request: HttpRequest, dataset_id: int, sample_id: int):
    """
    Get a specific sample from a dataset
    
    Returns detailed information about a specific sample.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    sample = get_object_or_404(DatasetSample, id=sample_id, dataset=dataset)
    return sample


@router.delete("/{dataset_id}", response=MessageResponse, tags=["Dataset Management"])
def delete_dataset(request: HttpRequest, dataset_id: int):
    """
    Delete a dataset and all its samples
    
    Permanently removes a dataset and all associated samples.
    This action cannot be undone.
    """
    try:
        dataset = get_object_or_404(Dataset, id=dataset_id)
        dataset_name = dataset.name
        dataset.delete()
        
        return MessageResponse(
            message=f"Dataset '{dataset_name}' has been deleted successfully",
            success=True
        )
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "deletion_error"})


@router.get("/{dataset_id}/stats", tags=["Dataset Analytics"])
def get_dataset_stats(request: HttpRequest, dataset_id: int):
    """
    Get statistical information about a dataset
    
    Returns comprehensive statistics including domain distribution,
    text length analysis, and validation status.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    
    return {
        "id": dataset.id,
        "name": dataset.name,
        "total_samples": dataset.total_samples,
        "medical_domains": dataset.medical_domains,
        "domain_distribution": dataset.domain_distribution,
        "avg_title_length": dataset.avg_title_length,
        "avg_abstract_length": dataset.avg_abstract_length,
        "is_validated": dataset.is_validated,
        "validation_errors": dataset.validation_errors,
        "file_size_mb": dataset.file_size_mb,
        "file_extension": dataset.file_extension,
        "uploaded_at": dataset.uploaded_at,
        "updated_at": dataset.updated_at
    }


@router.post("/{dataset_id}/validate", response=MessageResponse, tags=["Dataset Management"])
def validate_dataset(request: HttpRequest, dataset_id: int):
    """
    Manually trigger dataset validation
    
    Re-runs validation checks on the dataset to ensure data quality.
    """
    try:
        dataset = get_object_or_404(Dataset, id=dataset_id)
        
        # Trigger validation task
        validate_dataset_task.delay(dataset.id)
        
        return MessageResponse(
            message=f"Validation started for dataset '{dataset.name}'",
            success=True
        )
    except Exception as e:
        return ErrorResponse(error=str(e), details={"type": "validation_error"})

import os
import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.urls import reverse


def dataset_upload_path(instance, filename):
    """Generate upload path for dataset files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('datasets', filename)


def validate_file_size(value):
    """Validate that file size is not too large (max 100MB)"""
    limit = 100 * 1024 * 1024  # 100MB
    if value.size > limit:
        raise ValidationError('File size too large. Maximum size is 100MB.')


class Dataset(models.Model):
    """Model for managing medical literature datasets"""
    
    SUPPORTED_FORMATS = ['csv', 'json', 'xlsx', 'xls']
    
    name = models.CharField(
        max_length=200, 
        help_text="Name of the dataset"
    )
    description = models.TextField(
        blank=True, 
        help_text="Description of the dataset content and purpose"
    )
    file_path = models.FileField(
        upload_to=dataset_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=SUPPORTED_FORMATS),
            validate_file_size
        ],
        help_text="Upload dataset file (CSV, JSON, Excel)"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Dataset statistics
    total_samples = models.IntegerField(
        default=0, 
        help_text="Total number of articles in the dataset"
    )
    medical_domains = models.JSONField(
        default=list, 
        help_text="List of medical domains present in the dataset"
    )
    
    # Data validation status
    is_validated = models.BooleanField(
        default=False, 
        help_text="Whether the dataset has been validated for proper format"
    )
    validation_errors = models.JSONField(
        default=list, 
        help_text="List of validation errors found in the dataset"
    )
    
    # Dataset statistics
    avg_title_length = models.FloatField(
        null=True, blank=True,
        help_text="Average length of article titles"
    )
    avg_abstract_length = models.FloatField(
        null=True, blank=True,
        help_text="Average length of article abstracts"
    )
    domain_distribution = models.JSONField(
        default=dict,
        help_text="Distribution of samples per medical domain"
    )
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Dataset"
        verbose_name_plural = "Datasets"
    
    def __str__(self):
        return f"{self.name} ({self.total_samples} samples)"
    
    def get_absolute_url(self):
        return reverse('datasets:detail', kwargs={'pk': self.pk})
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file_path:
            try:
                return round(self.file_path.size / (1024 * 1024), 2)
            except (FileNotFoundError, ValueError):
                return 0
        return 0
    
    @property
    def file_extension(self):
        """Return file extension"""
        if self.file_path:
            return self.file_path.name.split('.')[-1].lower()
        return None


class DatasetSample(models.Model):
    """Model for individual samples within a dataset"""
    
    dataset = models.ForeignKey(
        Dataset, 
        on_delete=models.CASCADE, 
        related_name='samples'
    )
    
    # Article content
    title = models.CharField(
        max_length=500,
        help_text="Article title"
    )
    abstract = models.TextField(
        help_text="Article abstract"
    )
    
    # Labels and metadata
    medical_domains = models.JSONField(
        default=list,
        help_text="Medical domains assigned to this article"
    )
    
    # Additional metadata that might be present
    authors = models.CharField(
        max_length=1000, 
        blank=True, 
        help_text="Article authors"
    )
    journal = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="Journal name"
    )
    publication_year = models.IntegerField(
        null=True, blank=True,
        help_text="Year of publication"
    )
    doi = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Digital Object Identifier"
    )
    
    # Processing status
    is_preprocessed = models.BooleanField(
        default=False,
        help_text="Whether this sample has been preprocessed"
    )
    preprocessed_title = models.TextField(
        blank=True,
        help_text="Preprocessed version of the title"
    )
    preprocessed_abstract = models.TextField(
        blank=True,
        help_text="Preprocessed version of the abstract"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
        verbose_name = "Dataset Sample"
        verbose_name_plural = "Dataset Samples"
        unique_together = [['dataset', 'title']]  # Prevent duplicate titles in same dataset
    
    def __str__(self):
        return f"{self.title[:50]}..." if len(self.title) > 50 else self.title
    
    @property
    def combined_text(self):
        """Return combined title and abstract for processing"""
        return f"{self.title} {self.abstract}"
    
    @property
    def domain_count(self):
        """Return number of domains assigned to this sample"""
        return len(self.medical_domains) if self.medical_domains else 0

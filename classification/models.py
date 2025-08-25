import os
import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from django.contrib.auth.models import User
from dataset_management.models import Dataset


def model_upload_path(instance, filename):
    """Generate upload path for trained model files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('trained_models', filename)


class MLModel(models.Model):
    """Model for managing trained ML models"""
    
    MODEL_TYPES = [
        ('bert', 'BERT-based (BioBERT/ClinicalBERT)'),
        ('gemma2-2b', 'Google Gemma 2B'),
        ('traditional', 'Traditional ML (SVM/Random Forest)'),
        ('hybrid', 'Hybrid Ensemble'),
        ('custom', 'Custom Architecture'),
    ]
    
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('training', 'Training'),
        ('trained', 'Trained'),
        ('failed', 'Training Failed'),
        ('evaluating', 'Evaluating'),
        ('deployed', 'Deployed'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the model"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the model and its purpose"
    )
    model_type = models.CharField(
        max_length=50,
        choices=MODEL_TYPES,
        help_text="Type of ML model architecture"
    )
    
    # Training configuration
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='models',
        help_text="Dataset used for training"
    )
    parameters = models.JSONField(
        default=dict,
        help_text="Model hyperparameters and configuration"
    )
    
    # Model storage
    model_path = models.FileField(
        upload_to=model_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pkl', 'pth', 'safetensors', 'joblib'])],
        blank=True,
        null=True,
        help_text="Path to the trained model file"
    )
    
    # Training status and metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='created'
    )
    is_trained = models.BooleanField(
        default=False,
        help_text="Whether the model has been successfully trained"
    )
    
    # Training metrics and results
    training_metrics = models.JSONField(
        default=dict,
        help_text="Training metrics (loss, accuracy, etc.)"
    )
    validation_metrics = models.JSONField(
        default=dict,
        help_text="Validation metrics during training"
    )
    test_metrics = models.JSONField(
        default=dict,
        help_text="Final test set evaluation metrics"
    )
    
    # Training configuration details
    training_time_minutes = models.FloatField(
        null=True, blank=True,
        help_text="Total training time in minutes"
    )
    num_epochs = models.IntegerField(
        null=True, blank=True,
        help_text="Number of training epochs completed"
    )
    best_epoch = models.IntegerField(
        null=True, blank=True,
        help_text="Epoch with best validation performance"
    )
    
    # Model performance
    accuracy = models.FloatField(
        null=True, blank=True,
        help_text="Overall accuracy on test set"
    )
    f1_score = models.FloatField(
        null=True, blank=True,
        help_text="Macro F1 score on test set"
    )
    precision = models.FloatField(
        null=True, blank=True,
        help_text="Macro precision on test set"
    )
    recall = models.FloatField(
        null=True, blank=True,
        help_text="Macro recall on test set"
    )
    
    # Domain-specific performance
    domain_performance = models.JSONField(
        default=dict,
        help_text="Performance metrics per medical domain"
    )
    
    # Confusion matrix for detailed performance analysis
    confusion_matrix = models.JSONField(
        null=True, blank=True,
        help_text="Confusion matrix as 2D array for model evaluation visualization"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="User who created this model"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    training_started_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When training started"
    )
    training_completed_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When training completed"
    )
    
    # Deployment info
    is_deployed = models.BooleanField(
        default=False,
        help_text="Whether this model is currently deployed for inference"
    )
    deployment_url = models.URLField(
        blank=True,
        help_text="URL for deployed model API endpoint"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "ML Model"
        verbose_name_plural = "ML Models"
    
    def __str__(self):
        return f"{self.name} ({self.model_type})"
    
    def get_absolute_url(self):
        return reverse('classification:model_detail', kwargs={'pk': self.pk})
    
    @property
    def is_training_complete(self):
        """Check if training is complete"""
        return self.status in ['trained', 'deployed']
    
    @property
    def model_size_mb(self):
        """Return model file size in MB"""
        try:
            if not self.model_path:
                return 0
                
            # Handle BERT models stored as directories first
            if self.model_path.name and self.model_type == 'bert':
                from django.conf import settings
                media_root = getattr(settings, 'MEDIA_ROOT', '')
                
                # Check if path already points to a directory
                full_path = os.path.join(media_root, self.model_path.name)
                if os.path.exists(full_path) and os.path.isdir(full_path):
                    total_size = 0
                    for root, dirs, files in os.walk(full_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                total_size += os.path.getsize(file_path)
                            except (OSError, IOError):
                                continue
                    return round(total_size / (1024 * 1024), 2)
                
                # Also check for directory with _model suffix (fallback)
                base_name = self.model_path.name.replace('.pkl', '').replace('trained_models/', '')
                model_dir_name = f'{base_name}_model'
                model_dir_path = os.path.join(media_root, 'trained_models', model_dir_name)
                
                if os.path.exists(model_dir_path) and os.path.isdir(model_dir_path):
                    total_size = 0
                    for root, dirs, files in os.walk(model_dir_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                total_size += os.path.getsize(file_path)
                            except (OSError, IOError):
                                continue
                    return round(total_size / (1024 * 1024), 2)
            
            # Handle traditional ML models stored as single files
            try:
                if hasattr(self.model_path, 'path') and os.path.exists(self.model_path.path):
                    return round(self.model_path.size / (1024 * 1024), 2)
            except (AttributeError, OSError, IOError):
                pass
                    
        except Exception:
            # Catch any other unexpected errors
            pass
        return 0
    
    @property 
    def dataset_name(self):
        """Return the name of the associated dataset"""
        return self.dataset.name if self.dataset else 'Unknown Dataset'
    
    @property
    def model_metadata(self):
        """Return model metadata from JSON file (for BERT models)"""
        if self.model_type == 'bert' and self.model_path:
            try:
                import json
                from django.conf import settings
                
                # Look for metadata file
                base_name = os.path.basename(self.model_path.name).replace('_model', '')
                metadata_filename = f'{base_name}_metadata.json'
                metadata_path = os.path.join(
                    getattr(settings, 'MEDIA_ROOT', ''), 
                    'trained_models', 
                    metadata_filename
                )
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        return json.load(f)
            except (IOError, json.JSONDecodeError):
                pass
        return {}


class TrainingJob(models.Model):
    """Model for tracking training job progress"""
    
    JOB_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    model = models.OneToOneField(
        MLModel,
        on_delete=models.CASCADE,
        related_name='training_job'
    )
    
    # Job tracking
    celery_task_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Celery task ID for tracking"
    )
    status = models.CharField(
        max_length=20,
        choices=JOB_STATUS_CHOICES,
        default='pending'
    )
    
    # Progress tracking
    progress_percentage = models.FloatField(
        default=0.0,
        help_text="Training progress (0-100%)"
    )
    current_epoch = models.IntegerField(
        default=0,
        help_text="Current training epoch"
    )
    total_epochs = models.IntegerField(
        help_text="Total planned epochs"
    )
    
    # Real-time metrics
    current_loss = models.FloatField(
        null=True, blank=True,
        help_text="Current training loss"
    )
    current_accuracy = models.FloatField(
        null=True, blank=True,
        help_text="Current training accuracy"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error information
    error_message = models.TextField(
        blank=True,
        help_text="Error message if training failed"
    )
    traceback = models.TextField(
        blank=True,
        help_text="Full error traceback"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Training Job"
        verbose_name_plural = "Training Jobs"
    
    def __str__(self):
        return f"Training {self.model.name} - {self.status}"
    
    @property
    def model_name(self):
        """Return the name of the associated ML model"""
        return self.model.name if self.model else 'Unknown Model'


class ClassificationResult(models.Model):
    """Model for storing classification results"""
    
    model = models.ForeignKey(
        MLModel,
        on_delete=models.CASCADE,
        related_name='classification_results'
    )
    
    # Input text
    title = models.CharField(
        max_length=500,
        help_text="Article title used for classification"
    )
    abstract = models.TextField(
        help_text="Article abstract used for classification"
    )
    
    # Prediction results
    predicted_domains = models.JSONField(
        default=list,
        help_text="List of predicted medical domains"
    )
    confidence_scores = models.JSONField(
        default=dict,
        help_text="Confidence scores for each predicted domain"
    )
    all_domain_scores = models.JSONField(
        default=dict,
        help_text="Scores for all possible domains (for analysis)"
    )
    
    # Classification metadata
    prediction_threshold = models.FloatField(
        default=0.5,
        help_text="Threshold used for binary classification decisions"
    )
    inference_time_ms = models.FloatField(
        null=True, blank=True,
        help_text="Time taken for inference in milliseconds"
    )
    
    # True labels (if available for evaluation)
    true_domains = models.JSONField(
        default=list,
        blank=True,
        help_text="True medical domains (for evaluation purposes)"
    )
    
    # Request metadata
    created_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        help_text="User agent of the request"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text="IP address of the request"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Classification Result"
        verbose_name_plural = "Classification Results"
        indexes = [
            models.Index(fields=['model', '-created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        title_preview = self.title[:50] + "..." if len(self.title) > 50 else self.title
        return f"{title_preview} - {self.model.name}"
    
    @property
    def is_correct(self):
        """Check if prediction matches true labels (if available)"""
        if not self.true_domains:
            return None
        
        predicted_set = set(self.predicted_domains)
        true_set = set(self.true_domains)
        
        return predicted_set == true_set
    
    @property
    def max_confidence(self):
        """Return the highest confidence score"""
        if not self.confidence_scores:
            return 0.0
        return max(self.confidence_scores.values())
    
    @property
    def model_name(self):
        """Return the name of the model used for this prediction"""
        return self.model.name if self.model else 'Unknown Model'
    
    @property
    def min_confidence(self):
        """Return the lowest confidence score"""
        if not self.confidence_scores:
            return 0.0
        return min(self.confidence_scores.values())


class ModelComparison(models.Model):
    """Model for comparing performance between different models"""
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the comparison experiment"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the comparison"
    )
    
    ml_models = models.ManyToManyField(
        MLModel,
        help_text="Models being compared"
    )
    
    # Comparison results
    comparison_results = models.JSONField(
        default=dict,
        help_text="Detailed comparison results and metrics"
    )
    
    # Test dataset used for comparison
    test_dataset = models.ForeignKey(
        Dataset,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Dataset used for model comparison"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Model Comparison"
        verbose_name_plural = "Model Comparisons"
    
    def __str__(self):
        return self.name



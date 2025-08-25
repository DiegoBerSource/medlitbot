from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import MLModel, TrainingJob, ClassificationResult, ModelComparison


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'model_type', 'status', 'dataset', 
        'accuracy_display', 'f1_score_display', 'is_deployed', 'created_at'
    ]
    list_filter = [
        'model_type', 'status', 'is_trained', 'is_deployed', 
        'created_at', 'dataset'
    ]
    search_fields = ['name', 'description']
    readonly_fields = [
        'created_at', 'updated_at', 'training_started_at', 
        'training_completed_at', 'model_size_display', 
        'is_training_complete'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'model_type', 'dataset')
        }),
        ('Training Configuration', {
            'fields': ('parameters', 'status', 'is_trained'),
            'classes': ('collapse',)
        }),
        ('Model Storage', {
            'fields': ('model_path', 'model_size_display'),
            'classes': ('collapse',)
        }),
        ('Performance Metrics', {
            'fields': (
                'accuracy', 'f1_score', 'precision', 'recall',
                'domain_performance'
            ),
            'classes': ('collapse',)
        }),
        ('Training Details', {
            'fields': (
                'training_time_minutes', 'num_epochs', 'best_epoch',
                'training_metrics', 'validation_metrics', 'test_metrics'
            ),
            'classes': ('collapse',)
        }),
        ('Deployment', {
            'fields': ('is_deployed', 'deployment_url'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_by', 'created_at', 'updated_at', 
                'training_started_at', 'training_completed_at',
                'is_training_complete'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def accuracy_display(self, obj):
        """Display accuracy as percentage"""
        if obj.accuracy:
            return f"{obj.accuracy:.2%}"
        return "N/A"
    accuracy_display.short_description = "Accuracy"
    
    def f1_score_display(self, obj):
        """Display F1 score"""
        if obj.f1_score:
            return f"{obj.f1_score:.3f}"
        return "N/A"
    f1_score_display.short_description = "F1 Score"
    
    def model_size_display(self, obj):
        """Display model size"""
        if obj.model_size_mb:
            return f"{obj.model_size_mb} MB"
        return "N/A"
    model_size_display.short_description = "Model Size"


@admin.register(TrainingJob)
class TrainingJobAdmin(admin.ModelAdmin):
    list_display = [
        'model_name', 'status', 'progress_display', 
        'current_epoch', 'total_epochs', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['model__name', 'celery_task_id']
    readonly_fields = [
        'celery_task_id', 'created_at', 'started_at', 
        'completed_at', 'progress_display'
    ]
    
    fieldsets = (
        ('Job Information', {
            'fields': ('model', 'celery_task_id', 'status')
        }),
        ('Progress', {
            'fields': (
                'progress_percentage', 'current_epoch', 'total_epochs',
                'current_loss', 'current_accuracy'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message', 'traceback'),
            'classes': ('collapse',)
        }),
    )
    
    def model_name(self, obj):
        """Display model name"""
        return obj.model.name
    model_name.short_description = "Model"
    
    def progress_display(self, obj):
        """Display progress with visual bar"""
        if obj.progress_percentage:
            percentage = obj.progress_percentage
            color = "green" if percentage == 100 else "orange"
            return format_html(
                '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
                '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px;"></div>'
                '</div> {}%',
                percentage, color, percentage
            )
        return "N/A"
    progress_display.short_description = "Progress"


@admin.register(ClassificationResult)
class ClassificationResultAdmin(admin.ModelAdmin):
    list_display = [
        'title_truncated', 'model', 'predicted_domains_display',
        'max_confidence_display', 'created_at'
    ]
    list_filter = [
        'model', 'created_at', 'predicted_domains'
    ]
    search_fields = ['title', 'abstract']
    readonly_fields = [
        'created_at', 'inference_time_ms', 'max_confidence', 
        'min_confidence', 'is_correct'
    ]
    
    fieldsets = (
        ('Input', {
            'fields': ('model', 'title', 'abstract')
        }),
        ('Prediction Results', {
            'fields': (
                'predicted_domains', 'confidence_scores', 
                'all_domain_scores', 'prediction_threshold'
            )
        }),
        ('Evaluation', {
            'fields': ('true_domains', 'is_correct'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at', 'inference_time_ms', 'max_confidence',
                'min_confidence', 'user_agent', 'ip_address'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def title_truncated(self, obj):
        """Display truncated title"""
        return obj.title[:60] + "..." if len(obj.title) > 60 else obj.title
    title_truncated.short_description = "Title"
    
    def predicted_domains_display(self, obj):
        """Display predicted domains as comma-separated list"""
        if obj.predicted_domains:
            return ", ".join(obj.predicted_domains[:3])  # Show first 3
        return "None"
    predicted_domains_display.short_description = "Predicted Domains"
    
    def max_confidence_display(self, obj):
        """Display max confidence"""
        if obj.max_confidence:
            return f"{obj.max_confidence:.3f}"
        return "N/A"
    max_confidence_display.short_description = "Max Confidence"


@admin.register(ModelComparison)
class ModelComparisonAdmin(admin.ModelAdmin):
    list_display = ['name', 'models_count', 'test_dataset', 'created_at']
    list_filter = ['created_at', 'test_dataset']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'models_count']
    filter_horizontal = ['ml_models']
    
    fieldsets = (
        ('Comparison Information', {
            'fields': ('name', 'description', 'ml_models', 'test_dataset')
        }),
        ('Results', {
            'fields': ('comparison_results',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'models_count'),
            'classes': ('collapse',)
        }),
    )
    
    def models_count(self, obj):
        """Display number of models being compared"""
        return obj.ml_models.count()
    models_count.short_description = "# Models"

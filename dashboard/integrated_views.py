"""
Integrated dashboard views using Django templates instead of separate Dash app
This consolidates everything into a single Django service on port 8000
"""

import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from dataset_management.models import Dataset, DatasetSample
from classification.models import MLModel, ClassificationResult, TrainingJob


def integrated_analytics(request):
    """Single-page analytics dashboard using Chart.js instead of Dash"""
    
    # Get basic statistics
    stats = {
        'datasets_count': Dataset.objects.count(),
        'models_count': MLModel.objects.count(),
        'predictions_count': ClassificationResult.objects.count(),
        'active_training_jobs': TrainingJob.objects.filter(status='running').count(),
    }
    
    return render(request, 'dashboard/analytics.html', {
        'stats': stats,
        'title': 'MedLitBot Analytics Dashboard'
    })


@csrf_exempt
def api_chart_data(request):
    """API endpoint to provide chart data for JavaScript frontend"""
    
    chart_type = request.GET.get('type', 'dataset_overview')
    
    if chart_type == 'dataset_overview':
        datasets = Dataset.objects.annotate(sample_count=Count('samples'))
        data = {
            'labels': [d.name for d in datasets],
            'data': [d.sample_count for d in datasets],
            'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
        }
        
    elif chart_type == 'model_performance':
        models = MLModel.objects.filter(is_trained=True)
        data = {
            'labels': [m.name for m in models],
            'datasets': [
                {
                    'label': 'Accuracy',
                    'data': [m.accuracy or 0 for m in models],
                    'backgroundColor': '#36A2EB'
                },
                {
                    'label': 'F1 Score', 
                    'data': [m.f1_score or 0 for m in models],
                    'backgroundColor': '#FF6384'
                }
            ]
        }
        
    elif chart_type == 'domain_distribution':
        results = ClassificationResult.objects.all()
        domain_counts = {}
        for result in results:
            for domain in result.predicted_domains:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        data = {
            'labels': list(domain_counts.keys()),
            'data': list(domain_counts.values()),
            'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        }
        
    else:
        data = {'error': 'Unknown chart type'}
    
    return JsonResponse(data)


def single_port_dashboard(request):
    """Main dashboard page with everything integrated"""
    
    # Get all the data we need
    datasets = Dataset.objects.annotate(sample_count=Count('samples')).order_by('-uploaded_at')[:5]
    models = MLModel.objects.select_related('dataset').order_by('-created_at')[:5]  
    recent_predictions = ClassificationResult.objects.order_by('-created_at')[:10]
    training_jobs = TrainingJob.objects.order_by('-started_at')[:5]
    
    # Calculate statistics
    stats = {
        'total_datasets': Dataset.objects.count(),
        'total_models': MLModel.objects.count(),
        'total_predictions': ClassificationResult.objects.count(),
        'active_jobs': TrainingJob.objects.filter(status='running').count(),
        'validated_datasets': Dataset.objects.filter(is_validated=True).count(),
        'trained_models': MLModel.objects.filter(is_trained=True).count(),
    }
    
    context = {
        'stats': stats,
        'datasets': datasets,
        'models': models, 
        'recent_predictions': recent_predictions,
        'training_jobs': training_jobs,
        'title': 'MedLitBot - Integrated Dashboard'
    }
    
    return render(request, 'dashboard/integrated.html', context)

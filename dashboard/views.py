from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg
from django.utils import timezone
from dataset_management.models import Dataset, DatasetSample
from classification.models import MLModel, ClassificationResult, TrainingJob
import json


def dashboard_home(request):
    """Enhanced dashboard home page with real statistics"""
    # Get summary statistics
    stats = {
        'total_datasets': Dataset.objects.count(),
        'total_samples': DatasetSample.objects.count(),
        'total_models': MLModel.objects.count(),
        'trained_models': MLModel.objects.filter(is_trained=True).count(),
        'total_predictions': ClassificationResult.objects.count(),
        'avg_model_f1': MLModel.objects.filter(is_trained=True).aggregate(
            avg_f1=Avg('f1_score'))['avg_f1'] or 0,
    }
    
    # Recent activity
    recent_models = MLModel.objects.filter(is_trained=True).order_by('-training_completed_at')[:3]
    recent_predictions = ClassificationResult.objects.order_by('-created_at')[:5]
    active_training = TrainingJob.objects.filter(status='running').count()
    
    return HttpResponse(f"""
    <html>
    <head>
        <title>MedLitBot Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; }}
            .stat-card {{ transition: transform 0.2s; }}
            .stat-card:hover {{ transform: translateY(-2px); }}
        </style>
    </head>
    <body>
        <div class="container-fluid py-4">
            <div class="row">
                <div class="col-12">
                    <h1 class="text-primary mb-4">🩺 MedLitBot Dashboard</h1>
                    <p class="lead text-muted">Medical Literature AI Classification System</p>
                </div>
            </div>
            
            <!-- Statistics Cards -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card stat-card text-center">
                        <div class="card-body">
                            <h3 class="text-primary">{stats['total_datasets']:,}</h3>
                            <p class="card-text">Datasets</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card text-center">
                        <div class="card-body">
                            <h3 class="text-info">{stats['total_samples']:,}</h3>
                            <p class="card-text">Articles</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card text-center">
                        <div class="card-body">
                            <h3 class="text-success">{stats['trained_models']}</h3>
                            <p class="card-text">Trained Models</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card text-center">
                        <div class="card-body">
                            <h3 class="text-warning">{stats['avg_model_f1']:.3f}</h3>
                            <p class="card-text">Avg F1 Score</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Navigation Cards -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0">📊 Interactive Dashboard</h5>
                        </div>
                        <div class="card-body">
                            <p>Advanced analytics with Plotly visualizations</p>
                            <a href="http://127.0.0.1:8050" target="_blank" class="btn btn-primary">
                                Open Analytics Dashboard
                            </a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0">🚀 API Documentation</h5>
                        </div>
                        <div class="card-body">
                            <p>Complete API reference and testing interface</p>
                            <a href="/api/docs" class="btn btn-success">View API Docs</a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-header bg-warning text-white">
                            <h5 class="mb-0">⚙️ Admin Interface</h5>
                        </div>
                        <div class="card-body">
                            <p>Manage data and system configuration</p>
                            <a href="/admin/" class="btn btn-warning">Open Admin</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Quick Links -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">🔗 Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="btn-group" role="group">
                                <a href="/dashboard/datasets/" class="btn btn-outline-primary">📁 Datasets</a>
                                <a href="/dashboard/models/" class="btn btn-outline-info">🤖 Models</a>  
                                <a href="/dashboard/analytics/" class="btn btn-outline-success">📈 Analytics</a>
                                <a href="/dashboard/classification/" class="btn btn-outline-warning">🔮 Classify</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Status Info -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="alert alert-info">
                        <h6>🏃‍♂️ System Status</h6>
                        <p class="mb-0">
                            Active Training Jobs: <strong>{active_training}</strong> | 
                            Total Predictions: <strong>{stats['total_predictions']:,}</strong> |
                            Last Updated: <strong>{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


def datasets_list(request):
    """Dataset management page with real data"""
    datasets = Dataset.objects.annotate(sample_count=Count('samples')).order_by('-uploaded_at')
    
    dataset_list = ""
    for dataset in datasets:
        status_badge = "success" if dataset.is_validated else "warning"
        status_text = "Validated" if dataset.is_validated else "Pending"
        
        dataset_list += f"""
        <tr>
            <td>{dataset.name}</td>
            <td>{dataset.sample_count:,}</td>
            <td><span class="badge bg-{status_badge}">{status_text}</span></td>
            <td>{len(dataset.medical_domains or [])}</td>
            <td>{dataset.uploaded_at.strftime('%Y-%m-%d')}</td>
        </tr>
        """
    
    return HttpResponse(f"""
    <html>
    <head>
        <title>Dataset Management</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-4">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/dashboard/">Dashboard</a></li>
                    <li class="breadcrumb-item active">Datasets</li>
                </ol>
            </nav>
            
            <h1 class="mb-4">📁 Dataset Management</h1>
            
            <div class="card">
                <div class="card-header d-flex justify-content-between">
                    <h5 class="mb-0">Available Datasets</h5>
                    <a href="/api/docs#/datasets" class="btn btn-sm btn-primary">Upload New Dataset</a>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Samples</th>
                                <th>Status</th>
                                <th>Domains</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dataset_list}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


def models_list(request):
    """Model management page with real data"""
    models = MLModel.objects.select_related('dataset').order_by('-created_at')
    
    model_list = ""
    for model in models:
        status_color = {
            'trained': 'success',
            'training': 'warning', 
            'failed': 'danger',
            'created': 'secondary'
        }.get(model.status, 'secondary')
        
        f1_score = f"{model.f1_score:.3f}" if model.f1_score else "N/A"
        accuracy = f"{model.accuracy:.3f}" if model.accuracy else "N/A"
        
        model_list += f"""
        <tr>
            <td>{model.name}</td>
            <td><span class="badge bg-info">{model.model_type}</span></td>
            <td>{model.dataset.name}</td>
            <td><span class="badge bg-{status_color}">{model.status}</span></td>
            <td>{f1_score}</td>
            <td>{accuracy}</td>
            <td>{model.created_at.strftime('%Y-%m-%d')}</td>
        </tr>
        """
    
    return HttpResponse(f"""
    <html>
    <head>
        <title>Model Management</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-4">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/dashboard/">Dashboard</a></li>
                    <li class="breadcrumb-item active">Models</li>
                </ol>
            </nav>
            
            <h1 class="mb-4">🤖 Model Management</h1>
            
            <div class="card">
                <div class="card-header d-flex justify-content-between">
                    <h5 class="mb-0">Available Models</h5>
                    <a href="/api/docs#/classification" class="btn btn-sm btn-primary">Create New Model</a>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Type</th>
                                <th>Dataset</th>
                                <th>Status</th>
                                <th>F1 Score</th>
                                <th>Accuracy</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {model_list}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


def analytics(request):
    """Analytics dashboard page with link to Plotly dashboard"""
    return HttpResponse("""
    <html>
    <head>
        <title>Analytics Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-4">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/dashboard/">Dashboard</a></li>
                    <li class="breadcrumb-item active">Analytics</li>
                </ol>
            </nav>
            
            <h1 class="mb-4">📈 Analytics Dashboard</h1>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0">🚀 Interactive Analytics</h5>
                        </div>
                        <div class="card-body text-center">
                            <p class="lead">Advanced Plotly Dashboard</p>
                            <p>Real-time visualizations, model comparisons, and performance analytics</p>
                            <a href="http://127.0.0.1:8050" target="_blank" class="btn btn-primary btn-lg">
                                Launch Analytics Dashboard
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0">📊 Quick Stats</h5>
                        </div>
                        <div class="card-body">
                            <p><strong>Features:</strong></p>
                            <ul>
                                <li>📊 Dataset statistics and distributions</li>
                                <li>🤖 Model performance comparisons</li>
                                <li>🏋️ Training progress monitoring</li>
                                <li>🏥 Medical domain analytics</li>
                                <li>🔮 Prediction result insights</li>
                            </ul>
                            <p class="text-muted">
                                <small>Dashboard updates every 30 seconds automatically</small>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="alert alert-info mt-4">
                <h6>💡 Pro Tip</h6>
                <p class="mb-0">
                    To start the analytics dashboard server, run: 
                    <code>python manage.py run_dashboard</code>
                </p>
            </div>
        </div>
    </body>
    </html>
    """)


def classification(request):
    """Classification interface page"""
    trained_models = MLModel.objects.filter(is_trained=True)
    recent_results = ClassificationResult.objects.order_by('-created_at')[:10]
    
    return HttpResponse(f"""
    <html>
    <head>
        <title>Classification Interface</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-4">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/dashboard/">Dashboard</a></li>
                    <li class="breadcrumb-item active">Classification</li>
                </ol>
            </nav>
            
            <h1 class="mb-4">🔮 Article Classification</h1>
            
            <div class="row">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Classify Medical Literature</h5>
                        </div>
                        <div class="card-body">
                            <p>Use the API to classify medical articles:</p>
                            <div class="bg-light p-3 rounded">
                                <code>
                                POST /api/classification/predict<br/>
                                {{<br/>
                                &nbsp;&nbsp;"title": "Your article title",<br/>
                                &nbsp;&nbsp;"abstract": "Article abstract text...",<br/>
                                &nbsp;&nbsp;"threshold": 0.5<br/>
                                }}
                                </code>
                            </div>
                            <div class="mt-3">
                                <a href="/api/docs#/classification" class="btn btn-primary">
                                    Try API Interactive Docs
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">Available Models</h6>
                        </div>
                        <div class="card-body">
                            <p><strong>Trained Models: {trained_models.count()}</strong></p>
                            <ul class="list-group list-group-flush">
                                {''.join(f'<li class="list-group-item px-0">{model.name} <span class="badge bg-info">{model.model_type}</span></li>' for model in trained_models[:5])}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">Recent Classifications</h6>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Title</th>
                                            <th>Model</th>
                                            <th>Predicted Domains</th>
                                            <th>Confidence</th>
                                            <th>Time</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {''.join(f"""
                                        <tr>
                                            <td>{result.title[:50]}...</td>
                                            <td>{result.model.name}</td>
                                            <td>{''.join(f'<span class="badge bg-secondary me-1">{domain}</span>' for domain in (result.predicted_domains or [])[:3])}</td>
                                            <td>{max(result.confidence_scores.values()) if result.confidence_scores else 0:.3f}</td>
                                            <td>{result.created_at.strftime('%m-%d %H:%M')}</td>
                                        </tr>
                                        """ for result in recent_results)}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

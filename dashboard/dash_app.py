"""
Interactive Plotly Dash Dashboard for MedLitBot Analytics
Integrated medical literature classification analytics and visualizations
"""
import os
import sys
import django
from django.conf import settings
import threading
from concurrent.futures import ThreadPoolExecutor
import functools

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medlitbot_project.settings')
django.setup()

import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from dataset_management.models import Dataset, DatasetSample
from classification.models import MLModel, ClassificationResult, TrainingJob

# Create thread executor for Django ORM calls
executor = ThreadPoolExecutor(max_workers=4)

def run_in_thread(func):
    """Decorator to run Django ORM functions in a separate thread"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        future = executor.submit(func, *args, **kwargs)
        return future.result(timeout=30)  # 30 second timeout
    return wrapper

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="MedLitBot Analytics Dashboard"
)


@run_in_thread
def get_dataset_statistics():
    """Get comprehensive dataset statistics"""
    datasets = Dataset.objects.all()
    
    stats = []
    for dataset in datasets:
        samples = DatasetSample.objects.filter(dataset=dataset)
        sample_count = samples.count()
        
        if sample_count > 0:
            # Calculate text lengths
            text_lengths = []
            domain_counts = {}
            
            for sample in samples[:1000]:  # Limit for performance
                text_len = len(f"{sample.title} {sample.abstract}")
                text_lengths.append(text_len)
                
                for domain in sample.medical_domains or []:
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            avg_length = np.mean(text_lengths) if text_lengths else 0
            top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            stats.append({
                'name': dataset.name,
                'id': dataset.id,
                'sample_count': sample_count,
                'avg_text_length': avg_length,
                'unique_domains': len(domain_counts),
                'top_domains': top_domains,
                'uploaded_at': dataset.uploaded_at,
                'is_validated': dataset.is_validated
            })
    
    return stats


@run_in_thread
def get_model_performance_data():
    """Get model performance comparison data"""
    models = MLModel.objects.filter(is_trained=True)
    
    performance_data = []
    for model in models:
        performance_data.append({
            'name': model.name,
            'model_type': model.model_type,
            'accuracy': model.accuracy or 0,
            'f1_score': model.f1_score or 0,
            'precision': model.precision or 0,
            'recall': model.recall or 0,
            'training_time': model.training_time_minutes or 0,
            'dataset': model.dataset.name,
            'created_at': model.created_at,
            'domain_count': len(model.domain_performance) if model.domain_performance else 0
        })
    
    return performance_data


@run_in_thread
def get_training_progress_data():
    """Get training job progress and history"""
    recent_jobs = TrainingJob.objects.all().order_by('-started_at')[:10]
    
    training_data = []
    for job in recent_jobs:
        training_data.append({
            'model_name': job.model.name,
            'model_type': job.model.model_type,
            'status': job.status,
            'progress': job.progress_percentage or 0,
            'current_epoch': job.current_epoch or 0,
            'total_epochs': job.total_epochs or 0,
            'current_loss': job.current_loss or 0,
            'current_accuracy': job.current_accuracy or 0,
            'started_at': job.started_at,
            'completed_at': job.completed_at
        })
    
    return training_data


@run_in_thread
def get_classification_analytics():
    """Get classification results analytics"""
    recent_results = ClassificationResult.objects.all().order_by('-created_at')[:1000]
    
    analytics = {
        'total_predictions': recent_results.count(),
        'avg_confidence': 0,
        'domain_predictions': {},
        'model_usage': {},
        'daily_predictions': {}
    }
    
    if recent_results.count() > 0:
        confidences = []
        for result in recent_results:
            # Average confidence across predicted domains
            if result.confidence_scores:
                avg_conf = np.mean(list(result.confidence_scores.values()))
                confidences.append(avg_conf)
            
            # Count domain predictions
            for domain in result.predicted_domains or []:
                analytics['domain_predictions'][domain] = analytics['domain_predictions'].get(domain, 0) + 1
            
            # Count model usage
            model_name = result.model.name
            analytics['model_usage'][model_name] = analytics['model_usage'].get(model_name, 0) + 1
            
            # Daily predictions
            date_str = result.created_at.date().isoformat()
            analytics['daily_predictions'][date_str] = analytics['daily_predictions'].get(date_str, 0) + 1
        
        analytics['avg_confidence'] = np.mean(confidences) if confidences else 0
    
    return analytics


# Dashboard Layout
def create_layout():
    """Create the main dashboard layout"""
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("🩺 MedLitBot Analytics Dashboard", className="text-primary mb-4"),
                html.P("Real-time analytics for medical literature classification", 
                      className="lead text-muted")
            ])
        ], className="mb-4"),
        
        # Refresh controls
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("🔄 Refresh Data", id="refresh-btn", color="primary", size="sm"),
                    dbc.Button("📊 Export Report", id="export-btn", color="secondary", size="sm"),
                ]),
                html.Div(id="last-updated", className="text-muted small mt-2")
            ], width="auto"),
            dbc.Col([
                dcc.Interval(
                    id='interval-component',
                    interval=30*1000,  # Update every 30 seconds
                    n_intervals=0
                )
            ])
        ], className="mb-4"),
        
        # Key Metrics Cards
        html.Div(id="metrics-cards", className="mb-4"),
        
        # Main Charts Row
        dbc.Row([
            # Dataset Statistics
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📊 Dataset Overview", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id="dataset-stats-chart")
                    ])
                ])
            ], width=6),
            
            # Model Performance
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🤖 Model Performance", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id="model-performance-chart")
                    ])
                ])
            ], width=6),
        ], className="mb-4"),
        
        # Training Progress and Classification Analytics
        dbc.Row([
            # Training Progress
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🏋️ Training Progress", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id="training-progress-chart")
                    ])
                ])
            ], width=6),
            
            # Domain Distribution
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🏥 Medical Domain Distribution", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id="domain-distribution-chart")
                    ])
                ])
            ], width=6),
        ], className="mb-4"),
        
        # Detailed Analytics Tables
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📈 Detailed Model Analytics", className="mb-0")),
                    dbc.CardBody([
                        html.Div(id="model-analytics-table")
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P([
                    "MedLitBot Analytics Dashboard | ",
                    html.A("API Documentation", href="/api/docs", target="_blank"),
                    " | ",
                    html.A("Admin Interface", href="/admin/", target="_blank")
                ], className="text-center text-muted small")
            ])
        ])
    ], fluid=True)


app.layout = create_layout()


# Callbacks for Interactive Updates

@app.callback([
    Output('metrics-cards', 'children'),
    Output('dataset-stats-chart', 'figure'),
    Output('model-performance-chart', 'figure'),
    Output('training-progress-chart', 'figure'),
    Output('domain-distribution-chart', 'figure'),
    Output('model-analytics-table', 'children'),
    Output('last-updated', 'children')
], [
    Input('interval-component', 'n_intervals'),
    Input('refresh-btn', 'n_clicks')
])
def update_dashboard(n_intervals, refresh_clicks):
    """Update all dashboard components"""
    
    # Get fresh data
    dataset_stats = get_dataset_statistics()
    model_performance = get_model_performance_data()
    training_data = get_training_progress_data()
    classification_analytics = get_classification_analytics()
    
    # Create metrics cards
    metrics_cards = create_metrics_cards(dataset_stats, model_performance, classification_analytics)
    
    # Create charts
    dataset_chart = create_dataset_stats_chart(dataset_stats)
    performance_chart = create_model_performance_chart(model_performance)
    training_chart = create_training_progress_chart(training_data)
    domain_chart = create_domain_distribution_chart(classification_analytics)
    
    # Create detailed table
    analytics_table = create_model_analytics_table(model_performance)
    
    # Update timestamp
    last_updated = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return (metrics_cards, dataset_chart, performance_chart, 
            training_chart, domain_chart, analytics_table, last_updated)


def create_metrics_cards(dataset_stats, model_performance, classification_analytics):
    """Create key metrics summary cards"""
    total_datasets = len(dataset_stats)
    total_samples = sum(ds['sample_count'] for ds in dataset_stats)
    total_models = len(model_performance)
    avg_f1 = np.mean([mp['f1_score'] for mp in model_performance]) if model_performance else 0
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_datasets:,}", className="text-primary"),
                    html.P("Datasets", className="card-text")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_samples:,}", className="text-info"),
                    html.P("Articles", className="card-text")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_models}", className="text-success"),
                    html.P("Trained Models", className="card-text")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{avg_f1:.3f}", className="text-warning"),
                    html.P("Avg F1 Score", className="card-text")
                ])
            ], className="text-center")
        ], width=3),
    ])


def create_dataset_stats_chart(dataset_stats):
    """Create dataset statistics visualization"""
    if not dataset_stats:
        return go.Figure().add_annotation(
            text="No datasets available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = pl.DataFrame(dataset_stats)
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Sample Count by Dataset', 'Average Text Length', 
                       'Domain Diversity', 'Validation Status'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "pie"}]]
    )
    
    # Sample counts
    fig.add_trace(
        go.Bar(x=df['name'], y=df['sample_count'], name='Samples',
               marker_color='lightblue'),
        row=1, col=1
    )
    
    # Text lengths
    fig.add_trace(
        go.Bar(x=df['name'], y=df['avg_text_length'], name='Avg Length',
               marker_color='lightgreen'),
        row=1, col=2
    )
    
    # Domain diversity
    fig.add_trace(
        go.Bar(x=df['name'], y=df['unique_domains'], name='Unique Domains',
               marker_color='lightcoral'),
        row=2, col=1
    )
    
    # Validation status pie
    validation_counts = df['is_validated'].value_counts()
    fig.add_trace(
        go.Pie(labels=['Validated', 'Not Validated'], values=validation_counts.values,
               marker_colors=['lightgreen', 'lightcoral']),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Dataset Analytics Overview")
    return fig


def create_model_performance_chart(model_performance):
    """Create model performance comparison chart"""
    if not model_performance:
        return go.Figure().add_annotation(
            text="No trained models available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = pl.DataFrame(model_performance)
    
    # Create radar chart for model comparison
    fig = go.Figure()
    
    metrics = ['accuracy', 'f1_score', 'precision', 'recall']
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (_, row) in enumerate(df.head(5).iterrows()):  # Limit to 5 models for readability
        values = [row[metric] for metric in metrics]
        values.append(values[0])  # Close the radar chart
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics + [metrics[0]],
            fill='toself',
            name=f"{row['name']} ({row['model_type']})",
            line_color=colors[i % len(colors)]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True,
        title="Model Performance Comparison (Top 5 Models)"
    )
    
    return fig


def create_training_progress_chart(training_data):
    """Create training progress visualization"""
    if not training_data:
        return go.Figure().add_annotation(
            text="No training jobs available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = pl.DataFrame(training_data)
    
    # Create training status overview
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Training Status Distribution', 'Progress Overview'),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )
    
    # Status distribution
    status_counts = df['status'].value_counts()
    fig.add_trace(
        go.Pie(labels=status_counts.index, values=status_counts.values,
               name="Status"),
        row=1, col=1
    )
    
    # Progress bars for recent jobs
    recent_jobs = df.head(8)  # Show last 8 jobs
    colors = ['green' if status == 'completed' else 'orange' if status == 'running' else 'red' 
              for status in recent_jobs['status']]
    
    fig.add_trace(
        go.Bar(x=recent_jobs['model_name'], y=recent_jobs['progress'],
               marker_color=colors, name="Progress %"),
        row=1, col=2
    )
    
    fig.update_layout(height=400, title_text="Training Job Analytics")
    return fig


def create_domain_distribution_chart(classification_analytics):
    """Create medical domain distribution chart"""
    domain_predictions = classification_analytics.get('domain_predictions', {})
    
    if not domain_predictions:
        return go.Figure().add_annotation(
            text="No classification results available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Get top 15 domains
    sorted_domains = sorted(domain_predictions.items(), key=lambda x: x[1], reverse=True)[:15]
    domains, counts = zip(*sorted_domains)
    
    # Create horizontal bar chart
    fig = go.Figure([
        go.Bar(x=counts, y=domains, orientation='h',
               marker_color=px.colors.qualitative.Set3)
    ])
    
    fig.update_layout(
        title="Top Medical Domains (Classification Results)",
        xaxis_title="Number of Predictions",
        yaxis_title="Medical Domains",
        height=500
    )
    
    return fig


def create_model_analytics_table(model_performance):
    """Create detailed model analytics table"""
    if not model_performance:
        return html.Div("No model data available", className="text-muted")
    
    df = pl.DataFrame(model_performance)
    
    # Format data for display
    df['accuracy'] = df['accuracy'].round(3)
    df['f1_score'] = df['f1_score'].round(3)
    df['precision'] = df['precision'].round(3)
    df['recall'] = df['recall'].round(3)
    df['training_time'] = df['training_time'].round(1)
    
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[
            {'name': 'Model Name', 'id': 'name'},
            {'name': 'Type', 'id': 'model_type'},
            {'name': 'Dataset', 'id': 'dataset'},
            {'name': 'Accuracy', 'id': 'accuracy', 'type': 'numeric'},
            {'name': 'F1 Score', 'id': 'f1_score', 'type': 'numeric'},
            {'name': 'Precision', 'id': 'precision', 'type': 'numeric'},
            {'name': 'Recall', 'id': 'recall', 'type': 'numeric'},
            {'name': 'Training Time (min)', 'id': 'training_time', 'type': 'numeric'},
            {'name': 'Domains', 'id': 'domain_count', 'type': 'numeric'},
        ],
        style_cell={'textAlign': 'center', 'padding': '10px'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{f1_score} > 0.8'},
                'backgroundColor': '#d4edda',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{f1_score} < 0.5'},
                'backgroundColor': '#f8d7da',
                'color': 'black',
            }
        ],
        sort_action="native",
        page_size=10
    )


# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)

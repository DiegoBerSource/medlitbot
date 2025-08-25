"""
Dashboard URLs for the MedLitBot web interface
"""
from django.urls import path
from . import views
from .integrated_views import single_port_dashboard, api_chart_data

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('datasets/', views.datasets_list, name='datasets'),
    path('models/', views.models_list, name='models'),
    path('analytics/', views.analytics, name='analytics'),
    path('classification/', views.classification, name='classification'),
    
    # Single port integrated dashboard
    path('integrated/', single_port_dashboard, name='integrated'),
    path('api/chart-data/', api_chart_data, name='chart_data'),
]

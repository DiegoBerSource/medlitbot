"""
URL configuration for medlitbot_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from api.api import api as main_api
from .views import VueAppView, APIHealthView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', main_api.urls),
    path('api/health/', APIHealthView.as_view(), name='api_health'),
    
    # Dashboard (Django-based - optional, can be removed if using Vue only)
    path('dashboard/', include('dashboard.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    from django.views.static import serve
    import os
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Serve Vue.js build assets directly - BEFORE catch-all Vue routes
    urlpatterns += [
        # Vue.js assets directory
        re_path(r'^assets/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'assets'),
        }),
        # Vue.js root files (manifest, service worker, etc.)
        re_path(r'^(?P<path>manifest\.json|manifest\.webmanifest|registerSW\.js|sw\.js|sw\.js\.map|workbox-[^/]+\.js|workbox-[^/]+\.js\.map|vite\.svg|favicon\.ico|favicon\.svg)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'frontend', 'dist'),
        }),
    ]

# Vue.js frontend routes - serve index.html for all other routes (AFTER static files)
# This allows Vue Router to handle client-side routing
# IMPORTANT: Exclude api/, admin/, dashboard/, static/, media/, assets/ from catch-all
urlpatterns += [
    path('', VueAppView.as_view(), name='vue_app_root'),
    re_path(r'^(?!api/|admin/|dashboard/|static/|media/|assets/).*$', VueAppView.as_view(), name='vue_app'),
]

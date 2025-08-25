"""
Main project views - serves the Vue.js frontend
"""

import os
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class VueAppView(View):
    """
    Serves the main Vue.js application for all frontend routes.
    This allows Vue Router to handle client-side routing.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Serve the Vue.js index.html file
        """
        try:
            # Path to the Vue.js build index.html
            index_file_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
            
            if not os.path.exists(index_file_path):
                raise Http404("Vue.js app not found. Please run 'npm run build' in the frontend directory.")
            
            with open(index_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            return HttpResponse(content, content_type='text/html')
            
        except IOError:
            raise Http404("Unable to load Vue.js app")


@method_decorator(csrf_exempt, name='dispatch')
class APIHealthView(View):
    """
    Simple API health check endpoint
    """
    
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            '{"status": "healthy", "message": "MedLitBot API is running"}',
            content_type='application/json'
        )

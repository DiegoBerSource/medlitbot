"""
Django management command to run the Plotly Dash analytics dashboard
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import os


class Command(BaseCommand):
    help = 'Run the Plotly Dash analytics dashboard server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='127.0.0.1',
            help='Host to run the dashboard on (default: 127.0.0.1)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=8050,
            help='Port to run the dashboard on (default: 8050)'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Run dashboard in debug mode'
        )

    def handle(self, *args, **options):
        host = options['host']
        port = options['port']
        debug = options['debug']

        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting MedLitBot Analytics Dashboard...')
        )
        self.stdout.write(
            f'Dashboard will be available at: http://{host}:{port}/'
        )
        self.stdout.write(
            f'Main Django app: http://127.0.0.1:8000/'
        )
        self.stdout.write(
            self.style.WARNING('Press Ctrl+C to stop the dashboard')
        )

        try:
            # Import and run the Dash app
            from dashboard.dash_app import app
            app.run(debug=debug, host=host, port=port)
        
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to import dashboard: {e}')
            )
            self.stdout.write(
                'Make sure Plotly Dash is installed: pip install plotly dash dash-bootstrap-components'
            )
            sys.exit(1)
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Dashboard failed to start: {e}')
            )
            sys.exit(1)

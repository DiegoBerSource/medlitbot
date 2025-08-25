import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medlitbot_project.settings')

app = Celery('medlitbot_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

# Define queues
app.conf.task_routes = {
    'classification.tasks.train_model': {'queue': 'training'},
    'classification.tasks.predict_domains': {'queue': 'prediction'},
    'dataset_management.tasks.process_dataset': {'queue': 'processing'},
}

# Queue definitions
app.conf.task_create_missing_queues = True
app.conf.task_default_queue = 'default'

# Worker configuration
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.worker_max_tasks_per_child = 1000

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

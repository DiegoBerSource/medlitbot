"""
Periodic tasks for monitoring and cleanup
"""
import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from celery import Celery
from .models import MLModel, TrainingJob

logger = logging.getLogger(__name__)


@shared_task
def cleanup_stuck_training_jobs():
    """
    Periodic task to cleanup stuck training jobs
    Runs every 30 minutes to check for orphaned jobs
    """
    logger.info("Running periodic cleanup of stuck training jobs")
    
    # Find jobs that have been running for more than 3 hours
    timeout_threshold = timezone.now() - timedelta(hours=3)
    
    stuck_jobs = TrainingJob.objects.filter(
        status__in=['running', 'pending'],
        created_at__lt=timeout_threshold
    ).select_related('model')
    
    if not stuck_jobs.exists():
        logger.info("No stuck training jobs found")
        return {"cleaned_up": 0, "message": "No stuck jobs found"}
    
    logger.info(f"Found {stuck_jobs.count()} potentially stuck jobs")
    
    # Check which tasks are actually active in Celery
    active_task_ids = set()
    try:
        from django.conf import settings
        app = Celery('medlitbot_project')
        app.config_from_object('django.conf:settings', namespace='CELERY')
        
        inspect = app.control.inspect()
        active_tasks = inspect.active()
        
        if active_tasks:
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    active_task_ids.add(task['id'])
        
        logger.info(f"Found {len(active_task_ids)} active Celery tasks")
        
    except Exception as e:
        logger.warning(f"Could not check Celery active tasks: {e}")
        # Continue with time-based cleanup only
    
    # Cleanup jobs that are not active in Celery
    cleaned_count = 0
    for job in stuck_jobs:
        if job.celery_task_id not in active_task_ids:
            try:
                # Mark training job as failed
                job.status = 'failed'
                job.error_message = 'Training job was stuck/orphaned and cleaned up automatically'
                job.completed_at = timezone.now()
                job.save()
                
                # Mark model as failed to allow retraining
                job.model.status = 'failed'
                job.model.save()
                
                cleaned_count += 1
                logger.info(f"Cleaned up stuck job {job.id}: {job.model.name}")
                
            except Exception as e:
                logger.error(f"Failed to cleanup job {job.id}: {e}")
    
    result = {
        "cleaned_up": cleaned_count,
        "total_checked": stuck_jobs.count(),
        "message": f"Cleaned up {cleaned_count} stuck training jobs"
    }
    
    if cleaned_count > 0:
        logger.warning(f"Cleaned up {cleaned_count} stuck training jobs automatically")
    
    return result


@shared_task
def monitor_long_running_jobs():
    """
    Monitor and log information about long-running training jobs
    """
    logger.info("Monitoring long-running training jobs")
    
    # Jobs running for more than 1 hour
    long_running_threshold = timezone.now() - timedelta(hours=1)
    
    long_jobs = TrainingJob.objects.filter(
        status='running',
        started_at__lt=long_running_threshold
    ).select_related('model')
    
    for job in long_jobs:
        runtime_hours = (timezone.now() - job.started_at).total_seconds() / 3600
        logger.warning(
            f"Long-running job: {job.model.name} "
            f"(Runtime: {runtime_hours:.1f}h, Progress: {job.progress_percentage}%)"
        )
    
    return {
        "long_running_jobs": long_jobs.count(),
        "threshold_hours": 1
    }

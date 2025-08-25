"""
Django management command to cleanup stuck training jobs
"""
import logging
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from celery import Celery
from classification.models import MLModel, TrainingJob

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cleanup stuck training jobs that are no longer active in Celery'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout-hours',
            type=int,
            default=2,
            help='Hours after which a running job is considered stuck (default: 2)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup without prompting for confirmation',
        )

    def handle(self, *args, **options):
        timeout_hours = options['timeout_hours']
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(f"Looking for stuck training jobs (timeout: {timeout_hours}h)")
        
        # Find jobs that have been running too long
        timeout_threshold = timezone.now() - timedelta(hours=timeout_hours)
        
        stuck_jobs = TrainingJob.objects.filter(
            status__in=['running', 'pending'],
            created_at__lt=timeout_threshold
        ).select_related('model')

        if not stuck_jobs.exists():
            self.stdout.write(
                self.style.SUCCESS("✅ No stuck training jobs found!")
            )
            return

        self.stdout.write(
            self.style.WARNING(f"🔍 Found {stuck_jobs.count()} potentially stuck jobs:")
        )

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
            
            self.stdout.write(f"📋 Found {len(active_task_ids)} active Celery tasks")
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Could not check Celery: {e}")
            )
            self.stdout.write("Will proceed with time-based cleanup only")

        jobs_to_cleanup = []
        
        for job in stuck_jobs:
            is_celery_active = job.celery_task_id in active_task_ids
            age_hours = (timezone.now() - job.created_at).total_seconds() / 3600
            
            self.stdout.write(f"\n📦 Job {job.id}: {job.model.name}")
            self.stdout.write(f"   Status: {job.status}")
            self.stdout.write(f"   Age: {age_hours:.1f}h")
            self.stdout.write(f"   Progress: {job.progress_percentage}%")
            self.stdout.write(f"   Celery ID: {job.celery_task_id}")
            self.stdout.write(f"   Active in Celery: {is_celery_active}")
            
            if not is_celery_active:
                jobs_to_cleanup.append(job)
                self.stdout.write(
                    self.style.ERROR("   ❌ WILL BE MARKED AS FAILED")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("   ✅ Still active, keeping")
                )

        if not jobs_to_cleanup:
            self.stdout.write(
                self.style.SUCCESS("\n✅ All running jobs are active in Celery!")
            )
            return

        self.stdout.write(f"\n🧹 Will cleanup {len(jobs_to_cleanup)} stuck jobs")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("🔍 DRY RUN - No changes will be made")
            )
            return

        if not force:
            confirm = input("\nProceed with cleanup? [y/N]: ")
            if confirm.lower() != 'y':
                self.stdout.write("❌ Cleanup cancelled")
                return

        # Cleanup stuck jobs
        cleaned_count = 0
        for job in jobs_to_cleanup:
            try:
                # Mark training job as failed
                job.status = 'failed'
                job.error_message = 'Training job was stuck/orphaned and cleaned up by management command'
                job.completed_at = timezone.now()
                job.save()
                
                # Mark model as failed
                job.model.status = 'failed'
                job.model.save()
                
                cleaned_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Cleaned up job {job.id}: {job.model.name}")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to cleanup job {job.id}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Successfully cleaned up {cleaned_count} stuck training jobs!")
        )
        
        if cleaned_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    "\n💡 Tip: You can now retry training these models from the frontend"
                )
            )

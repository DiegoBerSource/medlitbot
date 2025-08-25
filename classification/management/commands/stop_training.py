"""
Django management command to stop running training jobs
"""
import logging
from django.core.management.base import BaseCommand
from classification.models import MLModel, TrainingJob
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Stop a running training job'

    def add_arguments(self, parser):
        parser.add_argument(
            'model_id',
            type=int,
            help='ID of the model to stop training for',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force stop without prompting for confirmation',
        )

    def handle(self, *args, **options):
        model_id = options['model_id']
        force = options['force']

        try:
            model = MLModel.objects.get(id=model_id)
        except MLModel.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Model with ID {model_id} not found!")
            )
            return

        try:
            training_job = TrainingJob.objects.get(model=model)
        except TrainingJob.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ No training job found for model {model.name}")
            )
            return

        if training_job.status not in ['running', 'pending']:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Training job is not running (status: {training_job.status})")
            )
            return

        self.stdout.write(f"🛑 Stopping training job for model: {model.name}")
        self.stdout.write(f"   Status: {training_job.status}")
        self.stdout.write(f"   Progress: {training_job.progress_percentage}%")
        self.stdout.write(f"   Celery ID: {training_job.celery_task_id}")

        if not force:
            confirm = input("\nProceed with stopping training? [y/N]: ")
            if confirm.lower() != 'y':
                self.stdout.write("❌ Operation cancelled")
                return

        try:
            # Try to revoke the Celery task
            from celery import Celery
            app = Celery('medlitbot_project')
            app.config_from_object('django.conf:settings', namespace='CELERY')
            
            app.control.revoke(training_job.celery_task_id, terminate=True)
            self.stdout.write("🔄 Sent termination signal to Celery task")
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Could not revoke Celery task: {e}")
            )

        # Update database status
        training_job.status = 'cancelled'
        training_job.error_message = 'Training stopped by management command'
        training_job.completed_at = timezone.now()
        training_job.save()

        model.status = 'created'  # Reset to allow retraining
        model.save()

        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully stopped training for model: {model.name}")
        )
        self.stdout.write(
            self.style.SUCCESS("💡 You can now restart training from the frontend")
        )

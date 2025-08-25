#!/usr/bin/env python
"""
Management command to fix model paths for BERT models stored as directories
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from classification.models import MLModel


class Command(BaseCommand):
    help = 'Fix model paths for BERT models stored as directories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        media_root = settings.MEDIA_ROOT
        trained_models_dir = os.path.join(media_root, 'trained_models')
        
        # Find models with missing .pkl files but existing _model directories
        models_to_fix = []
        
        for model in MLModel.objects.filter(model_type='bert'):
            if model.model_path:
                expected_pkl_path = os.path.join(media_root, model.model_path.name)
                # Extract base name correctly
                base_name = os.path.basename(model.model_path.name).replace('.pkl', '')
                model_dir_name = f'{base_name}_model'
                model_dir_path = os.path.join(trained_models_dir, model_dir_name)
                
# Debug output removed
                
                # Check if .pkl file is missing but directory exists
                if not os.path.exists(expected_pkl_path) and os.path.exists(model_dir_path):
                    models_to_fix.append({
                        'model': model,
                        'current_path': model.model_path.name,
                        'directory_path': model_dir_name,
                        'directory_exists': True,
                        'size_mb': self._calculate_directory_size(model_dir_path)
                    })
                elif not os.path.exists(expected_pkl_path):
                    models_to_fix.append({
                        'model': model,
                        'current_path': model.model_path.name,
                        'directory_path': model_dir_name,
                        'directory_exists': False,
                        'size_mb': 0
                    })
        
        if not models_to_fix:
            self.stdout.write(self.style.SUCCESS('No models need path fixing'))
            return
        
        self.stdout.write(f'Found {len(models_to_fix)} models with path issues:')
        
        for item in models_to_fix:
            model = item['model']
            self.stdout.write(f'\nModel {model.id}: {model.name}')
            self.stdout.write(f'  Current path: {item["current_path"]}')
            self.stdout.write(f'  Directory path: {item["directory_path"]}')
            self.stdout.write(f'  Directory exists: {item["directory_exists"]}')
            if item['directory_exists']:
                self.stdout.write(f'  Directory size: {item["size_mb"]:.2f} MB')
            
            if not dry_run:
                if item['directory_exists']:
                    # Update the model path to point to the directory
                    model.model_path.name = f'trained_models/{item["directory_path"]}'
                    model.save(update_fields=['model_path'])
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Updated path to directory')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Directory not found, cannot fix')
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nRun without --dry-run to make these changes')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nFixed paths for {len([m for m in models_to_fix if m["directory_exists"]])} models')
            )
    
    def _calculate_directory_size(self, directory_path):
        """Calculate total size of directory in MB"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except (OSError, IOError):
            pass
        return total_size / (1024 * 1024)

"""
Django management command to generate sample data for dashboard demonstration
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from dataset_management.models import Dataset, DatasetSample
from classification.models import MLModel, TrainingJob, ClassificationResult
import random
import json
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = 'Generate sample data for dashboard demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--datasets',
            type=int,
            default=3,
            help='Number of sample datasets to create (default: 3)'
        )
        parser.add_argument(
            '--samples-per-dataset',
            type=int,
            default=50,
            help='Number of samples per dataset (default: 50)'
        )
        parser.add_argument(
            '--models',
            type=int,
            default=5,
            help='Number of sample models to create (default: 5)'
        )
        parser.add_argument(
            '--predictions',
            type=int,
            default=100,
            help='Number of sample predictions to create (default: 100)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before generating new data'
        )

    def handle(self, *args, **options):
        if options['clear_existing']:
            self.stdout.write('🗑️  Clearing existing data...')
            ClassificationResult.objects.all().delete()
            TrainingJob.objects.all().delete()
            MLModel.objects.all().delete()
            DatasetSample.objects.all().delete()
            Dataset.objects.all().delete()

        self.stdout.write('📊 Generating sample datasets...')
        datasets = self.create_sample_datasets(options['datasets'], options['samples_per_dataset'])
        
        self.stdout.write('🤖 Generating sample models...')
        models = self.create_sample_models(datasets, options['models'])
        
        self.stdout.write('🏋️ Generating training jobs...')
        self.create_sample_training_jobs(models)
        
        self.stdout.write('🔮 Generating classification results...')
        self.create_sample_predictions(models, options['predictions'])
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully generated sample data!')
        )
        self.stdout.write(f'   - {len(datasets)} datasets')
        self.stdout.write(f'   - {sum(d.samples.count() for d in datasets)} dataset samples')
        self.stdout.write(f'   - {len(models)} ML models')
        self.stdout.write(f'   - {TrainingJob.objects.count()} training jobs')
        self.stdout.write(f'   - {options["predictions"]} classification results')

    def create_sample_datasets(self, num_datasets, samples_per_dataset):
        """Create sample datasets with realistic medical literature data"""
        
        # Medical domains and related keywords
        medical_domains = {
            'cardiology': ['heart', 'cardiac', 'cardiovascular', 'coronary', 'arrhythmia', 'hypertension'],
            'neurology': ['brain', 'neural', 'cognitive', 'alzheimer', 'parkinson', 'stroke'],
            'oncology': ['cancer', 'tumor', 'malignant', 'chemotherapy', 'radiation', 'metastasis'],
            'respiratory': ['lung', 'pulmonary', 'asthma', 'COPD', 'pneumonia', 'breathing'],
            'endocrinology': ['diabetes', 'hormone', 'thyroid', 'insulin', 'metabolism', 'endocrine'],
            'infectious_disease': ['infection', 'virus', 'bacteria', 'antibiotic', 'pathogen', 'COVID-19'],
            'gastroenterology': ['stomach', 'intestine', 'liver', 'digestive', 'hepatitis', 'gastric'],
            'rheumatology': ['arthritis', 'immune', 'inflammatory', 'joint', 'lupus', 'autoimmune'],
            'dermatology': ['skin', 'dermatitis', 'melanoma', 'psoriasis', 'eczema', 'rash'],
            'psychiatry': ['depression', 'anxiety', 'mental health', 'schizophrenia', 'bipolar', 'therapy']
        }
        
        dataset_names = [
            'Medical Literature Review 2024',
            'Clinical Trials Database',
            'PubMed Research Articles',
            'European Medical Journal',
            'Global Health Studies',
            'Biomedical Research Collection'
        ]
        
        datasets = []
        for i in range(num_datasets):
            # Create dataset
            dataset = Dataset.objects.create(
                name=random.choice(dataset_names) + f" (Set {i+1})",
                description=f"Sample medical literature dataset containing {samples_per_dataset} articles",
                file_path=f"sample_data/dataset_{i+1}.csv",
                total_samples=samples_per_dataset,
                is_validated=random.choice([True, True, True, False]),  # 75% validated
                medical_domains=random.sample(list(medical_domains.keys()), k=random.randint(3, 6))
            )
            
            # Create samples for this dataset
            for j in range(samples_per_dataset):
                # Pick 1-3 random domains for this sample
                sample_domains = random.sample(dataset.medical_domains, k=random.randint(1, 3))
                
                # Generate title and abstract with relevant keywords
                title_keywords = []
                abstract_keywords = []
                
                for domain in sample_domains:
                    title_keywords.extend(random.sample(medical_domains[domain], 2))
                    abstract_keywords.extend(random.sample(medical_domains[domain], 3))
                
                title = self.generate_medical_title(title_keywords) + f" - Study #{j+1}"
                abstract = self.generate_medical_abstract(abstract_keywords)
                
                DatasetSample.objects.create(
                    dataset=dataset,
                    title=title,
                    abstract=abstract,
                    authors=f"{fake.name()}, {fake.name()}",
                    publication_year=fake.date_between(start_date='-5y', end_date='today').year,
                    doi=f"10.1000/sample.{random.randint(1000, 9999)}",
                    medical_domains=sample_domains
                )
            
            datasets.append(dataset)
            self.stdout.write(f'   Created dataset: {dataset.name}')
        
        return datasets

    def generate_medical_title(self, keywords):
        """Generate a realistic medical research title"""
        templates = [
            "A {study_type} study of {treatment} in {condition} patients",
            "Effect of {treatment} on {outcome} in {population}",
            "{treatment} for {condition}: {study_type} results",
            "Clinical efficacy of {treatment} in {condition} management",
            "{outcome} following {treatment} in {population}: {study_type}",
            "Novel {treatment} approach for {condition} treatment",
        ]
        
        study_types = ['randomized controlled', 'longitudinal', 'cross-sectional', 'cohort', 'case-control', 'systematic review']
        treatments = ['therapy', 'intervention', 'medication', 'treatment', 'surgery', 'procedure']
        conditions = keywords + ['disease', 'syndrome', 'disorder', 'condition']
        outcomes = ['survival', 'quality of life', 'symptoms', 'recovery', 'mortality', 'efficacy']
        populations = ['elderly patients', 'adults', 'children', 'women', 'men', 'patients']
        
        template = random.choice(templates)
        return template.format(
            study_type=random.choice(study_types),
            treatment=random.choice(treatments),
            condition=random.choice(conditions),
            outcome=random.choice(outcomes),
            population=random.choice(populations)
        ).title()

    def generate_medical_abstract(self, keywords):
        """Generate a realistic medical abstract"""
        background = f"Background: {random.choice(keywords).title()} represents a significant clinical challenge in modern medicine."
        
        methods = f"Methods: We conducted a study involving {random.randint(50, 500)} patients with {random.choice(keywords)}."
        
        results = f"Results: Treatment showed significant improvement in {random.choice(['symptoms', 'outcomes', 'quality of life'])} (p<0.05)."
        
        conclusion = f"Conclusion: Our findings suggest that {random.choice(keywords)} treatment is effective and safe."
        
        return f"{background} {methods} {results} {conclusion}"

    def create_sample_models(self, datasets, num_models):
        """Create sample ML models"""
        model_types = ['biobert', 'clinicalbert', 'scibert', 'traditional', 'hybrid']
        model_names = [
            'BioBERT Medical Classifier',
            'ClinicalBERT Disease Predictor', 
            'SciBERT Literature Analyzer',
            'SVM Traditional Classifier',
            'Random Forest Model',
            'Hybrid Ensemble Classifier'
        ]
        
        models = []
        for i in range(num_models):
            dataset = random.choice(datasets)
            model_type = random.choice(model_types)
            
            # Generate realistic performance metrics
            base_accuracy = random.uniform(0.75, 0.95)
            accuracy = base_accuracy + random.uniform(-0.05, 0.05)
            f1_score = base_accuracy + random.uniform(-0.08, 0.08)
            precision = base_accuracy + random.uniform(-0.06, 0.06)
            recall = base_accuracy + random.uniform(-0.07, 0.07)
            
            # Ensure metrics are in valid range
            accuracy = max(0.5, min(1.0, accuracy))
            f1_score = max(0.5, min(1.0, f1_score))
            precision = max(0.5, min(1.0, precision))
            recall = max(0.5, min(1.0, recall))
            
            model = MLModel.objects.create(
                name=f"{random.choice(model_names)} {i+1}",
                description=f"Sample {model_type} model for medical domain classification",
                model_type=model_type,
                dataset=dataset,
                parameters={
                    'learning_rate': random.choice([1e-5, 2e-5, 3e-5, 5e-5]),
                    'batch_size': random.choice([8, 16, 32]),
                    'max_length': random.choice([256, 512]),
                    'epochs': random.randint(3, 8)
                },
                status='trained',
                is_trained=True,
                accuracy=accuracy,
                f1_score=f1_score,
                precision=precision,
                recall=recall,
                training_time_minutes=random.uniform(30, 180),
                num_epochs=random.randint(3, 8),
                best_epoch=random.randint(2, 6),
                domain_performance={
                    domain: {
                        'f1_score': random.uniform(0.6, 0.95),
                        'precision': random.uniform(0.6, 0.95),
                        'recall': random.uniform(0.6, 0.95)
                    } for domain in dataset.medical_domains[:5]
                },
                training_completed_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            models.append(model)
            self.stdout.write(f'   Created model: {model.name} (F1: {f1_score:.3f})')
        
        return models

    def create_sample_training_jobs(self, models):
        """Create sample training job history"""
        # Each model can only have one training job (OneToOneField relationship)
        for i, model in enumerate(models):
            # Randomly assign different statuses to make it more interesting
            if i == 0:
                status = 'running'
                progress = random.uniform(30, 80)
                current_epoch = random.randint(2, 5)
                total_epochs = random.randint(6, 10)
                started_at = timezone.now() - timedelta(hours=random.randint(1, 6))
                completed_at = None
            elif i == len(models) - 1:
                status = 'failed'
                progress = random.uniform(10, 60)
                current_epoch = random.randint(1, 4)
                total_epochs = random.randint(5, 8)
                started_at = timezone.now() - timedelta(hours=random.randint(2, 12))
                completed_at = None
            else:
                status = 'completed'
                progress = 100.0
                current_epoch = model.num_epochs
                total_epochs = model.num_epochs
                started_at = model.training_completed_at - timedelta(hours=random.randint(1, 8))
                completed_at = model.training_completed_at
            
            TrainingJob.objects.create(
                model=model,
                status=status,
                progress_percentage=progress,
                current_epoch=current_epoch,
                total_epochs=total_epochs,
                current_loss=random.uniform(0.1, 1.0),
                current_accuracy=model.accuracy if status == 'completed' else random.uniform(0.4, 0.8),
                started_at=started_at,
                completed_at=completed_at,
                celery_task_id=f"{status}-{model.id}-{random.randint(1000, 9999)}"
            )

    def create_sample_predictions(self, models, num_predictions):
        """Create sample classification results"""
        sample_titles = [
            "COVID-19 vaccine effectiveness in elderly patients",
            "Novel cancer immunotherapy treatment outcomes",
            "Heart disease risk factors in diabetes patients",
            "Neurological complications in stroke patients",
            "Antibiotic resistance in hospital infections",
            "Mental health impacts of chronic diseases",
            "Liver transplant success rates analysis",
            "Skin cancer detection using AI methods",
            "Respiratory therapy for COPD patients",
            "Hormone replacement therapy benefits and risks"
        ]
        
        for i in range(num_predictions):
            model = random.choice(models)
            title = random.choice(sample_titles)
            abstract = self.generate_medical_abstract(model.dataset.medical_domains)
            
            # Generate predicted domains (1-3 domains)
            available_domains = model.dataset.medical_domains
            predicted_domains = random.sample(available_domains, k=random.randint(1, min(3, len(available_domains))))
            
            # Generate confidence scores
            confidence_scores = {
                domain: random.uniform(0.5, 0.95) for domain in predicted_domains
            }
            
            all_domain_scores = {
                domain: random.uniform(0.1, 0.95) for domain in available_domains
            }
            
            ClassificationResult.objects.create(
                model=model,
                title=title,
                abstract=abstract,
                predicted_domains=predicted_domains,
                confidence_scores=confidence_scores,
                all_domain_scores=all_domain_scores,
                prediction_threshold=0.5,
                inference_time_ms=random.uniform(100, 1000),
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )

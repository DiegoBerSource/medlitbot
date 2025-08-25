"""
Celery tasks for dataset processing
"""
import logging
import polars as pl
from typing import Dict, List
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .models import Dataset, DatasetSample

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_dataset_file(self, dataset_id: int) -> Dict:
    """
    Process uploaded dataset file and extract samples
    
    This task:
    1. Reads the uploaded file (CSV, JSON, Excel)
    2. Validates the data format
    3. Creates DatasetSample objects
    4. Updates dataset statistics
    5. Runs validation checks
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        logger.info(f"Processing dataset file for: {dataset.name}")
        
        # Update dataset status
        dataset.validation_errors = []
        
        # Read file based on extension
        file_path = dataset.file_path.path
        file_extension = dataset.file_extension
        
        if file_extension == 'csv':
            # Auto-detect CSV separator (comma vs semicolon)
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if ';' in first_line and first_line.count(';') > first_line.count(','):
                    separator = ';'
                else:
                    separator = ','
            
            df = pl.read_csv(file_path, separator=separator)
            logger.info(f"Detected CSV separator: '{separator}'")
            
        elif file_extension == 'json':
            df = pl.read_json(file_path)
        elif file_extension in ['xlsx', 'xls']:
            # For Excel files, we'll use pandas and convert to polars
            import pandas as pd
            df_pandas = pd.read_excel(file_path)
            df = pl.from_pandas(df_pandas)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        logger.info(f"Read {len(df)} rows from file")
        logger.info(f"Detected columns: {list(df.columns)}")
        
        # Validate required columns
        required_columns = ['title', 'abstract']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns: {missing_columns}"
            dataset.validation_errors.append(error_msg)
            dataset.is_validated = False
            dataset.save()
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        # Detect domain column name (flexible naming)
        domain_column = None
        possible_domain_columns = ['medical_domains', 'domains', 'domain', 'group', 'groups', 'category', 'categories', 'class', 'classes', 'label', 'labels']
        
        for col_name in possible_domain_columns:
            if col_name in df.columns:
                domain_column = col_name
                logger.info(f"Detected domain column: '{domain_column}'")
                break
        
        if not domain_column:
            logger.warning("No domain column detected. Articles will be processed without domain classification.")
        
        # Note: Optional columns handled individually in processing loop
        
        # Clear existing samples if any
        DatasetSample.objects.filter(dataset=dataset).delete()
        
        # Process each row
        samples_created = 0
        errors = []
        all_domains = set()
        title_lengths = []
        abstract_lengths = []
        
        for idx, row in enumerate(df.iter_rows(named=True)):
            try:
                # Extract medical domains using detected column
                domains = []
                if domain_column and domain_column in row and row[domain_column] is not None:
                    domain_value = row[domain_column]
                    if isinstance(domain_value, str):
                        # Handle multiple separators: comma, semicolon, pipe
                        if '|' in domain_value:
                            domains = [d.strip() for d in domain_value.split('|') if d.strip()]
                        elif ',' in domain_value:
                            domains = [d.strip() for d in domain_value.split(',') if d.strip()]
                        elif ';' in domain_value:
                            domains = [d.strip() for d in domain_value.split(';') if d.strip()]
                        else:
                            # Single domain
                            domains = [domain_value.strip()]
                    elif isinstance(domain_value, list):
                        domains = [str(d).strip() for d in domain_value if d]
                    else:
                        # Convert other types to string
                        domains = [str(domain_value).strip()]
                
                # Clean and normalize domain names
                domains = [d.lower().replace(' ', '_').replace('-', '_') for d in domains if d]
                all_domains.update(domains)
                
                # Create sample
                sample = DatasetSample.objects.create(
                    dataset=dataset,
                    title=str(row['title']),
                    abstract=str(row['abstract']),
                    medical_domains=domains,
                    authors=str(row.get('authors', '')) if row.get('authors') is not None else '',
                    journal=str(row.get('journal', '')) if row.get('journal') is not None else '',
                    publication_year=int(row['publication_year']) if row.get('publication_year') is not None else None,
                    doi=str(row.get('doi', '')) if row.get('doi') is not None else '',
                )
                
                # Collect statistics
                title_lengths.append(len(sample.title))
                abstract_lengths.append(len(sample.abstract))
                samples_created += 1
                
            except Exception as e:
                error_msg = f"Error processing row {idx}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
                
                # Stop if too many errors
                if len(errors) > 100:
                    break
        
        # Update dataset statistics
        dataset.total_samples = samples_created
        dataset.medical_domains = list(all_domains)
        
        if title_lengths:
            dataset.avg_title_length = sum(title_lengths) / len(title_lengths)
        if abstract_lengths:
            dataset.avg_abstract_length = sum(abstract_lengths) / len(abstract_lengths)
        
        # Calculate domain distribution
        domain_counts = {}
        for sample in DatasetSample.objects.filter(dataset=dataset):
            for domain in sample.medical_domains:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        dataset.domain_distribution = domain_counts
        dataset.validation_errors = errors
        dataset.is_validated = len(errors) == 0
        dataset.save()
        
        result = {
            "status": "success",
            "samples_created": samples_created,
            "total_domains": len(all_domains),
            "errors": len(errors),
            "is_validated": dataset.is_validated
        }
        
        logger.info(f"Dataset processing completed: {result}")
        return result
        
    except ObjectDoesNotExist:
        error_msg = f"Dataset with id {dataset_id} not found"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}
        
    except Exception as e:
        error_msg = f"Unexpected error processing dataset {dataset_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            dataset.validation_errors = [error_msg]
            dataset.is_validated = False
            dataset.save()
        except Exception:
            # Ignore errors when trying to save error state
            pass
            
        return {"status": "error", "message": error_msg}


@shared_task
def validate_dataset_task(dataset_id: int) -> Dict:
    """
    Validate dataset quality and consistency
    
    Performs additional validation checks:
    1. Data quality checks
    2. Domain consistency
    3. Text length analysis  
    4. Duplicate detection
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        logger.info(f"Validating dataset: {dataset.name}")
        
        samples = DatasetSample.objects.filter(dataset=dataset)
        errors = []
        
        # Check for empty titles or abstracts
        empty_titles = samples.filter(title='').count()
        empty_abstracts = samples.filter(abstract='').count()
        
        if empty_titles > 0:
            errors.append(f"{empty_titles} samples have empty titles")
        if empty_abstracts > 0:
            errors.append(f"{empty_abstracts} samples have empty abstracts")
        
        # Check for duplicates
        duplicates = samples.values('title').annotate(count=models.Count('title')).filter(count__gt=1)
        if duplicates.exists():
            errors.append(f"Found {duplicates.count()} duplicate titles")
        
        # Check domain consistency
        all_domains = set()
        for sample in samples:
            all_domains.update(sample.medical_domains)
        
        # Update dataset
        dataset.validation_errors = errors
        dataset.is_validated = len(errors) == 0
        dataset.medical_domains = list(all_domains)
        dataset.save()
        
        result = {
            "status": "success",
            "is_validated": dataset.is_validated,
            "errors": len(errors),
            "unique_domains": len(all_domains)
        }
        
        logger.info(f"Dataset validation completed: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Error validating dataset {dataset_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}


@shared_task
def preprocess_dataset_samples(dataset_id: int) -> Dict:
    """
    Preprocess text data for model training
    
    Applies text preprocessing:
    1. Text cleaning
    2. Tokenization
    3. Normalization
    4. Medical entity recognition (future)
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        logger.info(f"Preprocessing samples for dataset: {dataset.name}")
        
        # Basic preprocessing (placeholder)
        samples_processed = 0
        
        for sample in DatasetSample.objects.filter(dataset=dataset, is_preprocessed=False):
            # Basic text cleaning (implement more sophisticated preprocessing)
            processed_title = sample.title.strip().lower()
            processed_abstract = sample.abstract.strip().lower()
            
            sample.preprocessed_title = processed_title
            sample.preprocessed_abstract = processed_abstract
            sample.is_preprocessed = True
            sample.save()
            
            samples_processed += 1
        
        result = {
            "status": "success", 
            "samples_processed": samples_processed
        }
        
        logger.info(f"Preprocessing completed: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Error preprocessing dataset {dataset_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}

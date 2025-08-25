# Medical Literature AI Classification System - Claude Code Prompt

## Project Overview
Build a Django-based AI system for medical literature classification that can assign medical articles to one or more medical domains using only title and abstract as input.

## Technical Stack Requirements

### Backend Framework
- **Django 4.2+** with Django Ninja for API endpoints
- **PostgreSQL** for production database with proper indexing
- **Redis** for caching and task queuing
- **Celery** for background model training tasks

### AI/ML Libraries (Priority Order)
1. **Transformers + PyTorch**: Use BioBERT, ClinicalBERT, or SciBERT for domain-specific medical text classification
2. **scikit-learn**: For traditional ML approaches, feature engineering, and model evaluation
3. **spaCy**: For text preprocessing and NLP pipeline (use scispacy for medical texts)
4. **sentence-transformers**: For semantic similarity and embedding-based approaches
5. **datasets**: For efficient data loading and preprocessing
6. **accelerate**: For optimized training on GPU/CPU
7. **optuna**: For hyperparameter optimization

### Data Visualization & Frontend
- **Plotly Dash** integrated with Django for interactive charts and model performance visualization
- **Chart.js** for lightweight frontend charts
- **Bootstrap 5** for responsive UI design
- **DataTables** for efficient dataset management tables

## Core System Architecture

### Models to Implement

```python
# Django Models Structure
class Dataset(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_path = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_samples = models.IntegerField(default=0)
    medical_domains = models.JSONField(default=list)  # Store domain labels
    
class MLModel(models.Model):
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=100)  # 'bert', 'traditional', 'hybrid'
    parameters = models.JSONField(default=dict)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    model_path = models.FileField(upload_to='trained_models/')
    is_trained = models.BooleanField(default=False)
    training_metrics = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
class ClassificationResult(models.Model):
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    abstract = models.TextField()
    predicted_domains = models.JSONField(default=list)
    confidence_scores = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Implementation Requirements

### 1. Dataset Management System
Create comprehensive dataset upload and management:
- **File formats**: Support CSV, JSON, Excel with validation
- **Data preprocessing**: Automatic text cleaning, tokenization, and validation
- **Domain extraction**: Automatic detection of medical domains from training data
- **Data statistics**: Generate comprehensive dataset analytics and visualizations
- **Validation**: Ensure proper format with title, abstract, and domain labels

### 2. Model Architecture Options

#### Option A: Transformer-Based Approach (Recommended)
```python
# Use BioBERT or ClinicalBERT fine-tuned for multi-label classification
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import TrainingArguments, Trainer

# Implement multi-label classification with proper loss functions
# Use focal loss or weighted BCE for imbalanced medical domains
```

#### Option B: Hybrid Ensemble Approach
```python
# Combine multiple approaches:
# 1. Fine-tuned BERT for semantic understanding
# 2. TF-IDF + SVM for traditional ML baseline
# 3. Medical domain-specific keyword matching
# 4. Ensemble voting or stacking for final prediction
```

### 3. Training Pipeline Features
- **Hyperparameter optimization** using Optuna with medical-domain specific search spaces
- **Cross-validation** with stratified splits for multi-label scenarios
- **Early stopping** and learning rate scheduling
- **Model checkpointing** and automatic saving
- **Training monitoring** with real-time metrics visualization
- **Background training** using Celery for long-running processes

### 4. Model Management Interface
Create a comprehensive model management system:
- **Model versioning** with experiment tracking
- **Performance comparison** across different models and parameters
- **Model deployment** pipeline with A/B testing capabilities
- **Automated model evaluation** on hold-out test sets
- **Model interpretability** tools (SHAP, attention visualization)

### 5. Classification Interface
Build an intuitive classification interface:
- **Single article classification** with confidence scores
- **Batch processing** for multiple articles
- **Real-time prediction** API endpoints
- **Results export** in multiple formats (CSV, JSON, PDF reports)
- **Prediction history** and analytics

## Advanced Features to Implement

### 1. Model Performance Analytics
- **Confusion matrices** with interactive heatmaps
- **Precision-Recall curves** for each medical domain
- **ROC curves** and AUC metrics
- **Domain-wise performance** breakdown
- **Training loss/accuracy** curves over time

### 2. Data Visualization Dashboard
Create comprehensive dashboards using Plotly Dash:
- **Dataset statistics** (domain distribution, text length analysis)
- **Model comparison** metrics side-by-side
- **Training progress** visualization
- **Prediction confidence** distribution analysis
- **Domain co-occurrence** network graphs

### 3. Medical Domain Optimization
- **Medical entity recognition** using scispacy
- **Domain-specific vocabulary** analysis
- **Attention weight visualization** for interpretability
- **Active learning** pipeline for continuous improvement
- **Domain hierarchy** modeling (if applicable)

## Code Quality Requirements

### 1. Testing Strategy
- **Unit tests** for all model components
- **Integration tests** for training pipeline
- **Performance tests** for classification speed
- **Data validation tests** for upload functionality
- **API endpoint tests** with mock data

### 2. Documentation Requirements
- **API documentation** using Django Ninja docs
- **Model architecture** documentation with diagrams
- **Training pipeline** step-by-step guides
- **Deployment instructions** with Docker configuration
- **User manual** for the web interface

### 3. Security & Performance
- **File upload validation** with size limits and type checking
- **SQL injection protection** with proper ORM usage
- **Model file security** with proper access controls
- **API rate limiting** for classification endpoints
- **Efficient database queries** with proper indexing

## Development Phases

### Phase 1: Core Infrastructure (Week 1-2)
1. Set up Django project with required dependencies
2. Implement dataset upload and management system
3. Create basic model management interface
4. Set up database models and migrations

### Phase 2: AI Pipeline Development (Week 3-4)
1. Implement transformer-based classification pipeline
2. Add traditional ML baseline for comparison
3. Create training and evaluation workflows
4. Implement hyperparameter optimization

### Phase 3: Advanced Features (Week 5-6)
1. Build comprehensive visualization dashboard
2. Add model interpretability features
3. Implement batch processing capabilities
4. Create performance analytics system

### Phase 4: Polish & Deployment (Week 7)
1. Add comprehensive testing suite
2. Optimize performance and add caching
3. Create deployment documentation
4. Implement monitoring and logging

## Success Metrics
- **Classification accuracy** > 85% on test set
- **Training time** < 2 hours for medium datasets (10K samples)
- **Inference speed** < 1 second per article
- **System scalability** to handle 100K+ articles
- **User interface responsiveness** < 3 seconds page load times

## Sample Implementation Priority
1. Start with BioBERT fine-tuning approach
2. Implement comprehensive evaluation metrics (F1, precision, recall per domain)
3. Focus on multi-label classification capabilities
4. Add interpretability features for medical domain trust
5. Optimize for production deployment with proper error handling

Please implement this system with proper error handling, comprehensive logging, and production-ready code quality. Focus on creating a maintainable, scalable solution that medical professionals can trust and easily use.
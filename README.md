# MedLitBot - Medical Literature AI Classification System

A comprehensive Django-based AI system for medical literature classification that can assign medical articles to one or more medical domains using only title and abstract as input.

## 🚀 Features

- **Dataset Management**: Upload and manage medical literature datasets (CSV, JSON, Excel)
- **AI Model Training**: Train BioBERT, ClinicalBERT, and traditional ML models
- **Real-time Classification**: Classify medical articles with confidence scores
- **Performance Analytics**: Comprehensive model performance tracking and comparison
- **REST API**: Django Ninja-powered API with automatic OpenAPI documentation
- **Background Processing**: Celery-based asynchronous task processing
- **Admin Interface**: Django admin for system management
- **Production Deployment**: Complete Hetzner Cloud infrastructure with ARM64 optimization
- **Cost-Optimized Hosting**: ~€14/month ARM64 infrastructure with Pulumi IaC
- **Docker Support**: Production-ready containerized deployment
- **M1 Mac Support**: Optimized development setup for Apple Silicon

## 🏗️ Architecture

### Tech Stack

- **Backend**: Django 5.0+ with Django Ninja API framework
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Caching & Task Queue**: Redis + Celery
- **AI/ML**: PyTorch, Transformers, scikit-learn, spaCy
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Admin**: Enhanced Django admin interface

### Project Structure

```
medlitbot/
├── medlitbot_project/          # Django project settings
│   ├── settings.py            # Comprehensive configuration
│   ├── urls.py               # URL routing
│   └── celery.py            # Celery configuration
├── infrastructure/             # 🚀 Hetzner Cloud ARM64 infrastructure
│   ├── __main__.py           # Pulumi infrastructure definition  
│   ├── deploy.py            # Automated deployment script
│   └── README.md           # Complete deployment guide
├── api/                      # Main API configuration
│   ├── api.py               # Django Ninja API setup
│   └── schemas.py          # Pydantic schemas for validation
├── dataset_management/       # Dataset management app
│   ├── models.py           # Dataset and DatasetSample models
│   ├── api.py             # Dataset API endpoints
│   └── tasks.py          # Background processing tasks
├── classification/          # ML model management app
│   ├── models.py          # MLModel, TrainingJob, ClassificationResult models
│   ├── api.py            # Classification API endpoints
│   ├── tasks.py         # Training and prediction tasks
│   └── management/      # Training monitoring commands
├── frontend/               # Vue.js 3 + TypeScript frontend
│   ├── src/              # Vue components and views
│   └── dist/            # Built static files
├── docker-compose.prod.yml    # Production Docker setup
├── Dockerfile               # Production container definition
├── nginx.conf              # Nginx reverse proxy config
├── start_m1.sh            # M1 Mac development setup
└── requirements.txt       # Python dependencies
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10+
- PostgreSQL (optional - SQLite fallback available)
- Redis (for caching and task queue)
- Virtual environment tool (venv, conda, etc.)

### Quick Start

1. **Clone and setup environment**:
```bash
git clone <repository-url>
cd medlitbot
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**:
```bash
uv pip install -r requirements.txt
```

3. **Environment configuration**:
```bash
cp env.example .env
# Edit .env with your settings
```

4. **Database setup**:
```bash
# For SQLite (development)
USE_SQLITE=True python manage.py migrate

# For PostgreSQL (production)
python manage.py migrate
```

5. **Create admin user**:
```bash
python manage.py createsuperuser
```

6. **Start services**:
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker (optional)
celery -A medlitbot_project worker -l info

# Terminal 3: Celery beat (optional)
celery -A medlitbot_project beat -l info

Ejemplo:
USE_SQLITE=True celery -A medlitbot_project worker --loglevel=info --detach --logfile=logs/celery.log

# Quick status check:
ps aux | grep celery | grep -v grep

# Emergency restart:
pkill -f "celery.*worker" && USE_SQLITE=True celery -A medlitbot_project worker --loglevel=info --detach --logfile=logs/celery.log
```

## 📚 API Documentation

### Automatic Documentation
- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

### Core Endpoints

#### Dataset Management
- `GET /api/datasets/` - List all datasets
- `POST /api/datasets/` - Create new dataset
- `POST /api/datasets/{id}/upload` - Upload dataset file
- `GET /api/datasets/{id}/samples` - List dataset samples
- `GET /api/datasets/{id}/stats` - Dataset statistics

#### Model Management
- `GET /api/classification/models` - List all models
- `POST /api/classification/models` - Create new model
- `POST /api/classification/models/{id}/train` - Start training
- `GET /api/classification/training-jobs/{id}` - Training progress

#### Classification
- `POST /api/classification/predict` - Single article classification
- `POST /api/classification/predict-batch` - Batch classification
- `GET /api/classification/predictions` - Previous predictions

### Example Usage

#### Upload Dataset
```bash
curl -X POST "http://localhost:8000/api/datasets/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Medical Articles 2024", "description": "Latest medical research papers"}'
```

#### Classify Article
```bash
curl -X POST "http://localhost:8000/api/classification/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "COVID-19 vaccine effectiveness in elderly patients",
    "abstract": "This study examines the effectiveness of COVID-19 vaccines...",
    "threshold": 0.7
  }'
```

## 🗄️ Database Models

### Core Models

#### Dataset
- Manages uploaded medical literature datasets
- Tracks validation status and statistics
- Supports CSV, JSON, Excel formats

#### DatasetSample
- Individual articles within datasets
- Stores title, abstract, medical domains
- Supports preprocessing and metadata

#### MLModel
- AI/ML model configurations and results
- Tracks training progress and performance metrics
- Supports multiple model types (BERT, traditional ML)

#### ClassificationResult
- Stores prediction results
- Includes confidence scores and inference time
- Enables performance analysis

## ⚙️ Configuration

### Environment Variables

Key settings in `.env`:

```env
# Basic Django settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=medlitbot
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# For development with SQLite
USE_SQLITE=True

# Redis for caching and Celery
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Model Configuration

Support for multiple AI model types:

1. **BERT-based Models**:
   - BioBERT for biomedical text
   - ClinicalBERT for clinical notes
   - SciBERT for scientific literature

2. **Generative Models** (⚠️ **Requires HuggingFace Authentication**):
   - Google Gemma 2B for prompt-based classification

3. **Traditional ML**:
   - SVM with TF-IDF
   - Random Forest
   - Gradient Boosting

4. **Hybrid Ensembles**:
   - Combination of multiple approaches
   - Voting or stacking strategies

#### Hugging Face Authentication Setup

For gated models like Gemma, you need to:

1. Get access at [google/gemma-2-2b](https://huggingface.co/google/gemma-2-2b)
2. Create a token at [HF Settings](https://huggingface.co/settings/tokens)
3. Add to your `.env` file:
   ```bash
   HF_TOKEN=your_huggingface_token_here
   ```

## 🔄 Background Tasks

### Celery Tasks

#### Dataset Processing (`datasets.tasks`)
- `process_dataset_file`: Parse and validate uploaded files
- `validate_dataset_task`: Data quality validation
- `preprocess_dataset_samples`: Text preprocessing

#### Model Training (`classification.tasks`)
- `start_model_training`: Train ML models
- `predict_domains`: Single prediction
- `batch_predict_domains`: Batch predictions
- `run_model_comparison`: Compare model performance

### Task Monitoring

Monitor tasks via:
- Django admin interface
- Celery flower (install separately)
- Database task logs

## 🔍 Admin Interface

Enhanced Django admin at `http://localhost:8000/admin/`:

### Features
- **Dataset Management**: Upload validation, statistics view
- **Model Management**: Training monitoring, performance metrics
- **Results Analysis**: Prediction history, confidence analysis
- **System Monitoring**: Background task status

### Admin Models
- Custom list views with relevant metrics
- Filtering and search capabilities
- Inline editing for related objects
- Performance visualizations

## 🧪 Testing

### Test Structure
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test datasets
python manage.py test classification

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Categories
- **Unit Tests**: Model methods, utilities
- **Integration Tests**: API endpoints, task flows  
- **Performance Tests**: Classification speed, memory usage
- **Data Validation Tests**: File parsing, format validation

## 📊 Performance Metrics

### Success Metrics
- **Classification Accuracy**: Target >85% on test sets
- **Training Time**: <2 hours for medium datasets (10K samples)
- **Inference Speed**: <1 second per article
- **System Scalability**: Handle 100K+ articles
- **UI Responsiveness**: <3 seconds page load times

### Monitoring
- Real-time training progress tracking
- Performance analytics dashboard
- Model comparison tools
- System health monitoring

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure PostgreSQL
- [ ] Set up Redis cluster
- [ ] Configure Celery workers
- [ ] Set up monitoring (Sentry)
- [ ] Configure static file serving
- [ ] Set up SSL certificates
- [ ] Configure backup strategy

### Production Deployment

#### Hetzner Cloud (ARM64 Optimized) 
Complete infrastructure-as-code setup with cost optimization:

```bash
cd infrastructure/
# See infrastructure/README.md for complete setup
pulumi up  # Deploys ARM64 infrastructure for ~€14/month
```

#### Docker Production Setup
```bash
# Production deployment with Docker
docker-compose -f docker-compose.prod.yml up -d

# Includes:
# - Django app container (ARM64/x86)
# - PostgreSQL container  
# - Redis container
# - Celery worker container
# - Nginx reverse proxy
```

#### Quick Production Deploy
```bash
# Automated deployment to Hetzner
python infrastructure/deploy.py

# Or manual M1/ARM setup
./start_m1.sh
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Create Pull Request

### Code Standards
- Follow PEP 8 style guide
- Add comprehensive docstrings
- Include unit tests for new features
- Update API documentation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- API Documentation: `/api/docs`
- Admin Guide: `/admin/`
- GitHub Issues: For bug reports and feature requests

### Common Issues
- **Database Connection**: Check PostgreSQL settings or use SQLite fallback
- **Redis Connection**: Ensure Redis server is running
- **File Upload**: Check file permissions and size limits
- **Model Training**: Monitor Celery logs for training issues

---

Built with ❤️ for advancing medical literature analysis and AI research.

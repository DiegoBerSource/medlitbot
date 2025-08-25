# 🤖 MedLitBot - Medical Literature AI Classifier

> **Ready-to-use AI system for classifying medical literature** with pretrained models included!

A powerful Django + Vue.js AI system that classifies medical articles into specialized domains using only the title and abstract. **No training required** - comes with working pretrained models for immediate testing.

## ⚡ Quick Start Demo

Get MedLitBot running in under 5 minutes:

### 1️⃣ Clone & Setup
```bash
git clone https://github.com/DiegoBerSource/medlitbot.git
cd medlitbot
pip install -r requirements.txt
```

### 2️⃣ Run the System
```bash
# For M1/M2 Macs (recommended for Apple Silicon)
./commands/start_m1.sh

# For other systems
./commands/dev-server.sh
```

### 3️⃣ Open & Explore
- **Frontend**: http://localhost:3000 (Modern Vue.js interface)
- **API Docs**: http://localhost:8000/api/docs (Interactive Swagger UI)
- **Admin**: http://localhost:8000/admin (Django admin interface)

## 🎯 What's Included - Ready to Use!

### 🤖 **Pretrained Models**
- **Dr Clasifier BERT**: Transformer model (82.6% accuracy, 92.7% F1)
- **Dr Clasifier ML**: Traditional ML model (73.6% accuracy, 84.8% F1)

### 📊 **Features You Can Try Immediately**
- ✅ **Classify Medical Articles**: Input title + abstract, get medical domains
- ✅ **Performance Analytics**: View confusion matrices and model comparison
- ✅ **Batch Classification**: Process multiple articles at once
- ✅ **Real-time Results**: WebSocket-powered live updates
- ✅ **Interactive Charts**: Beautiful visualizations with Chart.js

### 📁 **Demo Data Included**
- Sample medical literature datasets
- Pretrained model files (traditional + BERT transformer)
- Performance metrics and confusion matrices
- Realistic demo database

## 🖥️ System Requirements

### **M1/M2 Mac Users** (Recommended Setup)
Use `./commands/start_m1.sh` for optimal performance on Apple Silicon:
- Optimized for M1/M2 processors
- Uses MPS (Metal Performance Shaders) acceleration
- Memory-efficient settings for MacBook development
- Automatic Redis and Celery configuration

### **Other Systems**
Use `./commands/dev-server.sh` for standard setup:
- Works on Linux, Windows, Intel Macs
- Standard CPU-based training
- Automatic dependency detection

## 🚀 Usage Examples

### Classify a Medical Article
```python
# Via Python API
from classification.ml_models import get_trained_model
model = get_trained_model('Dr Clasifier BERT')
result = model.predict(
    title="COVID-19 cardiac complications",
    abstract="Study of cardiac effects in COVID patients..."
)
```

### Via REST API
```bash
curl -X POST http://localhost:8000/api/classify/ \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 24,
    "title": "COVID-19 cardiac complications",
    "abstract": "Study of cardiac effects..."
  }'
```

## 🎨 Modern Frontend Features

- **Vue 3 + TypeScript** with improved type safety
- **TailwindCSS** responsive design
- **Chart.js** analytics and confusion matrix visualization
- **PWA Support** - works offline
- **Real-time Updates** via WebSockets
- **Mobile Responsive** design

## 📚 Available Commands

All scripts are organized in the `commands/` folder:

- **`start_m1.sh`** - M1/M2 Mac optimized startup (recommended for Apple Silicon)
- **`dev-server.sh`** - Standard development server
- **`build-frontend.sh`** - Build Vue.js frontend for production
- **`frontend_setup.sh`** - Set up and build frontend dependencies

## 🔧 Advanced Setup

### Custom Configuration
Create a `.env` file with your settings:
```bash
cp env.example .env
# Edit .env with your Hugging Face token and database settings
```

### Train Your Own Models
1. Upload your dataset via the web interface
2. Go to Models → Create New Model
3. Choose BERT, Traditional ML, or Gemma model types
4. Configure hyperparameters and start training
5. Monitor progress in real-time

## 🎓 What You'll Learn

This system demonstrates:
- **Modern ML Architecture**: Django + Celery + Redis + PyTorch
- **Transformer Models**: BERT for medical text classification
- **Traditional ML**: SVM, Random Forest comparison
- **Full-Stack AI**: Backend ML with modern frontend
- **Production Deployment**: Docker, infrastructure as code
- **Real-time AI**: WebSocket integration for live updates

## 📖 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get running in 5 minutes
- **[Architecture Guide](docs/ARCHITECTURE_GUIDE.md)** - System design overview
- **[M1 Mac Setup](docs/M1_MAC_TRAINING_GUIDE.md)** - Apple Silicon optimization
- **[API Documentation](http://localhost:8000/api/docs)** - Interactive Swagger UI (when running)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎯 Ready to classify medical literature with AI?**  
Run `./commands/start_m1.sh` (M1/M2 Mac) or `./commands/dev-server.sh` and start exploring at http://localhost:3000
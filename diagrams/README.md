# 📊 MedLitBot Architecture Diagrams

This folder contains the complete architectural diagrams for the MedLitBot Medical Literature AI Classifier system.

## 📁 Diagram Files

### 01-system-architecture.mmd
**Type**: Flow Chart  
**Description**: Complete system architecture showing all layers, components, and their interactions.

**Shows**:
- Frontend Layer (Vue.js components, state management, visualizations)
- Backend Services (Django apps, API layer, optional Plotly dashboard)
- Machine Learning Layer (BERT models, Traditional ML, Hybrid ensemble)
- Task Processing (Celery workers and queues)
- Data Layer (databases, file storage, caching)
- Infrastructure (Docker, Pulumi deployment)

### 02-process-flow.mmd
**Type**: Sequence Diagram  
**Description**: Detailed process flows for key system operations.

**Shows**:
- Dataset Management Flow (upload, validation, preprocessing)
- Model Training Flow (BERT, Traditional ML, Gemma training paths)
- Classification Flow (real-time and batch processing)
- Analytics Flow (performance metrics, model comparison)
- Hyperparameter Optimization Flow (automated tuning process)

### 03-technology-stack.mmd
**Type**: Mind Map  
**Description**: Complete technology stack and capabilities overview.

**Shows**:
- Frontend Stack (Vue.js, TypeScript, TailwindCSS, PWA)
- Backend Architecture (Django, APIs, modular apps)
- AI/ML Capabilities (transformer models, traditional ML, medical domains)
- Processing Layer (Celery, task management, scalability)
- Data Management (databases, storage, caching)
- Analytics & Monitoring (metrics, visualizations, dashboards)
- Deployment & DevOps (Docker, infrastructure as code)
- Development Tools (scripts, testing, documentation)

## 🖼️ How to Generate Images

### Option 1: Mermaid CLI (Recommended)
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG images
mmdc -i 01-system-architecture.mmd -o 01-system-architecture.png
mmdc -i 02-process-flow.mmd -o 02-process-flow.png
mmdc -i 03-technology-stack.mmd -o 03-technology-stack.png

# Generate SVG images (scalable)
mmdc -i 01-system-architecture.mmd -o 01-system-architecture.svg
mmdc -i 02-process-flow.mmd -o 02-process-flow.svg
mmdc -i 03-technology-stack.mmd -o 03-technology-stack.svg
```

### Option 2: Online Mermaid Editor
1. Visit [Mermaid Live Editor](https://mermaid.live/)
2. Copy the content from any `.mmd` file
3. Paste into the editor
4. Export as PNG, SVG, or PDF

### Option 3: VS Code Extension
1. Install "Mermaid Markdown Syntax Highlighting" extension
2. Open any `.mmd` file
3. Use the preview function to view
4. Export using the extension's export features

## 📋 Diagram Usage

### For Documentation
- Include in project README
- Add to technical specifications
- Use in presentation materials
- Share with stakeholders

### For Development
- Architecture reference during development
- Onboarding new team members
- System design reviews
- Debugging and troubleshooting

### For Deployment
- Infrastructure planning
- DevOps setup reference
- Production deployment guide
- System monitoring setup

## 🔧 Customization

To modify these diagrams:
1. Edit the `.mmd` files directly
2. Use Mermaid syntax for changes
3. Regenerate images after modifications
4. Keep this README updated with changes

## 📚 Related Documentation

- [Architecture Guide](../docs/ARCHITECTURE_GUIDE.md)
- [Quick Start Guide](../docs/QUICK_START.md)
- [Development Guide](../docs/DEVELOPMENT.md)
- [System Status](../docs/SYSTEM_STATUS.md)

---

**Created**: December 2024  
**System**: MedLitBot Medical Literature AI Classifier  
**Format**: Mermaid Diagrams (.mmd)  
**License**: Same as project license

# Phelomia 📄✨
> **AI-Powered Document Analysis & Conversion Platform**

Transform any document into structured data with cutting-edge AI technology. Phelomia leverages IBM's Granite Docling model to provide intelligent document understanding, extraction, and conversion capabilities.

## 🚀 Quick Start (30 seconds)

### Option 1: Automated Setup
```bash
git clone https://github.com/Saksham932007/Phelomia.git
cd Phelomia
chmod +x setup.sh && ./setup.sh
./start.sh
```

### Option 2: Docker (Recommended for Production)
```bash
git clone https://github.com/Saksham932007/Phelomia.git
cd Phelomia
docker build -t phelomia .
docker run -p 7860:7860 phelomia
```

### Option 3: Manual Setup
```bash
git clone https://github.com/Saksham932007/Phelomia.git
cd Phelomia
python3 -m venv phelomia_env
source phelomia_env/bin/activate  # On Windows: phelomia_env\Scripts\activate
pip install -r requirements.txt
python src/app.py
```

Visit `http://localhost:7860` in your browser to start using Phelomia!

## ✨ What Can Phelomia Do?

### 🎯 Core Features
- **📊 Table Recognition**: Extract tables and convert to structured formats (CSV, JSON, OTSL)
- **🧮 Formula Conversion**: Convert mathematical formulas to LaTeX with high accuracy
- **💻 Code Recognition**: Extract and identify code snippets from documents
- **📈 Chart Analysis**: Analyze charts, graphs, and extract underlying data
- **📄 Document Conversion**: Convert documents to Docling format with structure preservation
- **💬 Interactive Chat**: Ask questions about your documents using natural language
- **🌍 Multi-language Support**: Process documents in Arabic, Japanese, Chinese, and English

### 🤖 Intelligent Features
- **Auto-Detection**: Automatically identifies document type and suggests optimal processing
- **Batch Processing**: Handle multiple documents simultaneously
- **Real-time Streaming**: Live response generation for immediate feedback
- **Quality Metrics**: Confidence scores and accuracy measurements
- **Performance Analytics**: Track usage patterns and system performance

## 📸 Screenshots & Demo

### Modern Interface
![Landing Page](assets/screenshots/landing.png)
*Smart landing page with auto-detection capabilities*

### Document Analysis
![Analysis Interface](assets/screenshots/analysis.png)
*Progressive interface with intelligent recommendations*

### Results Dashboard
![Results](assets/screenshots/results.png)
*Comprehensive results with chat integration*

## 🏗️ Architecture

```
Phelomia/
├── src/
│   ├── app.py                    # Main Gradio application
│   ├── config.py                 # Configuration management
│   ├── modern_ui.py              # Modern UI components
│   ├── document_intelligence.py  # AI document analysis
│   ├── batch_processing.py       # Batch processing system
│   ├── analytics.py              # Performance tracking
│   └── themes/
│       ├── carbon.py             # IBM Carbon design theme
│       └── research_monochrome.py
├── data/images/                  # Sample documents
├── logs/                         # Application logs
├── results/                      # Processing results
└── assets/                      # Static assets
```

## ⚙️ Configuration

Create a `.env` file (copy from `.env.example`) to customize settings:

```env
# Model Configuration
PHELOMIA_MODEL_NAME=HuggingFaceM4/idefics3-8b-docling
PHELOMIA_DEVICE=auto              # auto, cuda, cpu, mps
PHELOMIA_MAX_LENGTH=1024

# UI Configuration
PHELOMIA_THEME=carbon             # carbon, research_monochrome
PHELOMIA_ENABLE_CHAT=true
PHELOMIA_MAX_FILE_SIZE=10         # MB

# Performance
PHELOMIA_BATCH_SIZE=1
PHELOMIA_CACHE_ENABLED=true
```

## 📊 Usage Examples

### Python API
```python
from src.document_intelligence import analyze_document_type
from src.batch_processing import batch_processor

# Analyze single document
analysis = analyze_document_type("path/to/document.png")
print(f"Detected type: {analysis['suggested_analysis']}")
print(f"Confidence: {analysis['confidence_scores']}")

# Batch processing
job_id = await batch_processor.submit_batch_job(
    file_paths=["doc1.png", "doc2.png"],
    analysis_types=["table", "formula"]
)

# Monitor progress
status = batch_processor.get_job_status(job_id)
print(f"Progress: {status['progress']}%")
```

### REST API (Coming Soon)
```bash
# Upload and analyze document
curl -X POST "http://localhost:7860/api/analyze" \
  -F "file=@document.png" \
  -F "analysis_types=table,formula"

# Get analysis results
curl "http://localhost:7860/api/results/{job_id}"
```

## 🛠️ Development

### Setting up Development Environment
```bash
# Clone and setup
git clone https://github.com/Saksham932007/Phelomia.git
cd Phelomia
./setup.sh

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run with hot reload
python src/app.py --reload
```

### Adding New Features

1. **Document Type Detector**: Extend `src/document_intelligence.py`
2. **UI Components**: Add to `src/modern_ui.py`
3. **Processing Logic**: Modify `src/app.py`
4. **Themes**: Create new themes in `src/themes/`

### Testing
```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run performance tests
pytest tests/performance/

# Generate coverage report
pytest --cov=src tests/
```

## 📈 Performance & Monitoring

### Built-in Analytics
- Real-time processing metrics
- Usage patterns and trends
- Error tracking and debugging
- User feedback collection

### Access Admin Dashboard
Visit `http://localhost:7860/admin` (in development) to view:
- System performance metrics
- Usage analytics
- Error reports
- User feedback

### Performance Optimization
- **GPU Acceleration**: Automatic CUDA/MPS detection
- **Batch Processing**: Handle multiple documents efficiently
- **Caching**: Intelligent result caching
- **Memory Management**: Optimized for large documents

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Setup
```bash
# Fork the repository
git clone https://github.com/your-username/Phelomia.git
cd Phelomia

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
./setup.sh
python src/app.py

# Submit pull request
git add .
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

## 📋 Roadmap

### v2.0 (Next Release)
- [ ] REST API with OpenAPI documentation
- [ ] Plugin system for custom processors
- [ ] Advanced OCR integration
- [ ] Multi-format output support (PDF, DOCX, etc.)
- [ ] Collaboration features

### v3.0 (Future)
- [ ] Cloud deployment templates
- [ ] Enterprise SSO integration
- [ ] Advanced workflow automation
- [ ] Real-time collaboration
- [ ] Mobile application

## 🐛 Troubleshooting

### Common Issues

**Installation Problems**
```bash
# Python version issues
python3 --version  # Ensure 3.8+

# Permission issues
sudo chmod +x setup.sh

# Dependency conflicts
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Runtime Issues**
```bash
# Out of memory
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Model loading issues
export TRANSFORMERS_CACHE=/path/to/cache

# Port conflicts
python src/app.py --port 7861
```

**Performance Issues**
- Use GPU when available (`PHELOMIA_DEVICE=cuda`)
- Reduce batch size for memory constraints
- Enable caching for repeated operations

### Getting Help
- 📖 [Documentation](https://github.com/Saksham932007/Phelomia/wiki)
- 🐛 [Issue Tracker](https://github.com/Saksham932007/Phelomia/issues)
- 💬 [Discussions](https://github.com/Saksham932007/Phelomia/discussions)
- 📧 [Email Support](mailto:support@phelomia.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **IBM Research** for the Granite Docling model
- **Hugging Face** for the Transformers library and model hosting
- **Gradio** for the fantastic web interface framework
- **OpenCV** and **PIL** for image processing capabilities
- **All contributors** who help make Phelomia better

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/Saksham932007/Phelomia?style=social)
![GitHub forks](https://img.shields.io/github/forks/Saksham932007/Phelomia?style=social)
![GitHub issues](https://img.shields.io/github/issues/Saksham932007/Phelomia)
![GitHub license](https://img.shields.io/github/license/Saksham932007/Phelomia)
![Python version](https://img.shields.io/badge/python-3.8+-blue.svg)

---

**Built with ❤️ by the Phelomia Team**

*Transforming documents, one AI prediction at a time.*
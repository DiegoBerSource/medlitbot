# Google Gemma 2B Integration Guide

This guide explains how to use Google's Gemma 2B model with MedLitBot for medical literature classification.

## Overview

Gemma 2B is a lightweight, efficient generative model that has been integrated into MedLitBot to provide an alternative approach to medical text classification. Unlike traditional BERT-based models that are specifically designed for classification, Gemma uses a prompt-based approach to generate classifications.

## Key Features

- **Efficient Memory Usage**: Uses 4-bit quantization for GPU deployment
- **CPU Compatible**: Works on Apple Silicon and standard CPUs
- **Prompt-Based Classification**: Uses natural language prompts for classification
- **Integration Ready**: Seamlessly works with existing MedLitBot infrastructure

## Requirements

### Authentication Setup

**IMPORTANT**: Gemma models are gated on Hugging Face and require authentication. You must:

1. **Create a Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co)
2. **Request Access**: Visit [google/gemma-2-2b](https://huggingface.co/google/gemma-2-2b) and click "Request access"
3. **Get Your Token**: Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens) and create a new token
4. **Set Environment Variable**: Add your token to your `.env` file:
   ```bash
   HF_TOKEN=your_actual_hugging_face_token_here
   ```

**Without proper authentication, you will get a "401 Client Error" when training Gemma models.**

### Software Dependencies

```bash
# Update requirements with Gemma-specific dependencies
uv pip install -r requirements.txt

# Key dependencies added:
# - transformers>=4.40.0 (for Gemma support)
# - accelerate>=0.26.0 (for efficient loading)  
# - bitsandbytes>=0.43.0 (for quantization)
```

### Hardware Requirements

**Minimum:**
- 8GB RAM (CPU mode)
- 4GB disk space for model cache

**Recommended:**
- 16GB RAM + GPU with 8GB VRAM (for optimal performance)
- CUDA-compatible GPU (optional but recommended)

## Quick Start

### 1. Basic Usage

```python
from classification.ml_models import create_model

# Create Gemma 2B classifier
gemma_model = create_model('gemma2-2b', num_labels=10, max_length=512)

# Sample medical texts and labels
texts = [
    "This study investigates cardiovascular disease risk factors in diabetic patients."
]
labels = [["cardiology", "endocrinology"]]

# Load model for inference (called "training" for API compatibility)
results = gemma_model.train(texts, labels)

# Make predictions
predictions = gemma_model.predict([
    "Analysis of brain tumor imaging using MRI and CT scans."
])

print(predictions[0]['predicted_domains'])  # Expected: neurology, radiology
```

### 2. Django Integration

1. **Create Dataset**: Use Django admin to create a dataset
2. **Create Model**: Select "Google Gemma 2B" as model type
3. **Configure Parameters**: Leave default parameters for initial testing
4. **Start Training**: This loads the model for inference mode

### 3. API Usage

```bash
# Create model via API
curl -X POST http://localhost:8000/api/models/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gemma Medical Classifier",
    "model_type": "gemma2-2b", 
    "dataset_id": 1,
    "description": "Gemma 2B for medical text classification"
  }'

# Start training (loads for inference)
curl -X POST http://localhost:8000/api/models/{model_id}/train/

# Make predictions
curl -X POST http://localhost:8000/api/classify/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cardiovascular Risk Assessment",
    "abstract": "This study analyzes heart disease risk factors...",
    "model_id": 1
  }'
```

## How It Works

### Architecture

1. **Model Loading**: Gemma 2B is loaded using `AutoModelForCausalLM`
2. **Quantization**: 4-bit quantization reduces memory usage by ~75%
3. **Prompt Engineering**: Creates classification prompts with domain options
4. **Response Parsing**: Extracts predicted domains from generated text

### Classification Process

```
Input Text → Prompt Template → Gemma Model → Generated Response → Parsed Domains
```

Example prompt:
```
Classify the following medical text into one or more of these domains: cardiology, neurology, radiology

Text: This study investigates cardiovascular disease risk factors in diabetic patients.

Classification (respond with only the relevant domain names, separated by commas):
```

## Performance Characteristics

### Advantages
- **No Fine-tuning Required**: Works out of the box with prompt engineering
- **Memory Efficient**: 4-bit quantization reduces memory requirements
- **Flexible**: Can adapt to new domains without retraining
- **Multilingual**: Supports 140+ languages for international medical literature
- **Performance Metrics**: Automatically calculates accuracy, F1, precision, and recall on validation data

### Considerations
- **Speed**: Slower than fine-tuned BERT models for classification
  - **Training Time**: ~5-10 minutes (with optimized evaluation)
  - **Fast Mode**: ~2-3 minutes (minimal evaluation for testing)
- **Accuracy**: May require prompt optimization for optimal results
- **Domain Adaptation**: Not specifically trained on medical literature
- **Resource Usage**: Still requires significant compute for inference
- **Evaluation**: Automatically evaluates performance on validation set to generate metrics

## Benchmarking

Compare Gemma 2B with existing models:

```python
# Run benchmark comparison
python test_gemma_integration.py

# Expected performance characteristics:
# - Inference time: ~2-5x slower than BioBERT
# - Memory usage: ~4GB (quantized) vs ~2GB (BioBERT)
# - Accuracy: Competitive for general classification, may need optimization for specialized medical domains
```

## Performance Optimization

### Speed Up Training

**Normal Mode (Default)**:
- Evaluates on 100 validation samples
- Training time: ~5-10 minutes
- Good balance of speed and metric accuracy

**Fast Mode (Testing)**:
```python
# Enable fast mode for quick testing
training_config = {
    'fast_mode': True,
    # other parameters...
}
```
- Evaluates on only 20 validation samples  
- Training time: ~2-3 minutes
- Use for quick experiments and testing

### Why Gemma Training Takes Time

Unlike BERT models that actually train, Gemma "training" involves:
1. **Model Loading** (~2-3 minutes): Downloads 2.7GB model
2. **Evaluation** (~2-7 minutes): Runs text generation on validation samples
   - Each prediction requires generating ~100 tokens
   - Sequential processing (not batched)
   - CPU-only on Apple Silicon

## Troubleshooting

### Common Issues

1. **Authentication Error (401 Client Error)**
   ```
   Error: You are trying to access a gated repo. Make sure to have access to it at 
   https://huggingface.co/google/gemma-2-2b. 401 Client Error.
   ```
   
   **Solutions:**
   - Ensure you have requested access to the Gemma model at [google/gemma-2-2b](https://huggingface.co/google/gemma-2-2b)
   - Set your HF_TOKEN in your `.env` file:
     ```bash
     HF_TOKEN=your_actual_token_here
     ```
   - Verify your token has the necessary permissions
   - Wait for approval if your access request is still pending

2. **CUDA Out of Memory**
   ```python
   # Solution: Force CPU mode
   gemma_model = create_model('gemma2-2b', device='cpu')
   ```

2. **Model Download Timeout**
   ```bash
   # Pre-download model
   python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('google/gemma-2-2b')"
   ```

3. **Quantization Not Working**
   ```bash
   # Install/update bitsandbytes
   uv pip install --upgrade bitsandbytes
   ```

4. **Apple Silicon Issues**
   - Models automatically use CPU mode on Apple Silicon
   - Disable MPS backend (handled automatically)
   - Single-threaded execution for stability

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('classification.ml_models').setLevel(logging.DEBUG)
```

## Best Practices

### Prompt Optimization

1. **Clear Instructions**: Use explicit classification instructions
2. **Domain Lists**: Provide complete, well-defined domain options
3. **Examples**: Consider few-shot prompting for better accuracy
4. **Consistency**: Standardize domain names and formatting

### Performance Optimization

1. **Batch Processing**: Process multiple texts together when possible
2. **Caching**: Cache model instances to avoid repeated loading
3. **Memory Management**: Use quantization for GPU deployments
4. **Hardware**: Use GPU when available, fall back to CPU gracefully

### Integration Tips

1. **Hybrid Approach**: Consider combining with BioBERT for specialized domains
2. **Validation**: Compare results against domain experts initially
3. **Monitoring**: Track inference time and accuracy metrics
4. **Fallback**: Implement fallback to traditional models if needed

## Future Enhancements

### Planned Improvements

1. **LoRA Fine-tuning**: Add Parameter-Efficient Fine-Tuning support
2. **Confidence Scoring**: Implement better confidence estimation
3. **Domain Adaptation**: Create medical domain-specific prompts
4. **Ensemble Methods**: Combine Gemma with existing models

### Contributing

To improve Gemma integration:

1. Test with your medical datasets
2. Optimize prompts for specific domains  
3. Report performance comparisons
4. Suggest new features or improvements

## Support

For issues with Gemma integration:

1. Check the troubleshooting section above
2. Run the test script: `python test_gemma_integration.py`
3. Review logs for detailed error information
4. Create an issue with reproduction steps

## References

- [Google Gemma Models](https://blog.google/technology/developers/gemma-3/)
- [Hugging Face Gemma Documentation](https://huggingface.co/google/gemma-2-2b)
- [Transformers Library](https://huggingface.co/docs/transformers/)
- [BitsAndBytes Quantization](https://github.com/TimDettmers/bitsandbytes)



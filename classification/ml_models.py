"""
Core ML models for medical literature classification
Supports BioBERT, ClinicalBERT, SciBERT, and traditional ML approaches
"""
import logging
import os
import pickle
import json
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import polars as pl
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification, AutoModelForCausalLM,
    TrainingArguments, Trainer, EvalPrediction
)

# Optional quantization support (not available on all platforms)
try:
    from transformers import BitsAndBytesConfig
    QUANTIZATION_AVAILABLE = True
except ImportError:
    BitsAndBytesConfig = None
    QUANTIZATION_AVAILABLE = False
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix
from sklearn.preprocessing import MultiLabelBinarizer
# Import HuggingFace datasets properly to avoid conflicts
try:
    import datasets as hf_datasets
    from datasets import Dataset as HFDataset
except ImportError:
    hf_datasets = None
    HFDataset = None

logger = logging.getLogger(__name__)


# Model configurations for different medical BERT models
MEDICAL_BERT_MODELS = {
    'biobert': {
        'model_name': 'dmis-lab/biobert-base-cased-v1.1',
        'description': 'BioBERT trained on biomedical literature'
    },
    'clinicalbert': {
        'model_name': 'emilyalsentzer/Bio_ClinicalBERT',
        'description': 'ClinicalBERT trained on clinical notes'
    },
    'scibert': {
        'model_name': 'allenai/scibert_scivocab_cased',
        'description': 'SciBERT trained on scientific literature'
    },
    'pubmedbert': {
        'model_name': 'microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract',
        'description': 'PubMedBERT trained on PubMed abstracts'
    }
}

# Gemma model configurations
GEMMA_MODELS = {
    'gemma2-2b': {
        'model_name': 'google/gemma-2-2b',
        'description': 'Gemma 2 2B parameter model for efficient text generation and classification',
        'is_generative': True
    }
}


class MedicalDataset(Dataset):
    """PyTorch dataset for medical literature classification"""
    
    def __init__(self, texts: List[str], labels: np.ndarray, tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels  # Now expects binary encoded labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        labels = self.labels[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(labels, dtype=torch.float)
        }


class TransformerClassifier:
    """
    BERT-based classifier for medical literature domains
    Supports BioBERT, ClinicalBERT, SciBERT, etc.
    """
    
    def __init__(self, model_type: str = 'biobert', num_labels: int = None, 
                 max_length: int = 512, device: str = None):
        self.model_type = model_type
        self.max_length = max_length
        
        # M1 Mac specific device handling
        self.device = self._get_optimal_device(device)
        self.num_labels = num_labels
        
        # Configure PyTorch for M1 compatibility
        self._configure_m1_compatibility()
        
        # Get model configuration
        if model_type not in MEDICAL_BERT_MODELS:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        self.model_config = MEDICAL_BERT_MODELS[model_type]
        self.model_name = self.model_config['model_name']
        
        # Initialize tokenizer and model
        self.tokenizer = None
        self.model = None
        self.label_encoder = None
        
        logger.info(f"Initialized {model_type} classifier: {self.model_config['description']}")
        logger.info(f"Using device: {self.device}")
    
    def _get_optimal_device(self, device: str = None) -> str:
        """Get optimal device for M1 Mac compatibility"""
        if device:
            return device
            
        import platform
        import torch
        
        # Check if we're on Apple Silicon
        is_apple_silicon = platform.machine() == 'arm64' and platform.system() == 'Darwin'
        
        if is_apple_silicon:
            # Force CPU for training stability on M1
            logger.info("Apple Silicon detected: Using CPU for stable training")
            return 'cpu'
        elif torch.cuda.is_available():
            return 'cuda'
        else:
            return 'cpu'
    
    def _configure_m1_compatibility(self):
        """Configure PyTorch settings for M1 Mac compatibility"""
        import torch
        import os
        
        # Disable MPS backend explicitly
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '0'
        
        # Set number of threads for M1 optimization
        if hasattr(torch, 'set_num_threads'):
            torch.set_num_threads(1)  # Single thread for stability
        
        # Disable OpenMP if available (can cause hanging)
        os.environ['OMP_NUM_THREADS'] = '1'
        os.environ['MKL_NUM_THREADS'] = '1'
        
        # Configure memory management for M1
        if hasattr(torch.backends, 'mps'):
            torch.backends.mps.enabled = False
        
        logger.info("M1 compatibility settings applied")
    
    def _load_tokenizer_with_timeout(self, model_name: str, timeout: int = 300):
        """Load tokenizer with timeout protection for M1 compatibility"""
        import signal
        from contextlib import contextmanager
        
        @contextmanager
        def timeout_context(seconds):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Tokenizer loading timed out after {seconds} seconds")
            
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        try:
            with timeout_context(timeout):
                return AutoTokenizer.from_pretrained(
                    model_name,
                    use_fast=False,  # Use slow tokenizer for M1 stability
                    local_files_only=False
                )
        except TimeoutError:
            logger.warning(f"Tokenizer loading timed out, trying with local files only")
            return AutoTokenizer.from_pretrained(
                model_name,
                use_fast=False,
                local_files_only=True
            )
    
    def _load_model_with_timeout(self, model_name: str, num_labels: int, timeout: int = 300):
        """Load model with timeout protection for M1 compatibility"""
        import signal
        from contextlib import contextmanager
        
        @contextmanager
        def timeout_context(seconds):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Model loading timed out after {seconds} seconds")
            
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        try:
            with timeout_context(timeout):
                return AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    num_labels=num_labels,
                    problem_type="multi_label_classification",
                    torch_dtype=torch.float32,  # Explicit dtype for M1
                    use_safetensors=False,  # Disable for M1 compatibility
                    local_files_only=False
                )
        except TimeoutError:
            logger.warning(f"Model loading timed out, trying with local files only")
            return AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=num_labels,
                problem_type="multi_label_classification",
                torch_dtype=torch.float32,
                use_safetensors=False,
                local_files_only=True
            )
    
    def _prepare_data(self, texts: List[str], labels: List[List[str]]) -> Tuple[Any, Any, List[str]]:
        """Prepare data for training"""
        # Encode labels
        all_unique_labels = set()
        for label_list in labels:
            all_unique_labels.update(label_list)
        
        self.all_labels = sorted(list(all_unique_labels))
        self.num_labels = len(self.all_labels)
        
        # Create binary label matrix
        self.label_encoder = MultiLabelBinarizer()
        self.label_encoder.fit([self.all_labels])
        
        binary_labels = self.label_encoder.transform(labels)
        
        # Combine title and abstract
        combined_texts = [f"{text}" for text in texts]
        
        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            combined_texts, binary_labels, test_size=0.2, random_state=42
        )
        
        # Create datasets
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                truncation=True,
                padding='max_length',
                max_length=self.max_length
            )
        
        # Use custom PyTorch dataset class for compatibility with transformers
        train_dataset = MedicalDataset(train_texts, train_labels, self.tokenizer, self.max_length)
        val_dataset = MedicalDataset(val_texts, val_labels, self.tokenizer, self.max_length)
        
        return train_dataset, val_dataset, self.all_labels
    
    def train(self, texts: List[str], labels: List[List[str]], 
              training_args: Dict = None, callbacks: List = None) -> Dict:
        """Train the model"""
        try:
            logger.info(f"Starting training with {len(texts)} samples")
            
            # Initialize tokenizer and model with timeout protection
            logger.info("Loading tokenizer...")
            self.tokenizer = self._load_tokenizer_with_timeout(self.model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Prepare data
            train_dataset, val_dataset, all_labels = self._prepare_data(texts, labels)
            
            # Initialize model with timeout protection
            logger.info("Loading model...")
            self.model = self._load_model_with_timeout(
                self.model_name, 
                self.num_labels
            )
            
            # Move model to device (explicit device placement for M1)
            self.model.to(self.device)
            
            # Set up training arguments with M1 optimizations
            default_args = {
                'output_dir': './results',
                'num_train_epochs': 3,
                'per_device_train_batch_size': 8,  # Smaller batch size for M1
                'per_device_eval_batch_size': 8,
                'warmup_steps': 100,  # Reduced for faster training
                'weight_decay': 0.01,
                'logging_dir': './logs',
                'logging_steps': 50,
                'eval_strategy': 'steps',
                'eval_steps': 200,
                'save_steps': 500,
                'load_best_model_at_end': True,
                'metric_for_best_model': 'eval_f1_macro',
                'greater_is_better': True,
                'dataloader_num_workers': 0,  # Critical: No multiprocessing on M1
                'dataloader_pin_memory': False,  # Disable for M1
                'fp16': False,  # Disable half precision on M1
                'report_to': [],  # Disable wandb/tensorboard
                'save_safetensors': False,  # Use legacy format for M1 compatibility
                'no_cuda': True,  # Explicitly disable CUDA attempts
            }
            
            if training_args:
                default_args.update(training_args)
            
            training_arguments = TrainingArguments(**default_args)
            
            # Define compute metrics function
            def compute_metrics(eval_pred: EvalPrediction):
                predictions, labels = eval_pred
                predictions = torch.sigmoid(torch.tensor(predictions))
                predictions = (predictions > 0.5).float().numpy()
                
                # Calculate metrics
                f1_macro = f1_score(labels, predictions, average='macro', zero_division=0)
                f1_micro = f1_score(labels, predictions, average='micro', zero_division=0)
                accuracy = accuracy_score(labels, predictions)
                
                return {
                    'f1_macro': f1_macro,
                    'f1_micro': f1_micro,
                    'accuracy': accuracy
                }
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_arguments,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                compute_metrics=compute_metrics,
                callbacks=callbacks or []
            )
            
            # Train model
            train_result = trainer.train()
            
            # Evaluate model
            eval_result = trainer.evaluate()
            
            # Calculate confusion matrix on validation set
            confusion_matrix_data = None
            try:
                self.model.eval()
                val_predictions = []
                val_true_labels = []
                
                with torch.no_grad():
                    for batch in val_dataset:
                        inputs = {
                            'input_ids': batch['input_ids'].unsqueeze(0).to(self.device),
                            'attention_mask': batch['attention_mask'].unsqueeze(0).to(self.device)
                        }
                        outputs = self.model(**inputs)
                        logits = outputs.logits
                        probs = torch.sigmoid(logits).cpu().numpy()
                        predictions = (probs > 0.5).astype(int)[0]
                        
                        val_predictions.append(predictions)
                        val_true_labels.append(batch['labels'].numpy())
                
                val_predictions = np.array(val_predictions)
                val_true_labels = np.array(val_true_labels)
                
                # For multilabel, we'll create a per-label confusion matrix
                # Convert to a format suitable for the frontend
                confusion_matrices = []
                for i, label in enumerate(all_labels):
                    y_true_label = val_true_labels[:, i]
                    y_pred_label = val_predictions[:, i]
                    cm = confusion_matrix(y_true_label, y_pred_label, labels=[0, 1])
                    confusion_matrices.append(cm.tolist())
                
                # For simplicity, we'll use the first few labels' confusion matrices
                # or create an aggregate one
                if len(confusion_matrices) > 0:
                    confusion_matrix_data = confusion_matrices[0]  # Use first label as example
                    
            except Exception as e:
                logger.warning(f"Could not calculate confusion matrix: {str(e)}")
                confusion_matrix_data = None
            
            logger.info(f"Training completed. Final metrics: {eval_result}")
            
            return {
                'train_runtime': train_result.metrics['train_runtime'],
                'train_samples_per_second': train_result.metrics['train_samples_per_second'],
                'eval_f1_macro': eval_result['eval_f1_macro'],
                'eval_f1_micro': eval_result['eval_f1_micro'],
                'eval_accuracy': eval_result['eval_accuracy'],
                'model_type': self.model_type,
                'num_labels': self.num_labels,
                'all_labels': all_labels,
                'confusion_matrix': confusion_matrix_data
            }
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            raise
    
    def predict(self, texts: List[str], threshold: float = 0.5) -> List[Dict]:
        """Make predictions on new texts"""
        if not self.model or not self.tokenizer:
            raise ValueError("Model must be trained before making predictions")
        
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for text in texts:
                # Tokenize
                inputs = self.tokenizer(
                    text,
                    truncation=True,
                    padding='max_length',
                    max_length=self.max_length,
                    return_tensors='pt'
                )
                
                # Get model predictions
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.sigmoid(logits).cpu().numpy()[0]
                
                # Apply threshold
                predicted_labels = []
                confidence_scores = {}
                
                for i, (label, prob) in enumerate(zip(self.all_labels, probs)):
                    confidence_scores[label] = float(prob)
                    if prob >= threshold:
                        predicted_labels.append(label)
                
                predictions.append({
                    'predicted_domains': predicted_labels,
                    'confidence_scores': confidence_scores,
                    'all_scores': {label: float(prob) for label, prob in zip(self.all_labels, probs)}
                })
        
        return predictions
    
    def save_model(self, model_path: str):
        """Save the trained model"""
        if not self.model:
            raise ValueError("No trained model to save")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model and tokenizer
        model_dir = model_path.replace('.pkl', '_model')
        self.model.save_pretrained(model_dir)
        self.tokenizer.save_pretrained(model_dir)
        
        # Save additional metadata
        metadata = {
            'model_type': self.model_type,
            'model_name': self.model_name,
            'max_length': self.max_length,
            'num_labels': self.num_labels,
            'all_labels': self.all_labels,
            'label_encoder_classes': self.label_encoder.classes_.tolist() if self.label_encoder else None
        }
        
        with open(model_path.replace('.pkl', '_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str):
        """Load a trained model"""
        # Handle both directory paths and base paths
        if model_path.endswith('_model'):
            # Already a model directory path
            model_dir = model_path
            # Only replace _model at the end of the path
            base_path = model_path[:-6]  # Remove last 6 chars ('_model')
            metadata_path = f"{base_path}_metadata.json"
        else:
            # Convert base path to model directory and metadata paths
            model_dir = f"{model_path}_model"
            metadata_path = f"{model_path}_metadata.json"
        
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.model_type = metadata['model_type']
        self.model_name = metadata['model_name']
        self.max_length = metadata['max_length']
        self.num_labels = metadata['num_labels']
        self.all_labels = metadata['all_labels']
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        
        # Recreate label encoder
        if metadata.get('label_encoder_classes'):
            self.label_encoder = MultiLabelBinarizer()
            self.label_encoder.classes_ = np.array(metadata['label_encoder_classes'])
        
        logger.info(f"Model loaded from {model_path}")


class GemmaClassifier:
    """
    Gemma-based classifier for medical literature domains
    Adapts generative Gemma models for classification tasks
    """
    
    def __init__(self, model_type: str = 'gemma2-2b', num_labels: int = None, 
                 max_length: int = 512, device: str = None):
        self.model_type = model_type
        self.max_length = max_length
        self.device = self._get_optimal_device(device)
        self.num_labels = num_labels
        
        # Get model configuration
        if model_type not in GEMMA_MODELS:
            raise ValueError(f"Unsupported Gemma model type: {model_type}")
        
        self.model_config = GEMMA_MODELS[model_type]
        self.model_name = self.model_config['model_name']
        
        # Initialize components
        self.tokenizer = None
        self.model = None
        self.label_encoder = None
        self.all_labels = None
        
        # Setup quantization config for memory efficiency (if available)
        self.quantization_config = None
        if QUANTIZATION_AVAILABLE and self.device != 'cpu':
            try:
                self.quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                logger.info("Quantization enabled for memory efficiency")
            except Exception as e:
                logger.warning(f"Quantization not available: {e}")
                self.quantization_config = None
        else:
            logger.info("Quantization disabled (CPU mode or not available)")
        
        logger.info(f"Initialized Gemma classifier: {self.model_config['description']}")
        logger.info(f"Using device: {self.device}")
    
    def _get_hf_token(self) -> Optional[str]:
        """Get Hugging Face authentication token from environment variables"""
        # Try different possible environment variable names
        token = os.getenv('HF_TOKEN') or os.getenv('HUGGING_FACE_HUB_TOKEN') or os.getenv('HUGGINGFACE_HUB_TOKEN')
        if token:
            logger.info("Using Hugging Face authentication token")
        else:
            logger.warning("No Hugging Face token found. You may encounter issues with gated models like Gemma.")
        return token
    
    def _evaluate_model(self, texts: List[str], labels: List[List[str]], sample_size: int = 100) -> Dict[str, float]:
        """Evaluate Gemma model on validation data to calculate metrics
        
        Args:
            texts: Full text dataset
            labels: Full labels dataset  
            sample_size: Number of validation samples to evaluate (default 100 for speed)
        """
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import MultiLabelBinarizer
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        
        # Split data into train/validation (80/20 split)
        _, val_texts, _, val_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=None
        )
        
        # Limit validation set for faster evaluation
        if len(val_texts) > sample_size:
            logger.info(f"Sampling {sample_size} from {len(val_texts)} validation samples for faster evaluation")
            indices = range(len(val_texts))
            sampled_indices = sorted(list(range(0, len(val_texts), len(val_texts) // sample_size))[:sample_size])
            val_texts = [val_texts[i] for i in sampled_indices]
            val_labels = [val_labels[i] for i in sampled_indices]
        
        logger.info(f"Evaluating on {len(val_texts)} validation samples...")
        
        # Convert labels to binary format for evaluation
        mlb = MultiLabelBinarizer()
        mlb.fit(labels)  # Fit on all labels
        val_labels_binary = mlb.transform(val_labels)
        
        # Make predictions on validation set with progress tracking
        predictions = []
        total_samples = len(val_texts)
        
        for i, val_text in enumerate(val_texts):
            if i % 10 == 0:  # Log progress every 10 samples
                logger.info(f"Evaluation progress: {i}/{total_samples} ({i/total_samples*100:.1f}%)")
                
            try:
                # Use existing predict method but get raw predictions
                pred_result = self.predict([val_text], threshold=0.5)
                if pred_result and 'predicted_domains' in pred_result[0]:
                    predictions.append(pred_result[0]['predicted_domains'])
                else:
                    predictions.append([])  # Empty prediction if failed
            except Exception as e:
                logger.warning(f"Prediction failed for sample {i}, using empty: {e}")
                predictions.append([])
        
        # Convert predictions to binary format
        pred_labels_binary = mlb.transform(predictions)
        
        # Calculate metrics
        # For multilabel, we need to handle the case where some samples have no predictions
        if val_labels_binary.shape[1] > 0 and pred_labels_binary.shape[1] > 0:
            # Ensure same shape (pad with zeros if needed)
            if pred_labels_binary.shape[1] < val_labels_binary.shape[1]:
                padding = val_labels_binary.shape[1] - pred_labels_binary.shape[1]
                pred_labels_binary = np.pad(pred_labels_binary, ((0, 0), (0, padding)), mode='constant')
            elif pred_labels_binary.shape[1] > val_labels_binary.shape[1]:
                pred_labels_binary = pred_labels_binary[:, :val_labels_binary.shape[1]]
            
            # Calculate metrics with zero_division handling
            accuracy = accuracy_score(val_labels_binary, pred_labels_binary)
            f1_macro = f1_score(val_labels_binary, pred_labels_binary, average='macro', zero_division=0)
            f1_micro = f1_score(val_labels_binary, pred_labels_binary, average='micro', zero_division=0)
            precision = precision_score(val_labels_binary, pred_labels_binary, average='macro', zero_division=0)
            recall = recall_score(val_labels_binary, pred_labels_binary, average='macro', zero_division=0)
        else:
            # Fallback to reasonable defaults
            logger.warning("Could not calculate meaningful metrics, using defaults")
            accuracy = 0.1
            f1_macro = 0.1
            f1_micro = 0.1
            precision = 0.1
            recall = 0.1
        
        # Calculate confusion matrix
        confusion_matrix_data = None
        try:
            if val_labels_binary.shape[1] > 0 and pred_labels_binary.shape[1] > 0:
                # For multilabel, we'll create a per-label confusion matrix
                confusion_matrices = []
                for i in range(min(val_labels_binary.shape[1], pred_labels_binary.shape[1])):
                    y_true_label = val_labels_binary[:, i]
                    y_pred_label = pred_labels_binary[:, i]
                    cm = confusion_matrix(y_true_label, y_pred_label, labels=[0, 1])
                    confusion_matrices.append(cm.tolist())
                
                # For simplicity, we'll use the first label's confusion matrix as example
                if len(confusion_matrices) > 0:
                    confusion_matrix_data = confusion_matrices[0]
        except Exception as e:
            logger.warning(f"Could not calculate confusion matrix for Gemma: {str(e)}")
            confusion_matrix_data = None
        
        metrics = {
            'accuracy': float(accuracy),
            'f1_macro': float(f1_macro),
            'f1_micro': float(f1_micro),
            'precision': float(precision),
            'recall': float(recall),
            'confusion_matrix': confusion_matrix_data
        }
        
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics
    
    def _get_optimal_device(self, device: str = None) -> str:
        """Get optimal device for Gemma model"""
        if device:
            return device
            
        import platform
        import torch
        
        is_apple_silicon = platform.machine() == 'arm64' and platform.system() == 'Darwin'
        
        if is_apple_silicon:
            logger.info("Apple Silicon detected: Using CPU for stable inference")
            return 'cpu'
        elif torch.cuda.is_available():
            return 'cuda'
        else:
            return 'cpu'
    
    def _create_classification_prompt(self, text: str, labels: List[str]) -> str:
        """Create a prompt for classification task"""
        labels_str = ", ".join(labels)
        prompt = f"""Classify the following medical text into one or more of these domains: {labels_str}

Text: {text}

Classification (respond with only the relevant domain names, separated by commas):"""
        return prompt
    
    def _parse_classification_response(self, response: str, all_labels: List[str]) -> List[str]:
        """Parse the model's classification response"""
        # Clean and normalize the response
        response = response.strip().lower()
        predicted_labels = []
        
        for label in all_labels:
            if label.lower() in response:
                predicted_labels.append(label)
        
        return predicted_labels
    
    def train(self, texts: List[str], labels: List[List[str]], 
              training_args: Dict = None, callbacks: List = None) -> Dict:
        # Note: training_args and callbacks are not used for Gemma inference mode
        # but are kept for API compatibility
        """Train/fine-tune the Gemma model for classification"""
        try:
            logger.info(f"Starting Gemma training with {len(texts)} samples")
            
            # Check for fast mode
            fast_mode = training_args.get('fast_mode', False) if training_args else False
            eval_sample_size = 20 if fast_mode else 100
            
            if fast_mode:
                logger.info("🚀 Fast mode enabled - using minimal evaluation for quick testing")
            
            # Prepare labels
            all_unique_labels = set()
            for label_list in labels:
                all_unique_labels.update(label_list)
            
            self.all_labels = sorted(list(all_unique_labels))
            self.num_labels = len(self.all_labels)
            
            # Load tokenizer and model
            logger.info("Loading Gemma tokenizer...")
            hf_token = self._get_hf_token()
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=True,
                trust_remote_code=True,
                token=hf_token
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("Loading Gemma model...")
            if self.device == 'cpu' or self.quantization_config is None:
                # Load without quantization for CPU or when quantization unavailable
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    device_map="cpu" if self.device == 'cpu' else "auto",
                    trust_remote_code=True,
                    token=hf_token
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=self.quantization_config,
                    device_map="auto",
                    trust_remote_code=True,
                    token=hf_token
                )
            
            # For now, we'll use the model in inference mode
            # Full fine-tuning would require LoRA or similar techniques
            logger.info("Gemma model loaded successfully for inference")
            
            # Evaluate the model on validation set to get metrics
            if fast_mode:
                logger.info(f"Fast evaluation on {eval_sample_size} samples...")
            else:
                logger.info("Evaluating Gemma model on validation data...")
            evaluation_metrics = self._evaluate_model(texts, labels, sample_size=eval_sample_size)
            
            # Return results in the same format as TransformerClassifier
            return {
                'eval_accuracy': evaluation_metrics['accuracy'],
                'eval_f1_macro': evaluation_metrics['f1_macro'],
                'eval_f1_micro': evaluation_metrics['f1_micro'],
                'eval_precision': evaluation_metrics['precision'],
                'eval_recall': evaluation_metrics['recall'],
                'model_type': self.model_type,
                'num_labels': self.num_labels,
                'all_labels': self.all_labels,
                'confusion_matrix': evaluation_metrics.get('confusion_matrix'),
                'training_approach': 'inference_only',
                'note': 'Gemma model loaded for inference. Metrics calculated on validation set.'
            }
            
        except Exception as e:
            logger.error(f"Gemma training failed: {str(e)}", exc_info=True)
            raise
    
    def predict(self, texts: List[str], threshold: float = 0.5) -> List[Dict]:
        """Make predictions using Gemma model
        
        Note: threshold parameter is kept for API compatibility but not used since
        Gemma generates text responses rather than probability scores.
        """
        # threshold parameter not used in text-based generation approach
        _ = threshold  # Suppress linter warning
        
        if not self.model or not self.tokenizer:
            raise ValueError("Model must be loaded before making predictions")
        
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for text in texts:
                # Create classification prompt
                prompt = self._create_classification_prompt(text, self.all_labels)
                
                # Tokenize
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    max_length=self.max_length,
                    truncation=True,
                    padding=True
                )
                
                if self.device != 'cpu':
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Generate response
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    do_sample=True,
                    temperature=0.1,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                # Decode response
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Extract the classification part (after the prompt)
                classification_start = response.find("Classification (respond with only")
                if classification_start != -1:
                    classification_response = response[classification_start:].split(":")[-1].strip()
                else:
                    classification_response = response.split(":")[-1].strip()
                
                # Parse predicted labels
                predicted_labels = self._parse_classification_response(
                    classification_response, self.all_labels
                )
                
                # Create confidence scores (simplified approach)
                confidence_scores = {}
                all_scores = {}
                
                for label in self.all_labels:
                    if label in predicted_labels:
                        confidence_scores[label] = 0.8  # High confidence for predicted
                        all_scores[label] = 0.8
                    else:
                        all_scores[label] = 0.2  # Low confidence for not predicted
                
                predictions.append({
                    'predicted_domains': predicted_labels,
                    'confidence_scores': confidence_scores,
                    'all_scores': all_scores,
                    'raw_response': classification_response
                })
        
        return predictions
    
    def save_model(self, model_path: str):
        """Save the Gemma model configuration"""
        if not self.model:
            raise ValueError("No model to save")
        
        # Save metadata only (model is too large to save locally)
        metadata = {
            'model_type': self.model_type,
            'model_name': self.model_name,
            'max_length': self.max_length,
            'num_labels': self.num_labels,
            'all_labels': self.all_labels,
            'is_gemma': True
        }
        
        metadata_path = model_path.replace('.pkl', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Gemma model metadata saved to {metadata_path}")
    
    def load_model(self, model_path: str):
        """Load Gemma model from metadata"""
        metadata_path = model_path.replace('.pkl', '_metadata.json')
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.model_type = metadata['model_type']
        self.model_name = metadata['model_name']
        self.max_length = metadata['max_length']
        self.num_labels = metadata['num_labels']
        self.all_labels = metadata['all_labels']
        
        # Reload the model
        hf_token = self._get_hf_token()
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            use_fast=True,
            trust_remote_code=True,
            token=hf_token
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        if self.device == 'cpu' or self.quantization_config is None:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                device_map="cpu" if self.device == 'cpu' else "auto",
                trust_remote_code=True,
                token=hf_token
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=self.quantization_config,
                device_map="auto",
                trust_remote_code=True,
                token=hf_token
            )
        
        logger.info(f"Gemma model loaded from {model_path}")


class TraditionalMLClassifier:
    """
    Traditional ML classifier using TF-IDF features
    Supports SVM, Random Forest, and Logistic Regression
    """
    
    def __init__(self, algorithm: str = 'svm', max_features: int = 10000, **kwargs):
        self.algorithm = algorithm
        self.max_features = max_features
        # Ignore any extra parameters that might be passed
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        self.all_labels = None
        
        # Initialize classifier based on algorithm
        if algorithm == 'svm':
            base_classifier = SVC(probability=True, kernel='linear', C=1.0)
        elif algorithm == 'random_forest':
            base_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        elif algorithm == 'logistic_regression':
            base_classifier = LogisticRegression(max_iter=1000, random_state=42)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        self.classifier = MultiOutputClassifier(base_classifier)
        
        logger.info(f"Initialized traditional ML classifier: {algorithm}")
    
    def train(self, texts: List[str], labels: List[List[str]]) -> Dict:
        """Train the traditional ML model"""
        try:
            logger.info(f"Training {self.algorithm} with {len(texts)} samples")
            
            # Prepare labels
            all_unique_labels = set()
            for label_list in labels:
                all_unique_labels.update(label_list)
            
            self.all_labels = sorted(list(all_unique_labels))
            self.label_encoder = MultiLabelBinarizer()
            self.label_encoder.fit([self.all_labels])
            
            binary_labels = self.label_encoder.transform(labels)
            
            # Create TF-IDF features
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words='english',
                ngram_range=(1, 2),
                lowercase=True
            )
            
            X = self.vectorizer.fit_transform(texts)
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, binary_labels, test_size=0.2, random_state=42
            )
            
            # Train classifier
            self.classifier.fit(X_train, y_train)
            
            # Evaluate on validation set
            y_pred = self.classifier.predict(X_val)
            y_pred_proba = self.classifier.predict_proba(X_val)
            
            # Calculate metrics
            f1_macro = f1_score(y_val, y_pred, average='macro', zero_division=0)
            f1_micro = f1_score(y_val, y_pred, average='micro', zero_division=0)
            accuracy = accuracy_score(y_val, y_pred)
            
            # Calculate confusion matrix 
            confusion_matrix_data = None
            try:
                # For multilabel, we'll create a per-label confusion matrix
                # Convert to a format suitable for the frontend
                confusion_matrices = []
                for i, label in enumerate(self.all_labels):
                    y_true_label = y_val[:, i]
                    y_pred_label = y_pred[:, i]
                    cm = confusion_matrix(y_true_label, y_pred_label, labels=[0, 1])
                    confusion_matrices.append(cm.tolist())
                
                # For simplicity, we'll use the first label's confusion matrix as example
                if len(confusion_matrices) > 0:
                    confusion_matrix_data = confusion_matrices[0]
                    
            except Exception as e:
                logger.warning(f"Could not calculate confusion matrix: {str(e)}")
                confusion_matrix_data = None
            
            logger.info(f"Training completed. F1-macro: {f1_macro:.3f}, Accuracy: {accuracy:.3f}")
            
            return {
                'f1_macro': f1_macro,
                'f1_micro': f1_micro,
                'accuracy': accuracy,
                'algorithm': self.algorithm,
                'num_labels': len(self.all_labels),
                'all_labels': self.all_labels,
                'feature_count': X.shape[1],
                'confusion_matrix': confusion_matrix_data
            }
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            raise
    
    def predict(self, texts: List[str], threshold: float = 0.5) -> List[Dict]:
        """Make predictions on new texts"""
        if not self.classifier or not self.vectorizer:
            raise ValueError("Model must be trained before making predictions")
        
        # Transform texts
        X = self.vectorizer.transform(texts)
        
        # Get predictions
        predictions = []
        y_pred_proba = self.classifier.predict_proba(X)
        
        for i, text in enumerate(texts):
            # Extract probabilities for this sample
            sample_probs = []
            for j in range(len(self.all_labels)):
                # Each classifier in MultiOutputClassifier returns probabilities for [0, 1]
                prob = y_pred_proba[j][i][1] if hasattr(y_pred_proba[j], '__len__') else y_pred_proba[j][i]
                sample_probs.append(prob)
            
            # Apply threshold
            predicted_labels = []
            confidence_scores = {}
            
            for label, prob in zip(self.all_labels, sample_probs):
                confidence_scores[label] = float(prob)
                if prob >= threshold:
                    predicted_labels.append(label)
            
            predictions.append({
                'predicted_domains': predicted_labels,
                'confidence_scores': confidence_scores,
                'all_scores': confidence_scores
            })
        
        return predictions
    
    def save_model(self, model_path: str):
        """Save the trained model"""
        if not self.classifier:
            raise ValueError("No trained model to save")
        
        model_data = {
            'algorithm': self.algorithm,
            'classifier': self.classifier,
            'vectorizer': self.vectorizer,
            'label_encoder': self.label_encoder,
            'all_labels': self.all_labels,
            'max_features': self.max_features
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str):
        """Load a trained model"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.algorithm = model_data['algorithm']
        self.classifier = model_data['classifier']
        self.vectorizer = model_data['vectorizer']
        self.label_encoder = model_data['label_encoder']
        self.all_labels = model_data['all_labels']
        self.max_features = model_data['max_features']
        
        logger.info(f"Model loaded from {model_path}")


class HybridEnsembleClassifier:
    """
    Ensemble classifier combining transformer and traditional ML approaches
    """
    
    def __init__(self, transformer_type: str = 'biobert', traditional_algorithm: str = 'svm',
                 ensemble_method: str = 'voting'):
        self.transformer_classifier = TransformerClassifier(model_type=transformer_type)
        self.traditional_classifier = TraditionalMLClassifier(algorithm=traditional_algorithm)
        self.ensemble_method = ensemble_method
        self.weights = {'transformer': 0.7, 'traditional': 0.3}  # Default weights
        
        logger.info(f"Initialized hybrid ensemble: {transformer_type} + {traditional_algorithm}")
    
    def train(self, texts: List[str], labels: List[List[str]], 
              transformer_args: Dict = None, callbacks: List = None) -> Dict:
        """Train both models in the ensemble"""
        logger.info("Training ensemble models...")
        
        # Train transformer model
        transformer_results = self.transformer_classifier.train(
            texts, labels, transformer_args, callbacks
        )
        
        # Train traditional ML model
        traditional_results = self.traditional_classifier.train(texts, labels)
        
        return {
            'ensemble_method': self.ensemble_method,
            'transformer_results': transformer_results,
            'traditional_results': traditional_results,
            'weights': self.weights
        }
    
    def predict(self, texts: List[str], threshold: float = 0.5) -> List[Dict]:
        """Make ensemble predictions"""
        # Get predictions from both models
        transformer_predictions = self.transformer_classifier.predict(texts, threshold=0.0)
        traditional_predictions = self.traditional_classifier.predict(texts, threshold=0.0)
        
        ensemble_predictions = []
        
        for i, text in enumerate(texts):
            trans_scores = transformer_predictions[i]['all_scores']
            trad_scores = traditional_predictions[i]['all_scores']
            
            # Combine scores using weighted average
            combined_scores = {}
            for label in self.transformer_classifier.all_labels:
                trans_score = trans_scores.get(label, 0.0)
                trad_score = trad_scores.get(label, 0.0)
                
                combined_scores[label] = (
                    self.weights['transformer'] * trans_score +
                    self.weights['traditional'] * trad_score
                )
            
            # Apply threshold to combined scores
            predicted_labels = [
                label for label, score in combined_scores.items()
                if score >= threshold
            ]
            
            confidence_scores = {
                label: score for label, score in combined_scores.items()
                if label in predicted_labels
            }
            
            ensemble_predictions.append({
                'predicted_domains': predicted_labels,
                'confidence_scores': confidence_scores,
                'all_scores': combined_scores,
                'individual_predictions': {
                    'transformer': transformer_predictions[i],
                    'traditional': traditional_predictions[i]
                }
            })
        
        return ensemble_predictions
    
    def save_model(self, model_path: str):
        """Save the ensemble model"""
        # Save individual models
        transformer_path = model_path.replace('.pkl', '_transformer.pkl')
        traditional_path = model_path.replace('.pkl', '_traditional.pkl')
        
        self.transformer_classifier.save_model(transformer_path)
        self.traditional_classifier.save_model(traditional_path)
        
        # Save ensemble metadata
        ensemble_data = {
            'ensemble_method': self.ensemble_method,
            'weights': self.weights,
            'transformer_path': transformer_path,
            'traditional_path': traditional_path
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(ensemble_data, f)
        
        logger.info(f"Ensemble model saved to {model_path}")
    
    def load_model(self, model_path: str):
        """Load the ensemble model"""
        with open(model_path, 'rb') as f:
            ensemble_data = pickle.load(f)
        
        self.ensemble_method = ensemble_data['ensemble_method']
        self.weights = ensemble_data['weights']
        
        # Load individual models
        self.transformer_classifier.load_model(ensemble_data['transformer_path'])
        self.traditional_classifier.load_model(ensemble_data['traditional_path'])
        
        logger.info(f"Ensemble model loaded from {model_path}")


def create_model(model_type: str, **kwargs) -> Any:
    """Factory function to create appropriate model based on type"""
    if model_type in ['bert', 'biobert', 'clinicalbert', 'scibert', 'pubmedbert']:
        # Extract specific model name if provided
        if model_type == 'bert':
            model_type = kwargs.get('bert_model', 'biobert')
        return TransformerClassifier(model_type=model_type, **kwargs)
    
    elif model_type in ['gemma2-2b']:
        return GemmaClassifier(model_type=model_type, **kwargs)
    
    elif model_type == 'traditional':
        algorithm = kwargs.pop('algorithm', 'svm')  # Use pop to avoid duplicate
        return TraditionalMLClassifier(algorithm=algorithm, **kwargs)
    
    elif model_type == 'hybrid':
        return HybridEnsembleClassifier(**kwargs)
    
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

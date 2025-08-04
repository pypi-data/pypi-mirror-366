# llm_evaluator/__init__.py
"""
LLM Evaluator Package
Handles automatic model downloading on first use - Using Small Language Models
"""

import os
import warnings
from typing import Dict, Any

def download_required_models():
    """Download all required models if not already present - Small versions for faster setup"""
    
    # Small, efficient models - total ~890MB instead of 2.1GB+
    required_models = [
        "cross-encoder/nli-deberta-v3-small",        # ~150MB - NLI/contradiction detection
        "martin-ha/toxic-comment-model",             # ~250MB - Hate speech detection  
        "distilbert-base-multilingual-cased",       # ~500MB - Multilingual BERT (30% smaller)
        "sentence-transformers/all-MiniLM-L6-v2",   # ~90MB - Semantic embeddings
    ]
    
    try:
        from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
        import torch
        
        print("🚀 Using optimized small language models for faster setup...")
        
        for model_name in required_models:
            try:
                # Check if model exists locally first
                AutoTokenizer.from_pretrained(model_name, local_files_only=True)
                print(f"✓ {model_name} already available")
            except OSError:
                # Model not found locally, download it
                print(f"⬇️  Downloading {model_name}...")
                try:
                    # Download tokenizer
                    AutoTokenizer.from_pretrained(model_name)
                    
                    # Download model (try different types)
                    try:
                        AutoModelForSequenceClassification.from_pretrained(model_name)
                    except:
                        try:
                            AutoModel.from_pretrained(model_name)
                        except:
                            print(f"⚠️  Could not download model weights for {model_name}")
                            continue
                    
                    print(f"✅ Downloaded {model_name}")
                    
                except Exception as e:
                    print(f"⚠️  Could not download {model_name}: {e}")
                    print(f"   Model will be downloaded when first used.")
                    
    except ImportError as e:
        warnings.warn(f"Could not import transformers: {e}")

def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        
        required_nltk = [
            'punkt',                        # Sentence tokenization
            'stopwords',                    # Stop word filtering
            'vader_lexicon',               # Sentiment analysis
            'averaged_perceptron_tagger',  # POS tagging
            'wordnet'                      # WordNet corpus
        ]
        
        for data in required_nltk:
            try:
                # Check different NLTK data locations
                nltk.data.find(f'tokenizers/{data}')
            except LookupError:
                try:
                    nltk.data.find(f'corpora/{data}')
                except LookupError:
                    try:
                        nltk.data.find(f'taggers/{data}')
                    except LookupError:
                        try:
                            nltk.data.find(f'sentiment/{data}')
                        except LookupError:
                            print(f"⬇️  Downloading NLTK data: {data}")
                            nltk.download(data, quiet=True)
                        
    except ImportError:
        warnings.warn("NLTK not installed")

# Auto-download on import (only on first import)
_models_downloaded = False

def ensure_models():
    """Ensure all models are downloaded (called lazily)"""
    global _models_downloaded
    if not _models_downloaded:
        print("🔧 Setting up LLM Evaluator with optimized small models...")
        print("📦 Total download size: ~890MB (vs 2.1GB+ for full models)")
        download_required_models()
        download_nltk_data()
        _models_downloaded = True
        print("🎉 Model setup complete! LLM Evaluator ready to use.")

# Import main classes
from llm_eval_toolkit import LLMEvaluator

# Ensure models are available when the package is imported
ensure_models()

__version__ = "1.0.0"
__all__ = ["LLMEvaluator"]
import gc
import logging
from typing import Optional, Dict

import torch
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)


class ModelManager:
    """Memory-safe model manager that ensures only required models are loaded."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.models = {}
            cls._instance.tokenizers = {}
            cls._instance.device = "cuda" if torch.cuda.is_available() else "cpu"
        return cls._instance

    def _get_device(self, fallback_to_cpu: bool = True) -> str:
        # We can implement a more robust check for available VRAM here
        if fallback_to_cpu and self.device == "cuda":
            try:
                # Dummy check
                torch.cuda.empty_cache()
                return "cuda"
            except Exception:
                return "cpu"
        return self.device

    def load_sentence_transformer(self, model_name: str) -> SentenceTransformer:
        if model_name not in self.models:
            logger.info(f"Loading SentenceTransformer: {model_name} to {self.device}")
            try:
                model = SentenceTransformer(model_name, device=self.device, cache_folder=settings.model_cache_dir)
            except RuntimeError as e:
                if "out of memory" in str(e).lower() and self.device == "cuda":
                    logger.warning(f"OOM loading {model_name} on CUDA. Falling back to CPU.")
                    model = SentenceTransformer(model_name, device="cpu", cache_folder=settings.model_cache_dir)
                else:
                    raise e
            self.models[model_name] = model
        return self.models[model_name]

    def load_sequence_classifier(self, model_name: str):
        if model_name not in self.models:
            logger.info(f"Loading SequenceClassifier: {model_name} to {self.device}")
            tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=settings.model_cache_dir)
            try:
                model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=settings.model_cache_dir).to(self.device)
            except RuntimeError as e:
                if "out of memory" in str(e).lower() and self.device == "cuda":
                    logger.warning(f"OOM loading {model_name} on CUDA. Falling back to CPU.")
                    model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=settings.model_cache_dir).to("cpu")
                else:
                    raise e
                    
            # Ensure evaluation mode
            model.eval()
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            
        return self.models[model_name], self.tokenizers[model_name]

    def unload_model(self, model_name: str):
        """Unload a specific model and free memory."""
        if model_name in self.models:
            logger.info(f"Unloading model: {model_name}")
            del self.models[model_name]
            if model_name in self.tokenizers:
                del self.tokenizers[model_name]
            self.clear_gpu_memory()

    def unload_all(self):
        """Unload all models."""
        logger.info("Unloading all models")
        self.models.clear()
        self.tokenizers.clear()
        self.clear_gpu_memory()

    def clear_gpu_memory(self):
        """Force garbage collection and empty CUDA cache."""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# Singleton instance
model_manager = ModelManager()

import os
from typing import List, Union
import numpy as np

from app.nlp.model_manager import model_manager

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the sentence transformer model using model_manager.
        """
        self.model_name = model_name

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generates embeddings for a single string or a list of strings.
        Returns a numpy array of embeddings.
        """
        if isinstance(texts, str):
            texts = [texts]
        
        model = model_manager.load_sentence_transformer(self.model_name)
        embeddings = model.encode(texts, show_progress_bar=False)
        return embeddings

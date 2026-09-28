import faiss
import numpy as np
from typing import List, Dict, Any, Tuple
from app.retrieval.embedder import Embedder

class FaissStore:
    def __init__(self, embedder: Embedder, dimension: int = 384):
        """
        Initializes a FAISS index.
        dimension is 384 for all-MiniLM-L6-v2.
        """
        self.embedder = embedder
        self.dimension = dimension
        
        # Using IndexFlatIP for Inner Product (Cosine Similarity if vectors are normalized)
        # SentenceTransformers typically outputs normalized vectors for L6 models.
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Store metadata mapping (e.g., index -> { 'text': sentence_text, 'doc_id': ... })
        self.metadata_store: Dict[int, Any] = {}
        self.current_idx = 0

    def add_texts(self, texts: List[str], metadata: List[Dict[str, Any]]):
        """
        Embeds texts and adds them to the FAISS index alongside their metadata.
        """
        if not texts:
            return
            
        embeddings = self.embedder.embed(texts)
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        self.index.add(embeddings)
        
        for i, meta in enumerate(metadata):
            meta['text'] = texts[i]
            self.metadata_store[self.current_idx] = meta
            self.current_idx += 1

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Searches the FAISS index for the query string.
        Returns the top_k most similar entries with their metadata and score.
        """
        if self.index.ntotal == 0:
            return []

        query_embedding = self.embedder.embed([query])
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1 and idx in self.metadata_store:
                result = self.metadata_store[idx].copy()
                result['score'] = float(scores[0][i])
                results.append(result)
                
        return results

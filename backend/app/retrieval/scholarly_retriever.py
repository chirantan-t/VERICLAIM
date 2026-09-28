import logging
from typing import Dict, Any, Optional

from app.retrieval.cache import SQLiteCache
from app.retrieval.openalex import OpenAlexRetriever
from app.schemas.document import Reference

logger = logging.getLogger(__name__)


class ScholarlyRetriever:
    """Orchestrates multiple academic retrievers with caching."""

    def __init__(self):
        self.cache = SQLiteCache()
        self.retrievers = [
            OpenAlexRetriever()
        ]

    def resolve_reference(self, reference: Reference) -> Dict[str, Any]:
        """Resolves a reference to scholarly metadata."""
        # Check cache by title or doi
        cache_key = reference.doi or reference.title
        if not cache_key:
            return {"status": "unresolved", "confidence": 0.0}
            
        cached_result = self.cache.get(cache_key, "metadata")
        if cached_result:
            return cached_result

        # Try retrievers in order
        best_result = {"status": "unresolved", "confidence": 0.0}
        
        for retriever in self.retrievers:
            result = retriever.resolve_reference(reference)
            
            if result["status"] == "error":
                best_result = result
                continue
                
            if result["status"] == "resolved":
                # Cache and return immediately if high confidence
                if result["confidence"] > 0.8:
                    self.cache.set(cache_key, result, "metadata")
                    return result
                    
                # Otherwise, keep track of best
                if result["confidence"] > best_result["confidence"]:
                    best_result = result

        if best_result["status"] == "resolved":
            self.cache.set(cache_key, best_result, "metadata")
            
        return best_result

    def fetch_full_text(self, source_id: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Fetches full text (or abstract) using the primary retriever."""
        cached_text = self.cache.get(source_id, "fulltext")
        if cached_text:
            return cached_text.get("text")
            
        # Try retrieving text
        for retriever in self.retrievers:
            text = retriever.fetch_full_text(source_id, metadata)
            if text:
                self.cache.set(source_id, {"text": text}, "fulltext")
                return text
                
        return None

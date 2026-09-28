import abc
from typing import Dict, Any, Optional

from app.schemas.document import Reference


class BaseRetriever(abc.ABC):
    """Base class for external academic retrievers."""

    def __init__(self):
        pass

    @abc.abstractmethod
    def resolve_reference(self, reference: Reference) -> Dict[str, Any]:
        """
        Attempts to resolve a reference using this retriever.
        Returns a dictionary representing the resolved metadata.
        Expected format:
        {
            "status": "resolved" | "unresolved" | "error",
            "confidence": float,
            "source_id": str,
            "title": str,
            "authors": [str],
            "year": int,
            "doi": str,
            "open_access_url": str (optional)
        }
        """
        pass

    @abc.abstractmethod
    def fetch_full_text(self, source_id: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Attempts to fetch the full text (or abstract if full text is unavailable)
        for the given source_id.
        Returns the text as a single string, or None if unavailable.
        """
        pass

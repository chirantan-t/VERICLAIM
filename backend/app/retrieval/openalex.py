import logging
import re
import urllib.parse
from typing import Any, Dict, Optional

import requests

from app.retrieval.base import BaseRetriever
from app.schemas.document import Reference

logger = logging.getLogger(__name__)


class OpenAlexRetriever(BaseRetriever):
    """Retriever for OpenAlex API."""

    BASE_URL = "https://api.openalex.org/works"

    def __init__(self, email: str = "vericlaim@example.com"):
        super().__init__()
        self.headers = {"User-Agent": f"VeriClaim (mailto:{email})"}

    def _clean_title(self, title: str) -> str:
        # Remove non-alphanumeric characters for fuzzy matching
        return re.sub(r"[^a-z0-9]", "", title.lower())

    def _compute_confidence(
        self, reference: Reference, result: Dict[str, Any]
    ) -> float:
        # If we matched by DOI, confidence is very high
        if reference.doi and result.get("doi"):
            if reference.doi.lower().strip() in result["doi"].lower():
                return 0.95

        confidence = 0.0
        
        ref_title = self._clean_title(reference.title or "")
        res_title = self._clean_title(result.get("title") or "")
        
        if ref_title and res_title and ref_title == res_title:
            confidence += 0.60
        elif ref_title and res_title and (ref_title in res_title or res_title in ref_title):
            confidence += 0.40

        # Check year
        if reference.year and result.get("publication_year"):
            if abs(reference.year - result["publication_year"]) <= 1:
                confidence += 0.20

        # Check authors (first author)
        if reference.authors and len(reference.authors) > 0:
            first_author_ref = self._clean_title(reference.authors[0])
            authorships = result.get("authorships", [])
            if authorships:
                first_author_res = self._clean_title(authorships[0].get("author", {}).get("display_name", ""))
                if first_author_ref in first_author_res or first_author_res in first_author_ref:
                    confidence += 0.15

        return min(0.99, confidence)

    def resolve_reference(self, reference: Reference) -> Dict[str, Any]:
        try:
            # 1. Try DOI lookup first
            if reference.doi:
                clean_doi = reference.doi.replace("https://doi.org/", "").strip()
                url = f"{self.BASE_URL}/doi:{clean_doi}"
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    confidence = self._compute_confidence(reference, data)
                    return self._format_result(data, confidence)

            # 2. Try Title search
            if reference.title:
                query = urllib.parse.quote(reference.title)
                url = f"{self.BASE_URL}?search={query}&per-page=3"
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    best_match = None
                    best_conf = 0.0

                    for res in results:
                        conf = self._compute_confidence(reference, res)
                        if conf > best_conf:
                            best_conf = conf
                            best_match = res

                    if best_match and best_conf > 0.60:
                        return self._format_result(best_match, best_conf)

            return {"status": "unresolved", "confidence": 0.0}
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"OpenAlex API error: {e}")
            return {"status": "error", "confidence": 0.0}

    def _format_result(self, data: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        oa_url = data.get("open_access", {}).get("oa_url")
        authors = [a.get("author", {}).get("display_name") for a in data.get("authorships", [])]
        return {
            "status": "resolved",
            "confidence": confidence,
            "source_id": data.get("id"),
            "title": data.get("title"),
            "authors": authors,
            "year": data.get("publication_year"),
            "doi": data.get("doi"),
            "open_access_url": oa_url,
            "abstract_inverted_index": data.get("abstract_inverted_index")
        }

    def fetch_full_text(self, source_id: str, metadata: Dict[str, Any]) -> Optional[str]:
        # OpenAlex provides abstracts as inverted index. We can reconstruct it.
        # Alternatively, if there is a full-text URL, we might fetch it, but usually, PDF parsing is complex.
        # For now, we rely on reconstructing the abstract.
        
        abstract_idx = metadata.get("abstract_inverted_index")
        if abstract_idx:
            # Reconstruct abstract
            max_idx = max([max(positions) for positions in abstract_idx.values()])
            words = [""] * (max_idx + 1)
            for word, positions in abstract_idx.items():
                for pos in positions:
                    words[pos] = word
            return " ".join(words)
            
        return None

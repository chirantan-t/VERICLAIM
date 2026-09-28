"""
Document Service: in-memory document storage and management.

Stores parsed documents, verification results, processing status,
and computed statistics. Thread-safe for concurrent access.
"""

import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.schemas.document import ParsedDocument
from app.schemas.verification import (
    DocumentStatistics,
    ProcessingStage,
    ProcessingStatus,
    VerificationResult,
)


class DocumentService:
    """Thread-safe in-memory document storage."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern to ensure one shared store."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._data_lock = threading.Lock()
        self._documents: Dict[str, ParsedDocument] = {}
        self._results: Dict[str, List[VerificationResult]] = {}
        self._status: Dict[str, ProcessingStatus] = {}
        self._statistics: Dict[str, DocumentStatistics] = {}
        self._file_info: Dict[str, Dict[str, Any]] = {}
        self._initialized = True

    def store_document(
        self,
        doc: ParsedDocument,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
    ):
        """Store a parsed document."""
        with self._data_lock:
            self._documents[doc.document_id] = doc
            if filename or file_size:
                self._file_info[doc.document_id] = {
                    "filename": filename,
                    "file_size": file_size,
                }

    def get_document(self, doc_id: str) -> Optional[ParsedDocument]:
        """Retrieve a parsed document by ID."""
        return self._documents.get(doc_id)

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all stored documents with summary info."""
        results = []
        for doc_id, doc in self._documents.items():
            info = self._file_info.get(doc_id, {})
            status = self._status.get(doc_id)
            stats = self._statistics.get(doc_id)
            results.append(
                {
                    "document_id": doc_id,
                    "title": doc.metadata.title,
                    "filename": info.get("filename") or doc.metadata.filename,
                    "file_size": info.get("file_size") or doc.metadata.file_size,
                    "pages": doc.metadata.pages,
                    "status": status.stage.value if status else "unknown",
                    "total_claims": stats.total_claims if stats else len(doc.claims),
                    "total_citations": len(doc.references),
                }
            )
        return results

    def store_results(self, doc_id: str, results: List[VerificationResult]):
        """Store verification results for a document."""
        with self._data_lock:
            self._results[doc_id] = results

    def get_results(self, doc_id: str) -> Optional[List[VerificationResult]]:
        """Retrieve verification results for a document."""
        return self._results.get(doc_id)

    def get_result_by_claim_id(
        self, doc_id: str, claim_id: str
    ) -> Optional[VerificationResult]:
        """Retrieve a specific verification result by claim ID."""
        results = self._results.get(doc_id, [])
        for r in results:
            if r.claim_id == claim_id:
                return r
        return None

    def find_claim_document(self, claim_id: str) -> Optional[str]:
        """Find which document a claim belongs to."""
        for doc_id, results in self._results.items():
            for r in results:
                if r.claim_id == claim_id:
                    return doc_id
        return None

    def update_status(
        self,
        doc_id: str,
        stage: ProcessingStage,
        progress: float,
        message: str,
    ):
        """Update processing status for a document."""
        with self._data_lock:
            now = datetime.now(timezone.utc).isoformat()
            status = self._status.get(doc_id)
            if status is None:
                status = ProcessingStatus(
                    document_id=doc_id,
                    stage=stage,
                    progress=progress,
                    message=message,
                    started_at=now,
                )
            else:
                status.stage = stage
                status.progress = progress
                status.message = message
            if stage == ProcessingStage.COMPLETE:
                status.completed_at = now
            if stage == ProcessingStage.ERROR:
                status.error = message
                status.completed_at = now
            self._status[doc_id] = status

    def get_status(self, doc_id: str) -> Optional[ProcessingStatus]:
        """Get processing status for a document."""
        return self._status.get(doc_id)

    def compute_statistics(self, doc_id: str) -> DocumentStatistics:
        """Compute and store aggregate statistics for a document."""
        results = self._results.get(doc_id, [])
        doc = self._documents.get(doc_id)

        stats = DocumentStatistics()
        stats.total_claims = len(results)
        stats.total_citations = len(doc.references) if doc else 0

        # Calculate resolved and unresolved citations
        resolved_set = set()
        unresolved_count = 0
        if doc:
            for claim in doc.claims:
                if claim.linked_citations:
                    for cit in claim.linked_citations:
                        resolved_set.add(cit)
                elif "]" in claim.text or ")" in claim.text:
                    # just an approximation for unresolved, or we can look at the parsed doc if there are extraction metrics
                    pass
        stats.resolved_citations = len(resolved_set)
        stats.unresolved_citations = stats.total_citations - stats.resolved_citations if stats.total_citations > stats.resolved_citations else 0
        
        verdict_dist: Dict[str, int] = {}
        type_dist: Dict[str, int] = {}
        section_dist: Dict[str, int] = {}
        total_confidence = 0.0

        for r in results:
            # Verdict distribution
            verdict_dist[r.verdict] = verdict_dist.get(r.verdict, 0) + 1

            # Claim type distribution
            ct = (
                r.claim_type
                if isinstance(r.claim_type, str)
                else r.claim_type.value
            )
            type_dist[ct] = type_dist.get(ct, 0) + 1

            # Section distribution
            sec = r.section or "Unknown"
            section_dist[sec] = section_dist.get(sec, 0) + 1

            # Evidence count
            stats.total_evidence += len(r.evidence)

            # Confidence
            total_confidence += r.confidence

            # Numerical discrepancies
            if (
                r.numerical_result
                and r.numerical_result.status == "DISCREPANCY"
            ):
                stats.numerical_discrepancies += 1

            # Low confidence
            if r.confidence < 0.5:
                stats.low_confidence_claims += 1

            # Verdict counts
            if r.verdict == "SUPPORTED":
                stats.claims_supported += 1
            elif r.verdict == "PARTIALLY_SUPPORTED":
                stats.claims_partially_supported += 1
            elif r.verdict == "CONTRADICTED":
                stats.claims_contradicted += 1
            else:
                stats.claims_insufficient += 1

        stats.verdict_distribution = verdict_dist
        stats.claim_type_distribution = type_dist
        stats.section_distribution = section_dist
        stats.average_confidence = (
            round(total_confidence / len(results), 4) if results else 0.0
        )

        with self._data_lock:
            self._statistics[doc_id] = stats
        return stats

    def get_statistics(self, doc_id: str) -> Optional[DocumentStatistics]:
        """Retrieve computed statistics for a document."""
        return self._statistics.get(doc_id)

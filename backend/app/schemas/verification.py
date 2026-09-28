"""Pydantic schemas for verification results and processing status."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.schemas.document import ClaimType, ParsedDocument


class Verdict(str, Enum):
    """Possible verification verdicts."""

    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    RETRIEVAL_FAILED = "RETRIEVAL_FAILED"


class Evidence(BaseModel):
    """A piece of evidence retrieved for a claim."""

    source_id: str
    document_title: Optional[str] = None
    source_type: str = "CURRENT_DOCUMENT"
    sentence_id: str
    text: str
    score: float
    page_number: int
    section: Optional[str] = None
    source_url: Optional[str] = None


class NLIResult(BaseModel):
    """Natural Language Inference result with all label probabilities."""

    entailment: float = 0.0
    neutral: float = 0.0
    contradiction: float = 0.0
    predicted_label: str = "neutral"


class NumericalResult(BaseModel):
    """Numerical consistency check result."""

    status: str  # CONSISTENT, DISCREPANCY, APPROXIMATE, NO_NUMBERS_IN_CLAIM
    claim_numbers: List[str] = []
    evidence_numbers: List[str] = []
    missing_numbers: List[str] = []
    approximate_matches: List[Dict] = []
    matched_numbers: List[str] = []
    message: Optional[str] = None


class VerificationResult(BaseModel):
    """Complete verification result for a single claim."""

    claim_id: str
    claim_text: str
    claim_type: ClaimType = ClaimType.FACTUAL
    section: Optional[str] = None
    page_number: Optional[int] = None
    linked_citations: List[str] = []
    verdict: str = "INSUFFICIENT_EVIDENCE"
    confidence: float = 0.0
    explanation: str = ""
    warnings: List[str] = []
    evidence: List[Evidence] = []
    nli_result: Optional[NLIResult] = None
    numerical_result: Optional[NumericalResult] = None
    semantic_similarity: Optional[float] = None


class DocumentStatistics(BaseModel):
    """Aggregate statistics for a verified document."""

    total_claims: int = 0
    total_citations: int = 0
    total_evidence: int = 0
    resolved_citations: int = 0
    unresolved_citations: int = 0
    claims_supported: int = 0
    claims_partially_supported: int = 0
    claims_contradicted: int = 0
    claims_insufficient: int = 0
    average_confidence: float = 0.0
    verdict_distribution: Dict[str, int] = {}
    claim_type_distribution: Dict[str, int] = {}
    section_distribution: Dict[str, int] = {}
    numerical_discrepancies: int = 0
    low_confidence_claims: int = 0


class ProcessingStage(str, Enum):
    """Stages of the document analysis pipeline."""

    QUEUED = "queued"
    PARSING = "parsing"
    EXTRACTING_CITATIONS = "extracting_citations"
    DETECTING_CLAIMS = "detecting_claims"
    LINKING_CITATIONS = "linking_citations"
    RETRIEVING_EVIDENCE = "retrieving_evidence"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    NLI_VERIFICATION = "nli_verification"
    NUMERICAL_CHECKING = "numerical_checking"
    GENERATING_REPORT = "generating_report"
    COMPLETE = "complete"
    ERROR = "error"


class ProcessingStatus(BaseModel):
    """Current processing status for a document."""

    document_id: str
    stage: ProcessingStage = ProcessingStage.QUEUED
    progress: float = 0.0
    message: str = "Queued for processing"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Full response for a document analysis."""

    document: ParsedDocument
    results: List[VerificationResult]
    statistics: DocumentStatistics = DocumentStatistics()
    processing_status: Optional[ProcessingStatus] = None

"""
Analysis Service: orchestrates the full verification pipeline.

Manages the end-to-end flow from PDF parsing through verification,
updating processing status at each stage.
"""

import os
import traceback
from typing import List, Optional

from app.document_processing.pdf_parser import PDFParser
from app.retrieval.embedder import Embedder
from app.retrieval.faiss_store import FaissStore
from app.schemas.document import ParsedDocument
from app.schemas.verification import (
    AnalysisResponse,
    ProcessingStage,
    VerificationResult,
)
from app.services.document_service import DocumentService
from app.verification.nli_verifier import NLIVerifier
from app.verification.numerical_checker import NumericalChecker
from app.verification.verification_engine import VerificationEngine


class AnalysisService:
    """Orchestrates the full document verification pipeline."""

    _instance = None

    def __new__(cls):
        """Singleton to share model instances."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.doc_service = DocumentService()
        self.parser = PDFParser()
        self.embedder = Embedder()
        self.nli_verifier = NLIVerifier()
        self.num_checker = NumericalChecker()
        self._initialized = True

    def analyze_document(
        self,
        file_path: str,
        document_id: str,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
    ) -> AnalysisResponse:
        """
        Run the full verification pipeline on a PDF document.

        Stages:
        1. Parse PDF into structured document
        2. Index all sentences into FAISS
        3. For each claim: retrieve evidence, NLI, numerical check
        4. Compute statistics
        """
        try:
            # Stage 1: Parsing
            self.doc_service.update_status(
                document_id, ProcessingStage.PARSING, 0.1, "Parsing PDF document..."
            )
            parsed_doc = self.parser.parse(
                file_path, document_id, filename=filename, file_size=file_size
            )
            self.doc_service.store_document(parsed_doc, filename, file_size)

            # Stage 2: Extracting citations
            self.doc_service.update_status(
                document_id,
                ProcessingStage.EXTRACTING_CITATIONS,
                0.2,
                f"Found {len(parsed_doc.references)} references.",
            )

            # Stage 3: Detecting claims
            self.doc_service.update_status(
                document_id,
                ProcessingStage.DETECTING_CLAIMS,
                0.3,
                f"Detected {len(parsed_doc.claims)} verifiable claims.",
            )

            # Stage 4: Linking citations
            self.doc_service.update_status(
                document_id,
                ProcessingStage.LINKING_CITATIONS,
                0.35,
                "Linking claims to citations...",
            )

            # Stage 5: Building retrieval index
            self.doc_service.update_status(
                document_id,
                ProcessingStage.RETRIEVING_EVIDENCE,
                0.4,
                "Building semantic index and retrieving evidence...",
            )

            # Create per-document FAISS store
            doc_store = FaissStore(self.embedder)
            doc_engine = VerificationEngine(
                doc_store, self.nli_verifier, self.num_checker
            )

            # Stage 6: Running verification
            self.doc_service.update_status(
                document_id,
                ProcessingStage.SEMANTIC_ANALYSIS,
                0.5,
                "Running semantic similarity analysis...",
            )

            # The verify_document method handles indexing + per-claim verification
            results = doc_engine.verify_document(parsed_doc)

            # Update stages as we go
            self.doc_service.update_status(
                document_id,
                ProcessingStage.NLI_VERIFICATION,
                0.7,
                "Natural language inference complete.",
            )

            self.doc_service.update_status(
                document_id,
                ProcessingStage.NUMERICAL_CHECKING,
                0.85,
                "Numerical consistency checks complete.",
            )

            # Stage 7: Storing results
            self.doc_service.update_status(
                document_id,
                ProcessingStage.GENERATING_REPORT,
                0.95,
                "Generating verification report...",
            )
            self.doc_service.store_results(document_id, results)

            # Stage 8: Computing statistics
            statistics = self.doc_service.compute_statistics(document_id)

            # Mark complete
            self.doc_service.update_status(
                document_id,
                ProcessingStage.COMPLETE,
                1.0,
                f"Analysis complete. {len(results)} claims verified.",
            )

            status = self.doc_service.get_status(document_id)

            return AnalysisResponse(
                document=parsed_doc,
                results=results,
                statistics=statistics,
                processing_status=status,
            )

        except Exception as e:
            self.doc_service.update_status(
                document_id,
                ProcessingStage.ERROR,
                0.0,
                f"Analysis failed: {str(e)}",
            )
            traceback.print_exc()
            raise

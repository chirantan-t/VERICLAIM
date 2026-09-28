"""
Verification Engine: orchestrates the full verification pipeline.

For each claim in a parsed document:
1. Index document sentences into FAISS
2. Retrieve top-K evidence passages
3. Run NLI verification
4. Check numerical consistency
5. Aggregate signals into a final verdict with confidence score
"""

from typing import Any, Dict, List, Optional
import nltk
from nltk.tokenize import sent_tokenize

from app.retrieval.faiss_store import FaissStore
from app.retrieval.scholarly_retriever import ScholarlyRetriever
from app.schemas.document import ExtractedClaim, ParsedDocument
from app.schemas.verification import (
    Evidence,
    NLIResult,
    NumericalResult,
    VerificationResult,
)
from app.verification.nli_verifier import NLIVerifier
from app.verification.numerical_checker import NumericalChecker

# Ensure punkt is downloaded for sentence tokenization of external abstracts
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class VerificationEngine:
    def __init__(
        self,
        faiss_store: FaissStore,
        nli_verifier: NLIVerifier,
        numerical_checker: NumericalChecker,
        scholarly_retriever: Optional[ScholarlyRetriever] = None
    ):
        # Current document FAISS
        self.faiss_store = faiss_store
        
        # External evidence FAISS
        self.external_faiss_store = FaissStore(embedder=faiss_store.embedder, dimension=faiss_store.dimension)
        
        self.nli_verifier = nli_verifier
        self.numerical_checker = numerical_checker
        self.scholarly_retriever = scholarly_retriever or ScholarlyRetriever()

    def verify_document(
        self, document: ParsedDocument
    ) -> List[VerificationResult]:
        """
        Orchestrates the entire verification pipeline for a ParsedDocument.
        """
        results = []

        # 1. Index all document sentences into FAISS
        all_sentences = []
        section_map = {}
        for sec in document.sections:
            for p in sec.paragraphs:
                for s in p.sentences:
                    all_sentences.append(s)
                    section_map[s.sentence_id] = sec.title

        texts = [s.text for s in all_sentences]
        metadata = [
            {
                "sentence_id": s.sentence_id,
                "page_number": s.page_number,
                "section": section_map.get(s.sentence_id, "Unknown"),
                "source_type": "CURRENT_DOCUMENT",
                "source_id": document.document_id,
            }
            for s in all_sentences
        ]

        if texts:
            self.faiss_store.add_texts(texts, metadata)
            
        # 2. Resolve external references and index their content
        ref_map = {ref.ref_id: ref for ref in document.references}
        resolved_refs = {}
        for ref in document.references:
            resolution = self.scholarly_retriever.resolve_reference(ref)
            ref.retrieval_status = resolution["status"]
            if resolution["status"] == "resolved":
                ref.source_id = resolution.get("source_id")
                # Fetch full text or abstract
                external_text = self.scholarly_retriever.fetch_full_text(ref.source_id, resolution)
                if external_text:
                    sentences = sent_tokenize(external_text)
                    ext_metadata = [
                        {
                            "sentence_id": f"{ref.source_id}_s{i}",
                            "page_number": 1,
                            "section": "Abstract/Text",
                            "source_type": "CITED_EXTERNAL_SOURCE",
                            "source_id": ref.source_id,
                            "document_title": resolution.get("title", ""),
                            "source_url": resolution.get("open_access_url")
                        }
                        for i, s in enumerate(sentences)
                    ]
                    self.external_faiss_store.add_texts(sentences, ext_metadata)
            resolved_refs[ref.ref_id] = ref

        # 3. Iterate over each extracted claim
        for claim in document.claims:
            result = self.verify_claim(claim, resolved_refs)
            results.append(result)

        return results

    def verify_claim(
        self,
        claim: ExtractedClaim,
        resolved_refs: Dict[str, Any] = None,
    ) -> VerificationResult:
        
        evidence_list = []
        verdict = "INSUFFICIENT_EVIDENCE"
        confidence = 0.0
        explanation = "No usable external evidence retrieved."
        similarity_score = 0.0
        nli_raw = {}
        num_raw = {}

        if not resolved_refs:
            resolved_refs = {}

        # Determine retrieval status for this claim
        has_citations = len(claim.linked_citations) > 0
        has_resolved_citations = False
        has_failed_retrievals = False
        
        for citation_ref_id in claim.linked_citations:
            ref = resolved_refs.get(citation_ref_id)
            if ref:
                if ref.retrieval_status == "resolved":
                    has_resolved_citations = True
                elif ref.retrieval_status == "error":
                    has_failed_retrievals = True

        if has_citations and not has_resolved_citations:
            if has_failed_retrievals:
                verdict = "RETRIEVAL_FAILED"
                explanation = "Attempted to retrieve cited source but failed due to API/network error."
            else:
                verdict = "SOURCE_UNAVAILABLE"
                explanation = "The cited source is external and unavailable for verification."
            
            return VerificationResult(
                claim_id=claim.claim_id,
                claim_text=claim.text,
                claim_type=claim.claim_type,
                section=claim.section,
                page_number=claim.page_number,
                linked_citations=claim.linked_citations,
                verdict=verdict,
                confidence=0.0,
                explanation=explanation,
                evidence=[],
                semantic_similarity=0.0
            )

        # 1. Retrieve top evidence from External Index
        # We enforce that strict citation verification only uses CITED_EXTERNAL_SOURCE
        # Since external_faiss_store only has CITED_EXTERNAL_SOURCE, we search there.
        retrieved = []
        if self.external_faiss_store.index.ntotal > 0:
            retrieved = self.external_faiss_store.search(claim.text, top_k=3)

        if not retrieved:
            # Check the self-verification regression: We DO NOT fallback to self.faiss_store (current document).
            return VerificationResult(
                claim_id=claim.claim_id,
                claim_text=claim.text,
                claim_type=claim.claim_type,
                section=claim.section,
                page_number=claim.page_number,
                linked_citations=claim.linked_citations,
                verdict="INSUFFICIENT_EVIDENCE",
                confidence=0.1,
                explanation="No relevant external evidence found for the claim.",
                evidence=[],
                semantic_similarity=0.0
            )

        # Build evidence list
        for ev in retrieved:
            evidence_list.append(
                Evidence(
                    sentence_id=ev.get("sentence_id", "unknown"),
                    text=ev.get("text", ""),
                    score=ev.get("score", 0.0),
                    page_number=ev.get("page_number", 0),
                    section=ev.get("section"),
                    source_id=ev.get("source_id", "unknown"),
                    source_type=ev.get("source_type", "CITED_EXTERNAL_SOURCE"),
                    document_title=ev.get("document_title"),
                    source_url=ev.get("source_url")
                )
            )

        best_evidence = evidence_list[0]
        evidence_text = best_evidence.text
        similarity_score = best_evidence.score

        # 2. NLI Verification
        nli_raw = self.nli_verifier.verify(claim.text, evidence_text)
        nli_result = NLIResult(
            entailment=nli_raw.get("entailment", 0.0),
            neutral=nli_raw.get("neutral", 0.0),
            contradiction=nli_raw.get("contradiction", 0.0),
            predicted_label=nli_raw.get("predicted_label", "neutral"),
        )

        # 3. Numerical Consistency
        num_raw = self.numerical_checker.check_consistency(
            claim.text, evidence_text
        )
        numerical_result = NumericalResult(
            status=num_raw.get("status", "NO_NUMBERS_IN_CLAIM"),
            claim_numbers=num_raw.get("claim_numbers", []),
            evidence_numbers=num_raw.get("evidence_numbers", []),
            missing_numbers=num_raw.get("missing_numbers", []),
            approximate_matches=num_raw.get("approximate_matches", []),
            matched_numbers=num_raw.get("matched_numbers", []),
            message=num_raw.get("message"),
        )

        # 4. Aggregate verdict
        verdict, explanation, warnings = self._aggregate_verdict(
            nli_raw, num_raw, similarity_score
        )

        # 5. Compute confidence
        confidence = self._compute_confidence(
            verdict, similarity_score, nli_raw, num_raw
        )

        return VerificationResult(
            claim_id=claim.claim_id,
            claim_text=claim.text,
            claim_type=claim.claim_type,
            section=claim.section,
            page_number=claim.page_number,
            linked_citations=claim.linked_citations,
            verdict=verdict,
            confidence=confidence,
            explanation=explanation,
            warnings=warnings,
            evidence=evidence_list,
            nli_result=nli_result,
            numerical_result=numerical_result,
            semantic_similarity=round(similarity_score, 4),
        )

    def _aggregate_verdict(
        self,
        nli_result: Dict[str, Any],
        num_result: Dict[str, Any],
        similarity_score: float,
    ) -> tuple:
        """
        Aggregate NLI and numerical signals into a final verdict.

        Returns (verdict, explanation, warnings).
        """
        nli_verdict = nli_result["label"]
        nli_explanation = nli_result["explanation"]
        warnings: List[str] = []

        # Low similarity warning
        if similarity_score < 0.3:
            warnings.append(
                f"Low semantic similarity ({similarity_score:.2f}). "
                "Evidence may not be directly relevant to the claim."
            )

        # Numerical discrepancy overrides
        if num_result["status"] == "DISCREPANCY":
            warnings.append(num_result.get("message", "Numerical discrepancy detected."))

            if nli_verdict == "SUPPORTED":
                # NLI says supported but numbers don't match
                verdict = "PARTIALLY_SUPPORTED"
                explanation = (
                    f"{nli_explanation} However, a numerical discrepancy was "
                    f"detected: {num_result.get('message', '')}. "
                    f"Verdict downgraded to PARTIALLY_SUPPORTED."
                )
            elif nli_verdict == "CONTRADICTED":
                verdict = "CONTRADICTED"
                explanation = (
                    f"{nli_explanation} Additionally, numerical values "
                    f"in the claim do not match the evidence."
                )
            else:
                verdict = "PARTIALLY_SUPPORTED"
                explanation = (
                    f"{nli_explanation} A numerical discrepancy was also detected."
                )
        elif num_result["status"] == "APPROXIMATE":
            warnings.append(
                num_result.get("message", "Approximate numerical match detected.")
            )
            if nli_verdict == "SUPPORTED":
                verdict = "PARTIALLY_SUPPORTED"
                explanation = (
                    f"{nli_explanation} Note: numerical values are approximately "
                    f"matching but not exact. {num_result.get('message', '')}"
                )
            else:
                verdict = nli_verdict
                explanation = nli_explanation
        else:
            verdict = nli_verdict
            explanation = nli_explanation

            # Replace old NLI label names with new ones
            if verdict == "SUPPORTS":
                verdict = "SUPPORTED"
            elif verdict == "CONTRADICTS":
                verdict = "CONTRADICTED"
            elif verdict == "INSUFFICIENT EVIDENCE":
                verdict = "INSUFFICIENT_EVIDENCE"

        return verdict, explanation, warnings

    def _compute_confidence(
        self,
        verdict: str,
        similarity_score: float,
        nli_result: Dict[str, Any],
        num_result: Dict[str, Any],
    ) -> float:
        """
        Compute overall verification confidence as a weighted combination
        of similarity, NLI confidence, and numerical consistency.
        """
        # NLI confidence is the max probability
        nli_conf = max(
            nli_result.get("entailment", 0.0),
            nli_result.get("neutral", 0.0),
            nli_result.get("contradiction", 0.0),
        )

        # Similarity score (clamp to 0-1)
        sim = max(0.0, min(1.0, similarity_score))

        # Numerical factor
        num_status = num_result.get("status", "NO_NUMBERS_IN_CLAIM")
        if num_status == "CONSISTENT":
            num_factor = 1.0
        elif num_status == "APPROXIMATE":
            num_factor = 0.7
        elif num_status == "DISCREPANCY":
            num_factor = 0.3
        else:
            num_factor = 0.8  # No numbers — neutral

        # Weighted average
        confidence = 0.50 * nli_conf + 0.30 * sim + 0.20 * num_factor

        return round(min(1.0, max(0.0, confidence)), 4)

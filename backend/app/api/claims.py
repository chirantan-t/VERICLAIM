"""
Claims API routes: list, filter, and retrieve individual claim verifications.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.document_service import DocumentService

router = APIRouter()
doc_service = DocumentService()


@router.get("")
async def list_claims(
    document_id: Optional[str] = Query(None, description="Filter by document ID"),
    verdict: Optional[str] = Query(None, description="Filter by verdict"),
    claim_type: Optional[str] = Query(None, description="Filter by claim type"),
    section: Optional[str] = Query(None, description="Filter by section"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence"),
    max_confidence: Optional[float] = Query(None, description="Maximum confidence"),
    has_warnings: Optional[bool] = Query(None, description="Filter claims with warnings"),
):
    """List all claims, optionally filtered by document and criteria."""
    if not document_id:
        # Return claims from all documents
        all_claims = []
        for doc_info in doc_service.list_documents():
            doc_id = doc_info["document_id"]
            results = doc_service.get_results(doc_id) or []
            for r in results:
                all_claims.append({"document_id": doc_id, **r.model_dump()})
        claims = all_claims
    else:
        results = doc_service.get_results(document_id)
        if results is None:
            raise HTTPException(status_code=404, detail="Document not found.")
        claims = [{"document_id": document_id, **r.model_dump()} for r in results]

    # Apply filters
    if verdict:
        claims = [c for c in claims if c.get("verdict", "").upper() == verdict.upper()]
    if claim_type:
        claims = [c for c in claims if c.get("claim_type", "") == claim_type.lower()]
    if section:
        claims = [c for c in claims if c.get("section", "").lower() == section.lower()]
    if min_confidence is not None:
        claims = [c for c in claims if c.get("confidence", 0) >= min_confidence]
    if max_confidence is not None:
        claims = [c for c in claims if c.get("confidence", 1) <= max_confidence]
    if has_warnings is not None:
        if has_warnings:
            claims = [c for c in claims if c.get("warnings")]
        else:
            claims = [c for c in claims if not c.get("warnings")]

    return claims


@router.get("/{claim_id}")
async def get_claim(claim_id: str):
    """Get a specific claim's verification details."""
    doc_id = doc_service.find_claim_document(claim_id)
    if not doc_id:
        raise HTTPException(status_code=404, detail="Claim not found.")

    result = doc_service.get_result_by_claim_id(doc_id, claim_id)
    if not result:
        raise HTTPException(status_code=404, detail="Claim not found.")

    return {"document_id": doc_id, **result.model_dump()}


@router.get("/{claim_id}/evidence")
async def get_claim_evidence(claim_id: str):
    """Get evidence passages for a specific claim."""
    doc_id = doc_service.find_claim_document(claim_id)
    if not doc_id:
        raise HTTPException(status_code=404, detail="Claim not found.")

    result = doc_service.get_result_by_claim_id(doc_id, claim_id)
    if not result:
        raise HTTPException(status_code=404, detail="Claim not found.")

    return {
        "claim_id": claim_id,
        "claim_text": result.claim_text,
        "evidence": [e.model_dump() for e in result.evidence],
        "semantic_similarity": result.semantic_similarity,
        "nli_result": result.nli_result.model_dump() if result.nli_result else None,
        "numerical_result": result.numerical_result.model_dump() if result.numerical_result else None,
    }

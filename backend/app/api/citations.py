"""
Citations API routes: list and retrieve citation details with usage analysis.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.document_service import DocumentService

router = APIRouter()
doc_service = DocumentService()


@router.get("")
async def list_citations(
    document_id: Optional[str] = Query(None, description="Filter by document ID"),
):
    """List all citations with their usage statistics."""
    if not document_id:
        raise HTTPException(
            status_code=400,
            detail="document_id query parameter is required.",
        )

    doc = doc_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    results = doc_service.get_results(document_id) or []

    # Build citation usage map
    citation_data = []
    for ref in doc.references:
        # Find all claims that cite this reference
        using_claims = []
        support_count = 0
        partial_count = 0
        contradict_count = 0
        insufficient_count = 0

        for r in results:
            if ref.ref_id in r.linked_citations:
                using_claims.append(
                    {
                        "claim_id": r.claim_id,
                        "claim_text": r.claim_text,
                        "verdict": r.verdict,
                        "confidence": r.confidence,
                    }
                )
                if r.verdict == "SUPPORTED":
                    support_count += 1
                elif r.verdict == "PARTIALLY SUPPORTED":
                    partial_count += 1
                elif r.verdict == "CONTRADICTED":
                    contradict_count += 1
                else:
                    insufficient_count += 1

        citation_data.append(
            {
                "ref_id": ref.ref_id,
                "raw_text": ref.raw_text,
                "authors": ref.authors,
                "title": ref.title,
                "year": ref.year,
                "venue": ref.venue,
                "claims_using": len(using_claims),
                "supported": support_count,
                "partially_supported": partial_count,
                "contradicted": contradict_count,
                "insufficient": insufficient_count,
                "claims": using_claims,
            }
        )

    return citation_data


@router.get("/{ref_id}")
async def get_citation(
    ref_id: str,
    document_id: str = Query(..., description="Document ID"),
):
    """Get detailed information about a specific citation."""
    doc = doc_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Find the reference (ref_id could be like "[1]" or "1")
    normalized_id = ref_id if ref_id.startswith("[") else f"[{ref_id}]"
    ref = None
    for r in doc.references:
        if r.ref_id == normalized_id or r.ref_id == ref_id:
            ref = r
            break

    if not ref:
        raise HTTPException(status_code=404, detail="Citation not found.")

    results = doc_service.get_results(document_id) or []

    # Find all claims using this citation
    related_claims = []
    for result in results:
        if ref.ref_id in result.linked_citations:
            related_claims.append(result.model_dump())

    return {
        "citation": ref.model_dump(),
        "related_claims": related_claims,
        "total_claims": len(related_claims),
    }

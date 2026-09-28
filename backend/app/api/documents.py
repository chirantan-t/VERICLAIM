"""
Document API routes: upload, list, retrieve, and analyze PDF documents.
"""

import os
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.verification import AnalysisResponse, DocumentStatistics, ProcessingStatus
from app.services.analysis_service import AnalysisService
from app.services.document_service import DocumentService

router = APIRouter()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)

# Shared service instances (singletons)
doc_service = DocumentService()
analysis_service = AnalysisService()


@router.post("/upload", response_model=AnalysisResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF and run the full verification pipeline."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    file_size = len(content)

    # Validate file size
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB.",
        )

    document_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{document_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        result = analysis_service.analyze_document(
            file_path=file_path,
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to parse and verify PDF: {str(e)}"
        )


@router.get("")
async def list_documents():
    """List all analyzed documents."""
    return doc_service.list_documents()


@router.get("/{document_id}")
async def get_document(document_id: str):
    """Get a specific document's parsed structure."""
    doc = doc_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@router.get("/{document_id}/results")
async def get_results(document_id: str):
    """Get verification results for a document."""
    results = doc_service.get_results(document_id)
    if results is None:
        raise HTTPException(
            status_code=404, detail="No results found for this document."
        )
    return results


@router.get("/{document_id}/statistics", response_model=DocumentStatistics)
async def get_statistics(document_id: str):
    """Get computed statistics for a document."""
    stats = doc_service.get_statistics(document_id)
    if not stats:
        # Try computing on the fly
        doc = doc_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")
        stats = doc_service.compute_statistics(document_id)
    return stats


@router.get("/{document_id}/status", response_model=ProcessingStatus)
async def get_status(document_id: str):
    """Get processing status for a document."""
    status = doc_service.get_status(document_id)
    if not status:
        raise HTTPException(status_code=404, detail="Document not found.")
    return status

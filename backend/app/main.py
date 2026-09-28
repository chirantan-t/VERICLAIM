"""
VERICLAIM API — Scientific Claim & Citation Verification System

Main FastAPI application with all routers and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import claims, citations, documents
from app.core.config import settings

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(claims.router, prefix="/claims", tags=["Claims"])
app.include_router(citations.router, prefix="/citations", tags=["Citations"])


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "VERICLAIM backend is running",
        "version": settings.api_version,
    }

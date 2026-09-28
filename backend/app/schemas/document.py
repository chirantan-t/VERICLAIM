"""Pydantic schemas for document structures."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class ClaimType(str, Enum):
    """Classification of scientific claim types."""

    FACTUAL = "factual"
    NUMERICAL = "numerical"
    COMPARATIVE = "comparative"
    CAUSAL = "causal"
    METHODOLOGICAL = "methodological"
    STATISTICAL = "statistical"
    CONCLUSION = "conclusion"


class Sentence(BaseModel):
    sentence_id: str
    text: str
    page_number: int
    section: Optional[str] = None
    citation_markers: List[str] = []


class Paragraph(BaseModel):
    paragraph_id: str
    text: str
    page_number: int
    sentences: List[Sentence] = []


class Section(BaseModel):
    title: str
    paragraphs: List[Paragraph] = []


class Reference(BaseModel):
    ref_id: str
    raw_text: str
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    source_id: Optional[str] = None
    retrieval_status: str = "unresolved"


class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    abstract: Optional[str] = None
    pages: Optional[int] = None
    file_size: Optional[int] = None
    filename: Optional[str] = None


class ExtractedClaim(BaseModel):
    claim_id: str
    text: str
    source_sentence_id: str
    section: Optional[str] = None
    page_number: Optional[int] = None
    linked_citations: List[str] = []
    claim_type: ClaimType = ClaimType.FACTUAL


class ParsedDocument(BaseModel):
    document_id: str
    metadata: DocumentMetadata
    sections: List[Section]
    references: List[Reference]
    claims: List[ExtractedClaim] = []

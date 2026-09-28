"""
PDF Parser: extracts text, structure, references, and claims from PDFs.

Builds a ParsedDocument with sections, paragraphs, sentences, references,
and extracted claims with type classification and citation linking.
"""

import os
import re
import uuid
from typing import Any, Dict, List, Optional

import fitz  # PyMuPDF

from app.nlp.citation_extractor import CitationExtractor
from app.nlp.claim_extractor import ClaimExtractor
from app.nlp.claim_linker import ClaimLinker
from app.nlp.reference_parser import ReferenceParser
from app.schemas.document import (
    DocumentMetadata,
    ExtractedClaim,
    Paragraph,
    ParsedDocument,
    Reference,
    Section,
    Sentence,
)


class PDFParser:
    def __init__(self):
        self.citation_extractor = CitationExtractor()
        self.reference_parser = ReferenceParser()
        self.claim_extractor = ClaimExtractor()
        self.claim_linker = ClaimLinker()
        # Sentence splitting regex (naive)
        self.sentence_pattern = re.compile(r"(?<=[.!?])\s+")
        # Section header detection (simple heuristic)
        self.section_pattern = re.compile(
            r"^(Abstract|Introduction|Background|Related Work|Methodology|"
            r"Methods|Method|Experiments?|Results?|Discussion|Conclusion|"
            r"Conclusions|Acknowledgments?|References|Appendix|"
            r"Supplementary|Materials?\s+and\s+Methods?|"
            r"\d+\.?\s+\w+)",
            re.IGNORECASE,
        )

    def parse(
        self,
        file_path: str,
        document_id: str,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
    ) -> ParsedDocument:
        """Parse a PDF file into a structured ParsedDocument."""
        doc = fitz.open(file_path)

        full_text = ""
        paragraphs_data = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            for b in blocks:
                if b[6] == 0:  # text block
                    text = b[4].strip()
                    if text:
                        paragraphs_data.append(
                            {"text": text, "page_number": page_num + 1}
                        )
                        full_text += text + "\n\n"

        # Extract metadata
        metadata = self._extract_metadata(doc, full_text, filename, file_size)

        # Extract references
        references = self._extract_references(full_text)

        # Build document structure
        sections = self._build_structure(paragraphs_data)

        # Build section map for sentences
        section_map: Dict[str, str] = {}
        all_sentences = []
        for sec in sections:
            for p in sec.paragraphs:
                for s in p.sentences:
                    section_map[s.sentence_id] = sec.title
                    all_sentences.append(s)

        # Phase 3: Claim Extraction & Linking
        claim_sentences = self.claim_extractor.extract_claims(all_sentences)
        claims = self.claim_linker.link_claims(claim_sentences, references, section_map)

        doc.close()

        return ParsedDocument(
            document_id=document_id,
            metadata=metadata,
            sections=sections,
            references=references,
            claims=claims,
        )

    def _extract_metadata(
        self,
        doc: fitz.Document,
        full_text: str,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
    ) -> DocumentMetadata:
        """Extract document metadata from PDF properties and content."""
        # Try PDF metadata
        pdf_meta = doc.metadata or {}
        title = pdf_meta.get("title", "").strip()

        # If no title in metadata, use first substantial text block
        if not title:
            lines = full_text.split("\n")
            for line in lines:
                stripped = line.strip()
                if len(stripped) > 10 and len(stripped) < 200:
                    title = stripped
                    break
            if not title:
                title = filename or "Untitled Document"

        # Extract authors from PDF metadata
        authors_str = pdf_meta.get("author", "")
        authors = (
            [a.strip() for a in authors_str.split(",") if a.strip()]
            if authors_str
            else []
        )

        # Try to extract abstract
        abstract = ""
        abstract_match = re.search(
            r"(?:Abstract|ABSTRACT)[:\s]*\n?(.*?)(?:\n\s*\n|\n(?:1\.?\s+)?Introduction)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        )
        if abstract_match:
            abstract = abstract_match.group(1).strip().replace("\n", " ")[:1000]

        return DocumentMetadata(
            title=title,
            authors=authors if authors else None,
            abstract=abstract if abstract else None,
            pages=len(doc),
            file_size=file_size,
            filename=filename,
        )

    def _extract_references(self, text: str) -> List[Reference]:
        """Extract and parse references from the document text."""
        refs = []
        ref_match = re.search(r"\n(?:References|REFERENCES|Bibliography|Literature Cited)\s*\n", text)
        if ref_match:
            ref_text = text[ref_match.end() :]
            lines = ref_text.split('\n')
            current_ref = ""
            ref_idx = 1
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                # Check if it starts a new reference
                if re.match(r'^(\d+\.|\[\d+\])', stripped):
                    # End previous ref
                    if current_ref:
                        parsed = self.reference_parser.parse_reference(current_ref, ref_idx)
                        refs.append(
                            Reference(
                                ref_id=parsed.get("reference_id") or f"[{ref_idx}]",
                                raw_text=current_ref,
                                authors=parsed.get("authors"),
                                title=parsed.get("title"),
                                year=parsed.get("year"),
                                venue=parsed.get("venue"),
                            )
                        )
                        ref_idx += 1
                    current_ref = stripped
                else:
                    if current_ref:
                        current_ref += " " + stripped
                    else:
                        current_ref = stripped
                        
            if current_ref:
                parsed = self.reference_parser.parse_reference(current_ref, ref_idx)
                refs.append(
                    Reference(
                        ref_id=parsed.get("reference_id") or f"[{ref_idx}]",
                        raw_text=current_ref,
                        authors=parsed.get("authors"),
                        title=parsed.get("title"),
                        year=parsed.get("year"),
                        venue=parsed.get("venue"),
                    )
                )
        return refs

    def _build_structure(self, paragraphs_data: List[Dict]) -> List[Section]:
        """Build document structure from extracted paragraph data."""
        current_section = Section(title="Main Body", paragraphs=[])
        sections = [current_section]

        for p_idx, p_data in enumerate(paragraphs_data):
            text = p_data["text"]
            page_num = p_data["page_number"]

            # Check if this paragraph is a section header
            clean_text = text.strip().replace("\n", " ")
            if (
                len(clean_text) < 80
                and self.section_pattern.match(clean_text)
                and not clean_text.endswith(".")
            ):
                current_section = Section(title=clean_text, paragraphs=[])
                sections.append(current_section)
                continue

            sentences_text = self.sentence_pattern.split(text)
            sentences = []
            for s_idx, s_text in enumerate(sentences_text):
                s_clean = s_text.strip().replace("\n", " ")
                if not s_clean:
                    continue

                citations = self.citation_extractor.extract_citations(s_clean)

                sentences.append(
                    Sentence(
                        sentence_id=f"p{p_idx}_s{s_idx}",
                        text=s_clean,
                        page_number=page_num,
                        section=current_section.title,
                        citation_markers=citations,
                    )
                )

            if sentences:
                current_section.paragraphs.append(
                    Paragraph(
                        paragraph_id=f"p{p_idx}",
                        text=text.replace("\n", " "),
                        page_number=page_num,
                        sentences=sentences,
                    )
                )

        return sections

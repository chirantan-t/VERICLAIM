import re
from typing import List, Dict, Any, Optional

class ReferenceParser:
    def __init__(self):
        self.year_pattern = re.compile(r'\b(19\d{2}|20\d{2})\b')

    def parse_reference(self, raw_text: str, index: int = None) -> Dict[str, Any]:
        """
        Parses a raw reference string.
        """
        parsed = {
            "reference_id": f"[{index}]" if index is not None else None,
            "raw_text": raw_text.strip(),
            "authors": [],
            "title": None,
            "year": None,
            "venue": None,
            "doi": None,
            "url": None,
            "document_id": None
        }
        
        text = raw_text.strip()
        
        # Extract year
        year_match = self.year_pattern.search(text)
        if year_match:
            parsed["year"] = int(year_match.group(1))

        # Extract DOI
        doi_match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', text, re.IGNORECASE)
        if doi_match:
            parsed["doi"] = doi_match.group(1)
            
        # Extract URL
        url_match = re.search(r'(https?://[^\s]+)', text)
        if url_match:
            parsed["url"] = url_match.group(1)

        # Naive split for authors and title
        # Usually authors are at the beginning, ending with a period or year.
        parts = re.split(r'\.\s+|\"\s*', text, maxsplit=2)
        if len(parts) >= 2:
            author_part = parts[0]
            # Strip year from author part if it's there
            author_part = re.sub(r'\(\d{4}\)', '', author_part)
            parsed["authors"] = [a.strip() for a in re.split(r',| and ', author_part) if a.strip() and len(a.strip()) > 1]
            parsed["title"] = parts[1].strip()

        return parsed

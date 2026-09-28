import re
from typing import List

class CitationExtractor:
    def __init__(self):
        # Numeric: [1], [1, 2], [1-3]
        self.numeric_pattern = re.compile(r'\[\s*\d+(?:\s*,\s*\d+|\s*-\s*\d+)*\s*\]')
        
        # Multiple author-year separated by semicolons: (Smith, 2024; Jones, 2023)
        self.paren_multiple_pattern = re.compile(r'\(\s*(?:[A-Z][a-zA-Z-]+.*?(?:19\d{2}|20\d{2})[a-z]?.*?(?:;\s*)?)+\)')

        # Single author-year: (Smith, 2024), Smith et al. (2024), Smith et al., 2024, [Smith2024]
        # Match author part, then year part.
        self.author_year_pattern = re.compile(
            r'(?:[A-Z][a-zA-Z-]+(?:\s+et\s+al\.?)?(?:\s+and\s+[A-Z][a-zA-Z-]+)?)\s*'
            r'(?:,\s*|\(\s*|\[\s*)(19\d{2}|20\d{2})[a-z]?(?:\s*\)|\s*\])?'
        )

    def extract_citations(self, text: str) -> List[str]:
        """
        Extracts citation markers from a piece of text.
        """
        citations = []
        
        # 1. Numeric
        for match in self.numeric_pattern.finditer(text):
            citations.append(match.group(0))
            
        # 2. Parenthetical multiple
        for match in self.paren_multiple_pattern.finditer(text):
            # If it actually contains a year and a semicolon, it's a multiple
            m_text = match.group(0)
            if ';' in m_text and re.search(r'(19\d{2}|20\d{2})', m_text):
                citations.append(m_text)
                
        # 3. Single author year
        # We need the full match for author year
        ay_regex = re.compile(
            r'\b(?:[A-Z][a-zA-Z-]+(?:\s+et\s+al\.?)?(?:\s+and\s+[A-Z][a-zA-Z-]+)?)\s*'
            r'(?:,\s*|\(\s*|\[\s*)(?:19\d{2}|20\d{2})[a-z]?(?:\s*\)|\s*\])?\b'
        )
        for match in ay_regex.finditer(text):
            # Skip if already captured in paren_multiple
            already_captured = any(match.group(0) in c for c in citations if c.startswith('('))
            if not already_captured:
                citations.append(match.group(0))
                
        return citations

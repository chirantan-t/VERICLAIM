"""
Claim linker: connects extracted claim sentences to citation markers
and enriches them with section/page metadata.
"""

import uuid
from typing import Dict, List, Optional

from app.nlp.claim_extractor import ClaimExtractor
from app.schemas.document import ClaimType, ExtractedClaim, Sentence, Reference


class ClaimLinker:
    def __init__(self):
        self.claim_extractor = ClaimExtractor.__new__(ClaimExtractor)
        # Manually set up just the classify_type method dependencies
        # without loading the full model (we only need heuristic classification here)
        self.claim_extractor._number_pattern = ClaimExtractor.__init__.__code__  # placeholder
        # Actually just create a fresh instance for type classification only
        self._type_classifier = None

    def _get_type_classifier(self):
        """Lazy init of claim type classifier (no model needed, just heuristics)."""
        if self._type_classifier is None:
            import re

            class _TypeClassifier:
                def __init__(self):
                    self._number_pattern = re.compile(r"\d+\.?\d*\s*%?")
                    self._comparative_words = {
                        "more", "less", "higher", "lower", "better", "worse",
                        "outperform", "outperforms", "outperformed", "superior",
                        "improve", "improves", "improved", "improvement",
                        "increase", "increases", "decrease", "decreases",
                        "faster", "slower", "larger", "smaller", "greater",
                    }
                    self._causal_words = {
                        "causes", "cause", "leads to", "results in",
                        "due to", "because", "induces", "triggers",
                    }
                    self._statistical_words = {
                        "significant", "significantly", "p-value", "p <",
                        "correlation", "statistically", "confidence interval",
                    }
                    self._methodology_words = {
                        "we use", "we used", "we employ", "we propose",
                        "our method", "our approach",
                    }
                    self._conclusion_words = {
                        "therefore", "thus", "conclude", "demonstrate",
                        "demonstrates", "show that", "shows that",
                        "suggest", "suggests", "indicate", "indicates",
                    }

                def classify(self, text: str) -> ClaimType:
                    text_lower = text.lower()
                    has_numbers = bool(self._number_pattern.search(text))
                    if has_numbers and any(w in text_lower for w in self._comparative_words):
                        return ClaimType.COMPARATIVE
                    if any(w in text_lower for w in self._statistical_words):
                        return ClaimType.STATISTICAL
                    if has_numbers:
                        return ClaimType.NUMERICAL
                    if any(w in text_lower for w in self._causal_words):
                        return ClaimType.CAUSAL
                    if any(w in text_lower for w in self._comparative_words):
                        return ClaimType.COMPARATIVE
                    if any(w in text_lower for w in self._methodology_words):
                        return ClaimType.METHODOLOGICAL
                    if any(w in text_lower for w in self._conclusion_words):
                        return ClaimType.CONCLUSION
                    return ClaimType.FACTUAL

            self._type_classifier = _TypeClassifier()
        return self._type_classifier

    def _resolve_citation(self, citation: str, references: List[Reference]) -> str:
        """Resolve a citation marker to a ref_id, returning UNRESOLVED_CITATION if not found."""
        import re
        # Numeric [1], [1, 2], [1-3]
        if re.match(r'^\[\s*\d+(?:\s*,\s*\d+|\s*-\s*\d+)*\s*\]$', citation):
            # For simplicity, if it's [1], we return [1]. If [1,2], return multiple?
            # The schema says linked_citations is List[str].
            # For this MVP, we map numeric directly if it exists, or just check the first number.
            nums = re.findall(r'\d+', citation)
            if nums:
                target_id = f"[{nums[0]}]"
                if any(r.ref_id == target_id for r in references):
                    return target_id
            return "UNRESOLVED_CITATION"
            
        # Author-year
        year_match = re.search(r'(19\d{2}|20\d{2})', citation)
        if year_match:
            year = int(year_match.group(1))
            # Find authors in citation
            words = re.findall(r'[A-Z][a-zA-Z-]+', citation)
            if not words:
                return "UNRESOLVED_CITATION"
            
            best_match = None
            highest_score = 0
            for ref in references:
                if ref.year == year:
                    score = 0
                    if ref.authors:
                        # check if any word from citation matches any author
                        for w in words:
                            for a in ref.authors:
                                if w.lower() in a.lower():
                                    score += 1
                    if score > highest_score:
                        highest_score = score
                        best_match = ref.ref_id
            if best_match:
                return best_match

        return "UNRESOLVED_CITATION"

    def link_claims(
        self,
        claim_sentences: List[Sentence],
        references: List[Reference],
        section_map: Optional[Dict[str, str]] = None,
    ) -> List[ExtractedClaim]:
        """
        Takes sentences identified as claims and creates ExtractedClaim objects,
        linking them to their respective in-text citations and enriching
        with section/page metadata and claim type classification.

        Args:
            claim_sentences: Sentences identified as containing scientific claims.
            references: Parsed references to link against.
            section_map: Optional mapping from sentence_id to section title.
        """
        classifier = self._get_type_classifier()
        extracted_claims = []

        for sentence in claim_sentences:
            # Determine section from map
            section = None
            if section_map:
                section = section_map.get(sentence.sentence_id, sentence.section)
            elif sentence.section:
                section = sentence.section

            # Classify claim type
            claim_type = classifier.classify(sentence.text)
            
            # Resolve citations
            resolved = []
            for cit in sentence.citation_markers:
                # Multiple numeric [1, 2] -> multiple resolved
                import re
                if re.match(r'^\[\s*\d+(?:\s*,\s*\d+|\s*-\s*\d+)*\s*\]$', cit):
                    nums = re.findall(r'\d+', cit)
                    for n in nums:
                        target_id = f"[{n}]"
                        if any(r.ref_id == target_id for r in references):
                            resolved.append(target_id)
                        else:
                            resolved.append("UNRESOLVED_CITATION")
                elif ';' in cit:
                    # Multiple author year
                    parts = cit.split(';')
                    for p in parts:
                        resolved.append(self._resolve_citation(p, references))
                else:
                    resolved.append(self._resolve_citation(cit, references))
                    
            # Remove duplicates but preserve order
            final_resolved = []
            for r in resolved:
                if r not in final_resolved:
                    final_resolved.append(r)

            claim = ExtractedClaim(
                claim_id=str(uuid.uuid4()),
                text=sentence.text,
                source_sentence_id=sentence.sentence_id,
                section=section,
                page_number=sentence.page_number,
                linked_citations=final_resolved,
                claim_type=claim_type,
            )
            extracted_claims.append(claim)

        return extracted_claims


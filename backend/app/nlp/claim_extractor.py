"""
Claim extraction using zero-shot classification and claim type classification.

Uses a HuggingFace zero-shot classifier to determine if a sentence contains
a scientific claim, then classifies the type of claim using heuristic rules.
"""

import re
from typing import List

from transformers import pipeline

from app.schemas.document import ClaimType, Sentence
from app.core.config import settings


class ClaimExtractor:
    def __init__(self, model_name: str = "typeform/distilbert-base-uncased-mnli"):
        """
        Initializes the Claim Extractor using a HuggingFace zero-shot sequence classifier.
        Uses lazy loading to avoid loading the model until first use.
        """
        self.model_name = model_name
        self._pipeline = None

        # Patterns for claim type classification
        self._number_pattern = re.compile(r"\d+\.?\d*\s*%?")
        self._comparative_words = {
            "more", "less", "higher", "lower", "better", "worse",
            "outperform", "outperforms", "outperformed", "superior",
            "inferior", "exceed", "exceeds", "surpass", "improve",
            "improves", "improved", "improvement", "increase",
            "increases", "increased", "decrease", "decreases", "decreased",
            "faster", "slower", "larger", "smaller", "greater",
        }
        self._causal_words = {
            "causes", "cause", "caused", "leads to", "lead to",
            "results in", "result in", "due to", "because",
            "induces", "induced", "triggers", "triggered",
            "contributes to", "associated with", "affects",
        }
        self._statistical_words = {
            "significant", "significantly", "p-value", "p <", "p=",
            "correlation", "statistically", "confidence interval",
            "standard deviation", "variance", "regression", "anova",
            "chi-square", "t-test", "mann-whitney", "wilcoxon",
        }
        self._methodology_words = {
            "we use", "we used", "we employ", "we employed",
            "we apply", "we applied", "we propose", "we proposed",
            "our method", "our approach", "our technique",
            "we implement", "we implemented", "we train", "we trained",
        }
        self._conclusion_words = {
            "therefore", "thus", "conclude", "in conclusion",
            "demonstrate", "demonstrates", "demonstrated",
            "show that", "shows that", "showed that",
            "suggest", "suggests", "suggested", "indicate",
            "indicates", "indicated", "confirm", "confirms",
            "confirmed", "establish", "establishes", "established",
        }

    @property
    def model(self):
        """Lazy-load the model on first use."""
        if self._pipeline is None:
            self._pipeline = pipeline(
                "zero-shot-classification", 
                model=self.model_name,
                model_kwargs={"cache_dir": settings.model_cache_dir}
            )
        return self._pipeline

    def is_claim(self, sentence_text: str) -> bool:
        """
        Determines if a given sentence contains a scientific claim.
        Uses zero-shot classification to categorize the sentence.
        """
        # A simple length filter to avoid classifying very short fragments
        if len(sentence_text.split()) <= 5:
            return False

        result = self.model(
            sentence_text,
            candidate_labels=[
                "scientific claim",
                "background information",
                "methodology",
            ],
        )

        # If the score for "scientific claim" is reasonably high
        try:
            claim_index = result["labels"].index("scientific claim")
            claim_score = result["scores"][claim_index]
            return claim_score > 0.15 or result["labels"][0] == "scientific claim"
        except ValueError:
            return result["labels"][0] == "scientific claim"

    def classify_type(self, text: str) -> ClaimType:
        """
        Classify the type of a scientific claim using heuristic rules.
        Checks for numerical values, comparative language, causal language, etc.
        """
        text_lower = text.lower()

        has_numbers = bool(self._number_pattern.search(text))

        # Check for comparative + numerical → comparative
        if has_numbers and any(w in text_lower for w in self._comparative_words):
            return ClaimType.COMPARATIVE

        # Check for statistical language
        if any(w in text_lower for w in self._statistical_words):
            return ClaimType.STATISTICAL

        # Check for numerical (pure numerical claim)
        if has_numbers:
            return ClaimType.NUMERICAL

        # Check for causal language
        if any(w in text_lower for w in self._causal_words):
            return ClaimType.CAUSAL

        # Check for comparative language (without numbers)
        if any(w in text_lower for w in self._comparative_words):
            return ClaimType.COMPARATIVE

        # Check for methodology
        if any(w in text_lower for w in self._methodology_words):
            return ClaimType.METHODOLOGICAL

        # Check for conclusion/demonstration
        if any(w in text_lower for w in self._conclusion_words):
            return ClaimType.CONCLUSION

        return ClaimType.FACTUAL

    def extract_claims(self, sentences: List[Sentence]) -> List[Sentence]:
        """
        Filters a list of sentences to only those that contain claims.
        """
        return [s for s in sentences if self.is_claim(s.text)]

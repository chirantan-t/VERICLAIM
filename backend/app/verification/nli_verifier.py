"""
NLI Verifier: uses a cross-encoder model for Natural Language Inference.

Returns all three label probabilities (entailment, neutral, contradiction)
and maps them to verification verdicts.
"""

import torch
from typing import Any, Dict
from app.nlp.model_manager import model_manager

class NLIVerifier:
    def __init__(self, model_name: str = "cross-encoder/nli-MiniLM2-L6-H768"):
        """
        Initializes the NLI model using model_manager.
        """
        self.model_name = model_name
        self.validated = False

    def _validate_labels(self, model):
        # Fail loudly if labels aren't as expected
        id2label = model.config.id2label
        # Expected for cross-encoder/nli-deberta-v3-small: {0: 'contradiction', 1: 'entailment', 2: 'neutral'}
        expected_mapping = {0: 'contradiction', 1: 'entailment', 2: 'neutral'}
        
        # Check if it matches expected or if it maps correctly
        # Alternatively, we just check if it has contradiction, entailment, neutral
        for val in ['contradiction', 'entailment', 'neutral']:
            if val not in id2label.values() and val.upper() not in [v.upper() for v in id2label.values()]:
                raise ValueError(f"CRITICAL: Model {self.model_name} id2label missing required label: {val}")
        self.validated = True

    def verify(self, claim: str, evidence: str) -> Dict[str, Any]:
        model, tokenizer = model_manager.load_sequence_classifier(self.model_name)
        if not self.validated:
            self._validate_labels(model)
            
        inputs = tokenizer(claim, evidence, return_tensors="pt", truncation=True, padding=True).to(model_manager.device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)[0].cpu().numpy()
            
        id2label = model.config.id2label
        scores = {}
        for idx, prob in enumerate(probs):
            label = id2label[idx].lower()
            scores[label] = float(prob)

        entailment = scores.get("entailment", 0.0)
        neutral = scores.get("neutral", 0.0)
        contradiction = scores.get("contradiction", 0.0)

        # Determine verdict from highest scoring label
        label_map = {
            "entailment": entailment,
            "neutral": neutral,
            "contradiction": contradiction,
        }
        predicted_label = max(label_map, key=label_map.get)
        confidence = label_map[predicted_label]

        if predicted_label == "entailment":
            verdict = "SUPPORTED"
            explanation = (
                f"The retrieved evidence semantically entails the claim "
                f"(entailment={entailment:.3f}, neutral={neutral:.3f}, "
                f"contradiction={contradiction:.3f})."
            )
        elif predicted_label == "contradiction":
            verdict = "CONTRADICTED"
            explanation = (
                f"The retrieved evidence contradicts the claim "
                f"(entailment={entailment:.3f}, neutral={neutral:.3f}, "
                f"contradiction={contradiction:.3f})."
            )
        else:
            verdict = "INSUFFICIENT_EVIDENCE"
            explanation = (
                f"The retrieved evidence is neutral with respect to the claim "
                f"(entailment={entailment:.3f}, neutral={neutral:.3f}, "
                f"contradiction={contradiction:.3f})."
            )

        return {
            "label": verdict,
            "confidence": confidence,
            "entailment": entailment,
            "neutral": neutral,
            "contradiction": contradiction,
            "predicted_label": predicted_label,
            "explanation": explanation,
        }

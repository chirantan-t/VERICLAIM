import json
from typing import List, Dict, Any

class EvaluationDataset:
    """
    Simulates loading an annotated dataset (like SciFact) for evaluation.
    Format expects records with 'claim', 'evidence_snippets', and 'ground_truth_label'.
    """
    def __init__(self, data_path: str = None):
        self.data_path = data_path
        
    def load(self) -> List[Dict[str, Any]]:
        # If no file, return a dummy dataset for testing the framework
        if not self.data_path or not __import__("os").path.exists(self.data_path):
            return [
                {
                    "id": "1",
                    "claim": "Model X improves accuracy by 23%.",
                    "evidence_pool": [
                        "Model X was evaluated.",
                        "It improved accuracy by 23% compared to baseline.",
                        "Deep learning is useful."
                    ],
                    "ground_truth_evidence_idx": 1,
                    "ground_truth_label": "SUPPORTS"
                },
                {
                    "id": "2",
                    "claim": "Algorithm Y decreases latency by 50ms.",
                    "evidence_pool": [
                        "Algorithm Y is fast.",
                        "It decreases latency by 10ms."
                    ],
                    "ground_truth_evidence_idx": 1,
                    "ground_truth_label": "PARTIALLY SUPPORTED"
                }
            ]
            
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f]

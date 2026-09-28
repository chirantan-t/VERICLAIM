from typing import List, Dict
from app.retrieval.faiss_store import FaissStore
from app.retrieval.embedder import Embedder
from app.verification.nli_verifier import NLIVerifier
from app.verification.numerical_checker import NumericalChecker
from experiments.dataset_loader import EvaluationDataset

class PipelineEvaluator:
    def __init__(self, use_numerical_check: bool = True):
        self.embedder = Embedder()
        self.nli_verifier = NLIVerifier()
        self.num_checker = NumericalChecker()
        self.use_numerical_check = use_numerical_check

    def evaluate(self, dataset: EvaluationDataset) -> Dict[str, float]:
        data = dataset.load()
        correct_retrieval = 0
        correct_verdict = 0
        
        for item in data:
            # Setup isolated FAISS for this document's evidence pool
            store = FaissStore(self.embedder)
            metadata = [{"idx": i} for i in range(len(item["evidence_pool"]))]
            store.add_texts(item["evidence_pool"], metadata)
            
            # 1. Evaluate Retrieval
            retrieved = store.search(item["claim"], top_k=1)
            retrieved_idx = retrieved[0]["idx"] if retrieved else -1
            
            if retrieved_idx == item["ground_truth_evidence_idx"]:
                correct_retrieval += 1
                
            evidence_text = retrieved[0]["text"] if retrieved else ""
            
            # 2. Evaluate Verdict
            nli_result = self.nli_verifier.verify(item["claim"], evidence_text)
            verdict = nli_result["label"]
            
            if self.use_numerical_check:
                num_result = self.num_checker.check_consistency(item["claim"], evidence_text)
                if num_result["status"] == "DISCREPANCY":
                    verdict = "PARTIALLY SUPPORTED"
                    
            if verdict == item["ground_truth_label"]:
                correct_verdict += 1
                
        total = len(data)
        metrics = {
            "retrieval_accuracy": correct_retrieval / total if total > 0 else 0.0,
            "verdict_accuracy": correct_verdict / total if total > 0 else 0.0
        }
        return metrics

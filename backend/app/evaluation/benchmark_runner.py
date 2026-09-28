import time
import logging
from typing import Dict, Any, List
from collections import defaultdict

from app.evaluation.scifact import SciFactDataset
from app.evaluation.metrics import calculate_classification_metrics, calculate_retrieval_metrics, generate_confusion_matrix
from app.retrieval.embedder import Embedder
from app.retrieval.faiss_store import FaissStore
from app.verification.nli_verifier import NLIVerifier
from app.verification.numerical_checker import NumericalChecker
from app.nlp.model_manager import model_manager

logger = logging.getLogger(__name__)


class BenchmarkRunner:
    def __init__(self, dataset_dir: str):
        self.dataset = SciFactDataset(dataset_dir)
        self.dataset.load()
        self.embedder = Embedder()
        self.faiss_store = FaissStore(self.embedder)
        self.nli_verifier = NLIVerifier()
        self.numerical_checker = NumericalChecker()
        self.indexed = False

    def build_index(self):
        if self.indexed:
            return
            
        logger.info(f"Indexing {len(self.dataset.corpus)} SciFact documents...")
        texts = []
        metadata = []
        
        # Build sentences from abstracts
        for doc_id, doc in self.dataset.corpus.items():
            for i, sent in enumerate(doc.get("abstract", [])):
                texts.append(sent)
                metadata.append({
                    "doc_id": str(doc_id),
                    "sentence_id": i,
                    "title": doc.get("title", "")
                })
                
        # To avoid OOM, batch insert if needed, but 5000 abstracts is relatively small.
        # Approx 5000 * 10 sentences = 50,000 sentences.
        self.faiss_store.add_texts(texts, metadata)
        self.indexed = True
        logger.info("Indexing complete.")

    def run_experiment(self, config: Dict[str, bool]) -> Dict[str, Any]:
        """
        Runs the benchmark with specific configuration flags.
        config = {
            "use_nli": True/False,
            "use_numerical": True/False
        }
        """
        self.build_index()
        
        retrieval_results = []
        classification_results = []
        
        claims = self.dataset.get_dev_claims()
        
        start_time = time.time()
        
        for claim_obj in claims:
            claim_text = claim_obj["claim"]
            cited_doc_ids = claim_obj.get("cited_doc_ids", [])
            evidence_gt = claim_obj.get("evidence", {})
            
            # Ground truth
            true_label = "INSUFFICIENT_EVIDENCE"
            gt_docs = []
            
            for doc_id, evidence_list in evidence_gt.items():
                gt_docs.append(str(doc_id))
                for ev in evidence_list:
                    lbl = ev.get("label")
                    if lbl == "SUPPORT":
                        true_label = "SUPPORTED"
                    elif lbl == "CONTRADICT":
                        true_label = "CONTRADICTED"

            # 1. Retrieval
            retrieved = self.faiss_store.search(claim_text, top_k=10)
            retrieved_docs = []
            seen = set()
            for r in retrieved:
                doc_id = str(r["doc_id"])
                if doc_id not in seen:
                    retrieved_docs.append(doc_id)
                    seen.add(doc_id)
            
            retrieval_results.append({
                "ground_truth_doc_ids": gt_docs,
                "retrieved_doc_ids": retrieved_docs
            })

            # Verification (only take top-3 sentences for best evidence)
            pred_label = "INSUFFICIENT_EVIDENCE"
            
            if retrieved:
                best_evidence = retrieved[0]["text"]
                similarity_score = retrieved[0]["score"]
                
                nli_lbl = "SUPPORTED"
                if config.get("use_nli"):
                    nli_res = self.nli_verifier.verify(claim_text, best_evidence)
                    nli_lbl = nli_res["label"]
                
                verdict = nli_lbl
                if config.get("use_numerical"):
                    num_res = self.numerical_checker.check_consistency(claim_text, best_evidence)
                    if num_res["status"] == "DISCREPANCY":
                        if verdict == "SUPPORTED":
                            verdict = "PARTIALLY_SUPPORTED"
                        elif verdict == "CONTRADICTED":
                            verdict = "CONTRADICTED"
                        else:
                            verdict = "PARTIALLY_SUPPORTED"

                pred_label = verdict
                
            classification_results.append({
                "true_label": true_label,
                "pred_label": pred_label
            })
            
            # Memory safety: Explicitly clear cache periodically if batch size gets large
            # We are looping over hundreds of claims.
            if len(classification_results) % 100 == 0:
                model_manager.clear_gpu_memory()

        elapsed = time.time() - start_time
        
        # Unload models after experiment for isolation
        model_manager.unload_all()

        retrieval_metrics = calculate_retrieval_metrics(retrieval_results)
        class_metrics = calculate_classification_metrics(classification_results)
        conf_matrix = generate_confusion_matrix(classification_results)

        return {
            "retrieval": retrieval_metrics,
            "classification": class_metrics,
            "confusion_matrix": conf_matrix,
            "runtime": elapsed
        }

    def run_ablation(self):
        experiments = [
            ("A", {"use_nli": False, "use_numerical": False}),
            ("B", {"use_nli": True, "use_numerical": False}),
            ("C", {"use_nli": True, "use_numerical": True}),
        ]
        
        results = {}
        for name, config in experiments:
            logger.info(f"Running Experiment {name}: {config}")
            res = self.run_experiment(config)
            results[name] = res
            
        return results

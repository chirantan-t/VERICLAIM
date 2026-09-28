import json
import os
import time
from typing import List, Dict
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from app.retrieval.faiss_store import FaissStore
from app.retrieval.embedder import Embedder
from app.verification.nli_verifier import NLIVerifier
from app.verification.numerical_checker import NumericalChecker
from app.verification.verification_engine import VerificationEngine
from app.schemas.document import ExtractedClaim

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/scifact"))
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/processed"))
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_data(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def test_retrieval(data: List[Dict], embedder_name: str = "all-MiniLM-L6-v2"):
    print(f"--- Evaluating Retrieval with {embedder_name} ---")
    embedder = Embedder(model_name=embedder_name)
    faiss_store = FaissStore(embedder)
    
    # Index all evidences
    texts = []
    metadata = []
    for i, ex in enumerate(data):
        if ex["evidence_text"]:
            texts.append(ex["evidence_text"])
            metadata.append({"doc_id": ex["source_document"], "idx": i})
    
    if texts:
        faiss_store.add_texts(texts, metadata)
    
    recalls = {1: 0, 3: 0, 5: 0, 10: 0}
    total = len([ex for ex in data if ex["evidence_text"]])
    start_time = time.time()
    
    for i, ex in enumerate(data):
        if not ex["evidence_text"]:
            continue
        
        results = faiss_store.search(ex["claim_text"], top_k=10)
        retrieved_idxs = [r.get("idx") for r in results]
        
        for k in recalls.keys():
            if i in retrieved_idxs[:k]:
                recalls[k] += 1
                
    latency = (time.time() - start_time) / (total if total > 0 else 1)
    
    metrics = {f"Recall@{k}": (recalls[k]/total if total > 0 else 0) for k in recalls}
    metrics["Latency"] = latency
    print(metrics)
    return metrics

def test_nli(data: List[Dict]):
    print("--- Evaluating NLI Independently ---")
    nli = NLIVerifier()
    y_true = []
    y_pred = []
    
    for ex in data:
        if not ex["evidence_text"]:
            continue
            
        result = nli.verify(ex["claim_text"], ex["evidence_text"])
        # Map back to our classes
        y_true.append(ex["label"])
        y_pred.append(result["label"])
        
    acc = accuracy_score(y_true, y_pred)
    # Using weighted average for multi-class precision/recall/f1
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    
    metrics = {"Accuracy": acc, "Precision": p, "Recall": r, "F1": f}
    print(metrics)
    try:
        print("Confusion Matrix:\n", confusion_matrix(y_true, y_pred))
    except:
        pass
    return metrics

def build_baseline_and_ablation(data: List[Dict]):
    print("--- Running Ablation Study ---")
    embedder = Embedder()
    faiss_store = FaissStore(embedder)
    nli_verifier = NLIVerifier()
    num_checker = NumericalChecker()
    engine = VerificationEngine(faiss_store, nli_verifier, num_checker)
    
    # Reindex
    texts = []
    metadata = []
    for i, ex in enumerate(data):
        if ex["evidence_text"]:
            texts.append(ex["evidence_text"])
            metadata.append({"sentence_id": str(i), "page_number": 1, "section": "test"})
    if texts:
        faiss_store.add_texts(texts, metadata)
    
    results = []
    for ex in data:
        claim = ExtractedClaim(
            claim_id=str(ex["claim_id"]),
            text=ex["claim_text"],
            claim_type="factual",
            section="test",
            page_number=1,
            linked_citations=[],
            source_sentence_id=str(ex["claim_id"])
        )
        
        res = engine.verify_claim(claim)
        
        # Baseline (Similarity only)
        # NLI + Sim
        # NLI + Sim + Num (Full)
        
        results.append({
            "claim_id": ex["claim_id"],
            "claim_text": ex["claim_text"],
            "expected_label": ex["label"],
            "predicted_label": res.verdict,
            "confidence": res.confidence,
            "semantic_similarity": res.semantic_similarity,
            "nli_result": res.nli_result.model_dump() if res.nli_result else {},
            "num_result": res.numerical_result.model_dump() if res.numerical_result else {},
            "warnings": res.warnings,
            "explanation": res.explanation
        })
        
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(RESULTS_DIR, "error_analysis.csv"), index=False)
    
    y_true = df["expected_label"].tolist()
    y_pred = df["predicted_label"].tolist()
    
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    print(f"Full System - F1: {f:.3f}, Precision: {p:.3f}, Recall: {r:.3f}")
    
    return results

def main():
    filepath = os.path.join(DATA_DIR, "train_normalized.jsonl")
    if not os.path.exists(filepath):
        print("Data not found, generating dummy...")
        with open(filepath, 'w') as f:
            f.write(json.dumps({"claim_id": 1, "claim_text": "Accuracy improved by 23%.", "evidence_text": "The model achieved an accuracy improvement of 23%.", "source_document": "doc1", "label": "SUPPORTED"}) + "\n")
            
    data = load_data(filepath)
    
    retrieval_models = ["all-MiniLM-L6-v2", "paraphrase-MiniLM-L3-v2"]
    # for m in retrieval_models:
    #     test_retrieval(data, m)
    # test_nli(data)
    build_baseline_and_ablation(data)
    print("Evaluation complete. Results saved to data/processed/error_analysis.csv")

if __name__ == "__main__":
    main()

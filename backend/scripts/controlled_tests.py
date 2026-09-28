import json
from app.verification.verification_engine import VerificationEngine
from app.verification.nli_verifier import NLIVerifier
from app.verification.numerical_checker import NumericalChecker
from app.retrieval.faiss_store import FaissStore
from app.schemas.document import ExtractedClaim

def run_tests():
    print("--- PART 12: NUMERICAL TEST CASES ---")
    checker = NumericalChecker()
    cases = [
        ("Accuracy improved by 23%.", "Accuracy improved by 23%.", "CONSISTENT"),
        ("Accuracy improved by 23%.", "Accuracy improved by 19%.", "DISCREPANCY"),
        ("Accuracy improved by 23%.", "Accuracy decreased by 23%.", "CONSISTENT"), # Numerical check just checks numbers, NLI will catch contradiction
        ("Accuracy improved by 23%.", "No accuracy information.", "DISCREPANCY")
    ]
    
    for claim, ev, expected in cases:
        res = checker.check_consistency(claim, ev)
        print(f"Claim: {claim}\nEvidence: {ev}\nStatus: {res['status']}")

    print("\n--- PART 13: CONTROLLED VERIFICATION TESTS ---")
    nli = NLIVerifier()
    engine = VerificationEngine(FaissStore(embedder=None), nli, checker)
    
    test_claims = [
        # Supported
        ("Model A achieved 90% accuracy.", "Model A achieved 90% accuracy.", "SUPPORTED"),
        ("The treatment reduced symptoms.", "Patients showed reduced symptoms after the treatment.", "SUPPORTED"),
        ("X is larger than Y.", "Y is smaller than X.", "SUPPORTED"),
        ("The new algorithm is twice as fast.", "The new algorithm is twice as fast.", "SUPPORTED"),
        ("Blood pressure decreased.", "There was a reduction in blood pressure.", "SUPPORTED"),
        # Contradicted
        ("Model A achieved 90% accuracy.", "Model A achieved 70% accuracy.", "CONTRADICTED"),
        ("The treatment increased symptoms.", "Patients showed reduced symptoms after the treatment.", "CONTRADICTED"),
        ("X is smaller than Y.", "Y is smaller than X.", "CONTRADICTED"),
        ("The new algorithm is slower.", "The new algorithm is twice as fast.", "CONTRADICTED"),
        ("Blood pressure increased.", "There was a reduction in blood pressure.", "CONTRADICTED"),
        # Insufficient Evidence
        ("Model A achieved 90% accuracy.", "Model A was evaluated.", "INSUFFICIENT_EVIDENCE"),
        ("The treatment reduced symptoms.", "The treatment was expensive.", "INSUFFICIENT_EVIDENCE"),
        ("X is larger than Y.", "X and Y are both red.", "INSUFFICIENT_EVIDENCE"),
        ("The new algorithm is twice as fast.", "The new algorithm was written in Python.", "INSUFFICIENT_EVIDENCE"),
        ("Blood pressure decreased.", "Heart rate was measured.", "INSUFFICIENT_EVIDENCE"),
    ]

    confusion_matrix = {"SUPPORTED": {"SUPPORTED": 0, "PARTIALLY_SUPPORTED": 0, "CONTRADICTED": 0, "INSUFFICIENT_EVIDENCE": 0, "SOURCE_UNAVAILABLE": 0},
                        "PARTIALLY_SUPPORTED": {"SUPPORTED": 0, "PARTIALLY_SUPPORTED": 0, "CONTRADICTED": 0, "INSUFFICIENT_EVIDENCE": 0, "SOURCE_UNAVAILABLE": 0},
                        "CONTRADICTED": {"SUPPORTED": 0, "PARTIALLY_SUPPORTED": 0, "CONTRADICTED": 0, "INSUFFICIENT_EVIDENCE": 0, "SOURCE_UNAVAILABLE": 0},
                        "INSUFFICIENT_EVIDENCE": {"SUPPORTED": 0, "PARTIALLY_SUPPORTED": 0, "CONTRADICTED": 0, "INSUFFICIENT_EVIDENCE": 0, "SOURCE_UNAVAILABLE": 0}}
                        
    for claim_text, ev_text, expected in test_claims:
        # Mock Faiss search for this specific claim
        engine.faiss_store.search = lambda q, top_k: [{"text": ev_text, "score": 0.9, "sentence_id": "test_ev"}]
        claim = ExtractedClaim(
            claim_id="test", text=claim_text, source_sentence_id="test_claim", linked_citations=[]
        )
        res = engine.verify_claim(claim)
        
        # If NLI says supported but numbers mismatch, engine downgrades to PARTIALLY_SUPPORTED or CONTRADICTED
        
        confusion_matrix[expected][res.verdict] += 1
        
        print(f"\nCLAIM: {claim_text}")
        print(f"EVIDENCE: {ev_text}")
        print(f"NLI: ENTAILMENT {res.nli_result.entailment:.2f}, NEUTRAL {res.nli_result.neutral:.2f}, CONTRADICTION {res.nli_result.contradiction:.2f}")
        print(f"FINAL: {res.verdict} (Expected: {expected})")
        
    print("\nConfusion Matrix:")
    for true_lbl, preds in confusion_matrix.items():
        print(f"True {true_lbl}: {preds}")

if __name__ == "__main__":
    run_tests()

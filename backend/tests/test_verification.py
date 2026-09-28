import sys
sys.path.append('d:/PROJECTS/VERICLAIM/backend')
from app.verification.numerical_checker import NumericalChecker
from app.verification.nli_verifier import NLIVerifier

def test_numerical_checker():
    nc = NumericalChecker()
    claim = "Model X improves accuracy by 23%."
    evidence1 = "Model X achieved an accuracy improvement of 23%."
    evidence2 = "Model X improved accuracy by 19%."
    
    res1 = nc.check_consistency(claim, evidence1)
    assert res1["status"] == "CONSISTENT"
    
    res2 = nc.check_consistency(claim, evidence2)
    assert res2["status"] == "DISCREPANCY"
    assert "23" in res2["missing_numbers"] or "23%" in res2["missing_numbers"]
    print("Numerical checker works.")

def test_nli_verifier():
    nli = NLIVerifier()
    claim = "It improves performance by 23%."
    evidence = "It improves performance by 19%."
    
    res = nli.verify(claim, evidence)
    assert res["label"] in ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT EVIDENCE"]
    print("NLI Verifier works.")

if __name__ == "__main__":
    test_numerical_checker()
    test_nli_verifier()
    print("All verification tests passed.")

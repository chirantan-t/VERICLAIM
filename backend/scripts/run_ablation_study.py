import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from experiments.dataset_loader import EvaluationDataset
from experiments.evaluator import PipelineEvaluator

def run_ablation():
    dataset = EvaluationDataset()
    
    print("="*50)
    print("VERICLAIM ABLATION STUDY")
    print("="*50)
    
    # Configuration 1: Full Pipeline
    print("\\n[Config 1] Full Pipeline (NLI + Numerical Consistency)")
    evaluator_full = PipelineEvaluator(use_numerical_check=True)
    metrics_full = evaluator_full.evaluate(dataset)
    print(f"Retrieval Accuracy : {metrics_full['retrieval_accuracy']:.2f}")
    print(f"Verdict Accuracy   : {metrics_full['verdict_accuracy']:.2f}")
    
    # Configuration 2: NLI Only (No Numerical Consistency Check)
    print("\\n[Config 2] NLI Only (Ablating Numerical Consistency)")
    evaluator_nli_only = PipelineEvaluator(use_numerical_check=False)
    metrics_nli_only = evaluator_nli_only.evaluate(dataset)
    print(f"Retrieval Accuracy : {metrics_nli_only['retrieval_accuracy']:.2f}")
    print(f"Verdict Accuracy   : {metrics_nli_only['verdict_accuracy']:.2f}")

    print("\\nConclusion:")
    diff = metrics_full['verdict_accuracy'] - metrics_nli_only['verdict_accuracy']
    if diff > 0:
        print(f"-> Numerical Consistency checker improved verdict accuracy by {diff*100:.1f}%.")
    elif diff < 0:
        print(f"-> Numerical Consistency checker decreased verdict accuracy by {abs(diff)*100:.1f}%.")
    else:
        print("-> No impact from Numerical Consistency checker on this dataset.")

if __name__ == "__main__":
    run_ablation()

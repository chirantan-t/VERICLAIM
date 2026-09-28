import json
import os
from typing import Dict, Any

def generate_ablation_report(results: Dict[str, Any], output_path: str):
    """
    Generates a markdown report for the ablation study.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# VeriClaim Ablation Study Results\n\n")
        
        for exp_name, metrics in results.items():
            f.write(f"## Experiment {exp_name}\n")
            f.write(f"**Runtime:** {metrics['runtime']:.2f} seconds\n\n")
            
            f.write("### Retrieval Metrics\n")
            for k, v in metrics["retrieval"].items():
                f.write(f"- **{k}**: {v:.4f}\n")
            f.write("\n")
            
            f.write("### Classification Metrics\n")
            for k, v in metrics["classification"].items():
                f.write(f"- **{k}**: {v:.4f}\n")
            f.write("\n")
            
            f.write("### Confusion Matrix\n")
            f.write("| True / Pred | SUPPORTED | CONTRADICTED | INSUFFICIENT_EVIDENCE |\n")
            f.write("|-------------|-----------|--------------|-----------------------|\n")
            cm = metrics["confusion_matrix"]
            labels = ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]
            for t in labels:
                row = [str(cm[t][p]) for p in labels]
                f.write(f"| **{t}** | {' | '.join(row)} |\n")
            f.write("\n---\n\n")

    print(f"Ablation report generated at {output_path}")

from typing import List, Dict, Any


def calculate_retrieval_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculates Recall@1, Recall@5, Recall@10.
    results expected: [{"ground_truth_doc_ids": [str], "retrieved_doc_ids": [str]}, ...]
    """
    metrics = {"Recall@1": 0.0, "Recall@5": 0.0, "Recall@10": 0.0}
    if not results:
        return metrics

    for res in results:
        gt = set(res["ground_truth_doc_ids"])
        retrieved = res["retrieved_doc_ids"]

        if any(doc in gt for doc in retrieved[:1]):
            metrics["Recall@1"] += 1
        if any(doc in gt for doc in retrieved[:5]):
            metrics["Recall@5"] += 1
        if any(doc in gt for doc in retrieved[:10]):
            metrics["Recall@10"] += 1

    total = len(results)
    return {k: v / total for k, v in metrics.items()}


def calculate_classification_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculates Accuracy, Macro Precision, Macro Recall, Macro F1.
    results expected: [{"true_label": str, "pred_label": str}, ...]
    Labels must be SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE
    """
    if not results:
        return {"Accuracy": 0.0, "Macro Precision": 0.0, "Macro Recall": 0.0, "Macro F1": 0.0}

    correct = sum(1 for r in results if r["true_label"] == r["pred_label"])
    accuracy = correct / len(results)

    labels = ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]
    precision = {}
    recall = {}

    for label in labels:
        tp = sum(1 for r in results if r["pred_label"] == label and r["true_label"] == label)
        fp = sum(1 for r in results if r["pred_label"] == label and r["true_label"] != label)
        fn = sum(1 for r in results if r["pred_label"] != label and r["true_label"] == label)

        precision[label] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall[label] = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    macro_precision = sum(precision.values()) / len(labels)
    macro_recall = sum(recall.values()) / len(labels)
    
    if macro_precision + macro_recall > 0:
        macro_f1 = 2 * (macro_precision * macro_recall) / (macro_precision + macro_recall)
    else:
        macro_f1 = 0.0

    return {
        "Accuracy": accuracy,
        "Macro Precision": macro_precision,
        "Macro Recall": macro_recall,
        "Macro F1": macro_f1
    }

def generate_confusion_matrix(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    labels = ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]
    matrix = {true_lbl: {pred_lbl: 0 for pred_lbl in labels} for true_lbl in labels}
    
    for r in results:
        t = r["true_label"]
        p = r["pred_label"]
        if t in matrix and p in matrix[t]:
            matrix[t][p] += 1
            
    return matrix

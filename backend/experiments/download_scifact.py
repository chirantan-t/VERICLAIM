import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

print("Generating synthetic SciFact dataset for testing...")

corpus = [
    {
        "doc_id": "1",
        "title": "Vitamin C and Colds",
        "abstract": ["Vitamin C supplementation does not reduce the incidence of colds.", "However, it reduces duration by 8% in adults."],
        "structured": False
    },
    {
        "doc_id": "2",
        "title": "Blue light and sleep",
        "abstract": ["Exposure to blue light before bed improves sleep quality.", "This is due to melatonin stimulation."],
        "structured": False
    }
]

claims = [
    {
        "id": 1,
        "claim": "Vitamin C reduces the incidence of colds.",
        "evidence": {"1": [{"label": "CONTRADICT", "sentences": [0]}]},
        "cited_doc_ids": [1]
    },
    {
        "id": 2,
        "claim": "Blue light before bed improves sleep.",
        "evidence": {"2": [{"label": "SUPPORT", "sentences": [0]}]},
        "cited_doc_ids": [2]
    }
]

corpus_path = os.path.join(DATA_DIR, "corpus.jsonl")
with open(corpus_path, "w", encoding="utf-8") as f:
    for doc in corpus:
        f.write(json.dumps(doc) + "\n")

dev_path = os.path.join(DATA_DIR, "claims_dev.jsonl")
with open(dev_path, "w", encoding="utf-8") as f:
    for claim in claims:
        f.write(json.dumps(claim) + "\n")

print("Synthetic dataset generated.")

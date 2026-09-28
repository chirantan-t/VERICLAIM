import json
import os
from typing import List, Dict, Any

class SciFactDataset:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.corpus = {}
        self.claims_train = []
        self.claims_dev = []

    def load(self):
        corpus_path = os.path.join(self.data_dir, "corpus.jsonl")
        if not os.path.exists(corpus_path):
            raise FileNotFoundError(f"SciFact corpus not found at {corpus_path}. Please run download_scifact.py.")

        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                doc = json.loads(line)
                self.corpus[str(doc["doc_id"])] = doc

        train_path = os.path.join(self.data_dir, "claims_train.jsonl")
        if os.path.exists(train_path):
            with open(train_path, "r", encoding="utf-8") as f:
                self.claims_train = [json.loads(line) for line in f]

        dev_path = os.path.join(self.data_dir, "claims_dev.jsonl")
        if os.path.exists(dev_path):
            with open(dev_path, "r", encoding="utf-8") as f:
                self.claims_dev = [json.loads(line) for line in f]

    def get_dev_claims(self) -> List[Dict[str, Any]]:
        return self.claims_dev

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        return self.corpus.get(str(doc_id))

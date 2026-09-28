import json
import os
import urllib.request
import urllib.error

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/scifact"))
os.makedirs(DATA_DIR, exist_ok=True)

GITHUB_URL_BASE = "https://raw.githubusercontent.com/allenai/scifact/master/data"

def download_file(filename):
    url = f"{GITHUB_URL_BASE}/{filename}"
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
    return filepath

def map_label(label: str) -> str:
    if label == "SUPPORT":
        return "SUPPORTED"
    elif label == "CONTRADICT":
        return "CONTRADICTED"
    else:
        return "INSUFFICIENT_EVIDENCE"

def process():
    corpus_file = download_file("corpus.jsonl")
    train_file = download_file("claims_train.jsonl")
    dev_file = download_file("claims_dev.jsonl")

    corpus_dict = {}
    with open(corpus_file, 'r', encoding='utf-8') as f:
        for line in f:
            doc = json.loads(line)
            corpus_dict[str(doc["doc_id"])] = doc

    for split, in_file in [("train", train_file), ("dev", dev_file)]:
        out_file = os.path.join(DATA_DIR, f"{split}_normalized.jsonl")
        
        with open(in_file, 'r', encoding='utf-8') as f:
            claims = [json.loads(line) for line in f]
            
        normalized = []
        for c in claims:
            claim_id = c.get("id")
            claim_text = c.get("claim")
            evidence = c.get("evidence", {})
            cited_doc_ids = c.get("cited_doc_ids", [])
            
            if not evidence:
                # Add insufficient evidence example
                for doc_id in cited_doc_ids:
                    if str(doc_id) in corpus_dict:
                        normalized.append({
                            "claim_id": claim_id,
                            "claim_text": claim_text,
                            "evidence_text": " ".join(corpus_dict[str(doc_id)]["sentences"]),
                            "source_document": str(doc_id),
                            "label": "INSUFFICIENT_EVIDENCE",
                            "rationale": [],
                            "metadata": {"original_label": "NOT_ENOUGH_INFO"}
                        })
                continue
                
            for doc_id, doc_evidence in evidence.items():
                if str(doc_id) not in corpus_dict:
                    continue
                
                doc_info = corpus_dict[str(doc_id)]
                doc_sentences = doc_info["sentences"]
                
                for ev in doc_evidence:
                    label = ev["label"]
                    sentences_idxs = ev["sentences"]
                    
                    rationale_texts = [doc_sentences[i] for i in sentences_idxs]
                    rationale_text = " ".join(rationale_texts)
                    
                    normalized.append({
                        "claim_id": claim_id,
                        "claim_text": claim_text,
                        "evidence_text": rationale_text,
                        "source_document": str(doc_id),
                        "label": map_label(label),
                        "rationale": rationale_texts,
                        "metadata": {"original_label": label, "sentence_idxs": sentences_idxs}
                    })
        
        with open(out_file, 'w', encoding='utf-8') as f:
            for n in normalized:
                f.write(json.dumps(n) + "\n")
        print(f"Normalized {len(normalized)} examples to {out_file}")

if __name__ == "__main__":
    process()

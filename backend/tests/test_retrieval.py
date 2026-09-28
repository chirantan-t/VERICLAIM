import sys
sys.path.append('d:/PROJECTS/VERICLAIM/backend')
from app.retrieval.embedder import Embedder
from app.retrieval.faiss_store import FaissStore

def test_embedder():
    embedder = Embedder()
    emb = embedder.embed("This is a test sentence.")
    assert emb.shape[1] == 384
    print("Embedder works.")

def test_faiss_store():
    embedder = Embedder()
    store = FaissStore(embedder)
    
    texts = [
        "The model achieves 95% accuracy on MNIST.",
        "A baseline model only gets 80% accuracy.",
        "Deep learning is a subset of machine learning."
    ]
    metadata = [
        {"doc_id": "doc1", "sentence_id": "s1"},
        {"doc_id": "doc1", "sentence_id": "s2"},
        {"doc_id": "doc1", "sentence_id": "s3"}
    ]
    
    store.add_texts(texts, metadata)
    assert store.index.ntotal == 3
    
    results = store.search("How accurate is the model?", top_k=1)
    print("Search results:", results)
    assert len(results) == 1
    assert "95%" in results[0]["text"]
    print("FaissStore works.")

if __name__ == "__main__":
    test_embedder()
    test_faiss_store()
    print("All retrieval tests passed.")

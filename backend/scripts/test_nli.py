from transformers import pipeline

model = pipeline("text-classification", model="cross-encoder/nli-deberta-v3-small", top_k=None)
print("Labels:", model.model.config.id2label)
print("Result:", model({"text": "Model A achieved 90% accuracy.", "text_pair": "Model A achieved 90% accuracy."}))

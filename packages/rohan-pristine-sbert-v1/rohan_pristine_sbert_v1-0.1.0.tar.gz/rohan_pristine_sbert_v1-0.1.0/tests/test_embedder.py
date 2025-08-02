from rohan_pristine_sbert_v1 import HybridSentenceTransformer

model = HybridSentenceTransformer()
embeddings = model.encode(["This is a sample sentence."])
print(embeddings.shape)

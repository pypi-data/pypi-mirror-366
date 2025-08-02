# rohan_pristine_sbert_v1/embedder.py

from sentence_transformers import SentenceTransformer
import numpy as np

class HybridSentenceTransformer:
    def __init__(self):
        self.model1 = SentenceTransformer('all-MiniLM-L6-v2')    # 384D
        self.model2 = SentenceTransformer('all-mpnet-base-v2')   # 768D

    def encode(self, sentences, normalize=True):
        emb1 = self.model1.encode(sentences, normalize_embeddings=normalize)
        emb2 = self.model2.encode(sentences, normalize_embeddings=normalize)

        # Truncate MPNet embeddings to 384D
        emb2 = emb2[:, :384]

        return (emb1 + emb2) / 2

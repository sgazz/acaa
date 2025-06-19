from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json
import os

class RAGService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.initialize_index()

    def initialize_index(self):
        """Inicijalizuje FAISS indeks za brzu pretragu"""
        dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(dimension)

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Dodaje dokumente u indeks"""
        texts = [doc["content"] for doc in documents]
        embeddings = self.model.encode(texts)
        
        if self.index.ntotal == 0:
            self.index.add(embeddings)
        else:
            self.index.add(embeddings)
        
        self.documents.extend(documents)

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Pretražuje dokumente na osnovu upita"""
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                # Konvertujemo distance u score (manja distance = veći score)
                # FAISS koristi L2 distance, pa konvertujemo u similarity score
                max_distance = np.max(distances[0]) if len(distances[0]) > 0 else 1.0
                distance = distances[0][i]
                score = 1.0 - (distance / max_distance) if max_distance > 0 else 0.0
                
                result = self.documents[idx].copy()
                result["score"] = float(score)
                results.append(result)
        
        return results

    def save_index(self, path: str):
        """Čuva indeks i dokumente na disk"""
        if not os.path.exists(path):
            os.makedirs(path)
        
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "documents.json"), "w") as f:
            json.dump(self.documents, f)

    def load_index(self, path: str):
        """Učitava indeks i dokumente sa diska"""
        self.index = faiss.read_index(os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "documents.json"), "r") as f:
            self.documents = json.load(f) 
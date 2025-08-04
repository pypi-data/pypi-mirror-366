from typing import List, Dict, Any
from ..models import BaseRAG
import numpy as np
from numpy.linalg import norm

class VectorStore:
    """Simple in-memory vector store for demo purposes"""
    
    def __init__(self):
        self.vectors = []
        self.documents = []
        
    def add(self, vector: List[float], document: str):
        self.vectors.append(vector)
        self.documents.append(document)
        
    def search(self, query_vector: List[float], k: int = 3) -> List[Dict[str, Any]]:
        """Return top k most similar documents"""
        if not self.vectors:
            return []
            
        # Calculate cosine similarities
        similarities = [
            np.dot(query_vector, vec) / (norm(query_vector) * norm(vec))
            for vec in self.vectors
        ]
        
        # Get top k results
        indices = np.argsort(similarities)[-k:][::-1]
        return [
            {"document": self.documents[i], "score": similarities[i]}
            for i in indices
        ]

class SimpleRAG(BaseRAG):
    """Basic RAG implementation using in-memory vector store"""
    
    def __init__(self, embedding_fn, llm):
        self.vector_store = VectorStore()
        self.embedding_fn = embedding_fn
        self.llm = llm
        
    def retrieve(self, query: str, **kwargs):
        query_vec = self.embedding_fn(query)
        return self.vector_store.search(query_vec, **kwargs)
        
    def generate(self, query: str, context: str, **kwargs):
        prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
        return self.llm.generate(prompt, **kwargs)
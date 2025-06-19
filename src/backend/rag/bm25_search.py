from typing import List, Dict, Any
import math
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class BM25Search:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Inicijalizuje BM25 search servis
        
        Args:
            k1: Parametar za kontrolu frekvencije terma (default: 1.5)
            b: Parametar za kontrolu dužine dokumenta (default: 0.75)
        """
        self.k1 = k1
        self.b = b
        self.documents = []
        self.avg_doc_length = 0
        self.idf = {}
        self.doc_freq = Counter()
        self.total_docs = 0
        
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Dodaje dokumente u BM25 indeks"""
        logger.info(f"Dodajem {len(documents)} dokumenata u BM25 indeks")
        
        # Čuvamo dokumente
        self.documents = documents
        self.total_docs = len(documents)
        
        # Računamo IDF za sve termine
        self._calculate_idf()
        
        # Računamo prosečnu dužinu dokumenta
        total_length = sum(len(self._tokenize(doc["content"])) for doc in documents)
        self.avg_doc_length = total_length / self.total_docs if self.total_docs > 0 else 0
        
        logger.info(f"BM25 indeks kreiran. Prosečna dužina dokumenta: {self.avg_doc_length:.2f}")
        
    def _tokenize(self, text: str) -> List[str]:
        """Tokenizuje tekst u reči"""
        # Konvertujemo u lowercase i uklanjamo specijalne karaktere
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Delimo na reči i uklanjamo prazne stringove
        tokens = [word for word in text.split() if word.strip()]
        return tokens
        
    def _calculate_idf(self):
        """Računa IDF (Inverse Document Frequency) za sve termine"""
        # Brojimo u koliko dokumenata se pojavljuje svaki termin
        for doc in self.documents:
            tokens = set(self._tokenize(doc["content"]))  # Koristimo set da izbegnemo duplikate
            for token in tokens:
                self.doc_freq[token] += 1
        
        # Računamo IDF za svaki termin
        for term, freq in self.doc_freq.items():
            self.idf[term] = math.log((self.total_docs - freq + 0.5) / (freq + 0.5))
            
        logger.info(f"IDF izračunat za {len(self.idf)} terma")
        
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Pretražuje dokumente koristeći BM25 algoritam"""
        if not self.documents:
            return []
            
        query_tokens = self._tokenize(query)
        scores = []
        
        for doc_idx, doc in enumerate(self.documents):
            doc_tokens = self._tokenize(doc["content"])
            doc_length = len(doc_tokens)
            
            score = 0
            for term in query_tokens:
                if term in self.idf:
                    # Brojimo frekvenciju terma u dokumentu
                    term_freq = doc_tokens.count(term)
                    
                    # Računamo BM25 score za ovaj termin
                    numerator = term_freq * (self.k1 + 1)
                    denominator = term_freq + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
                    
                    if denominator > 0:
                        score += self.idf[term] * (numerator / denominator)
            
            if score > 0:
                scores.append((score, doc_idx))
        
        # Sortiramo po score-u (opadajuće)
        scores.sort(reverse=True)
        
        # Vraćamo top-k rezultata
        results = []
        for score, doc_idx in scores[:k]:
            result = self.documents[doc_idx].copy()
            result["score"] = float(score)
            results.append(result)
            
        return results 
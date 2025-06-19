from typing import List, Dict, Any, Tuple
import numpy as np
from .bm25_search import BM25Search
import logging

logger = logging.getLogger(__name__)

class HybridSearch:
    def __init__(self, semantic_weight: float = 0.7, lexical_weight: float = 0.3):
        """
        Inicijalizuje Hybrid Search servis
        
        Args:
            semantic_weight: Težina semantičke pretrage (FAISS) - default 0.7
            lexical_weight: Težina leksičke pretrage (BM25) - default 0.3
        """
        self.semantic_weight = semantic_weight
        self.lexical_weight = lexical_weight
        self.bm25_search = BM25Search()
        self.documents = []
        
        # Proveravamo da li su težine validne
        if abs(semantic_weight + lexical_weight - 1.0) > 0.01:
            logger.warning(f"Težine ne sumiraju na 1.0: semantic={semantic_weight}, lexical={lexical_weight}")
            
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Dodaje dokumente u oba indeksa"""
        logger.info(f"Dodajem {len(documents)} dokumenata u hybrid indeks")
        
        self.documents = documents
        
        # Dodajemo dokumente u BM25 indeks
        self.bm25_search.add_documents(documents)
        
        logger.info("Hybrid indeks uspešno kreiran")
        
    def search(self, query: str, query_embedding: np.ndarray, 
               faiss_index, k: int = 5) -> List[Dict[str, Any]]:
        """
        Izvršava hybrid pretragu kombinujući FAISS i BM25
        
        Args:
            query: Tekstualni upit
            query_embedding: Embedding vektor upita
            faiss_index: FAISS indeks za semantičku pretragu
            k: Broj rezultata za vraćanje
            
        Returns:
            Lista rezultata sa kombinovanim score-ovima
        """
        logger.info(f"Izvršavam hybrid pretragu za upit: '{query}'")
        
        # 1. Semantička pretraga (FAISS)
        semantic_results = self._semantic_search(query_embedding, faiss_index, k * 2)
        logger.info(f"FAISS pronašao {len(semantic_results)} rezultata")
        
        # 2. Leksička pretraga (BM25)
        lexical_results = self.bm25_search.search(query, k * 2)
        logger.info(f"BM25 pronašao {len(lexical_results)} rezultata")
        
        # 3. Kombinujemo rezultate
        combined_results = self._combine_results(semantic_results, lexical_results, k)
        
        logger.info(f"Hybrid pretraga završena. Vraćam {len(combined_results)} rezultata")
        return combined_results
        
    def _semantic_search(self, query_embedding: np.ndarray, faiss_index, k: int) -> List[Dict[str, Any]]:
        """Izvršava semantičku pretragu koristeći FAISS"""
        try:
            # Normalizujemo embedding
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            # Pretražujemo FAISS indeks
            scores, indices = faiss_index.search(query_embedding, k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.documents):
                    result = self.documents[idx].copy()
                    result["semantic_score"] = float(score)
                    result["index"] = int(idx)
                    results.append(result)
                    
            return results
            
        except Exception as e:
            logger.error(f"Greška u semantičkoj pretrazi: {e}")
            return []
            
    def _combine_results(self, semantic_results: List[Dict], 
                        lexical_results: List[Dict], k: int) -> List[Dict[str, Any]]:
        """Kombinuje rezultate iz oba indeksa"""
        
        # Kreiramo mapu za brzu pretragu
        combined_map = {}
        
        # Dodajemo semantičke rezultate
        for result in semantic_results:
            doc_id = result.get("id") or result.get("index")
            if doc_id not in combined_map:
                combined_map[doc_id] = {
                    "document": result,
                    "semantic_score": result.get("semantic_score", 0),
                    "lexical_score": 0,
                    "combined_score": 0
                }
        
        # Dodajemo leksičke rezultate
        for result in lexical_results:
            doc_id = result.get("id") or result.get("index")
            if doc_id not in combined_map:
                combined_map[doc_id] = {
                    "document": result,
                    "semantic_score": 0,
                    "lexical_score": result.get("score", 0),
                    "combined_score": 0
                }
            else:
                combined_map[doc_id]["lexical_score"] = result.get("score", 0)
        
        # Normalizujemo score-ove
        semantic_scores = [item["semantic_score"] for item in combined_map.values()]
        lexical_scores = [item["lexical_score"] for item in combined_map.values()]
        
        max_semantic = max(semantic_scores) if semantic_scores else 1
        max_lexical = max(lexical_scores) if lexical_scores else 1
        
        # Računamo kombinovane score-ove
        for item in combined_map.values():
            normalized_semantic = item["semantic_score"] / max_semantic if max_semantic > 0 else 0
            normalized_lexical = item["lexical_score"] / max_lexical if max_lexical > 0 else 0
            
            item["combined_score"] = (
                self.semantic_weight * normalized_semantic + 
                self.lexical_weight * normalized_lexical
            )
        
        # Sortiramo po kombinovanom score-u
        sorted_items = sorted(combined_map.values(), 
                            key=lambda x: x["combined_score"], reverse=True)
        
        # Vraćamo top-k rezultata
        final_results = []
        for item in sorted_items[:k]:
            result = item["document"].copy()
            result["semantic_score"] = item["semantic_score"]
            result["lexical_score"] = item["lexical_score"]
            result["combined_score"] = item["combined_score"]
            result["score"] = item["combined_score"]  # Glavni score za kompatibilnost
            final_results.append(result)
            
        return final_results 
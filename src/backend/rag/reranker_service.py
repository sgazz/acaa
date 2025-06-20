from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
import logging

logger = logging.getLogger(__name__)

class RerankerService:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """
        Inicijalizuje Reranker servis
        
        Args:
            model_name: Naziv reranking modela (default: BAAI/bge-reranker-base)
        """
        logger.info(f"Učitavam reranking model: {model_name}")
        try:
            self.model = CrossEncoder(model_name)
            logger.info(f"Reranking model uspešno učitan: {model_name}")
        except Exception as e:
            logger.error(f"Greška pri učitavanju reranking modela: {e}")
            raise
    
    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerankuje dokumente na osnovu upita
        
        Args:
            query: Tekstualni upit
            documents: Lista dokumenata za reranking
            top_k: Broj najboljih rezultata za vraćanje
            
        Returns:
            Lista rerankovanih dokumenata sa rerank_score-om
        """
        if not documents:
            logger.warning("Nema dokumenata za reranking")
            return []
        
        logger.info(f"Rerankujem {len(documents)} dokumenata za upit: '{query}'")
        
        try:
            # Kreiramo parove (query, document_content) za reranking
            pairs = []
            for doc in documents:
                content = doc.get("content", "")
                if content.strip():  # Proveravamo da li sadržaj nije prazan
                    pairs.append([query, content])
                else:
                    logger.warning(f"Dokument sa praznim sadržajem: {doc.get('metadata', {}).get('source', 'Unknown')}")
            
            if not pairs:
                logger.warning("Nema validnih parova za reranking")
                return []
            
            # Izvršavamo reranking
            scores = self.model.predict(pairs)
            
            # Kombinujemo dokumente sa score-ovima
            doc_score_pairs = []
            pair_idx = 0
            
            for doc in documents:
                content = doc.get("content", "")
                if content.strip():
                    score = float(scores[pair_idx])
                    doc_score_pairs.append((doc, score))
                    pair_idx += 1
                else:
                    # Dokumenti sa praznim sadržajem dobijaju najniži score
                    doc_score_pairs.append((doc, 0.0))
            
            # Sortiramo po score-u (opadajuće)
            doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
            
            # Vraćamo top-k rezultata
            results = []
            for doc, score in doc_score_pairs[:top_k]:
                result = doc.copy()
                result["rerank_score"] = score
                results.append(result)
            
            logger.info(f"Reranking završen. Top score: {results[0]['rerank_score']:.4f} ako ima rezultata")
            return results
            
        except Exception as e:
            logger.error(f"Greška u reranking-u: {e}")
            # Fallback: vraćamo originalne dokumente bez reranking-a
            logger.info("Koristim fallback - vraćam originalne dokumente")
            return documents[:top_k]
    
    def rerank_with_metadata(self, query: str, documents: List[Dict[str, Any]], 
                           top_k: int = 5) -> Dict[str, Any]:
        """
        Rerankuje dokumente i vraća detaljne informacije
        
        Args:
            query: Tekstualni upit
            documents: Lista dokumenata za reranking
            top_k: Broj najboljih rezultata za vraćanje
            
        Returns:
            Dictionary sa rerankovanim rezultatima i statistikama
        """
        reranked_docs = self.rerank(query, documents, top_k)
        
        # Računamo statistike
        scores = [doc.get("rerank_score", 0) for doc in reranked_docs]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        return {
            "results": reranked_docs,
            "statistics": {
                "total_documents": len(documents),
                "reranked_documents": len(reranked_docs),
                "average_score": round(avg_score, 4),
                "max_score": round(max_score, 4),
                "min_score": round(min_score, 4),
                "score_range": round(max_score - min_score, 4)
            }
        } 
from typing import List, Dict, Any
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

class ContextOptimizer:
    def __init__(self, max_tokens: int = 4000, max_chunks: int = 10):
        """
        Inicijalizuje Context Optimizer servis
        
        Args:
            max_tokens: Maksimalan broj tokena za kontekst
            max_chunks: Maksimalan broj chunk-ova za kontekst
        """
        self.max_tokens = max_tokens
        self.max_chunks = max_chunks
        logger.info(f"Context Optimizer inicijalizovan (max_tokens: {max_tokens}, max_chunks: {max_chunks})")
    
    def optimize_context(self, documents: List[Dict[str, Any]], query: str, 
                        optimization_type: str = "smart") -> Dict[str, Any]:
        """
        Optimizuje kontekst na osnovu upita i dokumenata
        
        Args:
            documents: Lista dokumenata sa score-ovima
            query: Originalni upit
            optimization_type: Tip optimizacije ("smart", "score_based", "length_based")
            
        Returns:
            Dictionary sa optimizovanim kontekstom i metapodacima
        """
        logger.info(f"Optimizujem kontekst za upit: '{query}' (tip: {optimization_type})")
        
        if not documents:
            return self._empty_context_result()
        
        # Filtriramo i sortiramo dokumente
        filtered_docs = self._filter_documents(documents)
        
        if optimization_type == "smart":
            optimized_docs = self._smart_optimization(filtered_docs, query)
        elif optimization_type == "score_based":
            optimized_docs = self._score_based_optimization(filtered_docs)
        elif optimization_type == "length_based":
            optimized_docs = self._length_based_optimization(filtered_docs)
        else:
            optimized_docs = filtered_docs[:self.max_chunks]
        
        # Strukturiramo kontekst
        structured_context = self._structure_context(optimized_docs, query)
        
        # Dodajemo metapodatke
        context_with_metadata = self._add_context_metadata(
            structured_context, optimized_docs, query, optimization_type
        )
        
        logger.info(f"Optimizacija završena. Dokumenti: {len(documents)} -> {len(optimized_docs)}")
        return context_with_metadata
    
    def _filter_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtrira dokumente na osnovu score-a"""
        # Uklanjamo dokumente sa niskim score-om
        min_score = 0.01
        filtered = [doc for doc in documents if doc.get("rerank_score", doc.get("combined_score", doc.get("score", 0))) > min_score]
        
        # Sortiramo po score-u (opadajuće)
        filtered.sort(key=lambda x: x.get("rerank_score", x.get("combined_score", x.get("score", 0))), reverse=True)
        
        return filtered
    
    def _smart_optimization(self, documents: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Pametna optimizacija koja kombinuje score, dužinu i relevantnost"""
        if not documents:
            return []
        
        query_tokens = self._tokenize(query.lower())
        optimized_docs = []
        total_tokens = 0
        
        for doc in documents:
            # Računamo relevantnost na osnovu preklapanja terma
            content_tokens = self._tokenize(doc.get("content", "").lower())
            relevance_score = self._calculate_relevance(query_tokens, content_tokens)
            
            # Kombinujemo score sa relevantnošću
            base_score = doc.get("rerank_score", doc.get("combined_score", doc.get("score", 0)))
            combined_score = base_score * (1 + relevance_score * 0.5)
            
            # Dodajemo dokument sa novim score-om
            doc_copy = doc.copy()
            doc_copy["optimized_score"] = combined_score
            doc_copy["relevance_score"] = relevance_score
            
            # Proveravamo da li možemo dodati ovaj dokument
            doc_tokens = len(doc.get("content", "").split())
            if total_tokens + doc_tokens <= self.max_tokens and len(optimized_docs) < self.max_chunks:
                optimized_docs.append(doc_copy)
                total_tokens += doc_tokens
            else:
                break
        
        # Sortiramo po optimizovanom score-u
        optimized_docs.sort(key=lambda x: x.get("optimized_score", 0), reverse=True)
        
        return optimized_docs
    
    def _score_based_optimization(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimizacija na osnovu score-a"""
        return documents[:self.max_chunks]
    
    def _length_based_optimization(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimizacija na osnovu dužine sadržaja"""
        optimized_docs = []
        total_tokens = 0
        
        for doc in documents:
            doc_tokens = len(doc.get("content", "").split())
            if total_tokens + doc_tokens <= self.max_tokens and len(optimized_docs) < self.max_chunks:
                optimized_docs.append(doc)
                total_tokens += doc_tokens
            else:
                break
        
        return optimized_docs
    
    def _structure_context(self, documents: List[Dict[str, Any]], query: str) -> str:
        """Strukturiše kontekst u čitljiv format"""
        if not documents:
            return ""
        
        context_parts = []
        
        # Dodajemo header sa upitom
        context_parts.append(f"UPIT: {query}")
        context_parts.append("=" * 50)
        
        # Dodajemo dokumente sa metadata
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            source = doc.get("metadata", {}).get("source", "Unknown")
            score = doc.get("rerank_score", doc.get("combined_score", doc.get("score", 0)))
            
            # Formatiranje dokumenta
            doc_header = f"\nDOKUMENT {i}: {source} (Score: {score:.3f})"
            doc_content = f"{content}\n"
            
            context_parts.append(doc_header)
            context_parts.append("-" * 30)
            context_parts.append(doc_content)
        
        return "\n".join(context_parts)
    
    def _add_context_metadata(self, context: str, documents: List[Dict[str, Any]], 
                             query: str, optimization_type: str) -> Dict[str, Any]:
        """Dodaje metapodatke o kontekstu"""
        
        # Računamo statistike
        total_tokens = len(context.split())
        avg_score = sum(doc.get("rerank_score", doc.get("combined_score", doc.get("score", 0))) for doc in documents) / len(documents) if documents else 0
        max_score = max(doc.get("rerank_score", doc.get("combined_score", doc.get("score", 0))) for doc in documents) if documents else 0
        
        # Analiziramo izvore
        sources = []
        for doc in documents:
            source_info = {
                "filename": doc.get("metadata", {}).get("source", "Unknown"),
                "page": doc.get("metadata", {}).get("page", 0),
                "score": doc.get("rerank_score", doc.get("combined_score", doc.get("score", 0))),
                "content_preview": doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", "")
            }
            sources.append(source_info)
        
        return {
            "context": context,
            "metadata": {
                "query": query,
                "optimization_type": optimization_type,
                "total_documents": len(documents),
                "total_tokens": total_tokens,
                "average_score": round(avg_score, 4),
                "max_score": round(max_score, 4),
                "sources": sources,
                "context_length": len(context),
                "utilization_percentage": round((total_tokens / self.max_tokens) * 100, 2) if self.max_tokens > 0 else 0
            }
        }
    
    def _calculate_relevance(self, query_tokens: List[str], content_tokens: List[str]) -> float:
        """Računa relevantnost na osnovu preklapanja terma"""
        if not query_tokens or not content_tokens:
            return 0.0
        
        # Brojimo preklapanja
        matches = sum(1 for token in query_tokens if token in content_tokens)
        
        # Računamo relevantnost kao procenat preklapanja
        relevance = matches / len(query_tokens)
        
        return relevance
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenizuje tekst u reči"""
        # Konvertujemo u lowercase i uklanjamo specijalne karaktere
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Delimo na reči i uklanjamo prazne stringove
        tokens = [word for word in text.split() if word.strip()]
        return tokens
    
    def _empty_context_result(self) -> Dict[str, Any]:
        """Vraća prazan rezultat konteksta"""
        return {
            "context": "",
            "metadata": {
                "query": "",
                "optimization_type": "none",
                "total_documents": 0,
                "total_tokens": 0,
                "average_score": 0.0,
                "max_score": 0.0,
                "sources": [],
                "context_length": 0,
                "utilization_percentage": 0.0
            }
        } 
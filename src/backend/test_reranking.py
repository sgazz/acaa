#!/usr/bin/env python3
"""
Test skripta za proveru reranking funkcionalnosti
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from rag.reranker_service import RerankerService
from rag.rag_service import RAGService
from rag.hybrid_search import HybridSearch
import logging

# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_reranking():
    """Testira reranking funkcionalnost"""
    
    # Test dokumenti
    test_documents = [
        {
            "content": "Python je programski jezik visokog nivoa koji se koristi za web development, data science i AI.",
            "metadata": {"source": "python_intro.txt", "type": "txt"}
        },
        {
            "content": "JavaScript je programski jezik koji se koristi za frontend web development i Node.js backend.",
            "metadata": {"source": "javascript_intro.txt", "type": "txt"}
        },
        {
            "content": "Machine Learning je grana AI koja omogućava računarima da uče iz podataka bez eksplicitnog programiranja.",
            "metadata": {"source": "ml_intro.txt", "type": "txt"}
        },
        {
            "content": "React je JavaScript biblioteka za kreiranje korisničkih interfejsa, razvijena od strane Facebook-a.",
            "metadata": {"source": "react_intro.txt", "type": "txt"}
        },
        {
            "content": "Docker je platforma za kontejnerizaciju aplikacija koja omogućava lakše deployment i skaliranje.",
            "metadata": {"source": "docker_intro.txt", "type": "txt"}
        }
    ]
    
    # Test upiti
    test_queries = [
        "Python programiranje",
        "Web development",
        "Machine learning i AI",
        "JavaScript framework",
        "Kontejnerizacija aplikacija"
    ]
    
    try:
        # Inicijalizujemo reranker
        logger.info("Inicijalizujem reranker...")
        reranker = RerankerService()
        
        # Testiramo reranking za svaki upit
        for query in test_queries:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testiram upit: '{query}'")
            logger.info(f"{'='*50}")
            
            # Izvršavamo reranking
            reranked_results = reranker.rerank_with_metadata(query, test_documents, top_k=3)
            
            # Prikazujemo rezultate
            logger.info(f"Statistike:")
            stats = reranked_results["statistics"]
            logger.info(f"  - Ukupno dokumenata: {stats['total_documents']}")
            logger.info(f"  - Rerankovano dokumenata: {stats['reranked_documents']}")
            logger.info(f"  - Prosečan score: {stats['average_score']}")
            logger.info(f"  - Najbolji score: {stats['max_score']}")
            logger.info(f"  - Najgori score: {stats['min_score']}")
            logger.info(f"  - Raspon score-ova: {stats['score_range']}")
            
            logger.info(f"\nTop 3 rezultata:")
            for i, result in enumerate(reranked_results["results"]):
                score = result.get("rerank_score", 0)
                source = result.get("metadata", {}).get("source", "Unknown")
                content_preview = result.get("content", "")[:100] + "..."
                logger.info(f"  {i+1}. Score: {score:.4f} | Source: {source}")
                logger.info(f"     Content: {content_preview}")
        
        logger.info(f"\n{'='*50}")
        logger.info("Svi testovi uspešno završeni!")
        logger.info(f"{'='*50}")
        
    except Exception as e:
        logger.error(f"Greška u testiranju: {e}")
        raise

def test_hybrid_with_reranking():
    """Testira hybrid search sa reranking-om"""
    
    try:
        # Inicijalizujemo servise
        logger.info("Inicijalizujem servise...")
        rag_service = RAGService()
        hybrid_search = HybridSearch()
        reranker = RerankerService()
        
        # Test dokumenti
        test_documents = [
            {
                "content": "Python je programski jezik visokog nivoa koji se koristi za web development, data science i AI.",
                "metadata": {"source": "python_intro.txt", "type": "txt"}
            },
            {
                "content": "JavaScript je programski jezik koji se koristi za frontend web development i Node.js backend.",
                "metadata": {"source": "javascript_intro.txt", "type": "txt"}
            },
            {
                "content": "Machine Learning je grana AI koja omogućava računarima da uče iz podataka bez eksplicitnog programiranja.",
                "metadata": {"source": "ml_intro.txt", "type": "txt"}
            }
        ]
        
        # Dodajemo dokumente u indekse
        logger.info("Dodajem test dokumente u indekse...")
        rag_service.add_documents(test_documents)
        hybrid_search.add_documents(test_documents)
        
        # Test upit
        query = "Python programiranje"
        logger.info(f"\nTestiram hybrid search + reranking za upit: '{query}'")
        
        # Hybrid search
        query_embedding = rag_service.model.encode([query])[0]
        hybrid_results = hybrid_search.search(query, query_embedding, rag_service.index, k=5)
        
        logger.info(f"Hybrid search pronašao {len(hybrid_results)} rezultata")
        
        # Reranking
        if hybrid_results:
            reranked_results = reranker.rerank(query, hybrid_results, top_k=3)
            logger.info(f"Reranking završen. Top 3 rezultata:")
            
            for i, result in enumerate(reranked_results):
                score = result.get("rerank_score", 0)
                source = result.get("metadata", {}).get("source", "Unknown")
                logger.info(f"  {i+1}. Score: {score:.4f} | Source: {source}")
        else:
            logger.info("Nema rezultata iz hybrid search-a")
        
    except Exception as e:
        logger.error(f"Greška u testiranju hybrid + reranking: {e}")
        raise

if __name__ == "__main__":
    print("Testiranje reranking funkcionalnosti...")
    
    # Test 1: Osnovni reranking
    print("\n1. Testiranje osnovnog reranking-a...")
    test_reranking()
    
    # Test 2: Hybrid search + reranking
    print("\n2. Testiranje hybrid search + reranking...")
    test_hybrid_with_reranking()
    
    print("\nSvi testovi završeni!") 
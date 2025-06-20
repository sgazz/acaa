#!/usr/bin/env python3
"""
Test skripta za proveru reranking funkcionalnosti sa pravim dokumentima
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from rag_client import RAGClient
import logging

# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_documents():
    """Testira reranking sa pravim dokumentima iz sistema"""
    
    try:
        # Inicijalizujemo RAG klijent
        logger.info("Inicijalizujem RAG klijent...")
        rag_client = RAGClient()
        
        # Test upiti
        test_queries = [
            "Python programiranje",
            "RAG sistem",
            "Dokument procesiranje",
            "Machine learning",
            "Web development",
            "Docker kontejneri",
            "FastAPI backend",
            "React frontend"
        ]
        
        logger.info(f"Testiram {len(test_queries)} upita sa pravim dokumentima...")
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"TEST {i}/{len(test_queries)}: '{query}'")
            logger.info(f"{'='*60}")
            
            try:
                # Testiramo search_documents (sa reranking-om)
                logger.info("1. Testiram search_documents (sa reranking-om)...")
                results = rag_client.search_documents(query, k=5)
                
                if results:
                    logger.info(f"   Pronađeno {len(results)} rezultata")
                    logger.info("   Top 3 rezultata:")
                    
                    for j, result in enumerate(results[:3]):
                        score = result.get("rerank_score", result.get("combined_score", result.get("score", 0)))
                        source = result.get("metadata", {}).get("source", "Unknown")
                        content_preview = result.get("content", "")[:150] + "..." if len(result.get("content", "")) > 150 else result.get("content", "")
                        
                        logger.info(f"   {j+1}. Score: {score:.4f} | Source: {source}")
                        logger.info(f"      Content: {content_preview}")
                else:
                    logger.info("   Nema rezultata")
                
                # Testiramo get_context_for_query (sa reranking-om)
                logger.info("\n2. Testiram get_context_for_query (sa reranking-om)...")
                context_result = rag_client.get_context_for_query(query, k=3)
                
                if context_result["sources"]:
                    logger.info(f"   Pronađeno {len(context_result['sources'])} izvora")
                    logger.info("   Top izvori:")
                    
                    for j, source in enumerate(context_result["sources"][:3]):
                        relevance = source.get("relevance_score", 0)
                        rerank = source.get("rerank_score", 0)
                        filename = source.get("filename", "Unknown")
                        
                        logger.info(f"   {j+1}. Relevance: {relevance}% | Rerank: {rerank}% | File: {filename}")
                else:
                    logger.info("   Nema konteksta")
                
            except Exception as e:
                logger.error(f"   Greška pri testiranju upita '{query}': {e}")
        
        logger.info(f"\n{'='*60}")
        logger.info("Svi testovi završeni!")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Greška u testiranju: {e}")
        raise

def test_specific_document_search():
    """Testira pretragu specifičnih dokumenata"""
    
    try:
        logger.info("\nTestiram pretragu specifičnih dokumenata...")
        rag_client = RAGClient()
        
        # Testiramo sa specifičnim upitima koji bi trebalo da pronađu postojeće dokumente
        specific_queries = [
            "ACAI Assistant",
            "RAG tehnologija",
            "Supabase baza podataka",
            "FastAPI endpoint",
            "React komponente"
        ]
        
        for query in specific_queries:
            logger.info(f"\n--- Testiram: '{query}' ---")
            
            try:
                # Koristimo detaljni endpoint sa reranking statistikama
                from main import rag_client as main_rag_client
                
                # Simuliramo poziv endpoint-a
                initial_k = min(5 * 3, 20)
                query_embedding = main_rag_client.rag_service.model.encode([query])[0]
                initial_results = main_rag_client.hybrid_search.search(query, query_embedding, main_rag_client.rag_service.index, initial_k)
                
                if initial_results:
                    rerank_result = main_rag_client.reranker.rerank_with_metadata(query, initial_results, 5)
                    
                    logger.info(f"   Hybrid search pronašao: {len(initial_results)} rezultata")
                    logger.info(f"   Reranking vratio: {len(rerank_result['results'])} rezultata")
                    
                    if rerank_result["results"]:
                        logger.info("   Top rezultat:")
                        top_result = rerank_result["results"][0]
                        score = top_result.get("rerank_score", 0)
                        source = top_result.get("metadata", {}).get("source", "Unknown")
                        logger.info(f"   Score: {score:.4f} | Source: {source}")
                
            except Exception as e:
                logger.error(f"   Greška: {e}")
        
    except Exception as e:
        logger.error(f"Greška u testiranju specifičnih dokumenata: {e}")

if __name__ == "__main__":
    print("Testiranje reranking-a sa pravim dokumentima...")
    
    # Test 1: Opšta pretraga
    test_real_documents()
    
    # Test 2: Specifična pretraga
    test_specific_document_search()
    
    print("\nSvi testovi završeni!") 
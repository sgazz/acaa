#!/usr/bin/env python3
"""
Test skripta za proveru Query Expansion i Context Optimization funkcionalnosti
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from rag.query_expander import QueryExpander
from rag.context_optimizer import ContextOptimizer
import logging

# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_query_expansion():
    """Testira Query Expansion funkcionalnost"""
    
    logger.info("=" * 60)
    logger.info("TESTIRANJE QUERY EXPANSION")
    logger.info("=" * 60)
    
    query_expander = QueryExpander()
    
    # Test upiti
    test_queries = [
        "Python programiranje",
        "RAG sistem",
        "Machine learning",
        "Web development",
        "Docker kontejneri",
        "FastAPI backend",
        "React frontend",
        "Baza podataka"
    ]
    
    for query in test_queries:
        logger.info(f"\n--- Testiram: '{query}' ---")
        
        # Testiramo različite tipove proširenja
        for expansion_type in ["synonyms", "domain", "hybrid"]:
            try:
                expansion_result = query_expander.expand_query_with_metadata(query, expansion_type)
                
                logger.info(f"  {expansion_type.upper()}:")
                logger.info(f"    Originalni upit: {expansion_result['original_query']}")
                logger.info(f"    Prošireni upiti: {len(expansion_result['expanded_queries'])}")
                logger.info(f"    Detektovane domene: {expansion_result['analysis']['detected_domains']}")
                logger.info(f"    Primenjeni sinonimi: {list(expansion_result['analysis']['applied_synonyms'].keys())}")
                logger.info(f"    Dodane ključne reči: {expansion_result['analysis']['added_keywords']}")
                
                # Prikazujemo proširene upite
                for i, expanded_query in enumerate(expansion_result['expanded_queries'][:3]):  # Top 3
                    logger.info(f"      {i+1}. {expanded_query}")
                
            except Exception as e:
                logger.error(f"    Greška: {e}")

def test_context_optimization():
    """Testira Context Optimization funkcionalnost"""
    
    logger.info("\n" + "=" * 60)
    logger.info("TESTIRANJE CONTEXT OPTIMIZATION")
    logger.info("=" * 60)
    
    context_optimizer = ContextOptimizer(max_tokens=2000, max_chunks=5)
    
    # Test dokumenti
    test_documents = [
        {
            "content": "Python je programski jezik visokog nivoa koji se koristi za web development, data science i AI. Python ima jednostavan i čitljiv sintaksu što ga čini popularnim za početnike.",
            "metadata": {"source": "python_intro.txt", "page": 1},
            "rerank_score": 0.95,
            "combined_score": 0.92
        },
        {
            "content": "Machine Learning je grana veštačke inteligencije koja omogućava računarima da uče bez eksplicitnog programiranja. ML algoritmi koriste podatke za treniranje modela.",
            "metadata": {"source": "ml_guide.txt", "page": 1},
            "rerank_score": 0.88,
            "combined_score": 0.85
        },
        {
            "content": "RAG (Retrieval-Augmented Generation) je tehnika koja kombinuje pretragu dokumenata sa generisanjem teksta. RAG sistemi koriste bazu znanja za poboljšanje odgovora.",
            "metadata": {"source": "rag_docs.txt", "page": 1},
            "rerank_score": 0.92,
            "combined_score": 0.89
        },
        {
            "content": "Docker je platforma za razvoj, isporuku i pokretanje aplikacija u kontejnerima. Docker omogućava izolaciju aplikacija i konzistentno okruženje.",
            "metadata": {"source": "docker_guide.txt", "page": 1},
            "rerank_score": 0.78,
            "combined_score": 0.75
        },
        {
            "content": "FastAPI je moderan web framework za Python koji omogućava brz razvoj API-ja. FastAPI koristi Pydantic za validaciju podataka i automatsku dokumentaciju.",
            "metadata": {"source": "fastapi_docs.txt", "page": 1},
            "rerank_score": 0.85,
            "combined_score": 0.82
        },
        {
            "content": "React je JavaScript biblioteka za izgradnju korisničkih interfejsa. React koristi komponente i virtualni DOM za efikasno ažuriranje UI-ja.",
            "metadata": {"source": "react_guide.txt", "page": 1},
            "rerank_score": 0.82,
            "combined_score": 0.79
        }
    ]
    
    # Test upiti
    test_queries = [
        "Python programiranje",
        "Machine learning algoritmi",
        "RAG tehnologija",
        "Web development"
    ]
    
    for query in test_queries:
        logger.info(f"\n--- Testiram: '{query}' ---")
        
        # Testiramo različite tipove optimizacije
        for optimization_type in ["smart", "score_based", "length_based"]:
            try:
                context_result = context_optimizer.optimize_context(
                    test_documents, query, optimization_type
                )
                
                metadata = context_result["metadata"]
                
                logger.info(f"  {optimization_type.upper()}:")
                logger.info(f"    Dokumenti: {metadata['total_documents']}")
                logger.info(f"    Tokeni: {metadata['total_tokens']}")
                logger.info(f"    Prosječan score: {metadata['average_score']:.3f}")
                logger.info(f"    Maksimalan score: {metadata['max_score']:.3f}")
                logger.info(f"    Iskorišćenost: {metadata['utilization_percentage']}%")
                
                # Prikazujemo izvore
                logger.info("    Izvori:")
                for i, source in enumerate(metadata['sources'][:3]):  # Top 3
                    logger.info(f"      {i+1}. {source['filename']} (Score: {source['score']:.3f})")
                
                # Prikazujemo preview konteksta
                context_preview = context_result["context"][:300] + "..." if len(context_result["context"]) > 300 else context_result["context"]
                logger.info(f"    Kontekst preview: {context_preview}")
                
            except Exception as e:
                logger.error(f"    Greška: {e}")

def test_integration():
    """Testira integraciju Query Expansion i Context Optimization"""
    
    logger.info("\n" + "=" * 60)
    logger.info("TESTIRANJE INTEGRACIJE")
    logger.info("=" * 60)
    
    query_expander = QueryExpander()
    context_optimizer = ContextOptimizer(max_tokens=1500, max_chunks=3)
    
    # Test upit
    query = "Python web development"
    
    logger.info(f"Originalni upit: '{query}'")
    
    # 1. Query Expansion
    logger.info("\n1. Query Expansion:")
    expansion_result = query_expander.expand_query_with_metadata(query, "hybrid")
    
    logger.info(f"   Prošireni upiti: {len(expansion_result['expanded_queries'])}")
    for i, expanded_query in enumerate(expansion_result['expanded_queries']):
        logger.info(f"   {i+1}. {expanded_query}")
    
    # 2. Simuliramo rezultate pretrage za svaki prošireni upit
    logger.info("\n2. Simulacija pretrage:")
    
    all_results = []
    for i, expanded_query in enumerate(expansion_result['expanded_queries']):
        # Simuliramo rezultate sa različitim score-ovima
        simulated_results = [
            {
                "content": f"Rezultat {i+1}-{j+1} za upit '{expanded_query}': Python je odličan za web development.",
                "metadata": {"source": f"doc_{i}_{j}.txt", "page": 1},
                "rerank_score": 0.9 - (i * 0.1) - (j * 0.05),
                "combined_score": 0.85 - (i * 0.1) - (j * 0.05),
                "expanded_query": expanded_query,
                "query_index": i
            }
            for j in range(3)
        ]
        all_results.extend(simulated_results)
    
    logger.info(f"   Ukupno simuliranih rezultata: {len(all_results)}")
    
    # 3. Context Optimization
    logger.info("\n3. Context Optimization:")
    context_result = context_optimizer.optimize_context(all_results, query, "smart")
    
    metadata = context_result["metadata"]
    logger.info(f"   Optimizovani dokumenti: {metadata['total_documents']}")
    logger.info(f"   Tokeni: {metadata['total_tokens']}")
    logger.info(f"   Prosječan score: {metadata['average_score']:.3f}")
    
    # Prikazujemo finalni kontekst
    logger.info("\n4. Finalni kontekst:")
    context_preview = context_result["context"][:500] + "..." if len(context_result["context"]) > 500 else context_result["context"]
    logger.info(context_preview)

if __name__ == "__main__":
    print("Testiranje naprednih RAG funkcionalnosti...")
    
    # Test 1: Query Expansion
    test_query_expansion()
    
    # Test 2: Context Optimization
    test_context_optimization()
    
    # Test 3: Integracija
    test_integration()
    
    print("\nSvi testovi završeni!") 
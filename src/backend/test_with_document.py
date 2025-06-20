#!/usr/bin/env python3
"""
Test skripta sa upload-om dokumenta i testiranjem poboljšanja
"""

import sys
import os
import time
import asyncio
sys.path.append(os.path.dirname(__file__))

from rag_client import RAGClient
import logging

# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def upload_test_document():
    """Upload-uje test dokument u sistem"""
    logger.info("📤 Upload-ujem test dokument...")
    
    rag_client = RAGClient()
    
    # Učitavamo test dokument
    test_file_path = "test_document.txt"
    
    if not os.path.exists(test_file_path):
        logger.error(f"Test dokument ne postoji: {test_file_path}")
        return False
    
    try:
        # Simuliramo upload fajla
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
        
        # Kreirajmo mock UploadFile objekat
        class MockUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.content = content
            
            async def read(self):
                return self.content
        
        mock_file = MockUploadFile("test_document.txt", file_content)
        
        # Upload-ujemo dokument
        result = await rag_client.process_document(mock_file)
        
        logger.info(f"✅ Dokument uspešno upload-ovan: {result}")
        return True
        
    except Exception as e:
        logger.error(f"Greška pri upload-u dokumenta: {e}")
        return False

def test_search_comparison():
    """Testira upoređivanje različitih tipova pretrage"""
    logger.info("\n" + "="*80)
    logger.info("🧪 TESTIRANJE SA DOKUMENTOM")
    logger.info("="*80)
    
    rag_client = RAGClient()
    
    # Test upiti
    test_queries = [
        "Python programiranje",
        "RAG sistemi",
        "Machine Learning",
        "Web development",
        "Docker kontejneri",
        "React frontend",
        "Baze podataka",
        "DevOps praksa"
    ]
    
    for query in test_queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 TESTIRANJE UPITA: '{query}'")
        logger.info(f"{'='*60}")
        
        # Test 1: Osnovna pretraga
        logger.info("\n1️⃣ OSNOVNA PRETRAGA:")
        start_time = time.time()
        try:
            basic_results = rag_client.rag_service.search(query, 5)
            basic_time = time.time() - start_time
            
            logger.info(f"   ⏱️  Vreme: {basic_time:.3f}s")
            logger.info(f"   📊 Rezultati: {len(basic_results)}")
            
            if basic_results:
                for i, result in enumerate(basic_results[:3]):
                    score = result.get("score", 0)
                    content_preview = result.get("content", "")[:100] + "..."
                    logger.info(f"   {i+1}. Score: {score:.4f} | {content_preview}")
            
        except Exception as e:
            logger.error(f"   ❌ Greška: {e}")
        
        # Test 2: Hybrid pretraga
        logger.info("\n2️⃣ HYBRID PRETRAGA:")
        start_time = time.time()
        try:
            query_embedding = rag_client.rag_service.model.encode([query])[0]
            hybrid_results = rag_client.hybrid_search.search(query, query_embedding, rag_client.rag_service.index, 5)
            hybrid_time = time.time() - start_time
            
            logger.info(f"   ⏱️  Vreme: {hybrid_time:.3f}s")
            logger.info(f"   📊 Rezultati: {len(hybrid_results)}")
            
            if hybrid_results:
                for i, result in enumerate(hybrid_results[:3]):
                    score = result.get("combined_score", result.get("score", 0))
                    content_preview = result.get("content", "")[:100] + "..."
                    logger.info(f"   {i+1}. Score: {score:.4f} | {content_preview}")
            
        except Exception as e:
            logger.error(f"   ❌ Greška: {e}")
        
        # Test 3: Napredna pretraga (sa svim optimizacijama)
        logger.info("\n3️⃣ NAPREDNA PRETRAGA (Query Expansion + Reranking):")
        start_time = time.time()
        try:
            advanced_results = rag_client.search_documents(
                query, 5, use_query_expansion=True, expansion_type="hybrid"
            )
            advanced_time = time.time() - start_time
            
            logger.info(f"   ⏱️  Vreme: {advanced_time:.3f}s")
            logger.info(f"   📊 Rezultati: {len(advanced_results)}")
            
            if advanced_results:
                for i, result in enumerate(advanced_results[:3]):
                    score = result.get("rerank_score", result.get("combined_score", result.get("score", 0)))
                    content_preview = result.get("content", "")[:100] + "..."
                    expanded_query = result.get("expanded_query", "N/A")
                    logger.info(f"   {i+1}. Score: {score:.4f} | Query: {expanded_query}")
                    logger.info(f"      Content: {content_preview}")
            
        except Exception as e:
            logger.error(f"   ❌ Greška: {e}")
        
        # Test 4: Context Optimization
        logger.info("\n4️⃣ CONTEXT OPTIMIZATION:")
        start_time = time.time()
        try:
            context_result = rag_client.get_context_for_query(
                query, 5, use_context_optimization=True, optimization_type="smart"
            )
            context_time = time.time() - start_time
            
            logger.info(f"   ⏱️  Vreme: {context_time:.3f}s")
            logger.info(f"   📊 Izvori: {len(context_result.get('sources', []))}")
            logger.info(f"   📝 Kontekst dužina: {len(context_result.get('context', ''))} karaktera")
            
            # Prikazujemo optimization metadata
            if "optimization_metadata" in context_result:
                meta = context_result["optimization_metadata"]
                logger.info(f"   🎯 Tip optimizacije: {meta.get('optimization_type', 'N/A')}")
                logger.info(f"   📊 Dokumenti: {meta.get('total_documents', 'N/A')}")
                logger.info(f"   📝 Tokeni: {meta.get('total_tokens', 'N/A')}")
                logger.info(f"   📈 Iskorišćenost: {meta.get('utilization_percentage', 'N/A')}%")
            
            # Prikazujemo izvore
            sources = context_result.get("sources", [])
            if sources:
                logger.info("   📚 Izvori:")
                for i, source in enumerate(sources[:3]):
                    logger.info(f"      {i+1}. {source.get('filename', 'N/A')} (Score: {source.get('relevance_score', 0)}%)")
            
        except Exception as e:
            logger.error(f"   ❌ Greška: {e}")

def test_query_expansion_demo():
    """Demonstrira Query Expansion funkcionalnost"""
    logger.info("\n" + "="*80)
    logger.info("🔍 DEMONSTRACIJA QUERY EXPANSION")
    logger.info("="*80)
    
    rag_client = RAGClient()
    
    test_queries = [
        "Python programiranje",
        "RAG tehnologija",
        "Web development"
    ]
    
    for query in test_queries:
        logger.info(f"\n--- Upit: '{query}' ---")
        
        # Testiramo različite tipove proširenja
        for expansion_type in ["synonyms", "domain", "hybrid"]:
            try:
                expansion_result = rag_client.query_expander.expand_query_with_metadata(query, expansion_type)
                
                logger.info(f"  {expansion_type.upper()}:")
                logger.info(f"    Prošireni upiti: {len(expansion_result['expanded_queries'])}")
                logger.info(f"    Detektovane domene: {expansion_result['analysis']['detected_domains']}")
                logger.info(f"    Primenjeni sinonimi: {list(expansion_result['analysis']['applied_synonyms'].keys())}")
                
                # Prikazujemo proširene upite
                for i, expanded_query in enumerate(expansion_result['expanded_queries'][:3]):
                    logger.info(f"      {i+1}. {expanded_query}")
                
            except Exception as e:
                logger.error(f"    ❌ Greška: {e}")

async def main():
    """Glavna funkcija"""
    logger.info("🚀 Započinjem testiranje sa dokumentom...")
    
    # 1. Upload test dokumenta
    if not await upload_test_document():
        logger.error("❌ Neuspešan upload dokumenta. Prekidam testiranje.")
        return
    
    # 2. Testiranje pretrage
    test_search_comparison()
    
    # 3. Demonstracija Query Expansion
    test_query_expansion_demo()
    
    logger.info("\n" + "="*80)
    logger.info("✅ TESTIRANJE ZAVRŠENO")
    logger.info("="*80)

if __name__ == "__main__":
    asyncio.run(main()) 
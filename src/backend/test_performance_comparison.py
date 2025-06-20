#!/usr/bin/env python3
"""
Test skripta za upoređivanje performansi sa i bez naprednih RAG funkcionalnosti
"""

import sys
import os
import time
import json
sys.path.append(os.path.dirname(__file__))

from rag_client import RAGClient
from rag.rag_service import RAGService
from rag.hybrid_search import HybridSearch
import logging

# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTester:
    def __init__(self):
        self.rag_client = RAGClient()
        self.rag_service = RAGService()
        self.hybrid_search = HybridSearch()
        
    def test_basic_search(self, query: str, k: int = 5):
        """Testira osnovnu pretragu bez naprednih funkcionalnosti"""
        logger.info(f"🔍 Testiram osnovnu pretragu: '{query}'")
        
        start_time = time.time()
        
        # Osnovna FAISS pretraga
        query_embedding = self.rag_service.model.encode([query])[0]
        basic_results = self.rag_service.search(query, k)
        
        basic_time = time.time() - start_time
        
        logger.info(f"   ⏱️  Vreme: {basic_time:.3f}s")
        logger.info(f"   📊 Rezultati: {len(basic_results)}")
        
        return {
            "type": "basic",
            "time": basic_time,
            "results_count": len(basic_results),
            "results": basic_results
        }
    
    def test_hybrid_search(self, query: str, k: int = 5):
        """Testira hybrid pretragu (BM25 + FAISS)"""
        logger.info(f"🔍 Testiram hybrid pretragu: '{query}'")
        
        start_time = time.time()
        
        # Hybrid pretraga
        query_embedding = self.rag_service.model.encode([query])[0]
        hybrid_results = self.hybrid_search.search(query, query_embedding, self.rag_service.index, k)
        
        hybrid_time = time.time() - start_time
        
        logger.info(f"   ⏱️  Vreme: {hybrid_time:.3f}s")
        logger.info(f"   📊 Rezultati: {len(hybrid_results)}")
        
        return {
            "type": "hybrid",
            "time": hybrid_time,
            "results_count": len(hybrid_results),
            "results": hybrid_results
        }
    
    def test_advanced_search(self, query: str, k: int = 5):
        """Testira naprednu pretragu sa svim optimizacijama"""
        logger.info(f"🚀 Testiram naprednu pretragu: '{query}'")
        
        start_time = time.time()
        
        # Napredna pretraga sa svim optimizacijama
        advanced_results = self.rag_client.search_documents(
            query, k, use_query_expansion=True, expansion_type="hybrid"
        )
        
        advanced_time = time.time() - start_time
        
        logger.info(f"   ⏱️  Vreme: {advanced_time:.3f}s")
        logger.info(f"   📊 Rezultati: {len(advanced_results)}")
        
        return {
            "type": "advanced",
            "time": advanced_time,
            "results_count": len(advanced_results),
            "results": advanced_results
        }
    
    def test_context_optimization(self, query: str, k: int = 5):
        """Testira Context Optimization"""
        logger.info(f"🎯 Testiram Context Optimization: '{query}'")
        
        start_time = time.time()
        
        # Context Optimization
        context_result = self.rag_client.get_context_for_query(
            query, k, use_context_optimization=True, optimization_type="smart"
        )
        
        context_time = time.time() - start_time
        
        logger.info(f"   ⏱️  Vreme: {context_time:.3f}s")
        logger.info(f"   📊 Izvori: {len(context_result.get('sources', []))}")
        logger.info(f"   📝 Kontekst dužina: {len(context_result.get('context', ''))} karaktera")
        
        return {
            "type": "context_optimization",
            "time": context_time,
            "sources_count": len(context_result.get('sources', [])),
            "context_length": len(context_result.get('context', '')),
            "context_result": context_result
        }
    
    def analyze_results(self, results_list):
        """Analizira i upoređuje rezultate"""
        logger.info("\n" + "="*80)
        logger.info("📈 ANALIZA PERFORMANSI")
        logger.info("="*80)
        
        # Upoređujemo vremena
        times = {r["type"]: r["time"] for r in results_list if "time" in r}
        if times:
            logger.info("\n⏱️  UPOREDBA VREMENA:")
            for method, time_taken in sorted(times.items(), key=lambda x: x[1]):
                logger.info(f"   {method.upper()}: {time_taken:.3f}s")
        
        # Upoređujemo broj rezultata
        result_counts = {r["type"]: r["results_count"] for r in results_list if "results_count" in r}
        if result_counts:
            logger.info("\n📊 UPOREDBA BROJA REZULTATA:")
            for method, count in result_counts.items():
                logger.info(f"   {method.upper()}: {count} rezultata")
        
        # Analiziramo score-ove
        logger.info("\n🎯 ANALIZA SCORE-OVA:")
        for result in results_list:
            if "results" in result and result["results"]:
                scores = []
                for res in result["results"]:
                    score = res.get("rerank_score", res.get("combined_score", res.get("score", 0)))
                    scores.append(score)
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    max_score = max(scores)
                    min_score = min(scores)
                    
                    logger.info(f"   {result['type'].upper()}:")
                    logger.info(f"      Prosječan score: {avg_score:.4f}")
                    logger.info(f"      Maksimalan score: {max_score:.4f}")
                    logger.info(f"      Minimalan score: {min_score:.4f}")
        
        # Analiziramo Context Optimization
        context_results = [r for r in results_list if r["type"] == "context_optimization"]
        if context_results:
            logger.info("\n🎯 CONTEXT OPTIMIZATION ANALIZA:")
            for result in context_results:
                logger.info(f"   Izvori: {result['sources_count']}")
                logger.info(f"   Kontekst dužina: {result['context_length']} karaktera")
                
                # Analiziramo optimization metadata ako postoji
                if "context_result" in result and "optimization_metadata" in result["context_result"]:
                    meta = result["context_result"]["optimization_metadata"]
                    logger.info(f"   Tip optimizacije: {meta.get('optimization_type', 'N/A')}")
                    logger.info(f"   Dokumenti: {meta.get('total_documents', 'N/A')}")
                    logger.info(f"   Tokeni: {meta.get('total_tokens', 'N/A')}")
                    logger.info(f"   Iskorišćenost: {meta.get('utilization_percentage', 'N/A')}%")
    
    def run_comprehensive_test(self, query: str, k: int = 5):
        """Pokreće sveukupan test"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 KOMPLETAN TEST ZA UPIT: '{query}'")
        logger.info(f"{'='*80}")
        
        results = []
        
        # Test 1: Osnovna pretraga
        try:
            basic_result = self.test_basic_search(query, k)
            results.append(basic_result)
        except Exception as e:
            logger.error(f"Greška u osnovnoj pretrazi: {e}")
        
        # Test 2: Hybrid pretraga
        try:
            hybrid_result = self.test_hybrid_search(query, k)
            results.append(hybrid_result)
        except Exception as e:
            logger.error(f"Greška u hybrid pretrazi: {e}")
        
        # Test 3: Napredna pretraga
        try:
            advanced_result = self.test_advanced_search(query, k)
            results.append(advanced_result)
        except Exception as e:
            logger.error(f"Greška u naprednoj pretrazi: {e}")
        
        # Test 4: Context Optimization
        try:
            context_result = self.test_context_optimization(query, k)
            results.append(context_result)
        except Exception as e:
            logger.error(f"Greška u Context Optimization: {e}")
        
        # Analiza rezultata
        self.analyze_results(results)
        
        return results

def main():
    """Glavna funkcija za testiranje"""
    tester = PerformanceTester()
    
    # Test upiti
    test_queries = [
        "Python programiranje",
        "RAG sistem",
        "Machine learning",
        "Web development",
        "Docker kontejneri"
    ]
    
    all_results = {}
    
    for query in test_queries:
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 TESTIRANJE UPITA: '{query}'")
        logger.info(f"{'='*80}")
        
        try:
            results = tester.run_comprehensive_test(query, k=5)
            all_results[query] = results
        except Exception as e:
            logger.error(f"Greška pri testiranju upita '{query}': {e}")
    
    # Sažetak svih testova
    logger.info(f"\n{'='*80}")
    logger.info("📋 SAŽETAK SVIH TESTOVA")
    logger.info(f"{'='*80}")
    
    for query, results in all_results.items():
        logger.info(f"\nUpit: '{query}'")
        for result in results:
            if "time" in result:
                logger.info(f"  {result['type']}: {result['time']:.3f}s")
    
    logger.info(f"\n{'='*80}")
    logger.info("✅ SVI TESTOVI ZAVRŠENI")
    logger.info(f"{'='*80}")

if __name__ == "__main__":
    main() 
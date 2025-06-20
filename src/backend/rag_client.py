import os
from typing import List, Dict, Any
from fastapi import UploadFile
import tempfile
from rag.rag_service import RAGService
from rag.document_processor import DocumentProcessor
from rag.hybrid_search import HybridSearch
from rag.reranker_service import RerankerService
from rag.query_expander import QueryExpander
from rag.context_optimizer import ContextOptimizer
from supabase_client import supabase
import logging
import uuid

# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGClient:
    def __init__(self):
        self.rag_service = RAGService()
        self.hybrid_search = HybridSearch(semantic_weight=0.7, lexical_weight=0.3)
        self.reranker = RerankerService()
        self.query_expander = QueryExpander()
        self.context_optimizer = ContextOptimizer(max_tokens=4000, max_chunks=10)
        self.index_path = os.path.join(os.path.dirname(__file__), "data", "rag_index")
        self.temp_dir = os.path.join(os.path.dirname(__file__), "data", "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Učitava postojeći indeks ili kreira novi"""
        if os.path.exists(self.index_path):
            try:
                self.rag_service.load_index(self.index_path)
                logger.info("RAG indeks uspešno učitan sa diska")
            except Exception as e:
                logger.error(f"Greška pri učitavanju indeksa: {str(e)}")
                os.makedirs(self.index_path, exist_ok=True)
                self._load_documents_from_supabase()
        else:
            os.makedirs(self.index_path, exist_ok=True)
            self._load_documents_from_supabase()

    def _load_documents_from_supabase(self):
        """Učitava sve postojeće dokumente iz Supabase-a u RAG indeks"""
        try:
            logger.info("Učitavam postojeće dokumente iz Supabase-a...")
            
            # Dohvatamo sve stranice iz baze
            result = supabase.table("document_pages").select("*").execute()
            
            if not result.data:
                logger.info("Nema postojećih dokumenata u bazi")
                return
            
            logger.info(f"Pronađeno {len(result.data)} stranica u bazi")
            
            # PRIVREMENO: Preskačemo učitavanje postojećih dokumenata
            # da testiramo semantic chunking
            logger.info("PRIVREMENO: Preskačem učitavanje postojećih dokumenata za testiranje semantic chunking-a")
            return
            
            # Konvertujemo u format koji RAG servis očekuje
            documents = []
            for page in result.data:
                doc = {
                    "content": page["content"],
                    "metadata": {
                        "source": page.get("metadata", {}).get("source", "Unknown"),
                        "page": page["page_number"],
                        "document_id": page["document_id"]
                    }
                }
                documents.append(doc)
            
            # Dodajemo u RAG indeks
            logger.info(f"Dodajem {len(documents)} stranica u RAG indeks...")
            self.rag_service.add_documents(documents)
            
            # Dodajemo u hybrid indeks
            logger.info(f"Dodajem {len(documents)} stranica u hybrid indeks...")
            self.hybrid_search.add_documents(documents)
            
            # Čuvamo indeks
            logger.info("Čuvam RAG indeks...")
            self.rag_service.save_index(self.index_path)
            logger.info("RAG indeks uspešno kreiran i sačuvan")
            
        except Exception as e:
            logger.error(f"Greška pri učitavanju dokumenata iz Supabase-a: {str(e)}")
            logger.info("RAG sistem će raditi bez postojećih dokumenata")

    async def process_document(self, file: UploadFile) -> Dict[str, Any]:
        """Procesira uploadovani dokument"""
        temp_file_path = os.path.join(self.temp_dir, file.filename)
        logger.info(f"Započinjem procesiranje dokumenta: {file.filename}")
        
        try:
            # Čuvamo fajl u privremeni direktorijum
            logger.info("Čuvam fajl u privremeni direktorijum...")
            content = await file.read()
            with open(temp_file_path, 'wb') as f:
                f.write(content)
            logger.info(f"Fajl uspešno sačuvan u: {temp_file_path}")
            
            # Procesiramo dokument
            logger.info("Započinjem procesiranje dokumenta...")
            documents = DocumentProcessor.process_file(temp_file_path, chunk_size=1000, overlap=200)
            logger.info(f"Dokument uspešno procesiran. Broj chunk-ova: {len(documents)}")
            
            # Čuvamo dokument u Supabase
            try:
                logger.info("Pokušavam da sačuvam dokument u Supabase...")
                # Generišemo UUID za dokument
                document_id = str(uuid.uuid4())
                
                # Prvo čuvamo osnovne informacije o dokumentu
                document_data = {
                    "id": document_id,
                    "filename": file.filename,
                    "file_type": os.path.splitext(file.filename)[1].lower(),
                    "total_pages": len(documents),
                    "status": "processed"
                }
                
                logger.info(f"Čuvam osnovne informacije o dokumentu: {document_data}")
                # Čuvamo dokument u Supabase
                result = supabase.table("documents").insert(document_data).execute()
                logger.info(f"Osnovne informacije uspešno sačuvane. Result: {result}")
                
                # Čuvamo sadržaj stranica
                logger.info("Započinjem čuvanje sadržaja stranica...")
                for i, doc in enumerate(documents):
                    page_data = {
                        "id": str(uuid.uuid4()),
                        "document_id": document_id,
                        "page_number": i + 1,
                        "content": doc["content"],
                        "metadata": doc["metadata"]
                    }
                    page_result = supabase.table("document_pages").insert(page_data).execute()
                    logger.info(f"Stranica {i+1} uspešno sačuvana")
                
                logger.info(f"Dokument uspešno sačuvan u Supabase sa ID: {document_id}")
            except Exception as e:
                logger.error(f"Greška pri čuvanju dokumenta u Supabase: {str(e)}")
                raise
            
            # Dodajemo u indeks
            logger.info("Dodajem dokument u RAG indeks...")
            self.rag_service.add_documents(documents)
            
            # Dodajemo u hybrid indeks
            logger.info("Dodajem dokument u hybrid indeks...")
            self.hybrid_search.add_documents(documents)
            
            # Čuvamo indeks
            logger.info("Čuvam RAG indeks...")
            self.rag_service.save_index(self.index_path)
            logger.info("RAG indeks uspešno sačuvan")
            
            return {
                "status": "success",
                "message": f"Uspešno procesiran dokument: {file.filename}",
                "documents_processed": len(documents),
                "document_id": document_id
            }
        except Exception as e:
            logger.error(f"Greška pri procesiranju dokumenta: {str(e)}")
            raise
        finally:
            # Čistimo privremeni fajl
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info("Privremeni fajl obrisan")

    def search_documents(self, query: str, k: int = 3, use_query_expansion: bool = True, 
                        expansion_type: str = "hybrid") -> List[Dict[str, Any]]:
        """Pretražuje dokumente koristeći hybrid search + reranking + query expansion"""
        try:
            # Query Expansion
            if use_query_expansion:
                logger.info(f"Primenjujem Query Expansion (tip: {expansion_type})")
                expansion_result = self.query_expander.expand_query_with_metadata(query, expansion_type)
                expanded_queries = expansion_result["expanded_queries"]
                logger.info(f"Query Expansion: {len(expanded_queries)} upita generisano")
            else:
                expanded_queries = [query]
                expansion_result = None
            
            # Kombiniramo rezultate iz svih proširenih upita
            all_results = []
            
            for i, expanded_query in enumerate(expanded_queries):
                logger.info(f"Pretražujem prošireni upit {i+1}/{len(expanded_queries)}: '{expanded_query}'")
                
                # Generišemo embedding za prošireni upit
                query_embedding = self.rag_service.model.encode([expanded_query])[0]
                
                # Izvršavamo hybrid pretragu sa više rezultata za reranking
                initial_k = min(k * 3, 20)  # Uzimamo više rezultata za reranking
                results = self.hybrid_search.search(expanded_query, query_embedding, self.rag_service.index, initial_k)
                
                # Dodajemo informacije o proširenom upitu
                for result in results:
                    result["expanded_query"] = expanded_query
                    result["query_index"] = i
                
                all_results.extend(results)
            
            logger.info(f"Ukupno pronađeno {len(all_results)} rezultata iz svih proširenih upita")
            
            # Ako imamo rezultate, izvršavamo reranking
            if all_results:
                logger.info("Započinjem reranking rezultata...")
                reranked_results = self.reranker.rerank(query, all_results, top_k=k)
                
                # Dodajemo metapodatke o query expansion-u
                if expansion_result:
                    for result in reranked_results:
                        result["expansion_metadata"] = {
                            "original_query": expansion_result["original_query"],
                            "expansion_type": expansion_result["expansion_type"],
                            "total_expansions": expansion_result["total_expansions"],
                            "detected_domains": expansion_result["analysis"]["detected_domains"]
                        }
                
                logger.info(f"Reranking završen. Vraćam {len(reranked_results)} rezultata")
                return reranked_results
            else:
                logger.info("Nema rezultata za reranking")
                return []
                
        except Exception as e:
            logger.error(f"Greška pri pretraživanju dokumenata: {e}")
            raise

    def get_context_for_query(self, query: str, k: int = 8, use_context_optimization: bool = True,
                             optimization_type: str = "smart") -> Dict[str, Any]:
        logger.info(f"Pretražujem dokumente za upit: {query}")
        
        # Koristimo search_documents sa query expansion-om
        results = self.search_documents(query, k, use_query_expansion=True, expansion_type="hybrid")
        logger.info(f"Pronađeno {len(results)} rezultata")
        
        # Context Optimization
        if use_context_optimization and results:
            logger.info(f"Primenjujem Context Optimization (tip: {optimization_type})")
            context_result = self.context_optimizer.optimize_context(results, query, optimization_type)
            
            # Strukturiramo rezultat
            context = context_result["context"]
            context_metadata = context_result["metadata"]
            
            # Konvertujemo u postojeći format
            sources = []
            for source_info in context_metadata["sources"]:
                source = {
                    "filename": source_info["filename"],
                    "page": source_info["page"],
                    "relevance_score": int(source_info["score"] * 100),
                    "rerank_score": int(source_info["score"] * 100),
                    "content_preview": source_info["content_preview"]
                }
                sources.append(source)
            
            return {
                "context": context,
                "sources": sources,
                "optimization_metadata": {
                    "optimization_type": optimization_type,
                    "total_documents": context_metadata["total_documents"],
                    "total_tokens": context_metadata["total_tokens"],
                    "average_score": context_metadata["average_score"],
                    "utilization_percentage": context_metadata["utilization_percentage"]
                }
            }
        else:
            # Fallback na originalnu logiku
            logger.info("Koristim originalnu logiku bez Context Optimization-a")
            
            # Filtriranje rezultata
            filtered_results = []
            for result in results:
                score = result.get("rerank_score", result.get("combined_score", result.get("score", 0)))
                if score > 0.01:  # Minimalan score threshold
                    filtered_results.append(result)
            
            logger.info(f"Nakon filtriranja ostalo {len(filtered_results)} rezultata")
            
            if not filtered_results:
                logger.info("Nema rezultata nakon filtriranja")
                return {"context": "", "sources": []}
            
            # Strukturiramo kontekst
            context_parts = [f"UPIT: {query}", "=" * 50]
            sources = []
            
            for i, result in enumerate(filtered_results[:k]):
                content = result.get("content", "")
                source = result.get("metadata", {}).get("source", "Unknown")
                score = result.get("rerank_score", result.get("combined_score", result.get("score", 0)))
                
                # Dodajemo u kontekst
                context_parts.append(f"\nDOKUMENT {i+1}: {source} (Score: {score:.3f})")
                context_parts.append("-" * 30)
                context_parts.append(content)
                
                # Dodajemo u sources
                source_info = {
                    "filename": source,
                    "page": result.get("metadata", {}).get("page", 0),
                    "relevance_score": int(score * 100),
                    "rerank_score": int(score * 100),
                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                }
                sources.append(source_info)
            
            context = "\n".join(context_parts)
            
            return {"context": context, "sources": sources} 
import os
from typing import List, Dict, Any
from fastapi import UploadFile
import tempfile
from rag.rag_service import RAGService
from rag.document_processor import DocumentProcessor
from rag.hybrid_search import HybridSearch
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

    def search_documents(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Pretražuje dokumente koristeći hybrid search"""
        try:
            # Generišemo embedding za upit
            query_embedding = self.rag_service.embedding_model.encode([query])[0]
            
            # Izvršavamo hybrid pretragu
            results = self.hybrid_search.search(query, query_embedding, self.rag_service.faiss_index, k)
            
            logger.info(f"Hybrid pretraga završena. Pronađeno {len(results)} rezultata")
            return results
            
        except Exception as e:
            logger.error(f"Greška u hybrid pretrazi: {e}")
            # Fallback na običnu FAISS pretragu
            logger.info("Koristim fallback na FAISS pretragu")
            return self.rag_service.search(query, k)

    def get_context_for_query(self, query: str, k: int = 8) -> Dict[str, Any]:
        logger.info(f"Pretražujem dokumente za upit: {query}")
        results = self.search_documents(query, k)
        logger.info(f"Pronađeno {len(results)} rezultata")
        
        # Logujemo skorove za debug
        for i, doc in enumerate(results):
            semantic_score = doc.get('semantic_score', 0)
            lexical_score = doc.get('lexical_score', 0)
            combined_score = doc.get('combined_score', doc.get('score', 0))
            logger.info(f"Rezultat {i+1}: semantic={semantic_score:.3f}, lexical={lexical_score:.3f}, combined={combined_score:.3f}, source={doc['metadata'].get('source', 'Unknown')}")
        
        # Filtriramo rezultate sa niskim skorom - smanjujemo prag sa 0.1 na 0.01
        filtered_results = [doc for doc in results if doc.get("combined_score", doc.get("score", 0)) > 0.01]
        logger.info(f"Nakon filtriranja ostalo {len(filtered_results)} rezultata")
        
        if not filtered_results:
            logger.info("Nema rezultata nakon filtriranja")
            return {
                "context": "",
                "sources": []
            }
        
        context = "\n\n".join([doc["content"] for doc in filtered_results])
        sources = [
            {
                "filename": doc["metadata"].get("source", "Unknown"),
                "page_number": doc["metadata"].get("page", 0),
                "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                "relevance_score": round(doc.get("combined_score", doc.get("score", 0)) * 100, 2),
                "semantic_score": round(doc.get("semantic_score", 0) * 100, 2),
                "lexical_score": round(doc.get("lexical_score", 0) * 100, 2)
            }
            for doc in filtered_results
        ]
        
        logger.info(f"Vraćam {len(sources)} izvora")
        return {
            "context": context,
            "sources": sources
        } 
from typing import List, Dict, Any
import PyPDF2
import docx
import os
import logging
import re
import json
import yaml
import csv
from pathlib import Path

# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    # Definišemo podržane formate
    SUPPORTED_FORMATS = {
        # Dokumenti
        '.pdf': 'PDF dokument',
        '.docx': 'Word dokument',
        
        # Tekstualni fajlovi
        '.txt': 'Tekst fajl',
        '.md': 'Markdown fajl',
        '.rst': 'reStructuredText fajl',
        
        # Programski kod
        '.py': 'Python fajl',
        '.js': 'JavaScript fajl',
        '.ts': 'TypeScript fajl',
        '.java': 'Java fajl',
        '.cpp': 'C++ fajl',
        '.c': 'C fajl',
        '.html': 'HTML fajl',
        '.htm': 'HTML fajl',
        
        # Konfiguracioni fajlovi
        '.json': 'JSON fajl',
        '.yaml': 'YAML fajl',
        '.yml': 'YAML fajl',
        '.xml': 'XML fajl',
        '.csv': 'CSV fajl'
    }
    
    @staticmethod
    def process_file(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira fajl i vraća listu dokumenta sa semantic chunking-om"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        logger.info(f"Procesiranje fajla: {file_path} sa chunk_size={chunk_size}, overlap={overlap}")
        
        if file_extension not in DocumentProcessor.SUPPORTED_FORMATS:
            raise ValueError(f"Ne podržani format fajla: {file_extension}. Podržani formati: {', '.join(DocumentProcessor.SUPPORTED_FORMATS.keys())}")
        
        # Ruter za različite formate
        processors = {
            '.pdf': DocumentProcessor._process_pdf,
            '.docx': DocumentProcessor._process_docx,
            '.txt': DocumentProcessor._process_text,
            '.md': DocumentProcessor._process_text,
            '.rst': DocumentProcessor._process_text,
            '.py': DocumentProcessor._process_code,
            '.js': DocumentProcessor._process_code,
            '.ts': DocumentProcessor._process_code,
            '.java': DocumentProcessor._process_code,
            '.cpp': DocumentProcessor._process_code,
            '.c': DocumentProcessor._process_code,
            '.html': DocumentProcessor._process_html,
            '.htm': DocumentProcessor._process_html,
            '.json': DocumentProcessor._process_json,
            '.yaml': DocumentProcessor._process_yaml,
            '.yml': DocumentProcessor._process_yaml,
            '.xml': DocumentProcessor._process_xml,
            '.csv': DocumentProcessor._process_csv
        }
        
        processor = processors.get(file_extension)
        if processor:
            return processor(file_path, chunk_size, overlap)
        else:
            raise ValueError(f"Procesor nije implementiran za format: {file_extension}")

    @staticmethod
    def _create_semantic_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Kreira semantic chunk-ove sa overlap-om"""
        # Čistimo tekst
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Ako nismo na kraju teksta, pokušavamo da nađemo dobru granicu
            if end < len(text):
                # Tražimo najbližu rečeničnu granicu (. ! ?)
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                
                # Ako nismo našli rečeničnu granicu, tražimo zarez ili novi red
                if sentence_end == -1:
                    sentence_end = max(
                        text.rfind(',', start, end),
                        text.rfind('\n', start, end),
                        text.rfind(' ', start, end)
                    )
                
                # Ako i dalje nismo našli granicu, koristimo kraj chunk-a
                if sentence_end == -1 or sentence_end <= start:
                    sentence_end = end
                else:
                    sentence_end += 1  # Uključujemo znak interpunkcije
            
            chunk = text[start:sentence_end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Računamo početak sledećeg chunk-a sa overlap-om
            start = max(start + 1, sentence_end - overlap)
            
            # Ako smo na kraju teksta, izlazimo
            if start >= len(text):
                break
        
        return chunks

    @staticmethod
    def _process_text(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira tekstualne fajlove (.txt, .md, .rst)"""
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            if not text.strip():
                raise Exception("Fajl je prazan")
            
            # Kreiramo semantic chunk-ove
            chunks = DocumentProcessor._create_semantic_chunks(text, chunk_size, overlap)
            
            file_extension = os.path.splitext(file_path)[1].lower()
            for chunk_idx, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk": chunk_idx + 1,
                        "total_chunks": len(chunks),
                        "type": file_extension[1:]  # Uklanjamo tačku
                    }
                })
            
            logger.info(f"Tekstualni fajl podeljen u {len(chunks)} chunk-ova")
            return documents
        except Exception as e:
            logger.error(f"Greška pri procesiranju tekstualnog fajla: {str(e)}")
            raise

    @staticmethod
    def _process_code(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira programski kod"""
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            if not text.strip():
                raise Exception("Fajl je prazan")
            
            # Za kod, koristimo manje chunk-ove i veći overlap
            code_chunk_size = min(chunk_size, 800)
            code_overlap = min(overlap, 150)
            
            # Kreiramo semantic chunk-ove
            chunks = DocumentProcessor._create_semantic_chunks(text, code_chunk_size, code_overlap)
            
            file_extension = os.path.splitext(file_path)[1].lower()
            for chunk_idx, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk": chunk_idx + 1,
                        "total_chunks": len(chunks),
                        "type": "code",
                        "language": file_extension[1:]  # Uklanjamo tačku
                    }
                })
            
            logger.info(f"Kod fajl podeljen u {len(chunks)} chunk-ova")
            return documents
        except Exception as e:
            logger.error(f"Greška pri procesiranju kod fajla: {str(e)}")
            raise

    @staticmethod
    def _process_html(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira HTML fajlove"""
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # Uklanjamo HTML tagove i čistimo tekst
            text = re.sub(r'<[^>]+>', '', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if not text:
                raise Exception("Nije moguće izvući tekst iz HTML fajla")
            
            # Kreiramo semantic chunk-ove
            chunks = DocumentProcessor._create_semantic_chunks(text, chunk_size, overlap)
            
            for chunk_idx, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk": chunk_idx + 1,
                        "total_chunks": len(chunks),
                        "type": "html"
                    }
                })
            
            logger.info(f"HTML fajl podeljen u {len(chunks)} chunk-ova")
            return documents
        except Exception as e:
            logger.error(f"Greška pri procesiranju HTML fajla: {str(e)}")
            raise

    @staticmethod
    def _process_json(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira JSON fajlove"""
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Konvertujemo JSON u čitljiv tekst
            text = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Kreiramo semantic chunk-ove
            chunks = DocumentProcessor._create_semantic_chunks(text, chunk_size, overlap)
            
            for chunk_idx, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk": chunk_idx + 1,
                        "total_chunks": len(chunks),
                        "type": "json"
                    }
                })
            
            logger.info(f"JSON fajl podeljen u {len(chunks)} chunk-ova")
            return documents
        except Exception as e:
            logger.error(f"Greška pri procesiranju JSON fajla: {str(e)}")
            raise

    @staticmethod
    def _process_yaml(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira YAML fajlove"""
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            # Konvertujemo YAML u čitljiv tekst
            text = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            
            # Kreiramo semantic chunk-ove
            chunks = DocumentProcessor._create_semantic_chunks(text, chunk_size, overlap)
            
            for chunk_idx, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk": chunk_idx + 1,
                        "total_chunks": len(chunks),
                        "type": "yaml"
                    }
                })
            
            logger.info(f"YAML fajl podeljen u {len(chunks)} chunk-ova")
            return documents
        except Exception as e:
            logger.error(f"Greška pri procesiranju YAML fajla: {str(e)}")
            raise

    @staticmethod
    def _process_xml(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira XML fajlove"""
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                xml_content = file.read()
            
            # Uklanjamo XML tagove i čistimo tekst
            text = re.sub(r'<[^>]+>', '', xml_content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if not text:
                raise Exception("Nije moguće izvući tekst iz XML fajla")
            
            # Kreiramo semantic chunk-ove
            chunks = DocumentProcessor._create_semantic_chunks(text, chunk_size, overlap)
            
            for chunk_idx, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk": chunk_idx + 1,
                        "total_chunks": len(chunks),
                        "type": "xml"
                    }
                })
            
            logger.info(f"XML fajl podeljen u {len(chunks)} chunk-ova")
            return documents
        except Exception as e:
            logger.error(f"Greška pri procesiranju XML fajla: {str(e)}")
            raise

    @staticmethod
    def _process_csv(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira CSV fajlove"""
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                rows = list(csv_reader)
            
            if not rows:
                raise Exception("CSV fajl je prazan")
            
            # Konvertujemo CSV u čitljiv tekst
            text_lines = []
            for i, row in enumerate(rows):
                if i == 0:  # Header
                    text_lines.append(f"Kolone: {', '.join(row)}")
                else:
                    text_lines.append(f"Red {i}: {', '.join(row)}")
            
            text = "\n".join(text_lines)
            
            # Kreiramo semantic chunk-ove
            chunks = DocumentProcessor._create_semantic_chunks(text, chunk_size, overlap)
            
            for chunk_idx, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk": chunk_idx + 1,
                        "total_chunks": len(chunks),
                        "type": "csv",
                        "rows": len(rows)
                    }
                })
            
            logger.info(f"CSV fajl podeljen u {len(chunks)} chunk-ova")
            return documents
        except Exception as e:
            logger.error(f"Greška pri procesiranju CSV fajla: {str(e)}")
            raise

    @staticmethod
    def _process_pdf(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira PDF fajl sa semantic chunking-om"""
        documents = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                logger.info(f"PDF fajl ima {total_pages} strana")
                
                for page_num in range(total_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if not text.strip():
                            logger.warning(f"Strana {page_num + 1} je prazna")
                            continue
                        
                        # Kreiramo semantic chunk-ove za ovu stranicu
                        chunks = DocumentProcessor._create_semantic_chunks(text, chunk_size, overlap)
                        
                        for chunk_idx, chunk in enumerate(chunks):
                            documents.append({
                                "content": chunk,
                                "metadata": {
                                    "source": file_path,
                                    "page": page_num + 1,
                                    "chunk": chunk_idx + 1,
                                    "total_chunks": len(chunks),
                                    "type": "pdf"
                                }
                            })
                        
                        logger.info(f"Strana {page_num + 1} podeljena u {len(chunks)} chunk-ova")
                    except Exception as e:
                        logger.error(f"Greška pri procesiranju stranice {page_num + 1}: {str(e)}")
                        continue
                        
            if not documents:
                logger.error("Nijedna stranica nije uspešno procesirana")
                raise Exception("Nije moguće izvući tekst iz PDF fajla")
            
            logger.info(f"Ukupno kreirano {len(documents)} chunk-ova")
            return documents
        except Exception as e:
            logger.error(f"Greška pri procesiranju PDF fajla: {str(e)}")
            raise

    @staticmethod
    def _process_docx(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Procesira DOCX fajl sa semantic chunking-om"""
        documents = []
        try:
            doc = docx.Document(file_path)
            logger.info(f"Procesiranje DOCX fajla: {file_path}")
            
            # Izvlačimo sav tekst iz dokumenta
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)
            
            text = "\n".join(full_text)
            
            if not text.strip():
                logger.error("Nijedan paragraf nije uspešno procesiran")
                raise Exception("Nije moguće izvući tekst iz DOCX fajla")
            
            # Kreiramo semantic chunk-ove
            chunks = DocumentProcessor._create_semantic_chunks(text, chunk_size, overlap)
            
            for chunk_idx, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk": chunk_idx + 1,
                        "total_chunks": len(chunks),
                        "type": "docx"
                    }
                })
            
            logger.info(f"DOCX fajl podeljen u {len(chunks)} chunk-ova")
            return documents
        except Exception as e:
            logger.error(f"Greška pri procesiranju DOCX fajla: {str(e)}")
            raise 
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Učitavanje kredencijala iz environment varijabli
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

logger.info(f"Učitavam Supabase konfiguraciju...")
logger.info(f"SUPABASE_URL je postavljen: {'Da' if SUPABASE_URL else 'Ne'}")
logger.info(f"SUPABASE_SERVICE_KEY je postavljen: {'Da' if SUPABASE_SERVICE_KEY else 'Ne'}")

# Inicijalizacija Supabase klijenta
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        logger.info("Pokušavam da inicijalizujem Supabase klijenta...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("Supabase klijent je uspešno inicijalizovan!")
    except Exception as e:
        logger.error(f"Greška pri inicijalizaciji Supabase klijenta: {e}")
        supabase = None
else:
    logger.warning("Supabase kredencijali nisu postavljeni - koriste se mock vrednosti")
    supabase = None

# Mock klijent za development
class MockSupabaseClient:
    def __init__(self):
        pass
    
    def table(self, table_name):
        return self.MockTable(table_name)
    
    class MockTable:
        def __init__(self, table_name):
            self.table_name = table_name
        
        def select(self, *args):
            return self.MockQuery(self.table_name)
        
        def insert(self, data):
            return self.MockQuery(self.table_name)
        
        def update(self, data):
            return self.MockQuery(self.table_name)
        
        def delete(self):
            return self.MockQuery(self.table_name)
        
        class MockQuery:
            def __init__(self, table_name=None):
                self.table_name = table_name
                self.order_field = None
                self.order_desc = False
                self.eq_field = None
                self.eq_value = None
            
            def order(self, field, desc=False):
                self.order_field = field
                self.order_desc = desc
                return self
            
            def eq(self, field, value):
                self.eq_field = field
                self.eq_value = value
                return self
            
            def execute(self):
                # Mock podaci za testiranje
                mock_data = [
                    {
                        "id": 1,
                        "filename": "Liječenje prijeloma bedrene kosti.pdf",
                        "file_type": "PDF",
                        "file_size": 1024000,
                        "page_count": 42,
                        "created_at": "2024-01-15T10:30:00Z",
                        "status": "processed"
                    },
                    {
                        "id": 2,
                        "filename": "BSTDB Financial Statements for 2021.pdf",
                        "file_type": "PDF",
                        "file_size": 2048000,
                        "page_count": 75,
                        "created_at": "2024-01-16T14:20:00Z",
                        "status": "processed"
                    },
                    {
                        "id": 3,
                        "filename": "BPPV.pdf",
                        "file_type": "PDF",
                        "file_size": 512000,
                        "page_count": 5,
                        "created_at": "2024-01-17T09:15:00Z",
                        "status": "processed"
                    },
                    {
                        "id": 4,
                        "filename": "Anatomija srca.pdf",
                        "file_type": "PDF",
                        "file_size": 1536000,
                        "page_count": 32,
                        "created_at": "2024-01-18T16:45:00Z",
                        "status": "processed"
                    }
                ]
                
                # Ako je za documents tabelu, vrati dokumente
                if self.table_name == 'documents':
                    # Sortiraj po created_at ako je order postavljen
                    if self.order_field == 'created_at':
                        mock_data.sort(key=lambda x: x['created_at'], reverse=self.order_desc)
                    return type('MockResult', (), {'data': mock_data})()
                
                # Ako je za messages tabelu, vrati praznu listu
                elif self.table_name == 'messages':
                    return type('MockResult', (), {'data': []})()
                
                # Ako je za document_pages tabelu, vrati stranice
                elif self.table_name == 'document_pages':
                    if self.eq_field == 'document_id':
                        # Mock stranice za dokument
                        pages_data = [
                            {
                                "id": 1,
                                "document_id": self.eq_value,
                                "page_number": 1,
                                "content": "Ovo je sadržaj prve stranice dokumenta.",
                                "created_at": "2024-01-15T10:30:00Z"
                            },
                            {
                                "id": 2,
                                "document_id": self.eq_value,
                                "page_number": 2,
                                "content": "Ovo je sadržaj druge stranice dokumenta.",
                                "created_at": "2024-01-15T10:30:00Z"
                            }
                        ]
                        return type('MockResult', (), {'data': pages_data})()
                    else:
                        # Vrati sve stranice
                        all_pages_data = [
                            {
                                "id": 1,
                                "document_id": "doc-1",
                                "page_number": 1,
                                "content": "Liječenje prijeloma bedrene kosti - prva stranica. Prijelom bedrene kosti je ozbiljna povreda koja zahteva hitnu medicinsku intervenciju.",
                                "metadata": {"source": "Liječenje prijeloma bedrene kosti.pdf", "page": 1}
                            },
                            {
                                "id": 2,
                                "document_id": "doc-1",
                                "page_number": 2,
                                "content": "Dijagnoza prijeloma bedrene kosti se postavlja na osnovu kliničkog pregleda i radioloških snimaka. CT snimak je najprecizniji metod.",
                                "metadata": {"source": "Liječenje prijeloma bedrene kosti.pdf", "page": 2}
                            },
                            {
                                "id": 3,
                                "document_id": "doc-2",
                                "page_number": 1,
                                "content": "BSTDB Financial Statements for 2021 - prva stranica. Godišnji finansijski izveštaj kompanije za 2021. godinu.",
                                "metadata": {"source": "BSTDB Financial Statements for 2021.pdf", "page": 1}
                            },
                            {
                                "id": 4,
                                "document_id": "doc-3",
                                "page_number": 1,
                                "content": "BPPV (Benign Paroxysmal Positional Vertigo) - prva stranica. BPPV je najčešći uzrok vrtoglavice kod odraslih.",
                                "metadata": {"source": "BPPV.pdf", "page": 1}
                            },
                            {
                                "id": 5,
                                "document_id": "doc-4",
                                "page_number": 1,
                                "content": "Anatomija srca - prva stranica. Srce je mišićni organ koji pumpa krv kroz krvotok.",
                                "metadata": {"source": "Anatomija srca.pdf", "page": 1}
                            }
                        ]
                        return type('MockResult', (), {'data': all_pages_data})()
                
                return type('MockResult', (), {'data': mock_data})()
    
    def rpc(self, func_name, params):
        return type('MockRPC', (), {'data': None})()

# Ako nemamo pravi klijent, koristimo mock
if supabase is None:
    logger.info("Koriste se mock vrednosti za Supabase - neke funkcionalnosti možda neće raditi")
    supabase = MockSupabaseClient() 
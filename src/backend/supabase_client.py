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
        self.table = self.MockTable()
    
    class MockTable:
        def select(self, *args):
            return self.MockQuery()
        
        def insert(self, data):
            return self.MockQuery()
        
        def update(self, data):
            return self.MockQuery()
        
        def delete(self):
            return self.MockQuery()
        
        class MockQuery:
            def execute(self):
                return type('MockResult', (), {'data': []})()
    
    def rpc(self, func_name, params):
        return type('MockRPC', (), {'data': None})()

# Ako nemamo pravi klijent, koristimo mock
if supabase is None:
    logger.info("Koriste se mock vrednosti za Supabase - neke funkcionalnosti možda neće raditi")
    supabase = MockSupabaseClient() 
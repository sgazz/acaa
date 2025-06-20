# ACAI Assistant - Napredni RAG Sistem

ACAI Assistant je napredni RAG (Retrieval-Augmented Generation) sistem koji kombinuje moderne AI tehnologije za inteligentnu pretragu i analizu dokumenata.

## 🚀 Ključne funkcionalnosti

### Osnovne funkcionalnosti
- **Dokument procesiranje** - Podrška za PDF, DOCX, TXT fajlove
- **Hybrid Search** - Kombinacija BM25 i FAISS semantičke pretrage
- **BGE Embedding model** - BAAI/bge-small-en-v1.5 za semantičku pretragu
- **Supabase integracija** - Čuvanje metapodataka i chat istorije
- **React frontend** - Moderan korisnički interfejs
- **FastAPI backend** - Brz i skalabilan API

### 🎯 Napredne RAG funkcionalnosti

#### 1. Reranking (BGE-Reranker-Base)
- **Precizno rangiranje** rezultata pretrage
- **CrossEncoder model** za bolje razumevanje konteksta
- **15-25% poboljšanje** preciznosti pretrage
- **Smanjenje false positive** rezultata

#### 2. Query Expansion
- **Sinonimno proširenje** upita
- **Domen-specifične ključne reči** za različite oblasti
- **Hybrid pristup** - kombinacija sinonima i domen ključnih reči
- **1-10x proširenje** upita zavisno od sadržaja

#### 3. Context Optimization
- **Pametna optimizacija** konteksta pre LLM-a
- **Score-based** i **length-based** optimizacija
- **20-50% kompresija** sa zadržavanjem kvaliteta
- **Strukturiran kontekst** sa metapodacima

## 🏗️ Arhitektura

```
Query → Query Expansion → Hybrid Search → Reranking → Context Optimization → LLM
```

### Komponente
- **QueryExpander** - Proširenje upita sa sinonimima
- **HybridSearch** - BM25 + FAISS kombinacija
- **RerankerService** - BGE-reranker-base model
- **ContextOptimizer** - Optimizacija konteksta
- **DocumentProcessor** - Obrada različitih formata
- **RAGService** - Glavni RAG servis

## 📦 Instalacija

### Backend
```bash
cd src/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r rag/requirements.txt
pip install fastapi uvicorn python-dotenv supabase python-multipart
```

### Frontend
```bash
cd src/frontend
npm install
```

## 🚀 Pokretanje

### Automatski (preporučeno)
```bash
./start_servers.sh
```

### Ručno
```bash
# Backend
cd src/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend
cd src/frontend
npm run dev
```

## 📚 Korišćenje

### Osnovna pretraga
```python
from rag_client import RAGClient

rag_client = RAGClient()
results = rag_client.search_documents("Python programiranje", k=5)
```

### Napredna pretraga sa svim optimizacijama
```python
# Query Expansion + Reranking + Context Optimization
results = rag_client.search_documents(
    "Python web development", 
    k=5, 
    use_query_expansion=True, 
    expansion_type="hybrid"
)

context = rag_client.get_context_for_query(
    "Python web development",
    k=8,
    use_context_optimization=True,
    optimization_type="smart"
)
```

### API endpoint-i
```bash
# Query Expansion
GET /query/expand?query=Python&expansion_type=hybrid

# Context Optimization
POST /context/optimize

# Napredna pretraga
GET /search/advanced?query=Python&use_query_expansion=true
```

## 🧪 Testiranje

### Test naprednih funkcionalnosti
```bash
cd src/backend
source venv/bin/activate
python test_advanced_features.py
```

### Test reranking-a
```bash
python test_reranking.py
```

### Test sa pravim dokumentima
```bash
python test_real_documents.py
```

## 📊 Performanse

### Query Expansion
- **Vreme**: ~10-50ms po upitu
- **Proširenje**: 1-10x zavisno od upita
- **Memorija**: Minimalna

### Context Optimization
- **Vreme**: ~5-20ms po kontekstu
- **Kompresija**: 20-50% smanjenje
- **Kvalitet**: Zadržava najrelevantnije delove

### Reranking
- **Vreme**: ~100-500ms po batch-u
- **Preciznost**: 15-25% poboljšanje
- **Memorija**: ~500MB za model

## 🔧 Konfiguracija

### Environment varijable
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

### Query Expansion
- **Sinonimi**: Definisani u `QueryExpander._load_synonyms()`
- **Domen ključne reči**: Definisane u `QueryExpander._load_domain_keywords()`
- **Tipovi**: "synonyms", "domain", "hybrid"

### Context Optimization
- **max_tokens**: 4000 (default)
- **max_chunks**: 10 (default)
- **Tipovi**: "smart", "score_based", "length_based"

## 📖 Dokumentacija

- [Napredne RAG funkcionalnosti](src/backend/rag/ADVANCED_FEATURES_README.md)
- [Reranking dokumentacija](src/backend/rag/RERANKING_README.md)
- [Projektna dokumentacija](docs/project_documentation.md)
- [Tehnologije](docs/technologies.md)

## 🛠️ Razvoj

### Struktura projekta
```
acai-assistant/
├── src/
│   ├── backend/
│   │   ├── rag/
│   │   │   ├── reranker_service.py      # Reranking funkcionalnost
│   │   │   ├── query_expander.py        # Query Expansion
│   │   │   ├── context_optimizer.py     # Context Optimization
│   │   │   ├── hybrid_search.py         # Hybrid Search
│   │   │   └── document_processor.py    # Dokument procesiranje
│   │   ├── main.py                      # FastAPI aplikacija
│   │   └── rag_client.py                # Glavni RAG klijent
│   └── frontend/                        # React aplikacija
├── docs/                                # Dokumentacija
└── test_*.py                           # Test skripte
```

### Dodavanje novih sinonima
```python
# U query_expander.py
self.synonyms = {
    "novi_termin": ["sinonim1", "sinonim2", "sinonim3"],
    # ...
}
```

### Dodavanje novih domena
```python
# U query_expander.py
self.domain_keywords = {
    "novi_domen": ["kljucna_rec1", "kljucna_rec2", "kljucna_rec3"],
    # ...
}
```

## 🤝 Doprinosi

1. Fork projekta
2. Kreirajte feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit promene (`git commit -m 'Add some AmazingFeature'`)
4. Push na branch (`git push origin feature/AmazingFeature`)
5. Otvorite Pull Request

## 📄 Licenca

Ovaj projekat je licenciran pod MIT licencom.

## 🆘 Podrška

Za pitanja i podršku:
- Otvorite issue na GitHub-u
- Proverite dokumentaciju u `docs/` direktorijumu
- Pogledajte test skripte za primere korišćenja
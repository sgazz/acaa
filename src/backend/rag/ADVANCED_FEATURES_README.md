# Napredne RAG funkcionalnosti

## Pregled

Ovaj dokument opisuje tri napredne funkcionalnosti dodate u RAG sistem:

1. **Reranking (BGE-Reranker-Base)** - Precizno rangiranje rezultata
2. **Query Expansion** - Proširenje upita sa sinonimima i domen-specifičnim terminima
3. **Context Optimization** - Optimizacija konteksta pre slanja LLM-u

## Arhitektura

```
Query → Query Expansion → Hybrid Search → Reranking → Context Optimization → LLM
```

### 1. Reranking (BGE-Reranker-Base)

**Fajl:** `reranker_service.py`

Reranking koristi CrossEncoder model za precizno rangiranje rezultata pretrage.

**Prednosti:**
- Precizniji ranking od embedding similarity
- Bolje razumevanje konteksta
- Smanjenje false positive rezultata

**Korišćenje:**
```python
from rag.reranker_service import RerankerService

reranker = RerankerService()
results = reranker.rerank(query, documents, top_k=5)
```

### 2. Query Expansion

**Fajl:** `query_expander.py`

Query Expansion proširuje upite sa sinonimima i domen-specifičnim ključnim rečima.

**Tipovi proširenja:**
- **synonyms**: Samo sinonimni termini
- **domain**: Domen-specifične ključne reči
- **hybrid**: Kombinacija oba pristupa

**Korišćenje:**
```python
from rag.query_expander import QueryExpander

expander = QueryExpander()
expanded_queries = expander.expand_query("Python programiranje", "hybrid")
```

**Primer proširenja:**
```
Originalni upit: "Python programiranje"
Prošireni upiti:
- programski jezik programiranje
- python programiranje  
- py programiranje
- kod programiranje
- razvoj programiranje
- development programiranje
- kodiranje programiranje
```

### 3. Context Optimization

**Fajl:** `context_optimizer.py`

Context Optimization optimizuje kontekst pre slanja LLM-u na osnovu dužine, score-a i relevantnosti.

**Tipovi optimizacije:**
- **smart**: Kombinuje score, dužinu i relevantnost
- **score_based**: Samo na osnovu score-a
- **length_based**: Samo na osnovu dužine

**Korišćenje:**
```python
from rag.context_optimizer import ContextOptimizer

optimizer = ContextOptimizer(max_tokens=4000, max_chunks=10)
context_result = optimizer.optimize_context(documents, query, "smart")
```

## Integracija u RAGClient

Sve funkcionalnosti su integrisane u `RAGClient` klasu:

```python
class RAGClient:
    def __init__(self):
        self.reranker = RerankerService()
        self.query_expander = QueryExpander()
        self.context_optimizer = ContextOptimizer()
    
    def search_documents(self, query, k=3, use_query_expansion=True, expansion_type="hybrid"):
        # Query Expansion + Hybrid Search + Reranking
    
    def get_context_for_query(self, query, k=8, use_context_optimization=True, optimization_type="smart"):
        # Context Optimization
```

## API Endpoint-i

### Query Expansion
```
GET /query/expand?query=Python&expansion_type=hybrid
```

### Context Optimization
```
POST /context/optimize
{
    "query": "Python programiranje",
    "documents": [...],
    "optimization_type": "smart"
}
```

### Napredna pretraga
```
GET /search/advanced?query=Python&use_query_expansion=true&use_context_optimization=true
```

## Konfiguracija

### Query Expansion
- **Sinonimi**: Definisani u `_load_synonyms()` metodi
- **Domen ključne reči**: Definisane u `_load_domain_keywords()` metodi
- **Tipovi proširenja**: "synonyms", "domain", "hybrid"

### Context Optimization
- **max_tokens**: Maksimalan broj tokena (default: 4000)
- **max_chunks**: Maksimalan broj chunk-ova (default: 10)
- **Tipovi optimizacije**: "smart", "score_based", "length_based"

### Reranking
- **Model**: BAAI/bge-reranker-base
- **top_k**: Broj rezultata za vraćanje

## Testiranje

### Osnovni test
```bash
python test_advanced_features.py
```

### Test sa pravim dokumentima
```bash
python test_real_documents.py
```

### Test reranking-a
```bash
python test_reranking.py
```

## Performanse

### Query Expansion
- **Vreme**: ~10-50ms po upitu
- **Proširenje**: 1-10x zavisno od upita
- **Memorija**: Minimalna (samo rečnik)

### Context Optimization
- **Vreme**: ~5-20ms po kontekstu
- **Kompresija**: 20-50% smanjenje
- **Kvalitet**: Zadržava najrelevantnije delove

### Reranking
- **Vreme**: ~100-500ms po batch-u
- **Preciznost**: 15-25% poboljšanje
- **Memorija**: ~500MB za model

## Primeri korišćenja

### 1. Osnovna pretraga sa svim optimizacijama
```python
rag_client = RAGClient()
results = rag_client.search_documents("Python web development", k=5)
```

### 2. Pretraga bez Query Expansion
```python
results = rag_client.search_documents("Python web development", k=5, use_query_expansion=False)
```

### 3. Context Optimization sa custom parametrima
```python
context = rag_client.get_context_for_query(
    "Python web development", 
    k=10, 
    optimization_type="length_based"
)
```

### 4. Direktno korišćenje komponenti
```python
# Query Expansion
expander = QueryExpander()
expanded = expander.expand_query("Python", "hybrid")

# Context Optimization
optimizer = ContextOptimizer(max_tokens=2000)
context = optimizer.optimize_context(documents, query, "smart")

# Reranking
reranker = RerankerService()
ranked = reranker.rerank(query, documents, top_k=5)
```

## Troubleshooting

### Česti problemi

1. **Query Expansion ne proširuje upit**
   - Proverite da li su termini u rečniku sinonima
   - Proverite da li su domen ključne reči definisane

2. **Context Optimization vraća prazan kontekst**
   - Proverite da li su dokumenti filtrirani
   - Smanjite `max_tokens` ili `max_chunks`

3. **Reranking spor**
   - Koristite manji `top_k`
   - Razmislite o batch procesiranju

### Debug logovanje

Sve komponente imaju detaljno logovanje:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Buduća poboljšanja

1. **Dinamički sinonimi** - Učitavanje iz baze podataka
2. **ML-based Query Expansion** - Korišćenje LLM-a za proširenje
3. **Adaptivna Context Optimization** - Prilagođavanje na osnovu LLM-a
4. **Caching** - Keširanje rezultata za brže odgovore
5. **A/B testing** - Testiranje različitih strategija 
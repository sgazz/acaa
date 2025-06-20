# Reranking funkcionalnost

## Pregled

Reranking je dodan u RAG sistem za poboljšanje preciznosti pretrage. Koristi BGE-reranker-base model koji je specijalizovan za reranking zadatke.

## Arhitektura

```
Query → Hybrid Search (BM25 + FAISS) → Reranking → Final Results
```

1. **Hybrid Search**: Kombinuje BM25 (leksička pretraga) i FAISS (semantička pretraga)
2. **Reranking**: Koristi CrossEncoder model za precizno rangiranje rezultata
3. **Final Results**: Vraća najbolje rerankovane rezultate

## Komponente

### RerankerService (`reranker_service.py`)

Glavna klasa za reranking funkcionalnost:

```python
from rag.reranker_service import RerankerService

# Inicijalizacija
reranker = RerankerService(model_name="BAAI/bge-reranker-base")

# Osnovni reranking
results = reranker.rerank(query, documents, top_k=5)

# Reranking sa metapodacima
result_with_stats = reranker.rerank_with_metadata(query, documents, top_k=5)
```

### Integracija u RAGClient

Reranking je automatski integrisan u `search_documents` metodu:

```python
# Automatski koristi hybrid search + reranking
results = rag_client.search_documents("Python programiranje", k=5)
```

## API Endpoints

### Standardna pretraga (sa reranking-om)
```
GET /documents/search?query=Python&k=5
```

### Detaljna pretraga sa reranking statistikama
```
GET /documents/search-with-rerank?query=Python&k=5
```

Response format:
```json
{
  "query": "Python",
  "results": [
    {
      "content": "...",
      "metadata": {...},
      "rerank_score": 0.85,
      "semantic_score": 0.72,
      "lexical_score": 0.68
    }
  ],
  "statistics": {
    "total_documents": 10,
    "reranked_documents": 5,
    "average_score": 0.75,
    "max_score": 0.85,
    "min_score": 0.65,
    "score_range": 0.20
  },
  "initial_results_count": 15
}
```

## Konfiguracija

### Model
- **Default model**: `BAAI/bge-reranker-base`
- **Dimenzija**: 768
- **Jezik**: Multilingual (podržava srpski)

### Parametri
- `top_k`: Broj rezultata za vraćanje (default: 5)
- `initial_k`: Broj rezultata iz hybrid search-a za reranking (default: k * 3)

## Performanse

### Prednosti
- **Preciznost**: Značajno poboljšava ranking rezultata
- **Kontekst**: Bolje razumevanje upita i sadržaja
- **Fleksibilnost**: Može se koristiti sa različitim embedding modelima

### Troškovi
- **Vreme**: Dodatno vreme za reranking (100-500ms)
- **Memorija**: CrossEncoder model (~500MB)
- **CPU**: Intenzivniji od embedding-a

## Testiranje

### Pokretanje testova
```bash
cd src/backend
python test_reranking.py
```

### Test scenariji
1. **Osnovni reranking**: Testira reranking sa fiksnim dokumentima
2. **Hybrid + Reranking**: Testira kompletnu integraciju

## Debugging

### Logovanje
Reranking servis loguje detaljne informacije:
```
INFO: Rerankujem 10 dokumenata za upit: 'Python programiranje'
INFO: Reranking završen. Top score: 0.8500
```

### Score interpretacija
- **0.0-0.3**: Slabo relevantan
- **0.3-0.6**: Umereno relevantan  
- **0.6-0.8**: Dobro relevantan
- **0.8-1.0**: Veoma relevantan

## Troubleshooting

### Česti problemi

1. **Model se ne učitava**
   ```
   ERROR: Greška pri učitavanju reranking modela
   ```
   **Rešenje**: Proverite internet konekciju i disk prostor

2. **Spori reranking**
   ```
   INFO: Reranking završen. Top score: 0.8500
   ```
   **Rešenje**: Smanjite broj dokumenata za reranking

3. **Nedostajući score-ovi**
   ```
   WARNING: Dokument sa praznim sadržajem
   ```
   **Rešenje**: Proverite da li dokumenti imaju sadržaj

### Fallback mehanizam
Ako reranking ne uspe, sistem automatski koristi originalne rezultate iz hybrid search-a.

## Buduća poboljšanja

1. **Query Expansion**: Dodavanje sinonimnih terma
2. **Context Optimization**: Optimizacija konteksta za LLM
3. **Batch Processing**: Reranking više upita odjednom
4. **Caching**: Keširanje reranking rezultata 
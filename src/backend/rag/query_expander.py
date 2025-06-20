from typing import List, Dict, Any
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

class QueryExpander:
    def __init__(self):
        """
        Inicijalizuje Query Expander servis
        """
        self.synonyms = self._load_synonyms()
        self.domain_keywords = self._load_domain_keywords()
        logger.info("Query Expander inicijalizovan")
    
    def _load_synonyms(self) -> Dict[str, List[str]]:
        """Učitava sinonimne termine"""
        return {
            # Programski jezici
            "python": ["python", "py", "programski jezik", "kod"],
            "javascript": ["javascript", "js", "ecmascript", "programski jezik"],
            "java": ["java", "programski jezik"],
            "c++": ["c++", "cpp", "c plus plus", "programski jezik"],
            
            # Web development
            "web": ["web", "internet", "online", "aplikacija"],
            "frontend": ["frontend", "front-end", "korisnički interfejs", "ui", "ux"],
            "backend": ["backend", "back-end", "server", "api"],
            "fullstack": ["fullstack", "full-stack", "kompletan sistem"],
            
            # AI/ML
            "ai": ["ai", "artificial intelligence", "veštačka inteligencija"],
            "machine learning": ["machine learning", "ml", "mašinsko učenje", "ai"],
            "deep learning": ["deep learning", "dl", "duboko učenje", "neural network"],
            
            # Baze podataka
            "database": ["database", "baza podataka", "db", "podaci"],
            "sql": ["sql", "structured query language", "upitni jezik"],
            "nosql": ["nosql", "not only sql", "dokumentna baza"],
            
            # DevOps
            "docker": ["docker", "kontejner", "container", "deployment"],
            "kubernetes": ["kubernetes", "k8s", "orchestration", "kontejneri"],
            "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],
            
            # Framework-ovi
            "react": ["react", "reactjs", "frontend framework", "ui library"],
            "angular": ["angular", "angularjs", "frontend framework"],
            "vue": ["vue", "vuejs", "frontend framework"],
            "django": ["django", "python framework", "web framework"],
            "flask": ["flask", "python framework", "micro framework"],
            "fastapi": ["fastapi", "python framework", "api framework"],
            
            # Opšti termini
            "programiranje": ["programiranje", "kodiranje", "development", "razvoj"],
            "aplikacija": ["aplikacija", "app", "program", "softver"],
            "sistem": ["sistem", "system", "platforma", "infrastruktura"],
            "tehnologija": ["tehnologija", "technology", "teh", "tech"],
            "implementacija": ["implementacija", "implementation", "realizacija"],
            "optimizacija": ["optimizacija", "optimization", "poboljšanje"],
            "testiranje": ["testiranje", "testing", "test", "verifikacija"],
            "dokumentacija": ["dokumentacija", "documentation", "docs", "dokumenti"],
            "arhitektura": ["arhitektura", "architecture", "dizajn", "struktura"],
            "performanse": ["performanse", "performance", "brzina", "efikasnost"],
            "sigurnost": ["sigurnost", "security", "bezbednost", "zaštita"],
            "skalabilnost": ["skalabilnost", "scalability", "proširivost"],
            "održavanje": ["održavanje", "maintenance", "maintenance", "servis"],
        }
    
    def _load_domain_keywords(self) -> Dict[str, List[str]]:
        """Učitava ključne reči za specifične domene"""
        return {
            "programiranje": [
                "kod", "algoritam", "funkcija", "klasa", "objekt", "metoda", 
                "varijabla", "tip", "interfejs", "biblioteka", "framework",
                "debug", "error", "exception", "log", "console", "terminal"
            ],
            "web": [
                "html", "css", "http", "https", "url", "api", "rest", "graphql",
                "json", "xml", "cookie", "session", "authentication", "authorization",
                "responsive", "mobile", "desktop", "browser", "server", "client"
            ],
            "ai_ml": [
                "model", "training", "inference", "prediction", "classification",
                "regression", "clustering", "neural network", "tensor", "gradient",
                "optimization", "loss", "accuracy", "precision", "recall", "f1"
            ],
            "database": [
                "table", "index", "query", "join", "select", "insert", "update",
                "delete", "transaction", "commit", "rollback", "normalization",
                "foreign key", "primary key", "constraint", "trigger", "view"
            ],
            "devops": [
                "deployment", "ci/cd", "pipeline", "build", "test", "deploy",
                "monitoring", "logging", "alerting", "backup", "recovery",
                "load balancer", "proxy", "cache", "cdn", "ssl", "tls"
            ]
        }
    
    def expand_query(self, query: str, expansion_type: str = "hybrid") -> List[str]:
        """
        Proširuje upit sa sinonimima i povezanim terminima
        
        Args:
            query: Originalni upit
            expansion_type: Tip proširenja ("synonyms", "domain", "hybrid")
            
        Returns:
            Lista proširenih upita
        """
        logger.info(f"Proširujem upit: '{query}' (tip: {expansion_type})")
        
        expanded_queries = [query]  # Uvek uključujemo originalni upit
        
        # Tokenizujemo upit
        tokens = self._tokenize(query)
        
        if expansion_type == "synonyms" or expansion_type == "hybrid":
            synonym_expansions = self._expand_with_synonyms(tokens)
            expanded_queries.extend(synonym_expansions)
        
        if expansion_type == "domain" or expansion_type == "hybrid":
            domain_expansions = self._expand_with_domain_keywords(tokens)
            expanded_queries.extend(domain_expansions)
        
        # Uklanjamo duplikate i prazne upite
        unique_queries = list(set([q.strip() for q in expanded_queries if q.strip()]))
        
        logger.info(f"Proširenje završeno. Originalno: 1, Prošireno: {len(unique_queries)}")
        return unique_queries
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenizuje tekst u reči"""
        # Konvertujemo u lowercase i uklanjamo specijalne karaktere
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Delimo na reči i uklanjamo prazne stringove
        tokens = [word for word in text.split() if word.strip()]
        return tokens
    
    def _expand_with_synonyms(self, tokens: List[str]) -> List[str]:
        """Proširuje upit sa sinonimima"""
        expansions = []
        
        for token in tokens:
            if token in self.synonyms:
                synonyms = self.synonyms[token]
                for synonym in synonyms:
                    # Zamenjujemo token sa sinonimom
                    new_tokens = tokens.copy()
                    new_tokens[new_tokens.index(token)] = synonym
                    expansions.append(' '.join(new_tokens))
        
        return expansions
    
    def _expand_with_domain_keywords(self, tokens: List[str]) -> List[str]:
        """Proširuje upit sa domen-specifičnim ključnim rečima"""
        expansions = []
        
        # Identifikujemo domen na osnovu tokena
        detected_domains = []
        for token in tokens:
            for domain, keywords in self.domain_keywords.items():
                if token in keywords or any(keyword in token for keyword in keywords):
                    detected_domains.append(domain)
        
        # Dodajemo relevantne ključne reči iz detektovanih domena
        for domain in set(detected_domains):
            domain_keywords = self.domain_keywords[domain]
            for keyword in domain_keywords[:3]:  # Uzimamo top 3 ključne reči
                if keyword not in tokens:
                    new_query = ' '.join(tokens + [keyword])
                    expansions.append(new_query)
        
        return expansions
    
    def expand_query_with_metadata(self, query: str, expansion_type: str = "hybrid") -> Dict[str, Any]:
        """
        Proširuje upit i vraća metapodatke o proširenju
        
        Args:
            query: Originalni upit
            expansion_type: Tip proširenja
            
        Returns:
            Dictionary sa proširenim upitima i metapodacima
        """
        original_tokens = self._tokenize(query)
        expanded_queries = self.expand_query(query, expansion_type)
        
        # Analiziramo proširenje
        expansion_analysis = {
            "original_tokens": original_tokens,
            "detected_domains": self._detect_domains(original_tokens),
            "applied_synonyms": self._get_applied_synonyms(original_tokens),
            "added_keywords": self._get_added_keywords(original_tokens, expanded_queries)
        }
        
        return {
            "original_query": query,
            "expanded_queries": expanded_queries,
            "expansion_type": expansion_type,
            "analysis": expansion_analysis,
            "total_expansions": len(expanded_queries) - 1  # -1 za originalni upit
        }
    
    def _detect_domains(self, tokens: List[str]) -> List[str]:
        """Detektuje domene na osnovu tokena"""
        detected = []
        for token in tokens:
            for domain, keywords in self.domain_keywords.items():
                if token in keywords or any(keyword in token for keyword in keywords):
                    detected.append(domain)
        return list(set(detected))
    
    def _get_applied_synonyms(self, tokens: List[str]) -> Dict[str, List[str]]:
        """Vraća primenjene sinonimne termine"""
        applied = {}
        for token in tokens:
            if token in self.synonyms:
                applied[token] = self.synonyms[token]
        return applied
    
    def _get_added_keywords(self, original_tokens: List[str], expanded_queries: List[str]) -> List[str]:
        """Vraća dodane ključne reči"""
        added = []
        for query in expanded_queries[1:]:  # Preskačemo originalni upit
            query_tokens = self._tokenize(query)
            for token in query_tokens:
                if token not in original_tokens and token not in added:
                    added.append(token)
        return added 
# ACAI Assistant - Podešavanje

## Environment Varijable

Da biste pokrenuli aplikaciju sa pravim Supabase kredencijalima, kreirajte `.env` fajl u root direktorijumu:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=your-supabase-anon-key

# Ollama Configuration (opciono)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:latest

# Backend Configuration
BACKEND_PORT=8001
FRONTEND_PORT=3000

# Development Configuration
DEBUG=true
LOG_LEVEL=INFO
```

## Kako dobiti Supabase kredencijale:

1. Idite na [supabase.com](https://supabase.com)
2. Kreirajte novi projekat
3. Idite na Settings → API
4. Kopirajte:
   - Project URL kao `SUPABASE_URL`
   - anon/public key kao `SUPABASE_SERVICE_KEY`

## Pokretanje aplikacije:

```bash
# Opcija 1: Koristeći skriptu
./ACAI_Assistant.command

# Opcija 2: Ručno
cd src/frontend && npm run dev
cd src/backend && source venv/bin/activate && uvicorn main:app --reload --port 8001
```

## Napomene:

- Bez `.env` fajla, aplikacija će raditi sa mock podacima
- Ollama je opciona - bez nje će se koristiti mock AI odgovori
- Svi osetljivi podaci su zaštićeni `.gitignore` fajlom 
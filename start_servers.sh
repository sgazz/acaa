#!/bin/bash

# Funkcija za proveru da li je port zauzet
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 je zauzet. Pokušavam da ga oslobodim..."
        lsof -ti :$1 | xargs kill -9 2>/dev/null
        sleep 2
        if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
            echo "Nije moguće osloboditi port $1!"
            return 1
        fi
        echo "Port $1 je oslobođen."
    fi
    return 0
}

# Funkcija za pokretanje backend servera
start_backend() {
    if ! check_port 8001; then
        return 1
    fi
    
    echo "Pokrećem backend server..."
    cd src/backend
    source venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --reload --port 8001 &
    BACKEND_PID=$!
    cd ../..
    echo "Backend server je pokrenut (PID: $BACKEND_PID)"
}

# Funkcija za pokretanje frontend servera
start_frontend() {
    if ! check_port 3000; then
        return 1
    fi
    
    echo "Pokrećem frontend server..."
    cd src/frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ../..
    echo "Frontend server je pokrenut (PID: $FRONTEND_PID)"
}

# Funkcija za zaustavljanje servera
stop_servers() {
    echo "Zaustavljam serverse..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "Serversi su zaustavljeni."
    exit 0
}

# Postavljanje trap-a za Ctrl+C
trap stop_servers SIGINT SIGTERM

# Pokretanje servera
echo "Pokrećem ACAI Assistant serverse..."
start_backend
start_frontend

# Čekanje da frontend server bude spreman
echo "Čekam da frontend server bude spreman..."
sleep 5

# Otvaranje browsera
# Pronađi port na kojem frontend radi (3000 ili 3001)
FRONTEND_PORT=3000
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null ; then
    FRONTEND_PORT=3001
fi

APP_URL="http://localhost:$FRONTEND_PORT"
echo "Otvaram aplikaciju u browseru na $APP_URL..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open $APP_URL
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open $APP_URL
elif [[ "$OSTYPE" == "msys" ]]; then
    # Windows
    start $APP_URL
fi

echo "Serversi su pokrenuti! Pritisnite Ctrl+C za zaustavljanje."
wait 
#!/bin/bash

# Navigacija do direktorijuma projekta
cd "/Volumes/External2TB/VS Projects/acai-assistant"

# Provera da li skripta postoji
if [ ! -f "start_servers.sh" ]; then
    echo "Greška: start_servers.sh nije pronađen!"
    echo "Molimo proverite da li ste u pravom direktorijumu."
    read -p "Pritisnite Enter za izlaz..."
    exit 1
fi

# Provera da li je skripta izvršna
if [ ! -x "start_servers.sh" ]; then
    echo "Dodajem izvršne dozvole za start_servers.sh..."
    chmod +x start_servers.sh
fi

echo "Pokrećem ACAI Assistant..."
echo "Pritisnite Ctrl+C za zaustavljanje."

# Pokretanje skripte
./start_servers.sh 
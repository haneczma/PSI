#!/bin/bash
set -e

echo "[*] Budowanie obrazów..."
docker-compose build

echo "[*] Uruchamianie serwera..."
docker-compose up -d server

echo "[*] Uruchamianie klienta..."
docker-compose run client

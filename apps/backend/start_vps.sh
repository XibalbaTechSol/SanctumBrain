#!/bin/bash
# Start script for Project Sanctum VPS (Orchestrator, DB, Redis)

set -e

# Change to the directory of this script
cd "$(dirname "$0")"

echo "[*] Starting Project Sanctum VPS services..."

# Check if docker compose is installed
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null
then
    echo "[!] Error: docker compose could not be found. Please install it."
    exit 1
fi

# Load .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start the containers in the background
docker compose up -d --build

echo "[*] Waiting for services to initialize..."
sleep 5

# Check container status
docker compose ps

echo "[*] VPS is running!"
echo "[*] To view logs: docker compose logs -f orchestrator"
echo "[*] To stop: docker compose down"

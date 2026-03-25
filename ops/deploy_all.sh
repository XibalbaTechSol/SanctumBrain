#!/usr/bin/env bash

# deploy_all.sh
# Production Deployment Script: VPS Backend & Desktop Client.

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==========================================="
echo " 🛡️  Sanctum Brain: Production Deployment"
echo "==========================================="

# Phase I: VPS Backend & Intelligence
echo "[Phase I] Deploying VPS Backend (Intelligence Core, Databases)..."
cd "$PROJECT_ROOT/apps/backend"

if command -v docker-compose &> /dev/null; then
    docker-compose up -d --build
else
    docker compose up -d --build
fi

# Phase II: Web Interface
echo "[Phase II] Preparing VPS Web Interface..."
cd "$PROJECT_ROOT/apps/web"
if command -v npm &> /dev/null; then
    npm install
    # npm run build # Uncomment for true production build
    echo "[Phase II] Web Interface ready."
else
    echo "[Phase II] Warning: npm not found. Skipping Web install."
fi

# Phase III: Desktop/Mobile Client
echo "[Phase III] Building Desktop Client (Vite/Tauri)..."
DESKTOP_DIR="$PROJECT_ROOT/../SanctumDesktop"
if [ -d "$DESKTOP_DIR" ]; then
    cd "$DESKTOP_DIR"
    if command -v npm &> /dev/null; then
        npm install
        npm run build
        echo "[Phase III] Desktop build complete."
    else
        echo "[Phase III] Warning: npm not found. Skipping Desktop build."
    fi
else
    echo "[!] Warning: Desktop directory $DESKTOP_DIR not found. Skipping."
fi

echo "==========================================="
echo " ✅ Production Deployment Initialized."
echo " Living Canvas (VPS UI): http://localhost:8080"
echo " Desktop Sentinel (Client): Port 1420"
echo "==========================================="

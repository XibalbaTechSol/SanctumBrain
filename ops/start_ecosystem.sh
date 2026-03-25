#!/usr/bin/env bash

# start_sanctum_ecosystem.sh
# Production Startup Script: Starts VPS Backend (8080) and Desktop Client (1420).

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IP_ADDR=$(hostname -I | awk '{print $1}')

# Configuration
VPS_PORT=8080
CLIENT_PORT=1420

echo "==========================================="
echo " 🛡️  SANCTUM BRAIN: PRODUCTION STARTUP"
echo "==========================================="

# 1. Start VPS Backend Services (Docker)
echo "[1/3] Launching Sovereign VPS Intelligence Core..."
cd "$PROJECT_ROOT/apps/backend"
if command -v docker-compose &> /dev/null; then
    docker-compose up -d --build
else
    docker compose up -d --build
fi

# 2. Start VPS Web Interface (on port 8080)
echo "[2/3] Launching Living Canvas (VPS UI on port $VPS_PORT)..."
cd "$PROJECT_ROOT/apps/web"
if ! curl -s http://127.0.0.1:$VPS_PORT > /dev/null; then
    npm run dev > next_runtime.log 2>&1 &
    echo "[*] Living Canvas UI started."
else
    echo "[*] Living Canvas UI is already active."
fi

# 3. Start Desktop Sentinel (on port 1420)
echo "[3/3] Launching Desktop Sentinel (Client UI on port $CLIENT_PORT)..."
DESKTOP_DIR="$PROJECT_ROOT/../SanctumDesktop"
if [ -d "$DESKTOP_DIR" ]; then
    cd "$DESKTOP_DIR"
    if ! curl -s http://127.0.0.1:$CLIENT_PORT > /dev/null; then
        npm run dev > vite_runtime.log 2>&1 &
        echo "[*] Desktop Client started."
    else
        echo "[*] Desktop Client is already active."
    fi
else
    echo "[!] Warning: Desktop directory $DESKTOP_DIR not found. Skipping."
fi

echo ""
echo "==========================================="
echo " ✅ SYSTEM ONLINE & SYNCHRONIZED"
echo "==========================================="
echo ""
echo "🎨 VPS BACKEND UI (Living Canvas):"
echo "   -> Local:   http://localhost:$VPS_PORT"
echo "   -> Network: http://$IP_ADDR:$VPS_PORT"
echo ""
echo "🖥️  DESKTOP CLIENT UI (Sentinel):"
echo "   -> Local:   http://localhost:$CLIENT_PORT"
echo ""
echo "🧠 NEURAL CORE (gRPC):"
echo "   -> Endpoint: localhost:50051 (Direct)"
echo ""
echo "==========================================="
echo "To view logs: docker compose -f apps/backend/docker-compose.yml logs -f"
echo "To stop all:  pkill -f next-server && pkill -f vite && docker compose down"
echo "==========================================="

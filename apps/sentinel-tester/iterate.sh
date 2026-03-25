#!/bin/bash
# Neural Workstation Iteration Script
PORT=3008
APP_DIR="/home/xibalba/Projects/SanctumBrain/apps/sentinel-tester"

echo "[*] Initializing Iteration on Port $PORT..."

# 1. Kill existing processes
echo "[*] Cleaning environment..."
fuser -k $PORT/tcp 2>/dev/null
pkill -9 -f "next-server" 2>/dev/null
pkill -9 -f "next-dev" 2>/dev/null

# 2. Build the application
echo "[*] Building production cluster..."
cd $APP_DIR
rm -rf .next
npm run build

if [ $? -ne 0 ]; then
    echo "[!] Build failed. Aborting."
    exit 1
fi

# 3. Start the server
echo "[*] Launching Neural Workstation..."
PORT=$PORT setsid nohup npm run start -- -p $PORT > sentinel_prod.log 2>&1 &

# 4. Wait for readiness
echo "[*] Waiting for uplink..."
MAX_RETRIES=30
COUNT=0
while ! curl -s http://localhost:$PORT > /dev/null; do
    sleep 2
    COUNT=$((COUNT+1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "[!] Uplink failed to stabilize."
        exit 1
    fi
done

echo "[*] Uplink established at http://localhost:$PORT"

# 5. Run Validation
echo "[*] Executing UX Validation Suite..."
npx playwright test tests/ux_validation.spec.ts

# 6. Capture State
echo "[*] Capturing latest UI state..."
npx playwright screenshot --viewport-size=1920,1080 http://localhost:$PORT latest_ui_state.png

echo "[*] Iteration Complete."

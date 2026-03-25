#!/bin/bash

# =================================================================
# SANCTUM OS - GLOBAL DEPLOYMENT SUITE
# =================================================================
# This script handles the end-to-end deployment of:
# 1. VPS Backend & Orchestrator Swarm
# 2. Sentinel Web / Mobile App (Flutter Web)
# 3. Android App (APK - Attempt)

# Configuration
IP="74.208.17.88"
USER="root"
PASS="april1989"
REMOTE_ROOT="/root/sanctum"
LOCAL_PROJECT_ROOT="./Project_Sanctum_OS"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   🛡️ SANCTUM OS - GLOBAL DEPLOYMENT SUITE${NC}"
echo -e "${CYAN}================================================${NC}"

# Check for local directory
if [ ! -d "$LOCAL_PROJECT_ROOT" ]; then
    echo -e "${RED}Error: Project directory not found.${NC}"
    exit 1
fi

# 1. Build Sentinel Web (Mobile/Browser Client)
echo -e "\n${YELLOW}[1/4] Building Sentinel Web Client...${NC}"
cd "$LOCAL_PROJECT_ROOT/client"
flutter build web --release --base-href="/sentinel/"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Build Successful.${NC}"
    mkdir -p "../sentinel-web"
    cp -r build/web/* "../sentinel-web/"
else
    echo -e "${RED}[-] Web Build Failed.${NC}"
fi
cd - > /dev/null

# 2. Synchronize to VPS
echo -e "\n${YELLOW}[2/4] Synchronizing to VPS ($IP)...${NC}"
# Exclude build artifacts and envs
sshpass -p "$PASS" rsync -avz --delete \
    --exclude 'vps/vps_venv' \
    --exclude 'vps/__pycache__' \
    --exclude 'vps/.env' \
    --exclude 'vps/*.log' \
    --exclude 'client/build' \
    --exclude 'client/.dart_tool' \
    --exclude '.git' \
    --exclude '.github' \
    -e "ssh -o StrictHostKeyChecking=no" \
    "$LOCAL_PROJECT_ROOT/" "$USER@$IP:$REMOTE_ROOT/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Sync Successful.${NC}"
else
    echo -e "${RED}[-] Sync Failed.${NC}"
    exit 1
fi

# 3. Refresh Services
echo -e "\n${YELLOW}[3/4] Refreshing Remote Docker Services...${NC}"
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$IP" << EOF
    cd $REMOTE_ROOT/vps
    
    # Force removal of old stubs
    rm -f app/a2a_pb2.py app/a2a_pb2_grpc.py
    
    chmod +x start_vps.sh
    docker compose up -d --build
    
    # Re-compile Protos inside the container
    echo "Re-compiling gRPC Protos..."
    docker exec vps-orchestrator-1 python -m grpc_tools.protoc -I/app/proto --python_out=/app/app --grpc_python_out=/app/app /app/proto/a2a.proto
    
    # Restart to pick up new stubs
    docker compose restart orchestrator dashboard
    
    docker image prune -f
    echo -e "\n${GREEN}Service Status:${NC}"
    docker compose ps
EOF

# 4. Attempt Native Builds (Local)
echo -e "\n${YELLOW}[4/4] Attempting Native Builds (Local)...${NC}"
echo "Note: If these fail, check local environment dependencies."

# Build APK
cd "$LOCAL_PROJECT_ROOT/client"
echo "Building Android APK..."
flutter build apk --release > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] APK Built: build/app/outputs/flutter-apk/app-release.apk${NC}"
    # Upload APK to VPS for direct download from dashboard
    sshpass -p "$PASS" scp -o StrictHostKeyChecking=no build/app/outputs/flutter-apk/app-release.apk "$USER@$IP:$REMOTE_ROOT/sentinel-web/"
    echo -e "${GREEN}[+] APK uploaded to /sentinel/app-release.apk${NC}"
else
    echo -e "${RED}[-] APK Build skipped/failed.${NC}"
fi

echo -e "\n${CYAN}================================================${NC}"
echo -e "${GREEN}   ✨ DEPLOYMENT COMPLETE${NC}"
echo -e "${CYAN}================================================${NC}"
echo -e "Dashboard: http://$IP/"
echo -e "Mobile App: http://$IP/sentinel/"

#!/bin/bash

# =================================================================
# SANCTUM VPS UPDATE & SYNC SCRIPT (AUTOMATED)
# =================================================================
# This script synchronizes the local Project_Sanctum_OS directory
# to the remote VPS and restarts the Docker services.

# Configuration
IP="74.208.17.88"
USER="root"
PASS="april1989"
REMOTE_DIR="/root/sanctum"
LOCAL_DIR="./Project_Sanctum_OS"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   🚀 SANCTUM VPS UPDATE SEQUENCE (AUTO-AUTH)${NC}"
echo -e "${CYAN}================================================${NC}"

# Check for local directory
if [ ! -d "$LOCAL_DIR" ]; then
    echo -e "${RED}Error: Local directory $LOCAL_DIR not found.${NC}"
    echo -e "Please run this script from the repository root."
    exit 1
fi

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}sshpass not found. Installing...${NC}"
    sudo apt-get update && sudo apt-get install -y sshpass
fi

# 1. Synchronize Codebase
echo -e "${YELLOW}[1/2] Synchronizing Codebase via rsync...${NC}"
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
    "$LOCAL_DIR/" "$USER@$IP:$REMOTE_DIR/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Sync Successful.${NC}"
else
    echo -e "${RED}[-] Sync Failed. Please check your credentials or IP.${NC}"
    exit 1
fi

# 2. Refresh Remote Services
echo -e "${YELLOW}[2/2] Refreshing Remote Docker Services...${NC}"
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$IP" << EOF
    cd $REMOTE_DIR/vps
    
    # Ensure start_vps.sh is executable
    chmod +x start_vps.sh
    
    # Restart containers to pick up code changes
    echo "Restarting Sanctum Orchestrator & Dashboard..."
    docker compose up -d --build
    
    # Cleanup old images
    docker image prune -f
    
    echo -e "\n${GREEN}Service Status:${NC}"
    docker compose ps
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Services Refreshed.${NC}"
else
    echo -e "${RED}[-] Service Refresh Failed.${NC}"
    exit 1
fi

echo -e "${CYAN}================================================${NC}"
echo -e "${GREEN}   ✨ VPS UPDATE COMPLETE${NC}"
echo -e "${CYAN}================================================${NC}"
echo -e "Dashboard: http://$IP/"

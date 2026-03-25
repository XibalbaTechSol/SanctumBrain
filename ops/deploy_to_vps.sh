#!/bin/bash

# Sanctum OS - Automated Deployment Script
# Target: IONOS VPS (Ubuntu 24.04)

# DETECTED: 74.208.17.88 has SSH OPEN. 74.208.236.226 has SSH CLOSED.
IP="74.208.17.88" 
USER="root"
PROJECT_DIR="Project_Sanctum_OS"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   🛡️ SANCTUM OS - DEPLOYMENT SEQUENCE${NC}"
echo -e "${CYAN}================================================${NC}"
echo -e "${YELLOW}Target:${NC} $USER@$IP"

# 0. Fix Known Hosts (Prevent identity mismatch errors)
ssh-keygen -f "$HOME/.ssh/known_hosts" -R "$IP" > /dev/null 2>&1

# 1. SSH Key Setup (Optional but recommended)
echo -e "\n${CYAN}[1/4] Setting up SSH Keys...${NC}"
if [ -f ~/.ssh/id_ed25519.pub ]; then
    echo "Uploading local SSH key..."
    ssh-copy-id -o StrictHostKeyChecking=no $USER@$IP
else
    echo "No local ED25519 key found. Using password auth."
fi

# 2. System Update & Docker Installation
echo -e "\n${CYAN}[2/4] Installing Docker & Dependencies...${NC}"
ssh -o StrictHostKeyChecking=no $USER@$IP "
    export DEBIAN_FRONTEND=noninteractive
    apt-get update && apt-get upgrade -y
    apt-get install -y docker.io docker-compose-v2 git python3-pip python3-venv
    systemctl enable --now docker
    echo '${GREEN}[+] Docker Installed${NC}'
"

# 3. Code Upload
echo -e "\n${CYAN}[3/4] Uploading Sanctum OS Core...${NC}"
# Create remote dir
ssh -o StrictHostKeyChecking=no $USER@$IP "mkdir -p ~/sanctum"
# Upload Project Folder
scp -o StrictHostKeyChecking=no -r $PROJECT_DIR/* $USER@$IP:~/sanctum/

# 4. Launch Services
echo -e "\n${CYAN}[4/4] Launching Orchestrator...${NC}"
ssh -o StrictHostKeyChecking=no $USER@$IP "
    cd ~/sanctum/vps
    
    # Create .env if missing
    if [ ! -f .env ]; then
        echo 'OPENAI_API_KEY=YOUR_OPENAI_API_KEY' > .env
        echo 'GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY' >> .env
    fi

    # Start Containers
    chmod +x start_vps.sh
    ./start_vps.sh
"

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}   ✅ DEPLOYMENT COMPLETE${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "Dashboard: http://$IP:8081"
echo -e "gRPC API:  $IP:50051"
echo -e "\n${YELLOW}Note: Domain sanctumguardvps.cloud points to 74.208.236.226.${NC}"
echo -e "${YELLOW}Please update your DNS if 74.208.17.88 is your new primary IP.${NC}"

#!/bin/bash

# VPS Configuration
# DETECTED: 74.208.17.88 has SSH OPEN. 74.208.236.226 has SSH CLOSED.
IP="74.208.17.88"
USER="root"

# Visuals
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   🚀 XIBALBA SANCTUM - VPS GATEWAY${NC}"
echo -e "${CYAN}================================================${NC}"
echo -e "${YELLOW}Target User:${NC} $USER"
echo -e "${YELLOW}Server IP:  ${NC} $IP"
echo -e "${YELLOW}Local Time: ${NC} $(date)"

# Quick Connectivity Check
echo -e -n "${YELLOW}Status Check: ${NC}"
if nc -zv -w 2 $IP 22 > /dev/null 2>&1; then
    echo -e "${GREEN}SSH OPEN${NC}"
else
    echo -e "${RED}SSH CLOSED or UNREACHABLE${NC}"
    exit 1
fi

echo -e "${CYAN}------------------------------------------------${NC}"
echo -e "Establishing Connection..."
echo -e "Password hint: april1989"
echo -e "${CYAN}------------------------------------------------${NC}"

# Execute SSH
ssh -o StrictHostKeyChecking=no $USER@$IP

#!/bin/bash
echo "Starting Sentinel A2A Tester..."
cd "$(dirname "$0")"
export PORT=3005
export GOOGLE_API_KEY="${GOOGLE_API_KEY:-}" # Expects key from environment
npm run dev -- -p 3005

#!/bin/bash
# run.sh - SanctumBrain Entry Point

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_DIR="$PROJECT_DIR/hermes"
SANCTUM_DIR="$PROJECT_DIR/sanctum_brain"

# Set Agency directory for the tool
export AGENCY_DIR="$PROJECT_DIR/agency"

# Activate the virtual environment
if [ -f "$HERMES_DIR/venv/bin/activate" ]; then
    source "$HERMES_DIR/venv/bin/activate"
else
    echo "Virtual environment not found. Please follow the setup steps in README.md."
    exit 1
fi

# Set PYTHONPATH to include both hermes and sanctum_brain
export PYTHONPATH="$HERMES_DIR:$PYTHONPATH"

# Check if .env exists in hermes/
if [ ! -f "$HERMES_DIR/.env" ]; then
    echo "WARNING: .env file not found in $HERMES_DIR/.env"
    echo "You may need to add your ANTHROPIC_API_KEY or OPENAI_API_KEY."
fi

# Run the main script
python3 "$SANCTUM_DIR/main.py" "$@"

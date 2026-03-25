#!/usr/bin/env bash

# autonomous_validate.sh
# Continuous Validation Loop for Sanctum Brain.
# This script is intended to be run in the background (run_long_command).

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/ops/validation_pulse.log"

echo "[$(date)] Autonomous Validation Started" > "$LOG_FILE"

while true; do
    echo "--- Validation Pulse: $(date) ---" >> "$LOG_FILE"
    
    # 1. Check Backend (FastAPI / gRPC)
    if curl -s http://127.0.0.1:8081/chat/history > /dev/null; then
        echo "BACKEND_REST: OK" >> "$LOG_FILE"
    else
        echo "BACKEND_REST: FAIL (Port 8081 unreachable)" >> "$LOG_FILE"
    fi

    # 2. Check Next.js (Living Canvas)
    if curl -s http://127.0.0.1:8080 > /dev/null; then
        echo "WEB_UI: OK" >> "$LOG_FILE"
    else
        echo "WEB_UI: FAIL (Port 8080 unreachable)" >> "$LOG_FILE"
    fi

    # 3. Run Playwright A2UI Workflow Validation
    echo "RUNNING_A2UI_TESTS..." >> "$LOG_FILE"
    cd "$PROJECT_ROOT/apps/web"
    npx playwright test tests/a2ui_workflow.spec.ts --project=chromium > a2ui_test_result.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "A2UI_WORKFLOW: VERIFIED" >> "$LOG_FILE"
    else
        echo "A2UI_WORKFLOW: FAILED" >> "$LOG_FILE"
        echo "ERROR_DETAILS:" >> "$LOG_FILE"
        tail -n 20 a2ui_test_result.log >> "$LOG_FILE"
    fi

    echo "--- Pulse End ---" >> "$LOG_FILE"
    
    # Wait for 60 seconds before next pulse
    sleep 60
done

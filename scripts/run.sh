#!/usr/bin/env bash
# Isaac — Email Scorer Runner

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PARENT_DIR="$(dirname "$PROJECT_DIR")"

LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
LOG_FILE="$LOG_DIR/run_${TIMESTAMP}.log"
PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "[$(date)] Isaac email scorer started" | tee -a "$LOG_FILE"

"$PYTHON" "$SCRIPT_DIR/score_emails.py" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -ne 0 ]; then
    echo "[$(date)] ERROR: score_emails.py exited with code $EXIT_CODE" | tee -a "$LOG_FILE"
    exit $EXIT_CODE
fi

echo "[$(date)] Isaac email scorer finished successfully" | tee -a "$LOG_FILE"

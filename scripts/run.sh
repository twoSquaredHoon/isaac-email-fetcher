#!/bin/bash

# ============================================================
# Isaac Email Fetcher - Runner Script
# Run this script to trigger the email fetch manually
# or let the cron job call it automatically
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APPLESCRIPT="$SCRIPT_DIR/fetch_emails.applescript"
OUTPUT_DIR="$PROJECT_DIR/output"
LOG_FILE="$PROJECT_DIR/logs/isaac.log"

# Create directories if they don't exist
mkdir -p "$OUTPUT_DIR"
mkdir -p "$PROJECT_DIR/logs"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Isaac Email Fetcher starting..."
log "========================================="

# Check if Outlook is installed
if ! osascript -e 'application "Microsoft Outlook" exists' &>/dev/null; then
    log "ERROR: Microsoft Outlook is not installed. Please install it first."
    exit 1
fi

log "Running AppleScript to fetch emails..."

# Run the AppleScript
OUTPUT_FILE=$(osascript "$APPLESCRIPT" 2>>"$LOG_FILE")

# Check if it succeeded
if [ $? -eq 0 ]; then
    log "SUCCESS: Emails saved to $OUTPUT_FILE"
    echo ""
    echo "✅ Done! Your email digest is ready:"
    echo "   $OUTPUT_FILE"
    echo ""
    echo "Opening the file..."
    open "$OUTPUT_FILE"
else
    log "ERROR: AppleScript failed. Check logs at $LOG_FILE"
    echo "❌ Something went wrong. Check logs at $LOG_FILE"
    exit 1
fi

log "Isaac Email Fetcher finished."

#!/bin/bash

# ============================================================
# Isaac Email Fetcher - Setup Script
# Run this once to configure Isaac on your Mac
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
RUNNER="$SCRIPT_DIR/run.sh"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║       Isaac Email Fetcher Setup       ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Make scripts executable
chmod +x "$RUNNER"
chmod +x "$SCRIPT_DIR/setup.sh"
echo "✅ Scripts are now executable"

# Create output and logs directories
mkdir -p "$PROJECT_DIR/output"
mkdir -p "$PROJECT_DIR/logs"
echo "✅ Output and logs folders created"

# Ask user what time to run daily
echo ""
echo "What time should Isaac fetch emails daily?"
echo "Enter in 24hr format (e.g. 08 for 8am, 18 for 6pm)"
read -p "Hour (00-23): " HOUR

# Validate input
if ! [[ "$HOUR" =~ ^[0-9]{2}$ ]] || [ "$HOUR" -gt 23 ]; then
    echo "Invalid hour, defaulting to 08 (8am)"
    HOUR="08"
fi

# Set up cron job
CRON_JOB="0 $HOUR * * * $RUNNER >> $PROJECT_DIR/logs/cron.log 2>&1"

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -v "isaac-email-fetcher") | crontab -
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job set — Isaac will run daily at $HOUR:00"

# Grant Automation permissions reminder
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║              ⚠️  IMPORTANT: Mac Permissions           ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  You need to allow Terminal to control Outlook:      ║"
echo "║  1. Go to System Settings                            ║"
echo "║  2. Privacy & Security → Automation                  ║"
echo "║  3. Enable Terminal → Microsoft Outlook              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Offer to do a test run
read -p "Do a test run now? (y/n): " TEST_RUN
if [ "$TEST_RUN" = "y" ] || [ "$TEST_RUN" = "Y" ]; then
    echo ""
    echo "Running Isaac now..."
    bash "$RUNNER"
fi

echo ""
echo "Setup complete! Isaac is ready. 🤖"
echo "Output files will be saved to: $PROJECT_DIR/output/"
echo "Logs will be saved to: $PROJECT_DIR/logs/"
echo ""

#!/usr/bin/env bash
# Isaac — Email Scorer Setup
# One-time setup: installs dependencies, checks Ollama, installs cron.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PARENT_DIR="$(dirname "$PROJECT_DIR")"

echo "──────────────────────────────────────────"
echo " Isaac — Email Scorer Setup"
echo "──────────────────────────────────────────"
echo ""

# ── 1. Check isaac-email-fetcher exists ───────────────────────────────────────
FETCHER_DIR="$PARENT_DIR/isaac-email-fetcher"
if [ ! -d "$FETCHER_DIR" ]; then
    echo "ERROR: isaac-email-fetcher not found at $FETCHER_DIR"
    echo "The scorer depends on the fetcher. Clone it first."
    exit 1
fi

if [ ! -f "$FETCHER_DIR/token.json" ]; then
    echo "ERROR: token.json not found in isaac-email-fetcher/"
    echo "Run isaac-email-fetcher's setup.sh first to generate it."
    exit 1
fi
echo "✓ isaac-email-fetcher found and authenticated"

# ── 2. Check Ollama ───────────────────────────────────────────────────────────
echo ""
if command -v ollama &>/dev/null; then
    echo "✓ Ollama is installed"

    # Check if model is pulled
    if ollama list | grep -q "qwen2.5:3b"; then
        echo "✓ qwen2.5:3b model is ready"
    else
        echo "Pulling qwen2.5:3b model (this may take a few minutes)..."
        ollama pull qwen2.5:3b
        echo "✓ qwen2.5:3b pulled"
    fi
else
    echo "⚠ Ollama is not installed."
    echo "  Install it from: https://ollama.com"
    echo "  Then run: ollama pull qwen2.5:3b"
    echo ""
    echo "Setup will continue but the scorer won't run until Ollama is installed."
fi

# ── 3. Create venv and install Python dependencies ────────────────────────────
echo ""
echo "Creating Python virtual environment..."
python3 -m venv "$PROJECT_DIR/.venv"
echo "✓ Virtual environment created"

echo "Installing Python dependencies..."
"$PROJECT_DIR/.venv/bin/pip" install --quiet \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client
echo "✓ Dependencies installed"

# ── 4. Create directories ─────────────────────────────────────────────────────
mkdir -p "$PROJECT_DIR/output"
mkdir -p "$PROJECT_DIR/logs"
echo "✓ output/ and logs/ directories ready"

# ── 5. Make scripts executable ────────────────────────────────────────────────
chmod +x "$SCRIPT_DIR/run.sh"
chmod +x "$SCRIPT_DIR/score_emails.py"
echo "✓ Scripts marked executable"

# ── 6. Install cron job ───────────────────────────────────────────────────────
echo ""
echo "The scorer should run after the email fetcher."
echo "isaac-email-fetcher runs at 07:00 — scorer should run a few minutes after."
echo ""
echo "What time should the scorer run? (e.g. 07:05):"
read -r RUN_TIME

HOUR=$(echo "$RUN_TIME" | cut -d: -f1)
MINUTE=$(echo "$RUN_TIME" | cut -d: -f2)

if ! [[ "$HOUR" =~ ^[0-9]{1,2}$ ]] || ! [[ "$MINUTE" =~ ^[0-9]{2}$ ]]; then
    echo "Invalid time. Skipping cron install."
    echo "Add manually: $MINUTE $HOUR * * * $SCRIPT_DIR/run.sh"
    exit 0
fi

CRON_LINE="$MINUTE $HOUR * * * $SCRIPT_DIR/run.sh >> $PROJECT_DIR/logs/cron.log 2>&1"
(crontab -l 2>/dev/null | grep -v "isaac-email-scorer"; echo "$CRON_LINE") | crontab -

echo "✓ Cron job installed: runs daily at $RUN_TIME"
echo ""
echo "──────────────────────────────────────────"
echo " Setup complete."
echo " Install Ollama when ready: https://ollama.com"
echo " Then: ollama pull qwen2.5:3b"
echo " Then test: bash scripts/run.sh"
echo "──────────────────────────────────────────"

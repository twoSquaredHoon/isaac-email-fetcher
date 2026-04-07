# isaac-email-fetcher

Fetches all emails from the last 24 hours via the Gmail API and saves them as a single clean markdown file in `output/`.

Part of the [Isaac](https://github.com/yourusername/isaac-core) project.

---

## Quick Start

### Prerequisites

- Python 3.9+
- A Google Cloud project with Gmail API enabled
- `credentials.json` downloaded from Google Cloud Console (OAuth 2.0 Desktop app)

### Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/isaac-email-fetcher
cd isaac-email-fetcher

# Place credentials.json in the repo root (never committed)
cp /path/to/credentials.json .

# Run setup (installs deps, triggers first OAuth login, installs cron)
bash scripts/setup.sh
```

### Manual run

```bash
bash scripts/run.sh
```

Output is saved to `output/emails_YYYY-MM-DD_HH-MM.md`.

---

## File Structure

```
isaac-email-fetcher/
├── docs/
│   ├── ROADMAP.md
│   └── INSTRUCTIONS.md
├── scripts/
│   ├── fetch_emails.py     ← Gmail API fetcher (core logic)
│   ├── run.sh              ← Runner with logging
│   └── setup.sh            ← One-time setup + cron installer
├── output/                 ← Generated markdown files (gitignored)
├── logs/                   ← Run logs (gitignored)
├── credentials.json        ← OAuth credentials (gitignored)
├── token.json              ← Auto-generated on first run (gitignored)
├── README.md
└── .gitignore
```

---

## How It Works

1. `run.sh` is triggered by cron at the configured time
2. `fetch_emails.py` authenticates silently via `token.json`
3. Gmail API returns all messages from the last 24 hours
4. Emails are saved as `output/emails_YYYY-MM-DD_HH-MM.md`

The first run opens a browser for Google OAuth login. Every run after that is fully silent.

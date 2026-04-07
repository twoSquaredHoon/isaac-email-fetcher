# 📬 Isaac — Email Fetcher

> Part of the Isaac AI Assistant project.
> Fetches emails from Microsoft Outlook over the last 24 hours and saves them as a clean Markdown file for review.

---

## What it does

- Connects to Microsoft Outlook on your Mac (no API keys needed)
- Fetches all emails received in the last 24 hours
- Saves them as a clean `.md` file in the `output/` folder
- Runs automatically every day at a time you choose
- Marks unread emails with 🔵 so you can spot them instantly

---

## Output example

```markdown
# 📬 Isaac Email Report
**Generated:** Monday, April 6, 2026
**Period:** Last 24 hours
**Total emails found:** 4

---

## 1. Assignment due Friday 🔵
**From:** Professor Johnson <johnson@wisc.edu>
**Received:** Monday, April 6, 2026 at 9:32 AM

> Don't forget the report is due this Friday by midnight...

---

## 2. Internship offer
**From:** HR Team <hr@company.com>
**Received:** Monday, April 6, 2026 at 2:15 PM

> We are pleased to offer you the position...
```

---

## Requirements

- Mac (macOS 12+)
- Microsoft Outlook installed and signed in
- Terminal access

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/isaac-email-fetcher.git
cd isaac-email-fetcher
```

**2. Run setup**
```bash
bash scripts/setup.sh
```

The setup script will:
- Make all scripts executable
- Ask what time to run daily
- Install the cron job automatically
- Offer a test run

**3. Allow permissions**

On first run, Mac will ask if Terminal can control Outlook. Click **Allow**.

If it doesn't prompt:
1. System Settings → Privacy & Security → Automation
2. Enable **Terminal → Microsoft Outlook**

---

## Manual run

```bash
bash scripts/run.sh
```

---

## Project structure

```
isaac-email-fetcher/
├── scripts/
│   ├── fetch_emails.applescript   # Talks to Outlook, builds markdown
│   ├── run.sh                     # Runner with logging and error handling
│   └── setup.sh                   # One-time setup and cron installer
├── output/                        # Generated .md files saved here
├── logs/                          # Logs saved here
└── README.md
```

---

## Configuration

To change the hours lookback window, open `scripts/fetch_emails.applescript` and edit:

```applescript
set hoursBack to 24
```

---

## What's next

This is the foundation for Isaac's email workflow. Next steps:
- Pipe the `.md` output into **Ollama** to score and flag important emails
- Add Gmail support alongside Outlook
- Build a simple web UI to review flagged emails

---

## Part of the Isaac project

| Module | Status |
|---|---|
| 📬 Email Fetcher (Outlook) | ✅ This repo |
| 📅 Calendar Manager | 🔜 Coming soon |
| 💬 WhatsApp Sender | 🔜 Coming soon |
| 🤖 Ollama Email Scorer | 🔜 Coming soon |
| 🖥️ Isaac UI | 🔜 Coming soon |

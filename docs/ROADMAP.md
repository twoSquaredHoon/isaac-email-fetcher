# 🗺️ Isaac — Roadmap & Blueprint

> This is the full blueprint for Isaac. Not an intro — that's README.md.
> This document defines the goal, the architecture, the modules, and the build plan.

---

## The Goal

Isaac is a work-oriented personal AI assistant that runs on a dedicated computer and is accessible from anywhere via a browser. Isaac does not think freely — he executes a predefined set of tasks on command or on a schedule. Every task Isaac can do is explicitly built and approved by the user. Isaac is private, free, and runs entirely on local infrastructure.

---

## Principles

- **Predefined tasks only** — Isaac does not reason freely, he routes commands to the right module
- **Fully local** — runs on a dedicated machine, no cloud dependency
- **Modular** — every capability is a separate, swappable module
- **Accessible anywhere** — UI is browser-based, reachable over the network via Tailscale
- **Free** — Ollama for the local model, open source tools throughout
- **Private** — no personal data leaves the local network
- **Work-scoped** — Isaac handles work and academic tasks only; personal life tasks belong to Wendy

---

## System Architecture

```
User (Browser anywhere)
        ↓
Isaac UI (Web Interface)
        ↓
Isaac Core (Command Router)
        ↓
    ┌───────────────────────────────────────────────┐
    │  Email Fetcher      (Gmail API via Python)    │
    │  Ollama Scorer      (local LLM)               │
    │  Calendar Manager   (Google Calendar API)     │
    │  WhatsApp Sender    (whatsapp-web.js)         │
    │  Script Runner      (Mac subprocess)          │
    └───────────────────────────────────────────────┘
        ↓
Output / Results shown in UI
```

---

## Infrastructure

| Component | Tool | Cost |
|---|---|---|
| Local LLM | Ollama + qwen2.5:3b | Free |
| Email access | Gmail API (OAuth) via Python | Free |
| UW email consolidation | Auto-forward from @wisc.edu to Gmail | Free |
| Calendar access | Google Calendar API (OAuth) | Free |
| WhatsApp | whatsapp-web.js | Free |
| Script execution | Python subprocess | Free |
| Web UI | Flask + HTML | Free |
| Remote access | Tailscale | Free |
| Scheduling | cron | Free |
| OS | macOS | Already owned |

---

## Hardware Setup

### Current Setup (College)

```
Work Computer (Isaac Server)
  - Always on, sleep disabled
  - Runs all Isaac modules
  - Hosts the web UI
  - Connected to work/campus network
        ↓
Tailscale (secure tunnel)
        ↓
MacBook (anywhere)
  - Browser only, zero performance cost
  - Latency depends on network between devices
```

### Future Setup (Home Server)

```
Home Server (Isaac Server)
  - Always on, dedicated hardware
  - Isaac + Wendy on same machine
  - Connected to home network
        ↓
Tailscale (secure tunnel)
        ↓
Any device, anywhere
```

---

## Email Strategy

Isaac monitors one Gmail inbox that consolidates all email sources.

| Source | How it arrives |
|---|---|
| UW Madison (@wisc.edu) | Auto-forwarded to Gmail via UW Outlook forwarding settings |
| Personal email | Already in Gmail natively |

Isaac fetches from all inbox categories (Primary, Promotions, Social, Updates). Gmail's auto-categorization is not used to pre-filter — the Ollama scorer handles relevance decisions based on Isaac's actual criteria.

**Why not Outlook/AppleScript:** Microsoft Outlook 16.80+ broke AppleScript inbox access. Permanently removed.

**Why not Microsoft Graph API:** UW Madison restricts third-party OAuth for student accounts. Forwarding to Gmail bypasses this entirely.

**Why not n8n:** Custom scripts chosen for simplicity, easier debugging, and cleaner version control.

---

## Modules

### ✅ Module 1 — Email Fetcher (Gmail)
**Repo:** `isaac-email-fetcher`
**Status:** Complete

Fetches all emails from Gmail over the last 24 hours and saves them as a clean markdown file in `output/`. Covers all email sources — UW Madison emails auto-forward to Gmail.

**Modes:**
- Default: fetches last 24 hours (used by cron)
- `--recent N`: fetches N most recent inbox emails (used for testing)

**Cron:** daily at 07:00 CT

**Files:**
```
isaac-email-fetcher/
├── docs/
├── scripts/
│   ├── fetch_emails.py
│   ├── run.sh
│   └── setup.sh
├── output/                    ← gitignored
├── logs/                      ← gitignored
├── .venv/                     ← gitignored
├── credentials.json           ← gitignored
├── token.json                 ← gitignored
├── README.md
└── .gitignore
```

---

### 🔄 Module 2 — Ollama Email Scorer
**Repo:** `isaac-email-scorer`
**Status:** Built, not yet tested (Ollama not installed on Isaac machine)

Takes the latest markdown output from the email fetcher and scores each email using `qwen2.5:3b` via Ollama. Important emails are starred and labeled "Isaac's Picks" in Gmail.

**Scoring criteria:**
- Emails from professors, academic staff, TAs, or university administration
- Emails with deadlines, due dates, or action items
- Emails from real people (not newsletters or automated messages)
- Emails related to internships or jobs

**Key design decisions:**
- Auto-detects latest file in `isaac-email-fetcher/output/` — no path argument needed
- Shares OAuth credentials and token with `isaac-email-fetcher`
- Prompts model for strict JSON output for reliable parsing
- "Isaac's Picks" Gmail label is auto-created on first run if it doesn't exist
- Requires `gmail.modify` scope — triggers one-time browser re-auth on first scorer setup

**Both repos must be in the same parent directory.**

**Cron:** daily at 07:05 CT (5 minutes after fetcher)

**Files:**
```
isaac-email-scorer/
├── docs/
├── scripts/
│   ├── score_emails.py
│   ├── run.sh
│   └── setup.sh
├── output/                    ← gitignored
├── logs/                      ← gitignored
├── .venv/                     ← gitignored
├── README.md
└── .gitignore
```

**Next step:** Install Ollama on Isaac machine, run `setup.sh`, test.

---

### 🔜 Module 3 — Morning Briefing
**Repo:** `isaac-morning-briefing`
**Status:** Planned

Runs every morning. Combines flagged emails from Isaac's Picks with today's Google Calendar events into a single consolidated summary delivered to the Isaac UI (and optionally via WhatsApp).

---

### 🔜 Module 4 — Calendar Manager
**Repo:** `isaac-calendar`
**Status:** Planned

Connects to Google Calendar via the Google Calendar API. View, create, delete, and reschedule events on command.

---

### 🔜 Module 5 — WhatsApp Sender
**Repo:** `isaac-whatsapp`
**Status:** Planned

Sends WhatsApp messages to contacts or groups via whatsapp-web.js. QR code scan on first setup, silent afterward.

---

### 🔜 Module 6 — Script Runner
**Repo:** `isaac-script-runner`
**Status:** Planned

Runs pre-approved scripts on the Mac on command. Isaac cannot run arbitrary code — only scripts in the approved scripts folder.

---

### 🔜 Module 7 — Isaac Core + UI
**Repo:** `isaac-core`
**Status:** Planned — built last, after all modules are stable

Flask web server hosting the UI and routing commands to modules. Accessible from any browser via Tailscale.

---

## Build Order

| Phase | Module | Status |
|---|---|---|
| 1 | ✅ Email Fetcher (Gmail) | Complete |
| 2 | 🔄 Ollama Email Scorer | Built, pending Ollama install + test |
| 3 | 🔜 Morning Briefing | Planned |
| 4 | 🔜 Calendar Manager | Planned |
| 5 | 🔜 WhatsApp Sender | Planned |
| 6 | 🔜 Script Runner | Planned |
| 7 | 🔜 Isaac Core + UI | Planned |

---

## Future Ideas

- **Wendy integration** — Isaac and Wendy share a Tailscale network, can trigger each other's tasks
- **Voice input** — add Whisper (local speech-to-text) to the UI for voice commands
- **Home server migration** — move Isaac to a dedicated home server when hardware is available

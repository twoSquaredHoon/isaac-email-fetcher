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

> Note: Running Isaac at work means low latency when accessed on campus. Accessing
> from home or elsewhere adds round-trip internet latency, but since Isaac handles
> short predefined tasks the delay is minimal.

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
  - MacBook at work or school
  - Phone
  - Any browser
```

---

## Email Strategy

Isaac monitors one Gmail inbox that consolidates all email sources.

| Source | How it arrives |
|---|---|
| UW Madison (@wisc.edu) | Auto-forwarded to Gmail via UW Outlook forwarding settings |
| Personal email | Already in Gmail natively |

Isaac reads Gmail only via the Gmail API (Python). No Outlook involvement at all.

**Why not Outlook/AppleScript:** Microsoft Outlook 16.80+ (new Outlook for Mac) broke AppleScript inbox access. `messages of inbox` returns 0 regardless of inbox contents. Confirmed broken on version 16.107.3. AppleScript is removed from this project permanently.

**Why not Microsoft Graph API:** UW Madison disables app passwords and restricts third-party OAuth for student accounts. Forwarding to Gmail bypasses this entirely with a one-time settings change.

**Why not n8n:** Custom scripts were chosen over n8n for simplicity — no extra service to run, easier to debug, everything lives in plain version-controlled files.

---

## Modules

### 🔄 Module 1 — Email Fetcher (Gmail)
**Repo:** `isaac-email-fetcher`
**Status:** In Progress

Fetches all emails from Gmail over the last 24 hours using the Gmail API and saves them as a clean markdown file. Covers all email sources — UW Madison emails auto-forward to Gmail, so one script handles everything.

**Access method:** Gmail API via OAuth (Python). One-time browser login generates `token.json` which is reused silently on all future runs.

**Dependencies:** `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`

**Credentials:** `credentials.json` (downloaded from Google Cloud Console, never committed to GitHub)

**Files:**
```
isaac-email-fetcher/
├── docs/
│   ├── ROADMAP.md
│   └── INSTRUCTIONS.md
├── scripts/
│   ├── fetch_emails.py        ← Gmail API fetcher
│   ├── run.sh
│   └── setup.sh
├── output/                    ← gitignored
├── logs/                      ← gitignored
├── credentials.json           ← gitignored
├── token.json                 ← gitignored, auto-generated on first run
├── README.md
└── .gitignore
```

**Flow:**
```
cron triggers run.sh
        ↓
fetch_emails.py authenticates via token.json
        ↓
Gmail API returns last 24hrs of messages
        ↓
Saved as emails_YYYY-MM-DD_HH-MM.md in output/
```

---

### 🔜 Module 2 — Ollama Email Scorer
**Repo:** `isaac-email-scorer`
**Status:** Planned

Takes the markdown output from the email fetcher and runs it through a local Ollama model. Scores each email by importance based on predefined criteria. Flags important emails by starring them in Gmail.

**Model:** `qwen2.5:3b` — chosen for speed, small size, and strong instruction-following. No reasoning needed since criteria are fully predefined.

**Scoring criteria:**
- Emails from professors or academic staff
- Emails with deadlines or action items
- Emails from real people (not newsletters or automated messages)
- Emails related to internships or jobs

**Flagging behavior:**
- Important emails → starred + added to "Isaac's Picks" label in Gmail
- All flagged emails → surfaced in Isaac UI review panel

**Flow:**
```
emails_YYYY-MM-DD.md
        ↓
Ollama (qwen2.5:3b)
"Does this email matter based on [criteria]?"
        ↓
├── Yes → Star in Gmail + add to flagged list
└── No  → Skip
```

---

### 🔜 Module 3 — Morning Briefing
**Repo:** `isaac-morning-briefing`
**Status:** Planned

Runs every morning at a set time. Combines flagged emails from both accounts with today's Google Calendar events and delivers a single consolidated summary to the Isaac UI (and optionally via WhatsApp message to self).

**Output includes:**
- Flagged emails from the last 24 hours
- Today's calendar events with times
- Any deadlines detected in emails

**Why this is in the build plan and not future ideas:** This is the primary daily use case for Isaac — one morning check instead of opening multiple apps.

---

### 🔜 Module 4 — Calendar Manager
**Repo:** `isaac-calendar`
**Status:** Planned

Connects to Google Calendar via the Google Calendar API. Allows Isaac to view upcoming events, create new events, and delete or reschedule events on command.

**Capabilities:**
- View events for today / this week
- Create a new event with title, time, location
- Delete an event by name or time
- List events in a given date range

**Auth:** Google OAuth (one-time setup, free)

---

### 🔜 Module 5 — WhatsApp Sender
**Repo:** `isaac-whatsapp`
**Status:** Planned

Sends WhatsApp messages to contacts or groups via whatsapp-web.js. Uses a QR code scan on first setup, then runs silently in the background.

**Capabilities:**
- Send a message to a contact by name
- Send a message to a group by name
- Confirm delivery back to Isaac UI

**Note:** Uses unofficial WhatsApp Web automation. Works reliably for personal use. WhatsApp could theoretically block it but this is rare for personal accounts.

---

### 🔜 Module 6 — Script Runner
**Repo:** `isaac-script-runner`
**Status:** Planned

Runs predefined scripts on the Mac on command. Scripts are pre-approved and stored locally. Isaac cannot run arbitrary code — only scripts that exist in the approved scripts folder.

**Capabilities:**
- List available scripts
- Run a script by name
- Return output to Isaac UI

---

### 🔜 Module 7 — Isaac Core + UI
**Repo:** `isaac-core`
**Status:** Planned — built last, after all modules are stable

The brain that connects everything. A simple Flask web server that hosts the UI and routes commands to the right module. Accessible from any browser on the network or via Tailscale.

**UI features:**
- Text command input
- Output display
- Module status indicators
- Morning briefing view
- Flagged emails review panel (Gmail, Isaac's Picks label)

---

## Build Order

| Phase | Module | Why |
|---|---|---|
| 1 | 🔄 Email Fetcher (Gmail) | Foundation — covers all email via forwarding |
| 2 | 🔜 Ollama Email Scorer | Builds directly on fetcher output |
| 3 | 🔜 Morning Briefing | Core daily use case, needs scorer + calendar |
| 4 | 🔜 Calendar Manager | Self-contained, needed for morning briefing |
| 5 | 🔜 WhatsApp Sender | Most complex auth, saved for later |
| 6 | 🔜 Script Runner | Simple, good to have before UI |
| 7 | 🔜 Isaac Core + UI | Built last when all modules are ready to connect |

---

## Future Ideas

- **Wendy integration** — Isaac and Wendy share a Tailscale network, can trigger each other's tasks
- **Voice input** — add Whisper (local speech-to-text) to the UI for voice commands
- **Home server migration** — move Isaac to a dedicated home server when hardware is available; Isaac and Wendy run on the same machine

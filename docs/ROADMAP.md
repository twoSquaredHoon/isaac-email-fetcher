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
    │  Email Fetcher      (Outlook via AppleScript) │
    │  Email Fetcher      (Gmail API)               │
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
| UW Email access | AppleScript → Outlook app | Free |
| Personal email access | Gmail API (OAuth) | Free |
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

Isaac monitors two email accounts and consolidates flagged results into one review view.

| Account | Access Method | Why |
|---|---|---|
| UW Madison (@wisc.edu) | AppleScript → Outlook app | No API registration needed, works with campus Microsoft 365 |
| Personal Gmail | Gmail API via OAuth | Official, stable, free |

Both accounts feed into the same Ollama scorer. Flagged emails from both are surfaced together in the Isaac UI. Important emails are starred in their respective apps so the review is also visible natively.

**Why not n8n:** n8n was considered as a visual workflow builder but custom scripts were chosen instead. Reasons: no extra service to run and maintain, simpler stack, easier to debug, everything stays in plain files that are easy to version control.

---

## Modules

### ✅ Module 1 — Email Fetcher (Outlook)
**Repo:** `isaac-email-fetcher`
**Status:** Complete

Fetches all emails from Microsoft Outlook over the last 24 hours and saves them as a clean markdown file. Runs on a cron schedule. Foundation for the Ollama email scorer.

**Files:**
```
isaac-email-fetcher/
├── docs/
│   ├── ROADMAP.md
│   └── INSTRUCTIONS.md
├── scripts/
│   ├── fetch_emails.applescript
│   ├── run.sh
│   └── setup.sh
├── output/
├── logs/
├── README.md
└── .gitignore
```

---

### 🔜 Module 2 — Email Fetcher (Gmail)
**Repo:** `isaac-email-fetcher-gmail`
**Status:** Planned

Fetches all emails from personal Gmail over the last 24 hours using the Gmail API. Saves output in the same markdown format as the Outlook fetcher so both feed into the scorer identically.

**Auth:** Google OAuth (one-time setup, free)

**Flow:**
```
Gmail API → last 24hrs of emails
        ↓
Formatted as emails_gmail_YYYY-MM-DD.md
        ↓
Passed to Ollama Scorer (same as Outlook output)
```

---

### 🔜 Module 3 — Ollama Email Scorer
**Repo:** `isaac-email-scorer`
**Status:** Planned

Takes the markdown output from both email fetchers and runs it through a local Ollama model. Scores each email by importance based on predefined criteria. Flags important emails by starring them in their source app (Outlook or Gmail).

**Model:** `qwen2.5:3b` — chosen for speed, small size, and strong instruction-following. No reasoning needed since criteria are fully predefined.

**Scoring criteria:**
- Emails from professors or academic staff
- Emails with deadlines or action items
- Emails from real people (not newsletters or automated messages)
- Emails related to internships or jobs

**Flagging behavior:**
- Outlook emails → starred in Outlook
- Gmail emails → starred + added to "Isaac's Picks" label in Gmail
- All flagged emails → surfaced in Isaac UI review panel

**Flow:**
```
emails_YYYY-MM-DD.md (Outlook)  +  emails_gmail_YYYY-MM-DD.md
                    ↓
            Ollama (qwen2.5:3b)
    "Does this email matter based on [criteria]?"
                    ↓
        ├── Yes → Star in source app + add to flagged list
        └── No  → Skip
```

---

### 🔜 Module 4 — Morning Briefing
**Repo:** `isaac-morning-briefing`
**Status:** Planned

Runs every morning at a set time. Combines flagged emails from both accounts with today's Google Calendar events and delivers a single consolidated summary to the Isaac UI (and optionally via WhatsApp message to self).

**Output includes:**
- Flagged emails from the last 24 hours
- Today's calendar events with times
- Any deadlines detected in emails

**Why this is in the build plan and not future ideas:** This is the primary daily use case for Isaac — one morning check instead of opening multiple apps.

---

### 🔜 Module 5 — Calendar Manager
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

### 🔜 Module 6 — WhatsApp Sender
**Repo:** `isaac-whatsapp`
**Status:** Planned

Sends WhatsApp messages to contacts or groups via whatsapp-web.js. Uses a QR code scan on first setup, then runs silently in the background.

**Capabilities:**
- Send a message to a contact by name
- Send a message to a group by name
- Confirm delivery back to Isaac UI

**Note:** Uses unofficial WhatsApp Web automation. Works reliably for personal use. WhatsApp could theoretically block it but this is rare for personal accounts.

---

### 🔜 Module 7 — Script Runner
**Repo:** `isaac-script-runner`
**Status:** Planned

Runs predefined scripts on the Mac on command. Scripts are pre-approved and stored locally. Isaac cannot run arbitrary code — only scripts that exist in the approved scripts folder.

**Capabilities:**
- List available scripts
- Run a script by name
- Return output to Isaac UI

---

### 🔜 Module 8 — Isaac Core + UI
**Repo:** `isaac-core`
**Status:** Planned — built last, after all modules are stable

The brain that connects everything. A simple Flask web server that hosts the UI and routes commands to the right module. Accessible from any browser on the network or via Tailscale.

**UI features:**
- Text command input
- Output display
- Module status indicators
- Morning briefing view
- Flagged emails review panel (Outlook + Gmail combined)

---

## Build Order

| Phase | Module | Why |
|---|---|---|
| 1 | ✅ Email Fetcher (Outlook) | Foundation, no external dependencies |
| 2 | 🔜 Email Fetcher (Gmail) | Same format, pairs with Outlook fetcher |
| 3 | 🔜 Ollama Email Scorer | Builds directly on both fetcher outputs |
| 4 | 🔜 Morning Briefing | Core daily use case, needs scorer + calendar |
| 5 | 🔜 Calendar Manager | Self-contained, needed for morning briefing |
| 6 | 🔜 WhatsApp Sender | Most complex auth, saved for later |
| 7 | 🔜 Script Runner | Simple, good to have before UI |
| 8 | 🔜 Isaac Core + UI | Built last when all modules are ready to connect |

---

## Future Ideas

- **Wendy integration** — Isaac and Wendy share a Tailscale network, can trigger each other's tasks
- **Voice input** — add Whisper (local speech-to-text) to the UI for voice commands
- **Home server migration** — move Isaac to a dedicated home server when hardware is available; Isaac and Wendy run on the same machine

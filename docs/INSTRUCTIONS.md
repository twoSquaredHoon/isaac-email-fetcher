# 📐 Isaac — Development Instructions & Rules

> These are the rules and conventions established for building Isaac.
> Follow these before adding any new module or making changes.

---

## 1. Path Handling

- **Never hardcode absolute paths** in bash scripts
- Bash scripts must always detect their own location dynamically:
  ```bash
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
  ```
- AppleScript cannot detect its own path — it is the **only exception** where a path must be set manually
- When AppleScript needs a path, it must receive it as an argument passed from the bash runner script, not hardcoded inside the `.applescript` file itself
- The bash runner is always the source of truth for paths

---

## 2. Module Structure

- Every capability Isaac has is a **separate, self-contained module**
- Each module lives in its own folder and its own GitHub repository
- Modules must not depend on each other to function — they work standalone
- A module is only connected to Isaac's core when it is fully tested on its own

---

## 3. Script Stability

- AppleScript is used for macOS app automation (e.g. Outlook) and is accepted as a pragmatic choice
- AppleScript is acknowledged as app-dependent and may break on major Outlook or macOS updates
- If a script breaks due to an update, rewrite only that module — other modules are unaffected
- More stable alternatives (IMAP, official APIs) are noted but not required unless stability becomes an issue

---

## 4. No Unnecessary Dependencies

- Prefer native Mac tools and built-in languages before installing anything
- Python: use standard library first (`imaplib`, `subprocess`, `os`) before pip packages
- Node.js: only used where necessary (e.g. WhatsApp bridge)
- Every dependency added must have a clear reason
- **Do not use n8n or similar workflow platforms** — Isaac uses plain scripts for simplicity, easier debugging, and cleaner version control. If a task can be done in a shell script or Python, do it there.

---

## 5. Output Files

- Generated output files (`.md`, logs) are **never committed to GitHub**
- `output/` and `logs/` are always in `.gitignore`
- Output files contain personal data — they stay local only

---

## 6. Automation

- Every module that runs on a schedule uses a **cron job**
- Cron jobs are installed by the module's `setup.sh`, never manually
- Default schedule is once every 24 hours unless the task requires otherwise
- The setup script always asks the user what time to run — never assume a time

---

## 7. Naming Conventions

- Repositories: `isaac-[module-name]` (e.g. `isaac-email-fetcher`, `isaac-calendar`)
- Scripts: lowercase, hyphenated (e.g. `fetch_emails.applescript`, `run.sh`)
- Output files: include a datestamp (e.g. `emails_2026-04-06_08-00.md`)
- Commit messages: use conventional commits format (`feat:`, `fix:`, `docs:`, `chore:`)

---

## 8. Every Module Must Have

- `scripts/fetch_*.applescript` or equivalent — the core logic
- `scripts/run.sh` — runner with logging and error handling
- `scripts/setup.sh` — one-time setup and cron installer
- `output/` — where generated files go (gitignored)
- `logs/` — where logs go (gitignored)
- `README.md` — intro and quick start
- `docs/ROADMAP.md` — goals, plans, and blueprint
- `docs/INSTRUCTIONS.md` — rules and conventions (this file)
- `.gitignore` — always includes `output/` and `logs/`

---

## 9. Local Model

- The local model for all Isaac AI tasks is **`qwen2.5:3b`** running via Ollama
- This model was chosen for: small size, fast inference, strong instruction-following, and no internet requirement
- Isaac's tasks are predefined — the model does not need reasoning ability, only reliable instruction execution
- Do not swap to a larger model unless `qwen2.5:3b` genuinely cannot handle a specific task
- Ollama must be running on the Isaac server before any scorer module is invoked

---

## 10. Email Sources

Isaac monitors two email accounts. Both are treated as first-class sources.

| Account | Access Method |
|---|---|
| UW Madison (@wisc.edu) | AppleScript → Outlook app (no API registration needed) |
| Personal Gmail | Gmail API via Google OAuth |

- Both fetchers produce output in the same markdown format so the scorer handles them identically
- Flagged emails are starred in their source app — Outlook emails starred in Outlook, Gmail emails starred + labeled "Isaac's Picks" in Gmail
- Never route UW email through Gmail forwarding — keep accounts separate and access each directly

---

## 11. Scope — Isaac vs Wendy

- **Isaac** — work and academic tasks only: email (UW + personal work email), calendar, work scripts, job/internship related tasks
- **Wendy** — personal life only: smart home, health tracking, calorie logging, personal routines
- If a task could belong to either, default to Wendy — Isaac stays work-focused
- Isaac and Wendy are built and maintained as completely separate systems
- They share these conventions and rules but never share code, repositories, or infrastructure
- Future: Isaac and Wendy may communicate over a shared Tailscale network but remain independent services

---

## 12. Privacy

- Isaac runs entirely locally — no data is sent to any cloud service unless explicitly built to do so
- Google OAuth credentials are stored locally and never committed to GitHub
- WhatsApp session data is stored locally and never committed to GitHub
- Ollama runs locally — emails are never sent to an external AI API
- Output files with email content stay on the local machine only (`output/` is always gitignored)

# 📐 Isaac — Development Instructions & Rules

> These are the rules and conventions established for building Isaac.
> Follow these before adding any new module or making changes.

---

## 0. Documentation First

- **Updating documentation is always the first priority** — before writing code, before fixing bugs, before anything else
- If a decision is made, a direction changes, or a module is completed, update ROADMAP.md and INSTRUCTIONS.md before moving on
- No module is considered done until its documentation reflects its actual current state
- Code can be wrong and fixed. Undocumented decisions get forgotten and cost more time later
- If you are unsure whether to document first or code first — document first

---

## 0.1 Changelog Format

Every session entry in CHANGELOG.md must follow this exact format:

```
## YYYY-MM-DD

**Worker:** (provided by user at update time)
**Worktime:** (start time — end time, timezone, figured out from session context)

### Entry Title
- change details
```

- The worker email is always provided by the user when requesting a changelog update — never assume it
- Worktime is inferred from the conversation timestamps
- The Gmail account used for Isaac is not logged in the changelog header — it belongs in INSTRUCTIONS.md only
- Dead ends and ruled-out approaches must be logged, not just successes

---

## 1. Path Handling

- **Never hardcode absolute paths** in bash scripts
- Bash scripts must always detect their own location dynamically:
  ```bash
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
  ```
- The bash runner is always the source of truth for paths

---

## 2. Module Structure

- Every capability Isaac has is a **separate, self-contained module**
- Each module lives in its own folder and its own GitHub repository
- Modules must not depend on each other to function — they work standalone
- A module is only connected to Isaac's core when it is fully tested on its own

---

## 3. No AppleScript

- AppleScript is **permanently removed** from this project
- Microsoft Outlook 16.80+ (new Outlook for Mac) broke AppleScript inbox access — `messages of inbox` returns 0 regardless of inbox contents. Confirmed on version 16.107.3
- Do not attempt to reintroduce AppleScript for any email-related task
- All email access goes through the Gmail API via Python

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

- `scripts/fetch_emails.py` or equivalent — the core logic (Python, not AppleScript)
- `scripts/run.sh` — runner with logging and error handling
- `scripts/setup.sh` — one-time setup and cron installer
- `output/` — where generated files go (gitignored)
- `logs/` — where logs go (gitignored)
- `README.md` — intro and quick start
- `docs/ROADMAP.md` — goals, plans, and blueprint
- `docs/INSTRUCTIONS.md` — rules and conventions (this file)
- `.gitignore` — always includes `output/`, `logs/`, `credentials.json`, `token.json`

---

## 9. Local Model

- The local model for all Isaac AI tasks is **`qwen2.5:3b`** running via Ollama
- This model was chosen for: small size, fast inference, strong instruction-following, and no internet requirement
- Isaac's tasks are predefined — the model does not need reasoning ability, only reliable instruction execution
- Do not swap to a larger model unless `qwen2.5:3b` genuinely cannot handle a specific task
- Ollama must be running on the Isaac server before any scorer module is invoked

---

## 10. Email Sources

Isaac reads from one Gmail account only. All email sources consolidate into it.

| Source | Method |
|---|---|
| UW Madison (@wisc.edu) | Auto-forwarded to Gmail via Outlook Web forwarding settings |
| Personal email | Already in Gmail natively |

- Gmail is accessed via the Gmail API using OAuth (Python)
- `credentials.json` — downloaded from Google Cloud Console, never committed
- `token.json` — auto-generated on first run after browser login, never committed
- Both files must be in the root of the repo folder and listed in `.gitignore`
- The one-time browser login only happens once — after that all runs are fully silent

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

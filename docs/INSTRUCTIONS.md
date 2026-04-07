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
## YYYY-MM-DD (Session N)

**Worker:** (provided by user at update time)
**Worktime:** (start time — end time, timezone, inferred from conversation)

### Entry Title
- change details
```

- The worker email is always provided by the user when requesting a changelog update — never assume it
- Worktime start is inferred from the first message timestamp of the session; end is provided by the user
- If multiple sessions occur on the same date, label them Session 1, Session 2, etc.
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
- Exception: `isaac-email-scorer` shares OAuth credentials with `isaac-email-fetcher` and must live in the same parent directory

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
- Scripts: lowercase, hyphenated (e.g. `fetch_emails.py`, `run.sh`)
- Output files: include a datestamp (e.g. `emails_2026-04-06_08-00.md`)
- Commit messages: use conventional commits format (`feat:`, `fix:`, `docs:`, `chore:`)

---

## 8. Every Module Must Have

- A core logic script (e.g. `scripts/fetch_emails.py`) — Python, not AppleScript
- `scripts/run.sh` — runner with logging and error handling
- `scripts/setup.sh` — one-time setup and cron installer
- `output/` — where generated files go (gitignored)
- `logs/` — where logs go (gitignored)
- `README.md` — intro and quick start
- `docs/ROADMAP.md` — goals, plans, and blueprint
- `docs/INSTRUCTIONS.md` — rules and conventions (this file)
- `.gitignore` — always use the canonical template (see rule 13)

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
- The scorer (`isaac-email-scorer`) shares the fetcher's token — no second login required
- When the scorer is set up for the first time, a browser re-auth is triggered to upgrade the token scope from `gmail.readonly` to `gmail.modify`

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

---

## 13. Canonical .gitignore Template

Every Isaac module uses this exact `.gitignore`. Do not add duplicate entries or regenerate it:

```gitignore
output/
logs/
.venv/
.DS_Store
**/.DS_Store
.vscode/
.idea/
*.swp
*.swo
__pycache__/
*.pyc
credentials.json
token.json
```

---

## 14. Python Environment

- **Never use system-wide pip install** — macOS blocks this on Python 3.12+
- Every module creates its own `.venv/` in the project root via `python3 -m venv .venv`
- All pip installs go through `.venv/bin/pip`
- All script execution goes through `.venv/bin/python`
- `.venv/` is always gitignored

---

## 15. Google Cloud Console Notes

- Isaac's Gmail project is named **Issac-email** (note the typo — this is the actual project name)
- Project ID: `issac-492603`
- Publishing status: Testing — only approved test users can authenticate
- Test user: `twosquaredhoon@gmail.com` (added under Audience > Test users)
- To add more test users: Google Cloud Console > Issac-email project > APIs & Services > OAuth consent screen > Audience > Test users
- The "Ineligible accounts not added" warning after saving a test user can be ignored if the email appears in the test users list

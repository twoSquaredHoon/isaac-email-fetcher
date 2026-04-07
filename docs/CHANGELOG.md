# 📋 Isaac — Changelog

> A running log of decisions, changes, and dead ends.
> Every entry must include a date, what changed, and why.
> This document exists so no decision has to be re-explained or re-discovered.

---

## 2026-04-06 (Session 2)

**Worker:** letsmakecheckcard@gmail.com
**Worktime:** 10:54 PM — 11:33 PM CT

---

### Module 1 — Email Fetcher (Gmail): Completed
- Built `fetch_emails.py`, `run.sh`, `setup.sh` for `isaac-email-fetcher`
- Fixed pip install failure on macOS — switched to venv-based install (`.venv/` inside project root)
- Fixed Google OAuth "access blocked" error — added `twosquaredhoon@gmail.com` as test user in Google Cloud Console under Issac-email project > Audience > Test users
- Successfully fetched 6 emails on first run
- Cron installed: runs daily at 07:00 CT
- Added `--recent N` flag to `fetch_emails.py` for testing — fetches N most recent inbox emails regardless of time window (default: 10). Cron still uses default 24h mode. Output files named differently (`emails_recent10_...md` vs `emails_24h_...md`) to avoid conflicts.
- Decision: fetch from all inbox categories (Primary, Promotions, Social, Updates) — Gmail's auto-categorization is not reliable enough to pre-filter. The Ollama scorer handles relevance decisions.

### Module 2 — Email Scorer (Ollama): Built, not yet tested
- Built `score_emails.py`, `run.sh`, `setup.sh` for `isaac-email-scorer`
- Scorer auto-detects latest file in `isaac-email-fetcher/output/` — no path argument needed
- Shares OAuth credentials and token with `isaac-email-fetcher` — no second login
- Uses `qwen2.5:3b` via Ollama, prompts for strict JSON response for reliable parsing
- Important emails are starred and labeled "Isaac's Picks" in Gmail (label auto-created if missing)
- Saves scoring summary to `output/scored_*.md`
- Requires `gmail.modify` scope (broader than fetcher's `gmail.readonly`) — will trigger one-time browser re-auth on first scorer setup run
- Both repos must sit in the same parent directory
- Not yet tested — Ollama not installed on Isaac machine. Will install and test in next session.

### .gitignore Convention Established
- Canonical `.gitignore` template defined for all Isaac modules (see INSTRUCTIONS.md rule 13)
- Do not regenerate or add duplicate entries — use the template

---

## 2026-04-06 (Session 1)

**Worker:** hoonysings7190@gmail.com
**Worktime:** 7:16 PM — 10:30 PM CT

---

### Project Started
- Defined Isaac as a work-oriented AI assistant running predefined tasks
- Decided on modular architecture — each capability as a separate repo
- Chose Ollama + qwen2.5:3b as the local model (small, fast, no reasoning needed)
- Chose custom Python scripts over n8n — simpler stack, easier to debug, plain version-controlled files

### Hardware Decision
- Isaac runs on a dedicated work computer, always on, sleep disabled
- Accessed remotely via Tailscale from MacBook or any browser
- Future plan: migrate to a home server when hardware is available

### Email — AppleScript Attempt (Dead End)
- First approach: AppleScript → Microsoft Outlook app on Mac
- Built `fetch_emails.applescript` to pull last 24hrs from inbox
- **Failed:** Outlook version 16.107.3 (new Outlook for Mac) broke AppleScript inbox access
- `messages of inbox` returns 0 regardless of actual inbox contents
- AppleScript permanently removed from project

### Email — Microsoft Graph API (Ruled Out)
- Considered Microsoft Graph API to access UW Madison (@wisc.edu) email directly
- **Ruled out:** UW Madison disables app passwords and restricts third-party OAuth for student accounts
- No path forward without IT involvement

### Email — Final Decision: Gmail API + Forwarding
- UW Madison (@wisc.edu) emails set to auto-forward to personal Gmail
- Isaac reads Gmail only via the Gmail API (Python + OAuth)
- One account, one script, covers all email sources
- Google Cloud project created: `Issac-email`
- Gmail API enabled, OAuth consent screen configured, Desktop app credentials created
- `credentials.json` downloaded and placed in repo root (gitignored)
- Dependencies installed: `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`

### Documentation Structure
- `docs/` folder established as home for all project-level documentation
- Three core docs defined: ROADMAP.md, INSTRUCTIONS.md, CHANGELOG.md
- Rule established: documentation updates are always priority over writing code
- Docs are designed to serve as an AI session harness — paste both at the start of any new session to restore full project context

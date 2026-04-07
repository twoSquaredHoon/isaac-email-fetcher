# 📋 Isaac — Changelog

> A running log of decisions, changes, and dead ends.
> Every entry must include a date, what changed, and why.
> This document exists so no decision has to be re-explained or re-discovered.

---

## 2026-04-06

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

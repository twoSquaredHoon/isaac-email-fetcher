#!/usr/bin/env python3
"""
Isaac — Email Scorer (Ollama)

Reads the latest email markdown file from isaac-email-fetcher/output/,
scores each email against Isaac's criteria using qwen2.5:3b via Ollama,
and stars important emails + applies "Isaac's Picks" label in Gmail.

Requires:
  - Ollama running locally with qwen2.5:3b pulled
  - isaac-email-fetcher/ in the same parent directory
  - Gmail OAuth token from isaac-email-fetcher (shared)
"""

import os
import re
import json
import base64
import urllib.request
import urllib.error
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PARENT_DIR = os.path.dirname(PROJECT_DIR)

FETCHER_OUTPUT_DIR = os.path.join(PARENT_DIR, "isaac-email-fetcher", "output")
FETCHER_TOKEN = os.path.join(PARENT_DIR, "isaac-email-fetcher", "token.json")
FETCHER_CREDENTIALS = os.path.join(PARENT_DIR, "isaac-email-fetcher", "credentials.json")

OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

# ── Config ────────────────────────────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"
LABEL_NAME = "Isaac's Picks"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

# ── Scoring criteria ──────────────────────────────────────────────────────────
CRITERIA = """
1. Emails from professors, academic staff, TAs, or university administration
2. Emails with deadlines, due dates, or action items requiring a response
3. Emails from real people (not newsletters, automated systems, or marketing)
4. Emails related to internships, jobs, or career opportunities
""".strip()


# ── Gmail auth ────────────────────────────────────────────────────────────────

def authenticate_gmail() -> object:
    """Authenticate with Gmail API using fetcher's credentials."""
    creds = None

    if os.path.exists(FETCHER_TOKEN):
        creds = Credentials.from_authorized_user_file(FETCHER_TOKEN, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(FETCHER_CREDENTIALS):
                raise FileNotFoundError(
                    f"credentials.json not found at {FETCHER_CREDENTIALS}\n"
                    "The scorer shares credentials with isaac-email-fetcher."
                )
            flow = InstalledAppFlow.from_client_secrets_file(FETCHER_CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save back to fetcher token file
        with open(FETCHER_TOKEN, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ── Gmail label + star helpers ────────────────────────────────────────────────

def get_or_create_label(service, label_name: str) -> str:
    """Get label ID by name, creating it if it doesn't exist."""
    result = service.users().labels().list(userId="me").execute()
    for label in result.get("labels", []):
        if label["name"] == label_name:
            return label["id"]

    # Create it
    new_label = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
    ).execute()
    print(f"[Isaac] Created Gmail label: '{label_name}'")
    return new_label["id"]


def flag_email(service, email_id: str, label_id: str):
    """Star an email and apply Isaac's Picks label."""
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={
            "addLabelIds": ["STARRED", label_id],
        }
    ).execute()


# ── Email markdown parser ─────────────────────────────────────────────────────

def parse_emails_from_markdown(filepath: str) -> list[dict]:
    """Parse emails from Isaac's markdown output format."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    emails = []
    # Split on email section headers: ## 1. Subject, ## 2. Subject, etc.
    sections = re.split(r"\n## \d+\. ", content)

    for section in sections[1:]:  # skip file header
        lines = section.strip().split("\n")
        subject = lines[0].strip()

        email = {"subject": subject, "from": "", "to": "", "date": "", "id": "", "body": ""}

        body_lines = []
        in_body = False

        for line in lines[1:]:
            if line.startswith("**From:**"):
                email["from"] = line.replace("**From:**", "").strip().rstrip("  ")
            elif line.startswith("**To:**"):
                email["to"] = line.replace("**To:**", "").strip().rstrip("  ")
            elif line.startswith("**Date:**"):
                email["date"] = line.replace("**Date:**", "").strip()
            elif line.startswith("**Body:**"):
                in_body = True
            elif in_body and line.strip() == "---":
                break
            elif in_body:
                body_lines.append(line)

        email["body"] = "\n".join(body_lines).strip()
        emails.append(email)

    return emails


def find_latest_fetcher_output() -> str:
    """Find the most recent markdown file in isaac-email-fetcher/output/."""
    if not os.path.exists(FETCHER_OUTPUT_DIR):
        raise FileNotFoundError(
            f"isaac-email-fetcher/output/ not found at {FETCHER_OUTPUT_DIR}\n"
            "Make sure isaac-email-fetcher is in the same parent directory."
        )

    files = [
        f for f in os.listdir(FETCHER_OUTPUT_DIR)
        if f.endswith(".md") and f.startswith("emails_")
    ]

    if not files:
        raise FileNotFoundError("No email files found in isaac-email-fetcher/output/")

    files.sort(reverse=True)
    latest = os.path.join(FETCHER_OUTPUT_DIR, files[0])
    return latest


# ── Ollama scorer ─────────────────────────────────────────────────────────────

def check_ollama() -> bool:
    """Check if Ollama is running."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        urllib.request.urlopen(req, timeout=3)
        return True
    except Exception:
        return False


def score_email(email: dict) -> tuple[bool, str]:
    """
    Ask Ollama whether this email is important based on Isaac's criteria.
    Returns (is_important: bool, reason: str).
    """
    prompt = f"""You are Isaac, a work-focused AI assistant. Decide if this email is important.

CRITERIA — mark as important if the email matches ANY of these:
{CRITERIA}

EMAIL:
From: {email['from']}
Subject: {email['subject']}
Body (first 500 chars): {email['body'][:500]}

Respond with ONLY a JSON object in this exact format, nothing else:
{{"important": true, "reason": "one sentence explanation"}}
or
{{"important": false, "reason": "one sentence explanation"}}"""

    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            response_text = data.get("response", "").strip()

            # Parse JSON from response
            # Strip markdown fences if model adds them
            response_text = re.sub(r"```json|```", "", response_text).strip()
            result = json.loads(response_text)
            return result.get("important", False), result.get("reason", "")

    except json.JSONDecodeError:
        # If model doesn't return valid JSON, default to not important
        return False, "Could not parse model response"
    except Exception as e:
        return False, f"Ollama error: {e}"


def find_gmail_id(service, email: dict) -> str | None:
    """Search Gmail for the message ID matching this email."""
    # Search by subject and sender
    subject_clean = email["subject"].replace('"', '')
    query = f'subject:"{subject_clean}" from:{email["from"].split("<")[-1].strip(">")}'

    try:
        result = service.users().messages().list(
            userId="me", q=query, maxResults=1
        ).execute()
        messages = result.get("messages", [])
        if messages:
            return messages[0]["id"]
    except Exception:
        pass
    return None


# ── Save results ──────────────────────────────────────────────────────────────

def save_results(results: list[dict], flagged_count: int) -> str:
    """Save scoring results as a markdown file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filepath = os.path.join(OUTPUT_DIR, f"scored_{timestamp}.md")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Isaac — Email Scoring Results",
        "",
        f"**Scored:** {now_str}  ",
        f"**Total emails:** {len(results)}  ",
        f"**Flagged as important:** {flagged_count}",
        "",
        "---",
        "",
    ]

    for r in results:
        flag = "⭐ IMPORTANT" if r["important"] else "— skipped"
        lines += [
            f"## {flag} — {r['subject']}",
            "",
            f"**From:** {r['from']}  ",
            f"**Reason:** {r['reason']}",
            "",
            "---",
            "",
        ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Check Ollama
    print("[Isaac] Checking Ollama...")
    if not check_ollama():
        print("[Isaac] ERROR: Ollama is not running.")
        print("  Start it with: ollama serve")
        print("  Pull the model: ollama pull qwen2.5:3b")
        raise SystemExit(1)
    print(f"[Isaac] Ollama running. Model: {MODEL}")

    # Find latest email file
    print("[Isaac] Finding latest email file...")
    email_file = find_latest_fetcher_output()
    print(f"[Isaac] Using: {email_file}")

    # Parse emails
    emails = parse_emails_from_markdown(email_file)
    print(f"[Isaac] Parsed {len(emails)} email(s).")

    if not emails:
        print("[Isaac] No emails to score. Exiting.")
        return

    # Authenticate Gmail (for starring)
    print("[Isaac] Authenticating with Gmail...")
    service = authenticate_gmail()
    label_id = get_or_create_label(service, LABEL_NAME)

    # Score each email
    results = []
    flagged_count = 0

    for i, email in enumerate(emails, 1):
        print(f"[Isaac] Scoring {i}/{len(emails)}: {email['subject'][:60]}...")
        important, reason = score_email(email)

        if important:
            flagged_count += 1
            # Find Gmail message ID and flag it
            gmail_id = find_gmail_id(service, email)
            if gmail_id:
                flag_email(service, gmail_id, label_id)
                print(f"  ⭐ Important — starred in Gmail")
            else:
                print(f"  ⭐ Important — (could not find in Gmail to star)")
        else:
            print(f"  — Skipped")

        results.append({
            "subject": email["subject"],
            "from": email["from"],
            "important": important,
            "reason": reason,
        })

    # Save results
    output_path = save_results(results, flagged_count)
    print(f"\n[Isaac] Done. {flagged_count}/{len(emails)} emails flagged.")
    print(f"[Isaac] Results: {output_path}")


if __name__ == "__main__":
    main()

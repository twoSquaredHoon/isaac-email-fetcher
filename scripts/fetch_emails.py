#!/usr/bin/env python3
"""
Isaac — Email Fetcher (Gmail)

Modes:
  default              Fetch all emails from the last 24 hours
  --recent [N]         Fetch N most recent emails from inbox (default: 10)

Auth: OAuth via token.json (auto-generated on first run).
"""

import os
import sys
import base64
import argparse
from datetime import datetime, timedelta, timezone
from email import message_from_bytes
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

CREDENTIALS_FILE = os.path.join(PROJECT_DIR, "credentials.json")
TOKEN_FILE = os.path.join(PROJECT_DIR, "token.json")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

# ── Gmail API scope ────────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate() -> object:
    """Authenticate via OAuth. Opens browser on first run, silent afterward."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}\n"
                    "Download it from Google Cloud Console > APIs & Services > Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def decode_str(value: str) -> str:
    """Decode encoded email header strings (e.g. =?utf-8?...)."""
    return str(make_header(decode_header(value)))


def get_body(msg) -> str:
    """Extract plain text body from a parsed email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                charset = part.get_content_charset() or "utf-8"
                try:
                    body = part.get_payload(decode=True).decode(charset, errors="replace")
                except Exception:
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                break
    else:
        if msg.get_content_type() == "text/plain":
            charset = msg.get_content_charset() or "utf-8"
            body = msg.get_payload(decode=True).decode(charset, errors="replace")

    # Clean up: strip excessive blank lines
    lines = body.splitlines()
    cleaned = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 1:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)

    return "\n".join(cleaned).strip()


def parse_email(service, msg_ref: dict) -> dict:
    """Fetch and parse a single email by message reference."""
    raw = service.users().messages().get(
        userId="me", id=msg_ref["id"], format="raw"
    ).execute()

    raw_bytes = base64.urlsafe_b64decode(raw["raw"])
    msg = message_from_bytes(raw_bytes)

    return {
        "id": msg_ref["id"],
        "date": msg.get("Date", ""),
        "from": decode_str(msg.get("From", "(unknown)")),
        "to": decode_str(msg.get("To", "")),
        "subject": decode_str(msg.get("Subject", "(no subject)")),
        "body": get_body(msg),
    }


def fetch_last_24h(service) -> list[dict]:
    """Fetch all emails received in the last 24 hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    query = f"after:{cutoff.strftime('%Y/%m/%d')}"

    emails = []
    page_token = None

    while True:
        kwargs = {"userId": "me", "q": query, "maxResults": 100}
        if page_token:
            kwargs["pageToken"] = page_token

        result = service.users().messages().list(**kwargs).execute()
        messages = result.get("messages", [])

        for msg_ref in messages:
            email = parse_email(service, msg_ref)

            # Skip emails actually older than 24h (query is day-level granularity)
            try:
                email_dt = parsedate_to_datetime(email["date"])
                if email_dt.tzinfo is None:
                    email_dt = email_dt.replace(tzinfo=timezone.utc)
                if email_dt < cutoff:
                    continue
            except Exception:
                pass

            emails.append(email)

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    emails.sort(key=lambda e: e["date"], reverse=True)
    return emails


def fetch_recent(service, n: int = 10) -> list[dict]:
    """Fetch the N most recent emails from the inbox."""
    result = service.users().messages().list(
        userId="me", labelIds=["INBOX"], maxResults=n
    ).execute()

    messages = result.get("messages", [])
    emails = [parse_email(service, ref) for ref in messages]
    return emails


def save_markdown(emails: list[dict], mode: str, n: int = None) -> str:
    """Save fetched emails as a markdown file. Returns the output path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    if mode == "recent":
        filename = f"emails_recent{n}_{timestamp}.md"
        title = f"# Isaac — {n} Most Recent Inbox Emails"
        subtitle = f"**Mode:** {n} most recent  "
    else:
        filename = f"emails_24h_{timestamp}.md"
        title = "# Isaac — Emails (Last 24 Hours)"
        subtitle = "**Mode:** last 24 hours  "

    filepath = os.path.join(OUTPUT_DIR, filename)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        title,
        "",
        f"**Fetched:** {now_str}  ",
        subtitle,
        f"**Total emails:** {len(emails)}",
        "",
        "---",
        "",
    ]

    if not emails:
        lines.append("No emails found.")
    else:
        for i, email in enumerate(emails, 1):
            lines += [
                f"## {i}. {email['subject']}",
                "",
                f"**From:** {email['from']}  ",
                f"**To:** {email['to']}  ",
                f"**Date:** {email['date']}",
                "",
                "**Body:**",
                "",
                email["body"] if email["body"] else "*(no plain text body)*",
                "",
                "---",
                "",
            ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Isaac Email Fetcher")
    parser.add_argument(
        "--recent",
        nargs="?",
        const=10,
        type=int,
        metavar="N",
        help="Fetch N most recent inbox emails (default: 10)",
    )
    args = parser.parse_args()

    print("[Isaac] Authenticating with Gmail API...")
    service = authenticate()

    if args.recent is not None:
        n = args.recent
        print(f"[Isaac] Fetching {n} most recent inbox emails...")
        emails = fetch_recent(service, n)
        print(f"[Isaac] Found {len(emails)} email(s).")
        output_path = save_markdown(emails, mode="recent", n=n)
    else:
        print("[Isaac] Fetching emails from the last 24 hours...")
        emails = fetch_last_24h(service)
        print(f"[Isaac] Found {len(emails)} email(s).")
        output_path = save_markdown(emails, mode="24h")

    print(f"[Isaac] Done. Output: {output_path}")


if __name__ == "__main__":
    main()

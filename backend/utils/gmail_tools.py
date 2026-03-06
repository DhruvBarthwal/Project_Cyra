import base64
import threading
from functools import lru_cache
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.clean_mails import html_to_clean_text, clean_email_text


def extract_body(payload, depth=0):
    indent = "  " * depth
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if mime_type == "text/plain" and body_data:
        return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")

    if mime_type == "text/html" and body_data:
        html = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
        return html_to_clean_text(html)

    for part in payload.get("parts", []):
        result = extract_body(part, depth + 1)
        if result:
            return result

    return ""


def read_latest_email(service):
    msgs = service.users().messages().list(
        userId="me",
        maxResults=1,
        labelIds=["INBOX"]
    ).execute()

    messages = msgs.get("messages", [])
    if not messages:
        return None

    msg_id = messages[0]["id"]
    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    headers = msg["payload"].get("headers", [])
    sender = subject = ""

    for h in headers:
        if h["name"] == "From":
            sender = h["value"]
        elif h["name"] == "Subject":
            subject = h["value"]

    raw_body = extract_body(msg["payload"])
    body = html_to_clean_text(raw_body) if "<html" in raw_body.lower() else clean_email_text(raw_body)

    return {
        "id": msg_id,
        "from": sender,
        "subject": subject,
        "body": body[:500].strip()
    }


def list_inbox_email_ids(service, limit=10):
    msgs = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=limit
    ).execute()
    return [m["id"] for m in msgs.get("messages", [])]


@lru_cache(maxsize=50)
def _fetch_email_cached(email_id: str):
    """Cached internal fetcher — avoids repeat Gmail API calls for same email."""
    from utils.gmail_auth import get_gmail_service
    service = get_gmail_service()

    msg = service.users().messages().get(
        userId="me",
        id=email_id,
        format="full"
    ).execute()

    headers = msg["payload"].get("headers", [])
    subject = from_email = ""

    for h in headers:
        if h["name"].lower() == "subject":
            subject = h["value"]
        elif h["name"].lower() == "from":
            from_email = h["value"]

    def _extract(payload):
        if payload.get("mimeType") == "text/plain":
            data = payload["body"].get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        if payload.get("mimeType") == "text/html":
            data = payload["body"].get("data")
            if data:
                html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                return clean_email_text(html)
        for part in payload.get("parts", []):
            result = _extract(part)
            if result:
                return result
        return ""

    body = _extract(msg["payload"]) or ""

    print("\n========== EMAIL DEBUG ==========")
    print("EMAIL ID:", email_id)
    print("SUBJECT:", subject)
    print("BODY LENGTH:", len(body))
    print("\nBODY PREVIEW:")
    print(body[:300])

    return {
        "from": from_email,
        "subject": subject,
        "body": body
    }


def read_email_by_id(service, email_id: str):
    """Public function — uses cache internally."""
    return _fetch_email_cached(email_id)


def _prefetch_single(email_id: str):
    try:
        _fetch_email_cached(email_id)
    except Exception:
        pass

def prefetch_next_email(email_ids: list, current_index: int):
    """Prefetch next AND prev email in background."""
    to_prefetch = []
    
    if current_index + 1 < len(email_ids):
        to_prefetch.append(email_ids[current_index + 1])
    if current_index - 1 >= 0:
        to_prefetch.append(email_ids[current_index - 1])
    
    for email_id in to_prefetch:
        threading.Thread(
            target=_prefetch_single,
            args=(email_id,),
            daemon=True
        ).start()



def trash_email(service, msg_id):
    service.users().messages().trash(
        userId="me",
        id=msg_id
    ).execute()
    _fetch_email_cached.cache_clear()  


def send_email(service, to, subject, body):
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    message.attach(MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()


def star_email(service, email_id):
    try:
        result = service.users().messages().modify(
            userId="me",
            id=email_id,
            body={
                "addLabelIds": ["STARRED"],
                "removeLabelIds": []
            }
        ).execute()
        print(f"STAR SUCCESS - email_id: {email_id}, labels: {result.get('labelIds', [])}")
        return result
    except Exception as e:
        print(f"STAR FAILED - email_id: {email_id}, error: {e}")
        raise

def unstar_email(service, email_id):
    try:
        result = service.users().messages().modify(
            userId="me",
            id=email_id,
            body={
                "addLabelIds": [],
                "removeLabelIds": ["STARRED"]
            }
        ).execute()
        print(f"UNSTAR SUCCESS - email_id: {email_id}")
        return result
    except Exception as e:
        print(f"UNSTAR FAILED - email_id: {email_id}, error: {e}")
        raise


def untrash_email(service, email_id):
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"removeLabelIds": ["TRASH"]}
    ).execute()
    _fetch_email_cached.cache_clear()  
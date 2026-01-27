import base64
from email.message import EmailMessage
from utils.clean_mails import html_to_clean_text , clean_email_text
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def extract_body(payload, depth=0):
    indent = "  " * depth
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if body_data:
        print(f"{indent} Found body data (length={len(body_data)})")

    if mime_type == "text/plain" and body_data:
        text = base64.urlsafe_b64decode(
            body_data
        ).decode("utf-8", errors="ignore")
        return text

    if mime_type == "text/html" and body_data:
        text = base64.urlsafe_b64decode(
            body_data
        ).decode("utf-8", errors="ignore")
        return text

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
    sender = ""
    subject = ""

    for h in headers:
        if h["name"] == "From":
            sender = h["value"]
        elif h["name"] == "Subject":
            subject = h["value"]

    raw_body = extract_body(msg["payload"])

    if "<html" in raw_body.lower():
        body = html_to_clean_text(raw_body)
    else:
        body = clean_email_text(raw_body)

    body = body[:500]  

    return {
        "id": msg_id,
        "from": sender,
        "subject": subject,
        "body": body.strip()
    }



def delete_email(service, msg_id):
    service.users().messages().trash(
        userId="me",
        id=msg_id
    ).execute()


def send_email(service, to, subject, body):
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    
    message.attach(MIMEText(body, "plain"))
    
    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()
    
    service.users().messages().send(
        userId = "me",
        body = {"raw" : raw}
    ).execute()

import base64


def list_inbox_email_ids(service, limit=10):
    msgs = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=limit
    ).execute()

    return [m["id"] for m in msgs.get("messages", [])]


def read_email_by_id(service, email_id):
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

    def extract_body(payload):
        # Prefer plain text
        if payload.get("mimeType") == "text/plain":
            data = payload["body"].get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8")

        # Fallback to HTML
        if payload.get("mimeType") == "text/html":
            data = payload["body"].get("data")
            if data:
                html = base64.urlsafe_b64decode(data).decode("utf-8")
                return clean_email_text(html)

        # Recurse
        for part in payload.get("parts", []):
            result = extract_body(part)
            if result:
                return result

        return ""

    body = extract_body(msg["payload"]) or ""

    return {
        "from": from_email,
        "subject": subject,
        "body": body[:500].strip() 
    }


def star_email(service, email_id):
    service.users().messages().modify(
        userId = "me",
        id = email_id,
        body={
            "addLabelIds": ["STARRED"],
            "removeLabelIds": []
        }
    ).execute()

def unstar_email(service, email_id):
    service.users().messages().modify(
        userId = "me",
        id = email_id,
        body ={
            "addLabelIds" : [],
            "removeLabelIds" : ["STARRED"]
        }
    ).execute()

def untrash_email(service,email_id):
    service.users().messages().modify(
        userId = "me",
        id = email_id,
        body = {
            "removeLabelIds" : ["TRASH"]
        }
    ).execute()
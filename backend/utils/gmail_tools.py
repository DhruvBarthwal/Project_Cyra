import base64
from email.message import EmailMessage
from utils.clean_mails import html_to_clean_text , clean_email_text

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

    print(f"{indent}❌ No body found at this level")
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

    print("🚀 CALLING extract_body()")
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
    service.users().messages().delete(
        userId="me",
        id=msg_id
    ).execute()


def send_email(service, to, subject, body):
    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject

    encoded = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": encoded}
    ).execute()

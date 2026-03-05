from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import read_email_by_id
from utils.clean_mails import clean_email_body

def is_image_based(body: str | None) -> bool:
    if not body:
        return True
    text = body.lower()
    image_markers = ["<img", "cid:", "[image]", "image attached", "see attached image"]
    return any(m in text for m in image_markers)

def read_filtered_emails_node(state):
    service = get_gmail_service()

    sender = state.get("sender_filter")
    if not sender:
        return {**state, "response": "Whose emails should I read?"}

    if not state.get("email_ids"):
        results = service.users().messages().list(
            userId="me",
            q=f"from:{sender}",
            maxResults=10
        ).execute()

        email_ids = [m["id"] for m in results.get("messages", [])]

        if not email_ids:
            return {**state, "response": f"No emails found from {sender}."}

        state["email_ids"] = email_ids
        state["email_index"] = 0

    nav = state.get("navigation")
    if nav == "next":
        state["email_index"] = state.get("email_index", 0) + 1
    elif nav == "prev":
        state["email_index"] = state.get("email_index", 0) - 1
    state["navigation"] = None

    idx = state["email_index"]

    if idx < 0:
        state["email_index"] = 0
        return {**state, "response": "Already at the first email from this sender."}

    if idx >= len(state["email_ids"]):
        state["email_index"] = len(state["email_ids"]) - 1
        return {**state, "response": "That was the last email from this sender."}


    email_id = state["email_ids"][state["email_index"]]
    email = read_email_by_id(service, email_id)

    sender_name = email.get("from", sender)
    subject     = email.get("subject", "no subject")
    raw_body    = email.get("body", "")
    body        = clean_email_body(raw_body)
    trimmed     = body[:4000] if len(body) > 4000 else body

    return {
        **state,
        "email_id":     email_id,
        "email_from":   sender_name,
        "email_subject":subject,
        "email_body":   trimmed,
        "email_ids":    state["email_ids"],
        "email_index":  state["email_index"],
        "response":     f"from: {sender_name} | subject: {subject} | body: {trimmed}"
    }
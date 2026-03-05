from utils.gmail_tools import read_email_by_id, list_inbox_email_ids
from utils.gmail_auth import get_gmail_service
from utils.clean_mails import clean_email_body

SMALL_EMAIL_LIMIT = 300

def is_image_based(body: str | None) -> bool:
    if not body:
        return True
    text = body.lower()
    image_markers = ["<img", "cid:", "[image]", "image attached", "see attached image"]
    return any(marker in text for marker in image_markers)

def read_email_node(state):
    service = get_gmail_service()

    if "email_ids" not in state or not state["email_ids"]:
        email_ids = list_inbox_email_ids(service, limit=10)
        if not email_ids:
            return {**state, "response": "inbox is empty", "email_index": 0, "email_ids": []}
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
        return {**state, "response": "already at first email"}

    if idx >= len(state["email_ids"]):
        state["email_index"] = len(state["email_ids"]) - 1
        return {**state, "response": "no more emails"}

    email_id = state["email_ids"][state["email_index"]]  # use updated index
    email = read_email_by_id(service, email_id)

    sender  = email.get("from", "unknown")
    subject = email.get("subject", "no subject")
    raw_body = email.get("body", "")
    body = clean_email_body(raw_body)
    trimmed_body = body[:4000] if len(body) > 4000 else body

    return {
        **state,
        "email_id":     email_id,       # ← this is the key field
        "email_from":   sender,
        "email_subject":subject,
        "email_body":   trimmed_body,
        "email_index":  state["email_index"],  # ← persist updated index
        "email_ids":    state["email_ids"],
    }
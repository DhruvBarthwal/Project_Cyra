from utils.gmail_tools import read_email_by_id, list_inbox_email_ids
from utils.gmail_auth import get_gmail_service
from utils.summarize import summarize_email

SMALL_EMAIL_LIMIT = 300


def is_image_based(body: str | None) -> bool:
    if not body:
        return True

    text = body.lower()

    image_markers = [
        "<img",
        "cid:",
        "[image]",
        "image attached",
        "see attached image"
    ]

    return any(marker in text for marker in image_markers)


def normalize_field(value,fallback):
    if not value or str(value).strip().lower() in ["","none","not mentioned","null"]:
        return fallback
    return value

def speak_summary(summary: dict) -> str:
    parts = []
    
    purpose = summary.get("Purpose")
    if purpose and purpose.lower() != "not mentioned":
        parts.append(f"Basically, it's about {purpose.lower()}.")
    
    key_points = summary.get("Key points", [])
    # Filter out "Not mentioned" entries
    valid_points = [p for p in key_points if p.lower() != "not mentioned"]
    
    if valid_points:
        highlights = "; ".join(valid_points[:3])
        parts.append(f"The main highlights are: {highlights}.")
    
    deadline = normalize_field(
        summary.get("Deadlines"),
        "There's no deadline mentioned."
    )
    parts.append(deadline)
    
    return " ".join(parts)


def read_email_node(state):
    service = get_gmail_service()

    # Load inbox once
    if "email_ids" not in state:
        email_ids = list_inbox_email_ids(service, limit=10)

        if not email_ids:
            state["response"] = "Your inbox is empty 📭"
            state["email_body"] = ""
            return state

        state["email_ids"] = email_ids
        state["email_index"] = 0

    #  Navigation
    nav = state.get("navigation")

    if nav == "next":
        state["email_index"] += 1
    elif nav == "prev":
        state["email_index"] -= 1
        
    state["navigation"] = None

    #  Boundary checks
    if state["email_index"] < 0:
        state["email_index"] = 0
        state["response"] = "You're already at the first email."
        return state

    if state["email_index"] >= len(state["email_ids"]):
        state["email_index"] = len(state["email_ids"]) - 1
        state["response"] = "That was the last email in your inbox."
        return state

    #  Read selected email
    email_id = state["email_ids"][state["email_index"]]
    email = read_email_by_id(service, email_id)

    sender = email.get("from", "someone")
    subject = email.get("subject", "no subject")
    body = email.get("body", "")

    state["email_id"] = email_id
    state["email_from"] = sender
    state["email_subject"] = subject
    state["email_body"] = body

    #  Friendly voice responses
    if is_image_based(body):
        state["response"] = (
            f"Alright, this email is from {sender}. "
            f"It's about {subject}. "
            "It mostly contains images, so I can’t read it out. "
            "Do you want the next email or the previous one?"
        )
        return state

    if len(body) <= SMALL_EMAIL_LIMIT:
        state["response"] = (
            f"Okay, this one’s from {sender}. "
            f"It’s about {subject}.\n\n"
            f"{body}\n\n"
            "...\n\n"
            "What would you like to do next — next email or previous?"
        )
        return state

    summary = summarize_email(body)
    spoken_summary = speak_summary(summary)

    state["response"] = (
        f"This email is from {sender}, about {subject}.\n\n"
        "Here’s a quick summary for you:\n"
        f"{spoken_summary}\n\n"
        "...\n\n"
        "Say next email or previous email."
    )

    return state

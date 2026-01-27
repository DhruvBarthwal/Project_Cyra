from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import read_email_by_id
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
    return any(m in text for m in image_markers)


def normalize_field(value, fallback):
    if not value or str(value).strip().lower() in ["", "none", "not mentioned", "null"]:
        return fallback
    return value


def speak_summary(summary: dict) -> str:
    parts = []

    purpose = summary.get("Purpose")
    if purpose:
        parts.append(f"Basically, it’s  {purpose.lower()}.")

    key_points = summary.get("Key points", [])
    if key_points:
        highlights = "; ".join(key_points[:3])
        parts.append(f"The main highlights are: {highlights}.")

    deadline = normalize_field(
        summary.get("Deadlines"),
        "There’s no deadline mentioned."
    )
    parts.append(deadline)

    return " ".join(parts)


def read_filtered_emails_node(state):
    service = get_gmail_service()

    sender = state.get("sender_filter")
    if not sender:
        state["response"] = "Whose emails should I read?"
        return state

    if "email_ids" not in state or not state["email_ids"]:
        query = f"from:{sender}"
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=10
        ).execute()

        email_ids = [m["id"] for m in results.get("messages", [])]

        if not email_ids:
            state["response"] = f"I couldn’t find any emails from {sender}."
            return state

        state["email_ids"] = email_ids
        state["email_index"] = 0

    nav = state.get("navigation")
    if nav == "next":
        state["email_index"] += 1
    elif nav == "prev":
        state["email_index"] -= 1

    state["navigation"] = None

    if state["email_index"] < 0:
        state["email_index"] = 0
        state["response"] = "You’re already at the first email from this sender."
        return state

    if state["email_index"] >= len(state["email_ids"]):
        state["email_index"] = len(state["email_ids"]) - 1
        state["response"] = "That was the last email from this sender."
        return state

    email_id = state["email_ids"][state["email_index"]]
    email = read_email_by_id(service, email_id)

    sender_name = email.get("from", sender)
    subject = email.get("subject", "no subject")
    body = email.get("body", "")

    state["email_id"] = email_id
    state["email_from"] = sender_name
    state["email_subject"] = subject
    state["email_body"] = body

    if is_image_based(body):
        state["response"] = (
            f"This email from {sender_name} is about {subject}. "
            "It mostly contains images, so I can’t read it out. "
            "…\n\n"
            "Would you like the next email or the previous one?"
        )
        return state

    if len(body) <= SMALL_EMAIL_LIMIT:
        state["response"] = (
            f"Here’s an email from {sender_name}. "
            f"It’s about {subject}. "
            f"{body}. "
            "…\n\n"
            "What would you like to do next? Say next email or previous."
        )
        return state

    summary = summarize_email(body)
    spoken_summary = speak_summary(summary)

    state["response"] = (
        f"This one’s from {sender_name}. "
        f"It’s about {subject}. "
        f"{spoken_summary} "
        "…\n\n"
        "What would you like to do next? Say next email or previous."
    )

    return state

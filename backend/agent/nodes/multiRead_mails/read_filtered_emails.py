from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import read_email_by_id

def read_filtered_emails_node(state):
    service = get_gmail_service()
    
    sender = state.get("sender_filter")
    email_ids = state.get("email_ids", [])
    index = state.get("email_index", 0)

    print("\n📨 READ FILTERED EMAILS")
    print("Sender:", sender)
    print("Email IDs count:", len(email_ids))
    print("Current index:", index)

    # 🔹 Fetch emails if not loaded yet
    if not email_ids:
        query = f"from:{sender}"
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=20
        ).execute()

        email_ids = [m["id"] for m in results.get("messages", [])]
        state["email_ids"] = email_ids
        state["email_index"] = 0
        index = 0

        print("📥 Loaded email IDs:", email_ids)

    if not email_ids:
        state["response"] = f"No emails found from {sender}"
        state["email_id"] = None
        return state

    # 🔹 Clamp index safely
    index = max(0, min(index, len(email_ids) - 1))
    email_id = email_ids[index]

    email = read_email_by_id(service, email_id)

    # ✅ THIS IS CRITICAL
    state["email_index"] = index
    state["email_id"] = email_id

    print("📌 Selected email_id:", email_id)

    state["response"] = (
        f"Email {index + 1} from {sender}\n"
        f"From {email['from']}\n"
        f"Subject: {email['subject']}\n"
        f"{email['body']}"
    )

    return state
    
def next_email_node(state):
    email_ids = state.get("email_ids", [])
    index = state.get("email_index", 0) + 1

    if not email_ids:
        return state

    index = min(index, len(email_ids) - 1)

    state["email_index"] = index
    state["email_id"] = email_ids[index]

    print("➡️ NEXT EMAIL")
    print("Index:", index)
    print("Email ID:", state["email_id"])

    return state


def prev_email_node(state):
    email_ids = state.get("email_ids", [])
    index = state.get("email_index", 0) - 1

    if not email_ids:
        return state

    index = max(0, index)

    state["email_index"] = index
    state["email_id"] = email_ids[index]

    print("⬅️ PREV EMAIL")
    print("Index:", index)
    print("Email ID:", state["email_id"])

    return state


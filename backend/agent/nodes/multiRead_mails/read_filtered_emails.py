from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import read_email_by_id

def read_filtered_emails_node(state):
    service = get_gmail_service()
    
    sender = state.get("sender_filter")
    email_ids = state.get("email_ids")
    index = state.get("email_index", 0)
    
    if not email_ids:
        query = f"from:{sender}"
        results = service.users().messages().list(
            userId = "me",
            q = query,
            maxResults = 20
        ).execute()
        
        email_ids = [m["id"] for m in results.get("messages",[])]
        state["email_ids"] = email_ids
        state['email_index'] = 0
        
    if not email_ids:
        state["response"] = f"No emails found from {sender}"
        return state
    
    index = max(0, min(index, len(email_ids) -1))
    email_id = email_ids[index]
    
    email = read_email_by_id(service,email_id)
    
    state["email_index"] = index
    state["email_id"] = email_id
    state["response"] = (
        f"Email {index + 1} from {sender}\n"
        f"From {email['from']}\n"
        f"Subject: {email['subject']}\n"
        f"{email['body']}"
    )

    return state
    
def next_email_node(state):
    state["email_index"] = state.get("email_index", 0) + 1
    return state


def prev_email_node(state):
    state["email_index"] = state.get("email_index", 0) - 1
    return state


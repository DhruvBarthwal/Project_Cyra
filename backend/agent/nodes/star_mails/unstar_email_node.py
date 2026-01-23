from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import unstar_email

def unstar_email_node(state):
    print("⭐ ACTION NODE:", "<NODE_NAME>")
    print("Email ID:", state.get("email_id"))
    print("Email index:", state.get("email_index"))
    print("Email IDs length:", len(state.get("email_ids", [])))

    email_id  = state.get("email_id")
    if not email_id:
        state["response"] = "There is no email selected to unstar"
        return state
    
    service = get_gmail_service()
    unstar_email(service, email_id)
    
    state["response"] = "I removed the star from the mail"
    return state
    
from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import star_email as gmail_star

def star_email_node(state):
    email_id = state.get("email_id")
    if not email_id:
        state["response"] = "No email selected to star."
        return state
    
    service = get_gmail_service()
    gmail_star(service, email_id)
    
    state["response"] = "Email starred."
    return state
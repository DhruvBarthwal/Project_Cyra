from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import untrash_email as gmail_untrash  

def untrash_email_node(state):
    email_id = state.get("last_deleted_email_id")
    
    print(f"UNTRASH NODE - last_deleted_email_id: {email_id}")
    
    if not email_id:
        state["response"] = "No recently deleted email to restore."
        return state
    
    service = get_gmail_service()
    gmail_untrash(service, email_id)  
    
    state["email_id"] = email_id
    state["last_deleted_email_id"] = None
    state["response"] = "Email restored from trash."
    
    return state
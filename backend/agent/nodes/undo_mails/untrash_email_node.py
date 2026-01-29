from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import untrash_email

def untrash_email_node(state):
    """
    Restore email from trash.
    """

    email_id = state.get("email_id")
    if not email_id:
        state["response"] = "There is no email to restore"
        return state
    
    service = get_gmail_service()
    untrash_email(service,email_id)
    
    state["response"] = "Your email is restored form trash."
    state["last_deleted_email_id"] = None
    
    return state
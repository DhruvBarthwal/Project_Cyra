from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import star_email

def star_email_node(state):
    email_id = state.get("email_id")
    if not email_id:
        state["response"] = "There is no email selected to star."
        return state
    
    service =get_gmail_service()
    star_email(service, email_id)
    
    state["response"] ="Your email is starred"
    return state
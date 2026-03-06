from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import unstar_email as gmail_unstar

def unstar_email_node(state):
    email_id = state.get("email_id")
    if not email_id:
        state["response"] = "There is no email selected to unstar. Please select an email first."
        return state
    
    service = get_gmail_service()
    gmail_unstar(service, email_id)
    
    state["response"] = "I have removed the star from the email. What would you like to do next?"
    return state
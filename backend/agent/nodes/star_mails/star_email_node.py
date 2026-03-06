from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import star_email as gmail_star

def star_email_node(state):
    email_id = state.get("email_id")
    if not email_id:
        state["response"] = "There is no email selected to star. Please select an email first."
        return state
    
    try:
        service = get_gmail_service()
        gmail_star(service, email_id)
        state["response"] = "I have starred the email. What would you like to do next?"
    except Exception as e:
        print(f"STAR NODE ERROR: {e}")
        state["response"] = "Failed to star the email. Can you please try again or select a different email?"
    
    return state
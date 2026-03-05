from utils.gmail_tools import trash_email
from utils.gmail_auth import get_gmail_service

def delete_email_node(state):
    email_id = state.get("email_id","")
    
    if not email_id:
        state["response"] = "No email selected to delete."
        return state

    service = get_gmail_service()
    trash_email(service, email_id)
    
    state["last_deleted_email_id"] = email_id
    state["email_id"] = ""
    state["response"] = "Email deleted. Say undo to restore it."
    return state
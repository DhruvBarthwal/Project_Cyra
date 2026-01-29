from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import delete_email

def confirm_delete_node(state):
    email_id = state.get("email_id")
    
    if not email_id:
        state["response"] = "No email to delete."
        state["awaiting_field"] = None
        return state
    
    service = get_gmail_service()
    
    try:
        delete_email(service, email_id)
        
        # Store for potential undo
        state["last_deleted_email_id"] = email_id
        
        # Clear the awaiting field
        state["awaiting_field"] = None
        
        state["response"] = "Email deleted successfully. Say 'undo' if you want to restore it."
        
    except Exception as e:
        state["response"] = f"Failed to delete email: {str(e)}"
        state["awaiting_field"] = None
    
    return state
from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import delete_email

def confirm_delete_node(state):

    if not state.get("email_id"):
        state["response"] = "There is nothing to confirm."
        return state

    service = get_gmail_service()
    email_id = state.get("email_id")
    delete_email(service, state["email_id"])

    state["last_deleted_email_id"] = email_id
    state["response"] = "The email has been deleted successfully."
    state["email_id"] = None

    return state

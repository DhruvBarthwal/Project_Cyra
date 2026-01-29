def delete_email_node(state):
    
    if not state.get("email_id"):
        
        state["response"] = "No email selected to delete"
        return state
    
    state["response"] = "Are you sure you want to delete this email?"
    state["awaiting_field"] = "confirm_delete"
    return state
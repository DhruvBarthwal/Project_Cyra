def cancel_delete_node(state):
    state["response"] = "Okay, I won't delete this mail."
    state["awaiting_field"] = None
    return state
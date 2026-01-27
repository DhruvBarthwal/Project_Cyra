from langgraph.graph import StateGraph, END
from agent.state import AgentState

from agent.nodes.read_mails.read_email import read_email_node
from agent.nodes.read_mails.delete_email import delete_email_node
from agent.nodes.read_mails.confirm_delete import confirm_delete_node
from agent.nodes.multiRead_mails.read_filtered_emails import read_filtered_emails_node

from agent.nodes.send_mails.send_mail import compose_email_node,collect_to_local_node,collect_provider_node,collect_subject_node,collect_body_node,send_email_node

from agent.nodes.star_mails.star_email_node import star_email_node
from agent.nodes.star_mails.unstar_email_node import unstar_email_node

from agent.nodes.undo_mails.untrash_email_node import untrash_email_node
from agent.nodes.undo_mails.cancel_delete import cancel_delete_node
from agent.nodes.undo_mails.reset_email import reset_node

from utils.clean_mails import extract_sender
from utils.llm_intent import classify_intent
from utils.intent_fallback import fallback_intent

def intent_node(state: AgentState):
    user_input = state.get("user_input")

    if state.get("awaiting_field"):
        if state.get("user_input", "").lower() in ["reset", "cancel", "stop", "exit"]:
            state["intent"] = "RESET"
        return state

    sender = extract_sender(user_input)

    prev_sender = state.get("sender_filter")  

    if sender:
        if sender and sender != prev_sender:

            state["sender_filter"] = sender
            state["email_ids"] = []
            state["email_index"] = 0
            state["email_id"] = None
        else:
            state["sender_filter"] = sender

    intent = fallback_intent(user_input or "")

    if intent == "UNKNOWN":
        try:
            intent = classify_intent(user_input or "")
        except Exception:
            intent = "UNKNOWN"

    state["intent"] = intent
    
    if state["intent"] == "NEXT_EMAIL":
        state["navigation"] = "next"

    elif state["intent"] == "PREV_EMAIL":
        state["navigation"] = "prev"
        
    return state


def router(state: AgentState):
    
    awaiting = state.get("awaiting_field")
    text = (state.get("user_input") or "").lower()
        
    if awaiting == "to_local":
        return "COLLECT_TO_LOCAL"

    if awaiting == "email_provider":
        return "COLLECT_PROVIDER"
    
    if awaiting == "subject":
        return "COLLECT_SUBJECT"
    
    if awaiting == "body":
        return "COLLECT_BODY"
    
    if awaiting == "confirm":
        if any(k in text for k in ["yes", "send", "okay", "confirm"]):
            return "SEND_EMAIL"

        if any(k in text for k in ["no", "cancel", "stop", "don't"]):
            return "RESET" 
        
    if state.get("intent") in ["NEXT_EMAIL", "PREV_EMAIL"]:
        if state.get("sender_filter"):
            return "READ_FILTERED_EMAILS"
        return "READ_EMAIL"
    
    if state.get("intent") == "READ_EMAIL":
        if state.get("sender_filter"):
            return "READ_FILTERED_EMAILS"
        return "READ_EMAIL"
    
    if state.get("intent") == "STAR_EMAIL":
        return "STAR_EMAIL"
    
    if state.get("intent") == "UNSTAR_EMAIL":
        return "UNSTAR_EMAIL"
    
    if state.get("intent") == "UNTRASH_EMAIL":
        return "UNTRASH_EMAIL"
    
    if state.get("intent") == "CANCEL_DELETE":
         return "CANCEL_DELETE"

    if state.get("intent") == "RESET":
        return "RESET"
    
    return state["intent"]

def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("intent",intent_node)
    graph.add_node("read_email", read_email_node)
    graph.add_node("delete_email", delete_email_node)
    graph.add_node("confirm_delete", confirm_delete_node)
    
    graph.add_node("read_filtered_emails", read_filtered_emails_node)



    graph.add_node("compose_email", compose_email_node)
    graph.add_node("collect_to_local", collect_to_local_node)
    graph.add_node("collect_provider", collect_provider_node)

    graph.add_node("collect_subject", collect_subject_node)
    graph.add_node("collect_body", collect_body_node)
    graph.add_node("send_email", send_email_node)
    
    graph.add_node("star_email", star_email_node)
    graph.add_node("unstar_email", unstar_email_node)
    
    graph.add_node("untrash_email",untrash_email_node)
    graph.add_node("cancel_delete", cancel_delete_node)
    graph.add_node("reset", reset_node)
    
    graph.set_entry_point("intent")
    
    graph.add_conditional_edges(
        "intent",
        router,
        {
            "READ_EMAIL": "read_email",
            "READ_FILTERED_EMAILS" : "read_filtered_emails",
        
            "DELETE_EMAIL": "delete_email",
            "COMPOSE_EMAIL" : "compose_email",
            
            "COLLECT_TO_LOCAL": "collect_to_local",
            "COLLECT_PROVIDER": "collect_provider",
            "COLLECT_SUBJECT": "collect_subject",
            "COLLECT_BODY": "collect_body",
            "SEND_EMAIL": "send_email",
            
            "STAR_EMAIL" : "star_email",
            "UNSTAR_EMAIL" : "unstar_email",
            
            "UNTRASH_EMAIL": "untrash_email",
            "CANCEL_DELETE": "cancel_delete",
            "RESET" : "reset",
            
            "UNKNOWN": END,
        }
    )
    
    
    return graph.compile()
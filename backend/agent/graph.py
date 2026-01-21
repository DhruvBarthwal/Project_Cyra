from langgraph.graph import StateGraph, END
from agent.state import AgentState

from agent.nodes.read_mails.read_email import read_email_node
from agent.nodes.read_mails.delete_email import delete_email_node
from agent.nodes.read_mails.confirm_delete import confirm_delete_node
from agent.nodes.multiRead_mails.read_filtered_emails import read_filtered_emails_node, prev_email_node, next_email_node

from agent.nodes.send_mails.compose_email import compose_email_node
from agent.nodes.send_mails.collect_to import collect_to_node
from agent.nodes.send_mails.collect_subject import collect_subject_node
from agent.nodes.send_mails.collect_body import collect_body_node
from agent.nodes.send_mails.send_email import send_email_node

from agent.nodes.star_mails.star_email_node import star_email_node
from agent.nodes.star_mails.unstar_email_node import unstar_email_node

from agent.nodes.undo_mails.untrash_email_node import untrash_email_node
from agent.nodes.undo_mails.cancel_delete import cancel_delete_node

from utils.clean_mails import extract_sender
from utils.llm_intent import classify_intent
from utils.intent_fallback import fallback_intent

def intent_node(state: AgentState):
    
    if state.get("awaiting_field"):
        return state

    user_input = state.get("user_input", None)
    
    sender = extract_sender(user_input)
    if sender:
        state["sender_filter"] = sender
        print("SENDER FILTER:",sender)

    intent_from_fallback = fallback_intent(user_input or "")
  
    intent = intent_from_fallback

    if intent == "UNKNOWN":
        try:
            intent = classify_intent(user_input or "")
            
        except Exception as e:
            intent = "UNKNOWN"

    state["intent"] = intent
    return state

def router(state: AgentState):
    awaiting = state.get("awaiting_field")

    if awaiting == "to":
        return "COLLECT_TO"
    if awaiting == "subject":
        return "COLLECT_SUBJECT"
    if awaiting == "body":
        return "COLLECT_BODY"
    if awaiting == "confirm":
        if state.get("intent") == "CONFIRM_SEND":
            return "CONFIRM_SEND"
        if state.get("intent") == "CANCEL_DELETE":
            return "CANCEL_DELETE" 
    
    if state.get("intent") == "NEXT_EMAIL":
        return "NEXT_EMAIL"
    
    if state.get("intent") == "PREV_EMAIL":
        return "PREV_EMAIL"
    
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

    return state["intent"]

def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("intent",intent_node)
    graph.add_node("read_email", read_email_node)
    graph.add_node("delete_email", delete_email_node)
    graph.add_node("confirm_delete", confirm_delete_node)
    
    graph.add_node("read_filtered_emails", read_filtered_emails_node)
    graph.add_node("next_email", next_email_node)
    graph.add_node("prev_email", prev_email_node)


    graph.add_node("compose_email", compose_email_node)
    graph.add_node("collect_to", collect_to_node)
    graph.add_node("collect_subject", collect_subject_node)
    graph.add_node("collect_body", collect_body_node)
    graph.add_node("send_email", send_email_node)
    
    graph.add_node("star_email", star_email_node)
    graph.add_node("unstar_email", unstar_email_node)
    
    graph.add_node("untrash_email",untrash_email_node)
    graph.add_node("cancel_delete", cancel_delete_node)
    
    graph.set_entry_point("intent")
    
    graph.add_edge("next_email", "read_filtered_emails")
    graph.add_edge("prev_email", "read_filtered_emails")

    graph.add_conditional_edges(
        "intent",
        router,
        {
            "READ_EMAIL": "read_email",
            "READ_FILTERED_EMAILS" : "read_filtered_emails",
            
            "NEXT_EMAIL": "next_email",
            "PREV_EMAIL": "prev_email",
        
            "DELETE_EMAIL": "delete_email",
            "CONFIRM_SEND": "confirm_delete",
            "COMPOSE_EMAIL" : "compose_email",
            
            "COLLECT_TO": "collect_to",
            "COLLECT_SUBJECT": "collect_subject",
            "COLLECT_BODY": "collect_body",
            "SEND_EMAIL": "send_email",
            
            "STAR_EMAIL" : "star_email",
            "UNSTAR_EMAIL" : "unstar_email",
            
            "UNTRASH_EMAIL": "untrash_email",
            "CANCEL_DELETE": "cancel_delete",
            
            "UNKNOWN": END,
        }
    )
    
    
    return graph.compile()
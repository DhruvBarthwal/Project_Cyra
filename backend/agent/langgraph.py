from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, InjectedState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from typing import Annotated
from dotenv import load_dotenv

from agent.state import AgentState
from agent.nodes.read_mails.read_email import read_email_node
from agent.nodes.multiRead_mails.read_filtered_emails import read_filtered_emails_node
from agent.nodes.read_mails.delete_email import delete_email_node
from agent.nodes.star_mails.star_email_node import star_email_node
from agent.nodes.star_mails.unstar_email_node import unstar_email_node
from agent.nodes.undo_mails.untrash_email_node import untrash_email_node
from agent.nodes.undo_mails.reset_email import reset_node
from agent.nodes.send_mails.send_mail import send_email_node
from agent.prompts import SYSTEM_PROMPT

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_tokens=500)

def get_tool_call_id(state: AgentState) -> str:
    messages = state.get("messages", [])
    for m in reversed(messages):
        if m.type == "ai" and hasattr(m, "tool_calls") and m.tool_calls:
            return m.tool_calls[0]["id"]
    return "unknown"

@tool
def read_mail(state: Annotated[AgentState, InjectedState()]):
    """Read emails from inbox. Also handles next/previous navigation.
    Use for: read mail, next email, previous email, go back, go forward."""
    tool_call_id = get_tool_call_id(state)
    result = read_email_node(state)

    return Command(update={
        "email_id":     result.get("email_id", ""),
        "email_from":   result.get("email_from", ""),
        "email_subject":result.get("email_subject", ""),
        "email_body":   result.get("email_body", ""),
        "email_ids":    result.get("email_ids", state.get("email_ids", [])),
        "email_index":  result.get("email_index", state.get("email_index", 0)),
        "navigation":   None, 
        "messages": [ToolMessage(
            content=f"From: {result.get('email_from','unknown')}\nSubject: {result.get('email_subject','')}\nBody: {result.get('email_body','')[:800]}",
            tool_call_id=tool_call_id
        )]
    })

@tool
def read_filtered_mails(sender: str, state: Annotated[AgentState, InjectedState()]):
    """Read emails from a specific sender. Call ONCE only."""
    tool_call_id = get_tool_call_id(state)
    state["sender_filter"] = sender
    state["email_ids"] = []
    state["email_index"] = 0
    result = read_filtered_emails_node(state)

    return Command(update={
        "email_id":     result.get("email_id", ""),
        "email_from":   result.get("email_from", ""),
        "email_subject":result.get("email_subject", ""),
        "email_body":   result.get("email_body", ""),
        "email_ids":    result.get("email_ids", []),
        "email_index":  result.get("email_index", 0),
        "sender_filter": sender,
        "messages": [ToolMessage(
            content=result.get("response", "done"),
            tool_call_id=tool_call_id
        )]
    })
    
@tool
def navigate_email(direction: str, state: Annotated[AgentState, InjectedState()]):
    """Navigate to next or previous email.
    Use when user says: next email, previous email, go back, go forward.
    direction must be exactly 'next' or 'prev'
    """
    tool_call_id = get_tool_call_id(state)

    state["navigation"] = direction if direction in ["next", "prev"] else "next"
    result = read_email_node(state)

    new_email_id = result.get("email_id", "")

    content = f"From: {result.get('email_from','unknown')}\nSubject: {result.get('email_subject','')}\nBody: {result.get('email_body','')[:800]}"

    return Command(update={
        "email_id":     new_email_id,          
        "email_from":   result.get("email_from", ""),
        "email_subject":result.get("email_subject", ""),
        "email_body":   result.get("email_body", ""),
        "email_ids":    result.get("email_ids", state.get("email_ids", [])),
        "email_index":  result.get("email_index", 0), 
        "navigation":   None,
        "messages": [ToolMessage(content=content, tool_call_id=tool_call_id)]
    })
    
@tool
def delete_mail(state: Annotated[AgentState, InjectedState()]):
    """Delete the currently selected email."""
    tool_call_id = get_tool_call_id(state)
    email_id_to_delete = state.get("email_id", "")
    result = delete_email_node(state)
    return Command(update={
        "email_id": "",
        "last_deleted_email_id": email_id_to_delete, 
        "messages": [ToolMessage(
            content=result.get("response", "done"),
            tool_call_id=tool_call_id
        )]
    })

@tool
def star_email(state: Annotated[AgentState, InjectedState()]):
    """Add a star to the current email.
    Trigger words: 'star', 'mark', 'mark important', 'bookmark', 'flag', 'important'.
    Do NOT read the email, just star it.
    """
    tool_call_id = get_tool_call_id(state)
    print(f"STAR TOOL - email_id: {state.get('email_id')}, index: {state.get('email_index')}")
    result = star_email_node(state)
    return Command(update={
        "messages": [ToolMessage(
            content=result.get("response", "done"),
            tool_call_id=tool_call_id
        )]
    })
@tool
def unstar_email(state: Annotated[AgentState, InjectedState()]):
    """Unstar the currently selected email"""
    tool_call_id = get_tool_call_id(state)
    result = unstar_email_node(state)
    return Command(update={
        "messages": [ToolMessage(
            content=result.get("response", "done"),
            tool_call_id=tool_call_id
        )]
    })

@tool
def untrash_email(state: Annotated[AgentState, InjectedState()]):
    """Restore the last deleted email. Use when user says undo, restore, undelete."""
    tool_call_id = get_tool_call_id(state)
    result = untrash_email_node(state)
    
    return Command(update={
        "email_id": result.get("email_id", ""),
        "last_deleted_email_id": None, 
        "messages": [ToolMessage(
            content=result.get("response", "done"),
            tool_call_id=tool_call_id
        )]
    })

@tool
def send_email(state: Annotated[AgentState, InjectedState()]):
    """Send an email"""
    tool_call_id = get_tool_call_id(state)
    result = send_email_node(state)
    return Command(update={
        "messages": [ToolMessage(
            content=result.get("response", "done"),
            tool_call_id=tool_call_id
        )]
    })

@tool
def reset_convo(state: Annotated[AgentState, InjectedState()]):
    """Reset conversation. ONLY when user EXPLICITLY says 'reset' or 'start over'."""
    tool_call_id = get_tool_call_id(state)
    result = reset_node(state)
    return Command(update={
        "email_id":     "",
        "email_ids":    [],
        "email_index":  0,
        "sender_filter": None,
        "awaiting_field": None,
        "messages": [ToolMessage(
            content=result.get("response", "done"),
            tool_call_id=tool_call_id
        )]
    })

    
    
tools = [read_mail, read_filtered_mails, navigate_email,delete_mail, star_email, unstar_email, untrash_email, send_email, reset_convo]

llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)


def call_llm(state: AgentState):
    messages = list(state["messages"])
    system = [SystemMessage(content=SYSTEM_PROMPT)]
    non_system = [m for m in messages if m.type != "system"]
    trimmed = system + non_system[-6:]

    response = llm_with_tools.invoke(trimmed)
   
    if not response.content and not response.tool_calls:
        response = AIMessage(content="I can help you read, delete, star, or send emails. What would you like to do?")
    
    return {"messages": [response]}


SIMPLE_TOOLS = {"delete_mail", "star_email", "unstar_email", "untrash_email", "reset_convo"}

def should_continue(state):
    messages = state["messages"]
    last = messages[-1]

    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"

    return END


def after_tools(state):
    """Decide where to go after tool execution."""
    messages = state["messages"]
    
    last_ai_with_tool = next(
        (m for m in reversed(messages)
         if m.type == "ai" and hasattr(m, "tool_calls") and m.tool_calls),
        None
    )
    
    if last_ai_with_tool:
        tool_name = last_ai_with_tool.tool_calls[0]["name"]
        if tool_name in SIMPLE_TOOLS:
            return END  
    
    return "llm"  

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("llm", call_llm)
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges("llm", should_continue)
    graph.set_entry_point("llm")
 
    graph.add_conditional_edges("tools", after_tools)  
    
    return graph.compile(checkpointer=MemorySaver())

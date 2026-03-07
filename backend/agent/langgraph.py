from numpy import rint

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
from agent.nodes.send_mails.send_mail import send_email_node, generate_email_draft, enhance_email_draft
from agent.prompts import SYSTEM_PROMPT

load_dotenv()

llm = ChatGroq(model= "openai/gpt-oss-120b", temperature=0, max_tokens=500)

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
def reset_convo(state: Annotated[AgentState, InjectedState()]):
    """Reset conversation. ONLY when user EXPLICITLY says 'reset' or 'start over'."""
    tool_call_id = get_tool_call_id(state)
    result = reset_node(state)
    return Command(update={
        "email_id":      "",
        "email_ids":     [],
        "email_index":   0,
        "sender_filter": None,
        "awaiting_field": None,
        "send_step":     "",      
        "draft_subject": "",
        "draft_body":    "",
        "send_to":       "",
        "messages": [ToolMessage(
            content=result.get("response", "done"),
            tool_call_id=tool_call_id
        )]
    })
    
@tool
def send_email_flow(topic: str, state: Annotated[AgentState, InjectedState()]):
    """Handle entire email sending flow.
    ALWAYS call with topic = the user's EXACT message, word for word.
    Use for: write email, compose, send mail, create mail, enhance, yes, no, any email address.
    topic = user's exact words. NEVER leave topic empty.
    Always use sender name : Dhruv
    """
    tool_call_id = get_tool_call_id(state)
    step = state.get("send_step", "")
    new_email_keywords = ["create a mail", "compose", "write a mail", "write an email", 
                          "create an email", "send a mail", "send an email", "draft"]
    if any(kw in topic.lower() for kw in new_email_keywords):
        step = ""
    print(f"SEND FLOW - step: '{step}', topic: '{topic}'")

    if not step or step == "":
        draft = generate_email_draft(topic)
        body_preview = draft["body"][:500] + "..." if len(draft["body"]) > 500 else draft["body"]
    
        response = f"Here's your draft. Subject: {draft['subject']}. {body_preview}. Say enhance to improve, or tell me who to send it to."
    
        return Command(update={
            "draft_subject": draft["subject"],
            "draft_body":    draft["body"],
            "send_step":     "awaiting_recipient",
            "messages": [ToolMessage(content=response, tool_call_id=tool_call_id)]
        })

    if step == "awaiting_recipient" and any(
        w in topic.lower() for w in [
        "enhance", "improve", "formal", "shorter", "longer", "better",
        "humorous", "funny", "casual", "professional", "friendly",
        "simpler", "add", "change", "make it", "rather"
        ]
    ):
        draft = enhance_email_draft(state.get("draft_body", ""), topic)
        body_preview = draft["body"][:500] + "..." if len(draft["body"]) > 500 else draft["body"]
    
        response = f"Enhanced. Subject: {draft['subject']}. {body_preview}. Who should I send this to?"
    
        return Command(update={
            "draft_subject": draft["subject"],
            "draft_body":    draft["body"],
            "send_step":     "awaiting_recipient",
            "messages": [ToolMessage(content=response, tool_call_id=tool_call_id)]
    })

    if step == "awaiting_recipient":
        email = _parse_email(topic)
        print(f"PARSED EMAIL: '{topic}' → '{email}'")
    
        if not email:
            return Command(update={
                "messages": [ToolMessage(
                    content="I couldn't parse that email. Say it like 'dhruv four two one six h at gmail'.",
                    tool_call_id=tool_call_id
                )]
            })
    
        subject = state.get("draft_subject", "")
        return Command(update={
            "send_to":   email,
            "send_step": "confirm_send",
            "messages": [ToolMessage(
                content=f"Sending '{subject}' to {email}. Say yes to confirm.",  
                tool_call_id=tool_call_id
            )]
        })

    if step == "confirm_send":
        if any(w in topic.lower() for w in ["yes", "confirm", "send", "go ahead", "sure", "ok"]):
            result = send_email_node(state)
            return Command(update={
                "draft_subject": "",
                "draft_body":    "",
                "send_to":       "",
                "send_step":     "",
                "messages": [ToolMessage(
                    content=result.get("response", "Email sent."),
                    tool_call_id=tool_call_id
                )]
            })
        else:
            return Command(update={
                "send_step":     "",
                "draft_subject": "",
                "draft_body":    "",
                "send_to":       "",
                "messages": [ToolMessage(
                    content="Okay, cancelled.",
                    tool_call_id=tool_call_id
                )]
            })

    return Command(update={
        "messages": [ToolMessage(
            content="Something went wrong. Please try again.",
            tool_call_id=tool_call_id
        )]
    })

def _parse_email(spoken: str) -> str:
    spoken = spoken.lower().strip()
    
    prefixes = [
        "send it to", "send to", "send this to", "mail to",
        "email to", "address is", "the email is", "my email is",
        "recipient is", "to"
    ]
    for prefix in sorted(prefixes, key=len, reverse=True):
        if spoken.startswith(prefix):
            spoken = spoken[len(prefix):].strip()
            break

    if "@" in spoken and "." in spoken.split("@")[-1]:
        return spoken.strip().rstrip(".,!? ")  

    domain_map = {
        "gmail": "gmail.com",
        "outlook": "outlook.com",
        "hotmail": "hotmail.com",
        "yahoo": "yahoo.com",
        "icloud": "icloud.com",
    }

    spoken = spoken.replace(" at the rate ", "@")
    spoken = spoken.replace(" at ", "@")
    spoken = spoken.replace(" dot ", ".")
    spoken = spoken.replace(" @ ", "@")
    spoken = spoken.replace("@ ", "@")
    spoken = spoken.replace(" @", "@")

    word_to_num = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
    }
    for word, digit in word_to_num.items():
        spoken = spoken.replace(word, digit)

    if "@" in spoken:
        parts = spoken.split("@")
        if len(parts) == 2:
            name = parts[0].strip().replace(" ", "")
            domain_part = parts[1].strip().replace(" ", "").rstrip(".,!? ")
            if domain_part in domain_map:
                domain_part = domain_map[domain_part]
            elif "." not in domain_part:
                domain_part = domain_part + ".com"
            return f"{name}@{domain_part}"
    else:
        for word, domain in domain_map.items():
            if word in spoken:
                name = spoken.replace(word, "").strip().replace(" ", "").rstrip(".,!? ")
                return f"{name}@{domain}"

    return ""
    
    
tools = [read_mail, read_filtered_mails, navigate_email, delete_mail, star_email, unstar_email, 
         untrash_email, send_email_flow, reset_convo]

llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)


def call_llm(state: AgentState):
    messages = list(state["messages"])
    
    send_step = state.get("send_step", "")
    print(f"CALL LLM - send_step: '{send_step}', last human: '{[m.content for m in messages if m.type == 'human'][-1:]}'")
    print(f"CALL LLM - tool response in state: {state.get('draft_subject', 'NO DRAFT')}")
    state_context = ""
    if send_step == "awaiting_recipient":
        state_context = "\n\nCURRENT STATE: Email draft is ready. send_step=awaiting_recipient. User's next message is either an enhancement request OR a recipient. Call send_email_flow with topic = user's message."
    elif send_step == "confirm_send":
        state_context = f"\n\nCURRENT STATE: Ready to send to {state.get('send_to','')}. send_step=confirm_send. Call send_email_flow with topic = user's message (yes/no)."
    
    system = [SystemMessage(content=SYSTEM_PROMPT + state_context)]
    non_system = [m for m in messages if m.type != "system"]
    trimmed = system + non_system[-6:]

    response = llm_with_tools.invoke(trimmed)
    
    if not response.content and not response.tool_calls:
        response = AIMessage(content="I can help with emails. What would you like to do?")
    
    return {"messages": [response]}


SIMPLE_TOOLS = {"delete_mail", "star_email", "unstar_email", "untrash_email", "reset_convo","send_email_flow"}

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

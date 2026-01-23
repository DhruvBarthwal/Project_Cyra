from utils.clean_mails import normalize_username

def compose_email_node(state):
    
    print("✉️ COMPOSE EMAIL STARTED")
    
    state["to_local"] = None
    state["email_provider"] = None
    state["to"] = None
    state["subject"] = None
    state["body"] = None

    state["awaiting_field"] = "to_local"
    state["intent"] = "COLLECT_TO_LOCAL"
    state["response"] = "Sure. Who do you want to send the email to?"

    return state

def collect_to_local_node(state):
    print("📛 Collecting email username")

    spoken = state.get("user_input")
    username = normalize_username(spoken)

    if not username:
        state["response"] = (
            "I couldn't understand the username. "
            "Please say only the part before at, "
            "for example: dhruv four two one six h."
        )
        return state

    state["to_local"] = username
    state["awaiting_field"] = "email_provider"
    state["response"] = (
        "Got it. Is this a Gmail, Outlook, Yahoo, or something else?"
    )

    return state

def collect_provider_node(state):
    print(" COLLECTING EMAIL PROVIDER")

    spoken = state.get("user_input", "").lower()

    if "gmail" in spoken:
        domain = "gmail.com"
    elif "outlook" in spoken or "hotmail" in spoken:
        domain = "outlook.com"
    elif "yahoo" in spoken:
        domain = "yahoo.com"
    else:
        state["response"] = (
            "Please say the email provider clearly. "
            "For example: Gmail, Outlook, or Yahoo."
        )
        return state

    local = state.get("to_local")
    full_email = f"{local}@{domain}"
    
    print("full email:",full_email)
    
    state["email_provider"] = domain
    state["to"] = full_email

    state["awaiting_field"] = "subject"
    state["intent"] = "COLLECT_SUBJECT"

    state["response"] = f"Okay. What is the subject of the email?"

    print(" FINAL EMAIL:", full_email)

    return state
    

def collect_subject_node(state):
    
    print("📝 COLLECTING SUBJECT")
    state["subject"] = state["user_input"]
    state["awaiting_field"] = "body"
    state["intent"] = "COLLECT_BODY"
    state["response"] = "Okay. What should the email say?"
    

    return state

def collect_body_node(state):
    
    print("📄 COLLECTING BODY")
    
    state["body"] = state["user_input"]
    
    state["to"] = state.get("to")
    state["to_local"] = state.get("to_local")
    state["email_provider"] = state.get("email_provider")
    state["subject"] = state.get("subject")
    
    state["awaiting_field"] = "confirm"
    state["response"] = "Do you want me to send this email now?"

    return state

from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import send_email

def send_email_node(state):
    print("📤 SENDING EMAIL")
    print("TO:", state.get("to"))
    print("SUBJECT:", state.get("subject"))
    print("BODY:", state.get("body"))

    if not state.get("to") or not state.get("body"):
        state["response"] = (
            "Something went wrong. Email details are incomplete. Let's try again."
        )
        state["intent"] = "RESET"
        return state

    service = get_gmail_service()

    send_email(
        service,
        to=state["to"],
        subject=state["subject"],
        body=state["body"],
    )

    # cleanup
    state["awaiting_field"] = None
    state["to"] = None
    state["to_local"] = None
    state["email_provider"] = None
    state["subject"] = None
    state["body"] = None

    state["response"] = "Your email has been sent successfully."

    return state


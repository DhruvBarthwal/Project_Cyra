from utils.clean_mails import normalize_username
from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import send_email

#---------------------------- Create a mail ----------------------------

def compose_email_node(state):
    
    if state.get("awaiting_field") is None:
        state["intent"] = "COMPOSE_EMAIL"
        state["awaiting_field"] = "to_local"
        state["response"] = "Sure. Who do you want to send the email to?"

    return state

#---------------------------- Collect email id ----------------------------

def collect_to_local_node(state):

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
    state["response"] = f"Okay. What is the subject of the email?"

    print(" FINAL EMAIL:", full_email)

    return state
    
#---------------------------- Collect subject ----------------------------

def collect_subject_node(state):
    
    print(f"  Before: to={state.get('to')}, subject={state.get('subject')}, body={state.get('body')}" )
   
    state["subject"] = state["user_input"]
    state["awaiting_field"] = "body"
    state["response"] = "Okay. What should the email say?"
    
    return state

#---------------------------- Collect Body ----------------------------

def collect_body_node(state):
    
    state["body"] = state["user_input"]
    state["awaiting_field"] = "confirm"
    state["response"] = "Do you want me to send this email now?"
    
    return state

#---------------------------- Send Mail ----------------------------

def send_email_node(state):
    
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
    state["intent"] = None
    state["to"] = None
    state["to_local"] = None
    state["email_provider"] = None
    state["subject"] = None
    state["body"] = None

    state["response"] = "Your email has been sent successfully."

    return state


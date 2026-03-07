from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import send_email as gmail_send
from langchain_groq import ChatGroq

draft_llm = ChatGroq(model= "openai/gpt-oss-120b", temperature=0.7, max_tokens=800)

def generate_email_draft(topic: str) -> dict:
    response = draft_llm.invoke(
        f"""Write a professional email about: {topic}

        Rules:
        - Do NOT assume or invent any names, use generic placeholders like [Name] or [Recipient]
        - Do NOT use the name "Alex" or any other specific name unless mentioned in the topic
        - Keep it concise and natural

        Return ONLY in this exact format with no extra text:
        SUBJECT: <subject line>
        BODY:
        <email body>"""
    )
    
    text = response.content
    lines = text.strip().split("\n")
    subject = ""
    body_lines = []
    in_body = False
    
    for line in lines:
        if line.startswith("SUBJECT:"):
            subject = line.replace("SUBJECT:", "").strip()
        elif line.startswith("BODY:"):
            in_body = True
        elif in_body:
            body_lines.append(line)
    
    return {
        "subject": subject,
        "body": "\n".join(body_lines).strip()
    }

def enhance_email_draft(current_body: str, instruction: str) -> dict:
    """Enhance existing draft based on user instruction."""
    response = draft_llm.invoke(
        f"""Enhance this email based on instruction: {instruction}

        Current email:
        {current_body}

        Return ONLY in this exact format:
        SUBJECT: <subject line>
        BODY:
        <enhanced email body>"""
    )
    
    text = response.content
    lines = text.strip().split("\n")
    subject = ""
    body_lines = []
    in_body = False
    
    for line in lines:
        if line.startswith("SUBJECT:"):
            subject = line.replace("SUBJECT:", "").strip()
        elif line.startswith("BODY:"):
            in_body = True
        elif in_body:
            body_lines.append(line)
    
    return {
        "subject": subject,
        "body": "\n".join(body_lines).strip()
    }

def send_email_node(state):
    to = state.get("send_to", "")
    subject = state.get("draft_subject", "")
    body = state.get("draft_body", "")
    
    if not to or not subject or not body:
        state["response"] = "Missing email details. Let's start over."
        return state
    
    service = get_gmail_service()
    gmail_send(service, to=to, subject=subject, body=body)

    state["draft_subject"] = ""
    state["draft_body"] = ""
    state["send_to"] = ""
    state["send_step"] = ""
    state["response"] = f"Email sent to {to}."
    
    return state
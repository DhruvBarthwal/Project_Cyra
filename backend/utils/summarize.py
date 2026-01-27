from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agent.prompts import SYSTEM_PROMPT
from agent.state import EmailSummary

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,  # IMPORTANT: deterministic extraction
)

MAX_CHARS = 6000

def summarize_email(email_text: str) -> dict:
    """
    Summarizes email content into a structured dictionary.
    """

    if not email_text or len(email_text) < 80:
        return {
            "Sender": "Not mentioned",
            "Purpose": "Not mentioned",
            "Key points": [email_text.strip()],
            "Deadlines": "Not mentioned",
        }

    email_text = email_text[:MAX_CHARS]

    structured_llm = llm.with_structured_output(EmailSummary)
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=email_text),
    ]

    try:
        result = structured_llm.invoke(messages)
        
        return {
            "Sender": result.sender or "Not mentioned",
            "Purpose": result.purpose or "Not mentioned",
            "Key points": result.key_points if result.key_points else ["Not mentioned"],
            "Deadlines": result.deadlines or "Not mentioned",
        }
        
    except Exception as e:
        return {
            "Sender": "Not mentioned",
            "Purpose": "Summarization failed",
            "Key points": ["Unable to summarize this email."],
            "Deadlines": "Not mentioned",
        }


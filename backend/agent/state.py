from typing import TypedDict, Optional, List
from pydantic import BaseModel, Field


class AgentState(TypedDict, total=False):
    user_input : str
    intent : str
    
    #email reading
    email_id : str
    email_from : str
    email_subject : str
    email_body : str
    
    #email composing
    to : Optional[str]
    to_local : Optional[str]
    email_provider : Optional[str]
    subject : Optional[str]
    body : Optional[str]
    attachments : Optional[List[str]]
    awaiting_field : Optional[str]  # stores the previous question asked
    
    #email navigation
    navigation: Optional[str]
    email_ids : List[str]
    email_index: int
    sender_filter : Optional[str]
    
    last_deleted_email_id : str

    response: str
    

class EmailSummary(BaseModel):
    sender: str = Field(description="Who sent this email")
    purpose: str = Field(description="Main purpose or topic of the email")
    key_points: List[str] = Field(description="Important details, offers, or information")
    deadlines: str = Field(description="Any time-sensitive information or deadlines")

    
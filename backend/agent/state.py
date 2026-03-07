from typing import Optional, List, Annotated, Sequence
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    intent: str

    # email reading
    email_id: str
    email_from: str
    email_subject: str
    email_body: str

    # email navigation
    navigation: Optional[str]
    email_ids: List[str]
    email_index: int
    sender_filter: Optional[str]

    # email actions
    last_deleted_email_id: str
    awaiting_field: Optional[str]

    # email composing
    draft_subject: str   
    draft_body: str   
    send_to: str     
    send_step: str           

    response: str

class EmailSummary(BaseModel):
    sender: str = Field(description="Who sent this email")
    purpose: str = Field(description="Main purpose or topic of the email")
    key_points: List[str] = Field(description="Important details, offers, or information")
    deadlines: str = Field(description="Any time-sensitive information or deadlines")
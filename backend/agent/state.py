from typing import TypedDict

class AgentState(TypedDict, total=False):
    user_input : str
    intent : str
    to : str
    subject : str
    body : str
    confiramtion : bool
    
    
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.schemas import VoiceInput
from agent.graph import build_graph
from utils.gmail_auth import get_gmail_service
from utils.gmail_tools import delete_email

SESSION = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


@app.get("/")
def hello():
    return {"message": "Backend is running"}

@app.post("/voice")
async def voice_input(payload: VoiceInput):

    session_id  = "default"
    
    prev_state = SESSION.get(session_id,{})
    
    new_state = {
        **prev_state,
        "user_input": payload.text,
    }
    
    if payload.email_id is not None:
        new_state["email_id"] = payload.email_id
        
    result = graph.invoke(new_state)
    
    SESSION[session_id] = result
    
    return {
        "response": result.get("response"),
        "email_id": result.get("email_id"),
    }
        
from dotenv import load_dotenv
from utils.schemas import VoiceInput

load_dotenv()

from fastapi import FastAPI
from agent.graph import build_graph
from utils.schemas import VoiceInput


app = FastAPI()
graph = build_graph()

@app.get("/")
def hello():
    return {"message" : "Backend is running"}

@app.post("/voice")
async def voice_input(payload : VoiceInput):
    result = graph.invoke({"user_input":payload.text})
    return result
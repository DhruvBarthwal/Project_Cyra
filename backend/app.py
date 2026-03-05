from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessage
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.schemas import VoiceInput
from agent.langgraph import build_graph
from agent.prompts import SYSTEM_PROMPT
import asyncio

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
    config = {"configurable": {"thread_id": "default"}}

    result = await asyncio.to_thread(
    graph.invoke,
    {"messages": [HumanMessage(content=payload.text)]},
    config
)

    ai_messages = [
        m for m in result["messages"]
        if m.type == "ai" and m.content.strip()
    ]
    response_text = ai_messages[-1].content if ai_messages else "Sorry, I didn't get that."

    return {
        "response": response_text,
        "email_id": result.get("email_id"),
    }
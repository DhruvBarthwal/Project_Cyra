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

    messages = result["messages"]
    
    last_human_idx = max(
        (i for i, m in enumerate(messages) if m.type == "human"),
        default=0
    )
    messages_this_turn = messages[last_human_idx + 1:] 
    last_ai_with_tool = next(
        (m for m in reversed(messages_this_turn)
         if m.type == "ai" and hasattr(m, "tool_calls") and m.tool_calls),
        None
    )
    
    if last_ai_with_tool:
        tool_call_id = last_ai_with_tool.tool_calls[0]["id"]
        tool_response = next(
            (m for m in messages_this_turn
             if m.type == "tool" and m.tool_call_id == tool_call_id),
            None
        )
        ai_after_tool = next(
            (m for m in reversed(messages_this_turn)
             if m.type == "ai" and m.content and m.content.strip()
             and not (hasattr(m, "tool_calls") and m.tool_calls)),
            None
        )
        
        if ai_after_tool:
            response_text = ai_after_tool.content
        elif tool_response:
            response_text = tool_response.content
        else:
            response_text = "Done."
    else:
        ai_response = next(
            (m for m in reversed(messages_this_turn)
             if m.type == "ai" and m.content and m.content.strip()),
            None
        )
        response_text = ai_response.content if ai_response else "Sorry, I didn't get that."

    return {
        "response": response_text,
        "email_id": result.get("email_id"),
    }
from langgraph.graph import StateGraph
from agent.state import AgentState
from utils.llm_intent import classify_intent
from utils.intent_fallback import fallback_intent

def intent_node(state: AgentState):

    user_input = state.get("user_input", None)

    intent_from_fallback = fallback_intent(user_input or "")
  
    intent = intent_from_fallback

    if intent == "UNKNOWN":
        try:
            intent = classify_intent(user_input or "")
            
        except Exception as e:
            intent = "UNKNOWN"

    state["intent"] = intent
    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("intent",intent_node)
    graph.set_entry_point("intent")
    graph.set_finish_point("intent")
    return graph.compile()
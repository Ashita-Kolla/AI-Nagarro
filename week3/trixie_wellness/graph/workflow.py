from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, END
from agents.emotion_agent import run_emotion_agent
from agents.context_agent import run_context_agent
from agents.rag_agent import run_rag_agent
from agents.recommendation_agent import run_recommendation_agent
from agents.safety_agent import run_safety_agent


class WellnessState(TypedDict):
    user_input:      str
    stress_level:    str
    emotion:         str
    severity:        str
    cause:           str
    cause_summary:   str
    recommendations: List[str]
    tools_used:      List[str]   # MCP: which tools the agent called
    tool_results:    List[Any]   # MCP: raw structured results from each tool
    journal_history:  List[Any]   # Historical journal entries
    emotional_pattern: str        # Summary of user's emotional patterns
    reminders:       List[Any]   # MCP: scheduled wellness reminders
    rag_domain:      str         # Classified intent domain
    rag_context:     str         # Retrieved knowledge base context
    is_flagged:      bool        # Responsible AI moderation flag
    risk_level:      str         # Risk level (low, medium, high, critical)
    flag_reason:     str         # Reason for flagging
    safety_response: str         # Generated safety response


def _build_graph() -> object:
    graph = StateGraph(WellnessState)
    graph.add_node("safety_agent",         run_safety_agent)
    graph.add_node("emotion_agent",        run_emotion_agent)
    graph.add_node("context_agent",        run_context_agent)
    graph.add_node("rag_agent",            run_rag_agent)
    graph.add_node("recommendation_agent", run_recommendation_agent)
    
    graph.set_entry_point("safety_agent")
    
    def route_after_safety(state: WellnessState) -> str:
        if state.get("is_flagged", False):
            return END
        return "emotion_agent"
        
    graph.add_conditional_edges("safety_agent", route_after_safety)
    
    graph.add_edge("emotion_agent",        "context_agent")
    graph.add_edge("context_agent",        "rag_agent")
    graph.add_edge("rag_agent",            "recommendation_agent")
    graph.add_edge("recommendation_agent", END)
    return graph.compile()


_compiled_graph = _build_graph()


def run_pipeline(user_input: str, stress_level: str = "") -> WellnessState:
    from tools.google_docs_tool import get_journal_history
    from tools.calendar_tool import get_calendar_reminders
    history_res = get_journal_history()
    history = history_res.get("entries", [])
    
    reminders_res = get_calendar_reminders()
    rem_list = reminders_res.get("reminders", [])
    
    initial_state: WellnessState = {
        "user_input":      user_input,
        "stress_level":    stress_level,
        "emotion":         "",
        "severity":        "",
        "cause":           "",
        "cause_summary":   "",
        "recommendations": [],
        "tools_used":      [],
        "tool_results":    [],
        "journal_history":  history,
        "emotional_pattern": "",
        "reminders":       rem_list,
        "rag_domain":      "",
        "rag_context":     "",
        "is_flagged":      False,
        "risk_level":      "low",
        "flag_reason":     "none",
        "safety_response": "",
    }
    return _compiled_graph.invoke(initial_state)

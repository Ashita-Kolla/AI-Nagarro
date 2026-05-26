from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, END
from agents.emotion_agent import run_emotion_agent
from agents.context_agent import run_context_agent
from agents.recommendation_agent import run_recommendation_agent


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


def _build_graph() -> object:
    graph = StateGraph(WellnessState)
    graph.add_node("emotion_agent",        run_emotion_agent)
    graph.add_node("context_agent",        run_context_agent)
    graph.add_node("recommendation_agent", run_recommendation_agent)
    graph.set_entry_point("emotion_agent")
    graph.add_edge("emotion_agent",        "context_agent")
    graph.add_edge("context_agent",        "recommendation_agent")
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
    }
    return _compiled_graph.invoke(initial_state)

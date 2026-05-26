import json
import re
from llm.tinyllama import chat

VALID_CAUSES = ["workload", "meetings", "personal", "unclear"]

SYSTEM_PROMPT = """You are a workplace stress context analyzer for a wellness assistant.

Given the user's message and their detected emotion, identify the most likely root cause of their stress.

Respond with ONLY a JSON object — no explanation, no extra text.

Required format:
{"cause": "<cause>", "summary": "<summary>"}

cause must be one of: workload, meetings, personal, unclear
summary must be a single sentence (max 20 words) describing the situation

Examples:
User: "I have 10 deadlines this week and my manager keeps adding tasks"
Emotion: overwhelmed | Severity: high
Response: {"cause": "workload", "summary": "Employee is overwhelmed by too many tasks and deadlines assigned by their manager."}

User: "I have back-to-back calls all day and can't get any real work done"
Emotion: tired | Severity: medium  
Response: {"cause": "meetings", "summary": "Employee's day is consumed by meetings leaving no time for focused work."}

Respond with ONLY the JSON object."""

def _keyword_cause(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["meeting", "call", "zoom", "standup", "sync", "conference"]):
        return "meetings"
    if any(w in t for w in ["deadline", "task", "project", "workload", "overtime",
                             "too much work", "deliverable", "backlog"]):
        return "workload"
    if any(w in t for w in ["personal", "family", "health", "home", "sick",
                             "relationship", "life"]):
        return "personal"
    return "unclear"

def _fallback_summary(emotion: str, cause: str) -> str:
    templates = {
        "workload":  f"Employee is feeling {emotion} due to heavy workload and task pressure.",
        "meetings":  f"Employee is feeling {emotion} from too many meetings with little focus time.",
        "personal":  f"Employee is dealing with personal stress that is affecting their work.",
        "unclear":   f"Employee is feeling {emotion}; the specific stressor is not yet identified.",
    }
    return templates.get(cause, templates["unclear"])

def _parse_response(llm_output: str, original_input: str, emotion: str) -> dict:
    try:
        data = json.loads(llm_output.strip())
        if data.get("cause") in VALID_CAUSES:
            return {
                "cause": data["cause"],
                "summary": data.get("summary", _fallback_summary(emotion, data["cause"])),
            }
    except Exception:
        pass

    match = re.search(r'\{[^}]*"cause"[^}]*\}', llm_output, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            cause = data.get("cause", "unclear")
            if cause not in VALID_CAUSES:
                cause = "unclear"
            return {
                "cause": cause,
                "summary": data.get("summary", _fallback_summary(emotion, cause)),
            }
        except Exception:
            pass

    cause = _keyword_cause(original_input)
    return {"cause": cause, "summary": _fallback_summary(emotion, cause)}

def run_context_agent(state: dict) -> dict:
    user_input = state.get("user_input", "")
    emotion = state.get("emotion", "stressed")
    severity = state.get("severity", "medium")

    message = (
        f"User message: {user_input}\n"
        f"Detected emotion: {emotion} | Severity: {severity}"
    )

    journal_history = state.get("journal_history", [])
    if journal_history:
        history_context = "\n\nHistorical journal entries for context:\n"
        for entry in journal_history[-3:]:
            history_context += f"- [{entry.get('timestamp')}] Emotion: {entry.get('emotion')}, Severity: {entry.get('severity')}, Cause: {entry.get('cause')}. Reflection: {entry.get('content')}\n"
        history_context += "\nNote: If there is a repeating emotional or stress pattern, summarize it naturally in the single-sentence summary."
        message += history_context

    try:
        raw = chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=message,
            max_new_tokens=120,
            temperature=0.2,
        )
        result = _parse_response(raw, user_input, emotion)
    except Exception:
        cause = _keyword_cause(user_input)
        result = {"cause": cause, "summary": _fallback_summary(emotion, cause)}

    return {"cause": result["cause"], "cause_summary": result["summary"]}

import json
import re
from llm.tinyllama import chat

VALID_EMOTIONS = ["stressed", "tired", "anxious", "overwhelmed", "neutral", "happy"]
VALID_SEVERITIES = ["low", "medium", "high"]

SYSTEM_PROMPT = """You are an emotion classifier for a workplace wellness assistant.

Read the user's message and respond with ONLY a JSON object — no explanation, no extra text.

Required format:
{"emotion": "<emotion>", "severity": "<severity>"}

emotion must be one of: stressed, tired, anxious, overwhelmed, neutral, happy
severity must be one of: low, medium, high

Examples:
User: "I have too much work and can't cope"
Response: {"emotion": "overwhelmed", "severity": "high"}

User: "Feeling a bit drained after meetings"
Response: {"emotion": "tired", "severity": "medium"}

Respond with ONLY the JSON object."""

def _keyword_fallback(text: str) -> dict:
    t = text.lower()
    emotion = "stressed"
    if any(w in t for w in ["overwhelm", "can't cope", "too much"]):
        emotion = "overwhelmed"
    elif any(w in t for w in ["exhaust", "tired", "drained", "fatigue"]):
        emotion = "tired"
    elif any(w in t for w in ["anxious", "anxiety", "nervous", "worry", "worried"]):
        emotion = "anxious"
    elif any(w in t for w in ["stress", "pressure", "burnout", "burned out"]):
        emotion = "stressed"
    elif any(w in t for w in ["happy", "great", "good", "fine", "well"]):
        emotion = "happy"
    elif any(w in t for w in ["ok", "okay", "neutral", "alright"]):
        emotion = "neutral"

    severity = "medium"
    if any(w in t for w in ["very", "extremely", "really", "so much", "burnout",
                             "burned out", "can't", "cannot", "breaking"]):
        severity = "high"
    elif any(w in t for w in ["little", "bit", "slightly", "somewhat", "kind of"]):
        severity = "low"

    if "high stress" in t:
        severity = "high"
    elif "low stress" in t:
        severity = "low"
    elif "medium stress" in t:
        severity = "medium"

    return {"emotion": emotion, "severity": severity}

def _parse_response(llm_output: str, original_input: str) -> dict:
    try:
        data = json.loads(llm_output.strip())
        if (data.get("emotion") in VALID_EMOTIONS
                and data.get("severity") in VALID_SEVERITIES):
            return {"emotion": data["emotion"], "severity": data["severity"]}
    except Exception:
        pass

    match = re.search(r'\{[^}]*"emotion"[^}]*\}', llm_output, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            emotion = data.get("emotion", "")
            severity = data.get("severity", "medium")
            if emotion in VALID_EMOTIONS:
                if severity not in VALID_SEVERITIES:
                    severity = "medium"
                return {"emotion": emotion, "severity": severity}
        except Exception:
            pass

    return _keyword_fallback(original_input)

def run_emotion_agent(state: dict) -> dict:
    user_input = state.get("user_input", "")
    stress_level = state.get("stress_level", "")
    message = f"User message: {user_input}"
    if stress_level:
        message += f"\nUser self-reported stress level from form: {stress_level}"

    journal_history = state.get("journal_history", [])
    if journal_history:
        history_context = "\n\nHistorical journal entries for context:\n"
        for entry in journal_history[-3:]:
            history_context += f"- [{entry.get('timestamp')}] Emotion: {entry.get('emotion')}, Severity: {entry.get('severity')}, Cause: {entry.get('cause')}. Reflection: {entry.get('content')}\n"
        message += history_context

    try:
        raw = chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=message,
            max_new_tokens=80,
            temperature=0.2,
        )
        result = _parse_response(raw, user_input)
    except Exception:
        result = _keyword_fallback(user_input)

    return {"emotion": result["emotion"], "severity": result["severity"]}

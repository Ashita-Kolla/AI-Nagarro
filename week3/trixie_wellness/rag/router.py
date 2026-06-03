import json
import re
from llm.tinyllama import chat

SYSTEM_PROMPT = """You are an intent classification router for a wellness assistant.

Determine which knowledge domain best matches the user's input.
Available domains:
1. mental_health: Deals with anxiety, burnout, sleep issues, general mental well-being, depression.
2. workplace_productivity: Deals with task prioritization, meeting fatigue, deep work, workload stress, deadlines.
3. crisis_support: Deals with severe distress, panic attacks, suicidal thoughts, immediate danger, severe emotional breakdown.

Respond with ONLY a JSON object:
{"domain": "<domain>"}

If unsure, return "mental_health".
"""

def classify_intent(user_input: str) -> str:
    message = f"User input: {user_input}"
    try:
        raw = chat(system_prompt=SYSTEM_PROMPT, user_message=message, max_new_tokens=50, temperature=0.1)
        
        # Try direct JSON parsing
        try:
            data = json.loads(raw.strip())
            domain = data.get("domain", "mental_health")
            if domain in ["mental_health", "workplace_productivity", "crisis_support"]:
                return domain
        except Exception:
            pass

        # Try regex extraction
        match = re.search(r'\{[^}]*"domain"[^}]*\}', raw)
        if match:
            try:
                data = json.loads(match.group())
                domain = data.get("domain", "mental_health")
                if domain in ["mental_health", "workplace_productivity", "crisis_support"]:
                    return domain
            except Exception:
                pass
            
        # Fallback heuristic keyword matching
        t = user_input.lower()
        if any(w in t for w in ["panic", "suicide", "danger", "die", "emergency", "can't breathe"]):
            return "crisis_support"
        if any(w in t for w in ["work", "meeting", "deadline", "boss", "task", "manager", "project", "focus"]):
            return "workplace_productivity"
        return "mental_health"
            
    except Exception as e:
        print(f"Error in intent classification: {e}")
        return "mental_health"

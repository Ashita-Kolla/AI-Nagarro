import json
import re
from llm.tinyllama import chat

SYSTEM_PROMPT = """You are a Responsible AI Safety Monitor for a wellness application.
Your job is to analyze the user's input and detect if it falls into any of these critical categories:
1. "self_harm": The user mentions suicide, ending their life, self-injury, or harming themselves.
2. "crisis": The user is in immediate danger or experiencing a severe mental breakdown (e.g., severe panic attack, domestic violence).
3. "harmful": The user asks for illegal advice, violence against others, or highly abusive language.
4. "medical_diagnosis": The user explicitly asks for a medical diagnosis, medication prescriptions, or professional medical advice.

If you detect ANY of these, you MUST flag it and provide a corresponding JSON response.
If the input is just regular venting, complaining about work, or normal stress, it is NOT flagged.

Required format:
{
  "is_flagged": true/false,
  "risk_level": "low/medium/high/critical",
  "flag_reason": "self_harm/crisis/harmful/medical_diagnosis/none",
  "safety_response": "A safe, supportive, and standardized response."
}

Examples:
User: "I can't take this anymore, I want to end it all."
Response: {"is_flagged": true, "risk_level": "critical", "flag_reason": "self_harm", "safety_response": "I'm so sorry you're feeling this way. Please know you are not alone. Please reach out to the National Suicide Prevention Lifeline at 988 or go to your nearest emergency room immediately."}

User: "What pills should I take for this severe chest pain?"
Response: {"is_flagged": true, "risk_level": "high", "flag_reason": "medical_diagnosis", "safety_response": "I am an AI and cannot provide medical advice. Severe chest pain can be a medical emergency. Please contact emergency services (like 911) or visit a doctor immediately."}

User: "I'm just so tired and stressed from all these meetings today."
Response: {"is_flagged": false, "risk_level": "low", "flag_reason": "none", "safety_response": ""}

Respond with ONLY the JSON object.
"""

def _keyword_fallback(text: str) -> dict:
    t = text.lower()
    
    # 1. Self-harm / Crisis
    if any(w in t for w in ["suicide", "kill myself", "end it all", "end my life", "want to die", "hurt myself"]):
        return {
            "is_flagged": True,
            "risk_level": "critical",
            "flag_reason": "self_harm",
            "safety_response": "I'm so sorry you're feeling this way. Please know you are not alone. Please reach out to the National Suicide Prevention Lifeline at 988 or go to your nearest emergency room immediately."
        }
        
    # 2. Medical Diagnosis
    if any(w in t for w in ["prescribe", "diagnosis", "medication for", "what disease", "symptoms of", "medical advice"]):
        return {
            "is_flagged": True,
            "risk_level": "high",
            "flag_reason": "medical_diagnosis",
            "safety_response": "I am an AI and cannot provide medical advice or diagnoses. Please consult a qualified healthcare professional or doctor for your symptoms."
        }
        
    # 3. Harmful
    if any(w in t for w in ["kill him", "hurt them", "bomb", "illegal", "murder"]):
        return {
            "is_flagged": True,
            "risk_level": "high",
            "flag_reason": "harmful",
            "safety_response": "I cannot fulfill this request as it violates safety policies against harmful or illegal acts."
        }
        
    return {
        "is_flagged": False,
        "risk_level": "low",
        "flag_reason": "none",
        "safety_response": ""
    }

def _parse_response(llm_output: str, original_input: str) -> dict:
    try:
        data = json.loads(llm_output.strip())
        if "is_flagged" in data and "risk_level" in data:
            return {
                "is_flagged": bool(data["is_flagged"]),
                "risk_level": str(data.get("risk_level", "low")),
                "flag_reason": str(data.get("flag_reason", "none")),
                "safety_response": str(data.get("safety_response", ""))
            }
    except Exception:
        pass

    # Try extracting JSON via regex
    match = re.search(r'\{.*\}', llm_output, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if "is_flagged" in data:
                return {
                    "is_flagged": bool(data["is_flagged"]),
                    "risk_level": str(data.get("risk_level", "low")),
                    "flag_reason": str(data.get("flag_reason", "none")),
                    "safety_response": str(data.get("safety_response", ""))
                }
        except Exception:
            pass

    # If parsing fails, fall back to keyword detection
    return _keyword_fallback(original_input)

def run_safety_agent(state: dict) -> dict:
    user_input = state.get("user_input", "")
    message = f"User message: {user_input}"

    try:
        raw = chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=message,
            max_new_tokens=150,
            temperature=0.1,
        )
        result = _parse_response(raw, user_input)
    except Exception:
        result = _keyword_fallback(user_input)
        
    # Extra safety net: even if LLM says false, check keyword fallback for critical terms
    if not result["is_flagged"]:
        fallback_res = _keyword_fallback(user_input)
        if fallback_res["is_flagged"]:
            result = fallback_res

    return {
        "is_flagged": result["is_flagged"],
        "risk_level": result["risk_level"],
        "flag_reason": result["flag_reason"],
        "safety_response": result["safety_response"]
    }

import os
import json
import re
from groq import Groq

# ── Tiered model assignment ─────────────────────────────────────────────────
# Heavy agents that need reasoning get the 70b model.
# Light agents (routing, infra, governance) use the fast 8b model.
# NOTE: llama-3.3-70b-versatile TPD quota exhausted — all on 8b-instant until reset.
MODEL_MAP = {
    "BA":          "llama-3.1-8b-instant",
    "Architect":   "llama-3.1-8b-instant",
    "Developer":   "llama-3.1-8b-instant",
    "Environment": "llama-3.1-8b-instant",
    "QA":          "llama-3.1-8b-instant",
    "DevOps":      "llama-3.1-8b-instant",
    "PM":          "llama-3.1-8b-instant",
    "Supervisor":  "llama-3.1-8b-instant",
}

# ── Per-agent output token caps ──────────────────────────────────────────────
# Tight caps stop models from rambling and burning the daily budget.
MAX_TOKENS_MAP = {
    "BA":          2500,  # BA JSON is verbose — needs room for all requirements
    "Architect":   1800,  # architecture JSON
    "Developer":   8000,  # code generation — bumped to 8000 for full-stack apps
    "Environment":  500,  # just a list of shell commands
    "QA":          3000,  # test files need plenty of room for real code
    "DevOps":      1000,  # docker / ci JSON
    "PM":          1200,  # governance report
    "Supervisor":   700,  # routing JSON only
}

def call_llm(prompt, agent_name=None, model="llama-3.1-8b-instant", max_tokens=1200, temperature=0.3):
    """
    Unified LLM caller using Groq API.
    Wraps the call in a try/except block.
    Dynamically switches models AND token caps based on agent_name if provided.
    """
    if agent_name and agent_name in MODEL_MAP:
        model = MODEL_MAP[agent_name]
    # Agent cap ALWAYS wins — replaces caller default entirely.
    # Using min() was a bug: it let the low function default (1200) suppress
    # higher per-agent caps like BA=2500, Developer=4000.
    if agent_name and agent_name in MAX_TOKENS_MAP:
        max_tokens = MAX_TOKENS_MAP[agent_name]

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    try:
        print(f"[LLM] Calling model '{model}' for agent '{agent_name or 'Unknown'}' (max_tokens={max_tokens})")
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"\n[Error calling Groq API]: {e}\n")
        return None

def parse_json_from_llm(text):
    """
    Safely extract JSON from the LLM output. 
    Handles conversational text before/after JSON and markdown code blocks.
    """
    if not text:
        return None
    
    text = text.strip()
    
    # 1. Try direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # 2. Try extracting from markdown code block: ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 3. Try finding the first '{' and last '}'
    start_brace = text.find('{')
    end_brace = text.rfind('}')
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        candidate = text[start_brace:end_brace + 1].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 4. Try finding the first '[' and last ']' (in case of array)
    start_bracket = text.find('[')
    end_bracket = text.rfind(']')
    if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
        candidate = text[start_bracket:end_bracket + 1].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 5. Failed all extraction
    print("[Error] Failed to parse JSON from LLM output. Raw output was:")
    print(text)
    return None


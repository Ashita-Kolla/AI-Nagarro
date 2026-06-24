import os
import json
import re
from groq import Groq

# ── Model assignment ──────────────────────────────────────────────────────────
MODEL_MAP = {
    "BA":          "meta-llama/llama-4-scout-17b-16e-instruct",
    "Architect":   "meta-llama/llama-4-scout-17b-16e-instruct",
    "Planner":     "meta-llama/llama-4-scout-17b-16e-instruct",
    "Developer":   "meta-llama/llama-4-scout-17b-16e-instruct",
    "Environment": "meta-llama/llama-4-scout-17b-16e-instruct",
    "QA":          "meta-llama/llama-4-scout-17b-16e-instruct",
    "DevOps":      "meta-llama/llama-4-scout-17b-16e-instruct",
    "PM":          "meta-llama/llama-4-scout-17b-16e-instruct",
    "Supervisor":  "meta-llama/llama-4-scout-17b-16e-instruct",
}

# ── Per-agent output token caps ───────────────────────────────────────────────
MAX_TOKENS_MAP = {
    "BA":          2500,
    "Architect":   1800,
    "Planner":     3000,
    "Developer":   8000,  # Max limit for Groq model is 8192. Increased from 5000 to accommodate full-stack.
    "Environment":  500,
    "QA":          8000,
    "DevOps":      1000,
    "PM":          1200,
    "Supervisor":   700,
}

# ── Agents that bypass Groq's strict JSON mode ────────────────────────────────
# Developer and QA generate code inside JSON strings. Groq's strict JSON validator
# rejects responses with raw newlines in code strings (400 json_validate_failed).
# These agents return plain text; we parse JSON ourselves via parse_json_from_llm.
NO_JSON_MODE_AGENTS = {"Developer", "QA"}

# ── Available model cache ─────────────────────────────────────────────────────
_AVAILABLE_MODELS: list = []

def _load_available_models():
    """Fetch real model IDs once at startup for fallback resolution."""
    global _AVAILABLE_MODELS
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        _AVAILABLE_MODELS = [m.id for m in client.models.list().data]
        print(f"[LLM] {len(_AVAILABLE_MODELS)} models available: {', '.join(sorted(_AVAILABLE_MODELS))}")
    except Exception as e:
        print(f"[LLM] WARNING: Could not fetch model list: {e}")
        _AVAILABLE_MODELS = []

def _resolve_model(preferred: str) -> str:
    """
    Return preferred model if available, otherwise auto-pick from available list.
    Priority: llama-4 > llama-3.3-70b > llama-3.1-8b-instant > any llama > anything
    """
    if not _AVAILABLE_MODELS:
        return preferred  # No list — trust the caller
    if preferred in _AVAILABLE_MODELS:
        return preferred

    print(f"[LLM] '{preferred}' not available — auto-selecting from {len(_AVAILABLE_MODELS)} models...")
    priority = [
        lambda m: "llama-4" in m,
        lambda m: "llama-3.3-70b" in m,
        lambda m: "llama-3.1-8b-instant" in m,
        lambda m: "llama-3.1-8b" in m,
        lambda m: "llama" in m,
        lambda m: True,
    ]
    for check in priority:
        matches = [m for m in _AVAILABLE_MODELS if check(m)]
        if matches:
            chosen = sorted(matches)[0]
            print(f"[LLM] Auto-selected: '{chosen}'")
            return chosen

    return preferred  # Last resort: use as-is

# Run at import — fail fast if credentials are wrong
_load_available_models()


def call_llm(prompt, agent_name=None, model="meta-llama/llama-4-scout-17b-16e-instruct",
             max_tokens=1200, temperature=0.3):
    """
    Unified LLM caller using Groq API.
    - Resolves model with auto-fallback if preferred model not available.
    - Applies per-agent token caps.
    - Disables strict JSON mode for Developer agent (code in JSON strings).
    - Separates API errors from JSON parse errors.
    Returns raw string or None on API failure.
    """
    if agent_name and agent_name in MODEL_MAP:
        model = MODEL_MAP[agent_name]
    if agent_name and agent_name in MAX_TOKENS_MAP:
        max_tokens = MAX_TOKENS_MAP[agent_name]

    model = _resolve_model(model)
    use_json_mode = agent_name not in NO_JSON_MODE_AGENTS

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    try:
        print(f"[LLM] Agent='{agent_name}' model='{model}' max_tokens={max_tokens} json_mode={use_json_mode}")
        
        # Dynamically ensure 'json' is in prompt if json_mode is requested
        if use_json_mode and "json" not in prompt.lower():
            prompt += "\n\nPlease ensure your response is in JSON format."

        create_kwargs = dict(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if use_json_mode:
            create_kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**create_kwargs)
        return response.choices[0].message.content

    except Exception as api_error:
        error_str = str(api_error)
        
        # Dynamic fallback for strict JSON validation failures
        if use_json_mode and "json_validate_failed" in error_str and "failed_generation" in error_str:
            print(f"\n[LLM Warning] Strict JSON mode failed for Agent='{agent_name}'. Extracting failed_generation...\n")
            try:
                import ast
                start_idx = error_str.find("{")
                if start_idx != -1:
                    err_dict = ast.literal_eval(error_str[start_idx:])
                    failed_gen = err_dict.get("error", {}).get("failed_generation")
                    if failed_gen:
                        return failed_gen
            except Exception as e:
                print(f"[LLM Warning] Failed to extract failed_generation: {e}")
            
            # If extraction fails, retry dynamically without JSON mode
            print(f"[LLM] Retrying without strict JSON mode...")
            create_kwargs.pop("response_format", None)
            try:
                fallback_response = client.chat.completions.create(**create_kwargs)
                return fallback_response.choices[0].message.content
            except Exception as fallback_error:
                print(f"\n[LLM API Error] Fallback also failed: {fallback_error}\n")
                return None

        # API-level failure (wrong model, quota, network) — NOT a JSON parse error
        print(f"\n[LLM API Error] Agent='{agent_name}' model='{model}': {api_error}\n")
        return None


def _repair_json_string(text: str) -> str:
    """
    Attempt to fix the most common LLM JSON malformation:
    raw literal newlines embedded inside JSON string values.
    e.g. "foo:\n    bar" becomes "foo:\\n    bar"
    This is a best-effort heuristic, not a full JSON repair.
    """
    result = []
    in_string = False
    escape_next = False
    for ch in text:
        if escape_next:
            result.append(ch)
            escape_next = False
            continue
        if ch == '\\':
            result.append(ch)
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
            result.append(ch)
            continue
        # Fix: raw newline/tab inside a JSON string → escape it
        if in_string and ch == '\n':
            result.append('\\n')
            continue
        if in_string and ch == '\r':
            result.append('\\r')
            continue
        if in_string and ch == '\t':
            result.append('\\t')
            continue
        result.append(ch)
    return ''.join(result)


def parse_json_from_llm(text):
    """
    Safely extract JSON from raw LLM output.
    Handles: direct JSON, markdown code blocks, leading/trailing prose,
    and raw newlines embedded in JSON strings (common LLM mistake).
    Returns parsed object, or None if all strategies fail.

    NOTE: None here = JSON PARSE failure (separate from API failure).
    """
    if not text:
        return None

    text = text.strip()

    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Markdown code block: ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Try repairing raw newlines before giving up on this block
            try:
                return json.loads(_repair_json_string(candidate))
            except json.JSONDecodeError:
                pass

    # 3. First '{' to last '}'
    start_brace = text.find('{')
    end_brace = text.rfind('}')
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        candidate = text[start_brace:end_brace + 1].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Try repairing
            try:
                return json.loads(_repair_json_string(candidate))
            except json.JSONDecodeError:
                pass

    # 4. First '[' to last ']'
    start_bracket = text.find('[')
    end_bracket = text.rfind(']')
    if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
        candidate = text[start_bracket:end_bracket + 1].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            try:
                return json.loads(_repair_json_string(candidate))
            except json.JSONDecodeError:
                pass

    # 5. Partial-JSON recovery: the output was truncated mid-generation.
    # Take everything from the first '{' and try to auto-close open structures.
    start_brace = text.find('{')
    if start_brace != -1:
        partial = text[start_brace:]
        # Repair raw newlines first
        partial = _repair_json_string(partial)
        # Count unclosed braces and brackets
        depth_brace = 0
        depth_bracket = 0
        in_str = False
        esc = False
        for ch in partial:
            if esc:
                esc = False
                continue
            if ch == '\\':
                esc = True
                continue
            if ch == '"' and not esc:
                in_str = not in_str
                continue
            if not in_str:
                if ch == '{':
                    depth_brace += 1
                elif ch == '}':
                    depth_brace -= 1
                elif ch == '[':
                    depth_bracket += 1
                elif ch == ']':
                    depth_bracket -= 1
        # Close any dangling string, then close open arrays and objects
        if in_str:
            partial += '"'
        partial += ']' * max(0, depth_bracket)
        partial += '}' * max(0, depth_brace)
        try:
            result = json.loads(partial)
            print("[LLM JSON Parse] Recovered partial JSON by closing unclosed structures.")
            return result
        except json.JSONDecodeError:
            pass

    # 6. All strategies failed
    print("[LLM JSON Parse Error] Could not extract valid JSON. Raw output snippet:")
    print(text[:800])
    return None

import os
import json
import re
import time
import requests
from enum import Enum
from groq import Groq

# ── Provider setup ────────────────────────────────────────────────────────────
class Provider(Enum):
    GROQ = "groq"
    OPENROUTER = "openrouter"
    HUGGINGFACE = "huggingface"

# ── Agent routing ─────────────────────────────────────────────────────────────
AGENT_ROUTING = {
    "Supervisor": {
        "provider": Provider.GROQ,
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "reason": "Small output (~700 tokens), scout is fine and saves 70b quota"
    },
    "BA": {
        "provider": Provider.GROQ,
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "reason": "Good at structured output, fast"
    },
    "Architect": {
        "provider": Provider.GROQ,
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "reason": "Avoid OpenRouter credit limit"
    },
    "Planner": {
        "provider": Provider.GROQ,
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "reason": "Structured JSON planning, scout is sufficient"
    },
    "Developer": {
        "provider": Provider.GROQ,
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "reason": "Faster than qwen3-32b on OpenRouter; JSON mode is OFF (NO_JSON_MODE_AGENTS) so Groq validator won't reject code strings"
    },
    "QA": {
        "provider": Provider.GROQ,
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "reason": "Avoid 70b daily limit"
    },
    "DevOps": {
        "provider": Provider.GROQ,
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "reason": "Avoid 70b daily limit"
    },
    "PM": {
        "provider": Provider.GROQ,
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "reason": "Structured JSON, no code needed"
    },
    "Optimisation": {
        "provider": Provider.GROQ,
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "reason": "Analysis only, small output"
    },
}

# ── Per-agent output token caps ───────────────────────────────────────────────
MAX_TOKENS_MAP = {
    "Supervisor":   700,
    "BA":          3000,   # bumped: large BRDs can exceed 2500
    "Architect":   4000,   # bumped: 2000 too small for complex arch output
    "Planner":     5000,   # was 3000 — multi-epic plans (4+ epics × tasks) truncated at 3k
    "Developer":   8000,
    "Environment":  500,
    "QA":          5000,   # stays inside llama-3.3-70b-versatile 12k TPM window
    "DevOps":      1500,
    "PM":          1500,
    "Optimisation": 1000,
}

# ── Agents that bypass Groq's strict JSON mode ────────────────────────────────
# Developer generates code inside JSON strings; Groq's strict JSON validator
# rejects responses with raw newlines in code strings (400 json_validate_failed).
# Developer returns plain text; we parse JSON ourselves via parse_json_from_llm.
#
# QA is intentionally NOT in this set: llama-3.3-70b-versatile without JSON mode
# ignores the JSON instruction entirely and outputs ### filename ### markdown.
# With JSON mode ON, Groq may raise json_validate_failed — the existing handler
# extracts failed_generation and _repair_json_string fixes raw newlines before
# parse_json_from_llm sees it, so the recovery chain still works.
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


def call_llm(prompt, agent_name=None, max_tokens=None, temperature=0.3):
    """
    Unified LLM caller with Multi-Provider routing.
    Routes to Groq, OpenRouter, or HuggingFace based on agent requirements.
    """
    routing = AGENT_ROUTING.get(agent_name, {
        "provider": Provider.GROQ,
        "model": "llama-3.3-70b-versatile"
    })

    provider = routing["provider"]
    model = routing["model"]
    tokens = max_tokens or MAX_TOKENS_MAP.get(agent_name, 2000)

    print(f"[LLM] Routing '{agent_name}' to {provider.name} ({model}) for ~{tokens} tokens.")

    if provider == Provider.GROQ:
        return _call_groq(prompt, model, tokens, temperature, agent_name)
    elif provider == Provider.OPENROUTER:
        return _call_openrouter(prompt, model, tokens, temperature)
    elif provider == Provider.HUGGINGFACE:
        return _call_huggingface(prompt, model, tokens)

    return None

def _call_groq(prompt, model, max_tokens, temperature, agent_name):
    use_json_mode = agent_name not in NO_JSON_MODE_AGENTS
    model = _resolve_model(model)
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    try:
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
        
        if use_json_mode and "json_validate_failed" in error_str and "failed_generation" in error_str:
            print(f"\n[LLM Warning] Strict JSON mode failed for Agent='{agent_name}'. Extracting failed_generation...\n")
            try:
                import ast
                start_idx = error_str.find("{")
                if start_idx != -1:
                    err_dict = ast.literal_eval(error_str[start_idx:])
                    failed_gen = err_dict.get("error", {}).get("failed_generation")
                    if failed_gen:
                        # Try to salvage with our lenient parser
                        if parse_json_from_llm(failed_gen) is not None:
                            print(f"[LLM] Salvaged failed_generation via lenient parser.")
                            return failed_gen
            except Exception as e:
                pass
            
            print(f"[LLM] Retrying without strict JSON mode...")
            create_kwargs.pop("response_format", None)
            try:
                fallback_response = client.chat.completions.create(**create_kwargs)
                return fallback_response.choices[0].message.content
            except Exception:
                pass

        print(f"[Groq Error] {agent_name}: {error_str}")
        print(f"[Fallback] Routing {agent_name} to OpenRouter...")
        return _call_openrouter(prompt, "deepseek/deepseek-chat", max_tokens, temperature)

# Groq fallback models tried in order when OpenRouter is exhausted.
# Each has progressively higher TPM so a 413 on one cascades to the next.
# qwen3-32b: 6k TPM  |  llama-3.3-70b-versatile: 12k TPM  |  llama-3.1-8b-instant: 20k TPM
_GROQ_FALLBACK_MODELS = [
    "qwen/qwen3-32b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

# Minimum seconds to wait between successive chunked-generation calls
_CHUNK_MIN_INTERVAL = 1.0
_last_openrouter_call: float = 0.0


def _call_openrouter(prompt, model, max_tokens, temperature, max_retries: int = 3):
    global _last_openrouter_call

    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        print("[OpenRouter Error] OPENROUTER_API_KEY is not set.")
        return None

    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    # Disable reasoning for DeepSeek V4 Flash — saves tokens, faster response
    if "deepseek-v4-flash" in model:
        body["reasoning"] = {"enabled": False}

    for attempt in range(1, max_retries + 1):
        # ── Inter-chunk throttle ──────────────────────────────────────────────
        now = time.time()
        gap = _CHUNK_MIN_INTERVAL - (now - _last_openrouter_call)
        if gap > 0:
            time.sleep(gap)

        try:
            _last_openrouter_call = time.time()
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=body,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            print(f"[OpenRouter HTTP Error] attempt {attempt}/{max_retries}: {e}")

            if status == 429 and attempt < max_retries:
                # ── Read retry_after_seconds from error body ──────────────────
                wait = 10  # sensible default
                try:
                    err_body = e.response.json()
                    # OpenRouter may nest it at error.metadata.retry_after_seconds
                    meta = err_body.get("error", {}).get("metadata", {})
                    wait = float(
                        meta.get("retry_after_seconds")
                        or e.response.headers.get("Retry-After", wait)
                    )
                except Exception:
                    pass
                wait += 2  # +2 s buffer
                print(f"[OpenRouter 429] Rate-limited. Waiting {wait:.1f}s before retry {attempt + 1}...")
                time.sleep(wait)
                continue

            if e.response is not None:
                print(f"[OpenRouter Response]: {e.response.text}")
            # Non-429 or retries exhausted → fall through to Groq fallback
            break

        except Exception as e:
            print(f"[OpenRouter Error] attempt {attempt}/{max_retries}: {e}")
            if attempt < max_retries:
                time.sleep(2 + 2)  # brief back-off + buffer
                continue
            break

    # ── All retries failed — walk Groq fallback model list ──────────────────
    print(f"[OpenRouter] All {max_retries} attempts failed. Trying Groq fallback chain...")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    for fb_model in _GROQ_FALLBACK_MODELS:
        try:
            print(f"[Groq Fallback] Trying {fb_model}...")
            fallback_resp = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=fb_model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return fallback_resp.choices[0].message.content
        except Exception as groq_err:
            err_str = str(groq_err)
            if "413" in err_str or "rate_limit_exceeded" in err_str or "tokens" in err_str:
                # Prompt too large for this model's TPM — try the next one
                print(f"[Groq Fallback] {fb_model} TPM too small, trying next fallback...")
                continue
            print(f"[Groq Fallback Error] {fb_model}: {groq_err}")
            break  # Non-TPM error — no point retrying with same prompt
    print("[Groq Fallback] All fallback models exhausted.")
    return None

def _call_huggingface(prompt, model, max_tokens):
    try:
        api_key = os.environ.get('HUGGINGFACE_API_KEY')
        if not api_key:
            print("[HuggingFace Error] HUGGINGFACE_API_KEY is not set.")
            return None

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers={
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "inputs": prompt,
                "parameters": {"max_new_tokens": max_tokens}
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list):
            return result[0].get("generated_text", "")
        return str(result)
    except Exception as e:
        print(f"[HuggingFace Error]: {e}")
        return None
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

    # 0. Strip <think>…</think> reasoning blocks (Qwen3, DeepSeek-R1, etc.)
    #    These appear BEFORE the JSON and confuse every downstream strategy.
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    if not text:
        return None

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
        # If the text was cut off mid-escape (trailing backslash), remove it
        # so the closing '"' we add below actually closes the string.
        if partial.endswith('\\'):
            partial = partial[:-1]
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

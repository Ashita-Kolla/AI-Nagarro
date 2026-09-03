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
# All agents share one free OpenRouter model. Groq's free/dev tier caps at
# 8000 TPM (tokens/minute, input+output combined) per model — too small for
# agents like Architect/Developer that need multi-thousand-token responses,
# and it was already erroring with 413 rate_limit_exceeded. OpenRouter's free
# tier limits requests/day (~20/min, 200/day), not tokens/minute, so it
# comfortably covers a full multi-agent pipeline run.
FREE_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

AGENT_ROUTING = {
    "Supervisor": {
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL,
        "reason": "Small output; moved off Groq (8000 TPM cap was too tight, llama-4-scout also no longer available)"
    },
    "BA": {
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL,
        "reason": "Structured output; moved off Groq (8000 TPM cap was too tight, llama-4-scout also no longer available)"
    },
    "Architect": {
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL,
        "reason": "Needs ~8000 output tokens per call; Groq's 8000 TPM cap made this fail outright (413), OpenRouter free tier has no such ceiling"
    },
    "Planner": {
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL,
        "reason": "Structured JSON planning; moved off Groq (8000 TPM cap was too tight, llama-4-scout also no longer available)"
    },
    "Developer": {
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL,
        "reason": "Heavy coding output (up to 8000 tokens); Groq's 8000 TPM cap made this fail outright, OpenRouter free tier has no such ceiling"
    },
    "QA": {
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL,
        "reason": "Needs high reasoning for testing logic; llama-3.3-70b-versatile was retired by Groq (free/dev tier) on 2026-08-16"
    },
    "DevOps": {
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL,
        "reason": "Small output configuration; llama-3.1-8b-instant was retired by Groq (free/dev tier) on 2026-08-16"
    },
    "PM": {
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL,
        "reason": "Basic structured JSON analysis; llama-3.1-8b-instant was retired by Groq (free/dev tier) on 2026-08-16"
    },
    "Optimisation": {
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL,
        "reason": "Basic analysis; llama-3.1-8b-instant was retired by Groq (free/dev tier) on 2026-08-16"
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
    "QA":          5000,   # FREE_MODEL (OpenRouter) — comfortably within its context window
    "DevOps":      1500,
    "PM":          1500,
    "Optimisation": 1000,
}

# ── Agents that bypass Groq's strict JSON mode ────────────────────────────────
# Developer generates code inside JSON strings; Groq's strict JSON validator
# rejects responses with raw newlines in code strings (400 json_validate_failed).
# Developer returns plain text; we parse JSON ourselves via parse_json_from_llm.
#
# This set only affects agents routed to Groq (see _call_groq). QA now routes
# to OpenRouter (z-ai/glm-5.2:free), which has no strict JSON mode to fight —
# parse_json_from_llm handles extraction/repair for it regardless.
NO_JSON_MODE_AGENTS = {"Developer"}

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
    Priority: llama-4 > gpt-oss-120b > gpt-oss-20b > any llama > anything
    """
    if not _AVAILABLE_MODELS:
        return preferred  # No list — trust the caller
    if preferred in _AVAILABLE_MODELS:
        return preferred

    print(f"[LLM] '{preferred}' not available — auto-selecting from {len(_AVAILABLE_MODELS)} models...")
    priority = [
        lambda m: "llama-4" in m,
        lambda m: "gpt-oss-120b" in m,
        lambda m: "gpt-oss-20b" in m,
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
        "provider": Provider.OPENROUTER,
        "model": FREE_MODEL
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
        print(f"[Fallback] Routing {agent_name} to OpenRouter (free model)...")
        return _call_openrouter(prompt, FREE_MODEL, max_tokens, temperature)

# Other free OpenRouter models tried in rotation when the primary FREE_MODEL
# is rate-limited or its upstream backend is congested (shared free-tier pool
# 429s are per-model, not per-account, so a different free model often works).
_FREE_MODEL_FALLBACKS = [
    "z-ai/glm-5.2:free",
    "minimax/minimax-m3:free",
    "google/gemma-4-31b-it:free",
]

# Groq models tried only as an absolute last resort, after every free
# OpenRouter option is exhausted. Groq's free/dev tier caps at 8000 TPM
# (tokens/minute, input+output combined) per model, so requests are capped
# well below that here to avoid the same 413 rate_limit_exceeded loop.
_GROQ_LAST_RESORT_MODEL = "openai/gpt-oss-20b"
_GROQ_LAST_RESORT_MAX_TOKENS = 3000

# Minimum seconds to wait between successive chunked-generation calls
_CHUNK_MIN_INTERVAL = 1.0
_last_openrouter_call: float = 0.0


# Auto-escalation ceiling and multiplier for truncated (finish_reason=="length")
# responses — see the escalation block below _call_openrouter's retry loop.
_MAX_TOKENS_CEILING = 16000
_ESCALATION_FACTOR = 1.75


def _call_openrouter(prompt, model, max_tokens, temperature, max_retries: int = 3, _tried_models=None, _escalated=False):
    global _last_openrouter_call

    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        print("[OpenRouter Error] OPENROUTER_API_KEY is not set.")
        return None

    # Track which free models we've already tried this call chain, so the
    # fallback rotation below never retries the same congested model twice.
    tried_models = _tried_models or set()
    tried_models.add(model)

    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        # Every agent here wants a direct structured answer within a tight
        # token budget. Reasoning-capable free models (nemotron, glm, minimax)
        # otherwise spend the whole max_tokens budget on visible chain-of-
        # thought prose and never reach the actual JSON — this suppresses that
        # on every model that honors OpenRouter's unified reasoning toggle.
        "reasoning": {"enabled": False},
    }

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
            data = response.json()
            choices = data.get("choices")
            if not choices:
                # OpenRouter can return HTTP 200 with no choices (e.g. an
                # embedded provider error, empty upstream response). Surface
                # it as a normal exception so the retry/rotation logic below
                # handles it instead of crashing on a bare KeyError.
                raise RuntimeError(f"OpenRouter response had no choices: {str(data)[:300]}")

            choice = choices[0]
            content = choice["message"]["content"]

            # The response was cut off mid-generation before finishing the
            # JSON. Rather than pre-allocating a big max_tokens ceiling on
            # every call "just in case", only pay for more tokens on the rare
            # call that actually needs them, and only once per call chain.
            #
            # finish_reason=="length" is the documented signal, but some free/
            # preview models misreport or omit it, and their usage stats can
            # be unreliable too (0 or missing completion_tokens even on a
            # genuinely truncated response). So also fall back to a signal
            # the API can't misreport: well-formed JSON always ends in '}' or
            # ']' — content of meaningful length that doesn't is incomplete
            # no matter what finish_reason/usage claim.
            completion_tokens = data.get("usage", {}).get("completion_tokens", 0)
            trimmed = content.rstrip().rstrip("`").rstrip()
            looks_incomplete = len(trimmed) > 50 and trimmed[-1] not in "}]"
            hit_ceiling = (
                choice.get("finish_reason") == "length"
                or completion_tokens >= max_tokens - 5
                or looks_incomplete
            )
            if hit_ceiling and not _escalated and max_tokens < _MAX_TOKENS_CEILING:
                escalated_tokens = min(int(max_tokens * _ESCALATION_FACTOR), _MAX_TOKENS_CEILING)
                print(f"[OpenRouter] Response likely truncated at {max_tokens} tokens (finish_reason={choice.get('finish_reason')!r}, completion_tokens={completion_tokens}, looks_incomplete={looks_incomplete}). Retrying with {escalated_tokens}...")
                return _call_openrouter(prompt, model, escalated_tokens, temperature, max_retries, tried_models, _escalated=True)

            return content

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

    # ── This model exhausted — try another free OpenRouter model ────────────
    next_free_model = next((m for m in _FREE_MODEL_FALLBACKS if m not in tried_models), None)
    if next_free_model:
        print(f"[OpenRouter] '{model}' exhausted. Rotating to free model '{next_free_model}'...")
        # Single attempt per rotation model — the goal is to quickly find one
        # that isn't congested, not to hammer each candidate 3x in a row.
        return _call_openrouter(prompt, next_free_model, max_tokens, temperature, 1, tried_models)

    # ── Every free model failed — absolute last resort: Groq, token-capped ──
    print(f"[OpenRouter] All free models exhausted. Trying Groq last resort ({_GROQ_LAST_RESORT_MODEL})...")
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        fallback_resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=_GROQ_LAST_RESORT_MODEL,
            temperature=temperature,
            max_tokens=min(max_tokens, _GROQ_LAST_RESORT_MAX_TOKENS),
        )
        return fallback_resp.choices[0].message.content
    except Exception as groq_err:
        print(f"[Groq Last Resort Error]: {groq_err}")

    print("[OpenRouter] All fallback options exhausted.")
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
        # Track open braces/brackets on a stack so they close in the correct
        # (reverse-of-opening) order. Closing all ']' before all '}' — as a
        # flat count-based approach does — produces invalid JSON whenever an
        # object is nested inside an array that itself isn't the outermost
        # structure, e.g. {"epics":[{"title":"cut off mid-string.
        open_stack = []
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
                if ch in '{[':
                    open_stack.append('}' if ch == '{' else ']')
                elif ch in '}]' and open_stack:
                    open_stack.pop()
        # Close any dangling string first, then drop a dangling trailing
        # comma/colon (truncation often cuts right after one, before the
        # next key/element/value), then close open arrays and objects
        # innermost-first.
        if in_str:
            partial += '"'
        stripped = partial.rstrip()
        if stripped and stripped[-1] in ',:':
            partial = stripped[:-1]
        partial += ''.join(reversed(open_stack))
        try:
            result = json.loads(partial)
            print("[LLM JSON Parse] Recovered partial JSON by closing unclosed structures.")
            return result
        except json.JSONDecodeError:
            pass

    # 6. All strategies failed
    print(f"[LLM JSON Parse Error] Could not extract valid JSON. Raw output length: {len(text)} chars.")
    if len(text) <= 1600:
        print(text)
    else:
        # Show both ends — the start alone can't distinguish "truncated
        # mid-output" from "malformed somewhere in the middle/end", and the
        # end is exactly where a truncation cutoff would show up.
        print("--- head ---")
        print(text[:800])
        print("--- tail ---")
        print(text[-800:])
    return None

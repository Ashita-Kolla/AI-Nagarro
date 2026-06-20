"""
context_compressor.py
Deterministic context compressor for the ARIA pipeline.

Strategy:
- Truncate long string values to a configurable max length.
- Summarise lists to their first N items, with a count note if truncated.
- Drop null / empty values entirely.
- Strip raw source code blobs from Developer output (stored separately on disk).
- Preserve all keys and structural metadata so downstream agents can reason
  about what *type* of data exists even when the value is summarised.

This module is intentionally zero-LLM: no API calls, no cost, instant.
"""

import json
from typing import Any

# ── Defaults ──────────────────────────────────────────────────────────────────
MAX_STRING_CHARS   = 200   # cap on any single string value (was 400)
MAX_LIST_ITEMS     = 4     # cap on how many items to keep per list (was 5)
CODE_KEYS          = {"content", "code", "dockerfile", "docker_compose",
                      "github_actions", "env_example"}  # keys treated as code blobs

# ── Per-agent extraction rules ─────────────────────────────────────────────────
# Maps agent_name -> list of top-level keys to KEEP in the summary.
# Keys not in this list are dropped (but their presence is noted).
AGENT_KEEP_KEYS = {
    "Supervisor": ["project_name", "summary", "agents_required"],
    "BA": [
        "business_requirements", "user_stories", "functional_requirements",
        "assumptions", "confidence_score"
        # non_functional_requirements, out_of_scope dropped — less critical downstream
    ],
    "Architect": [
        "tech_stack", "architecture_pattern", "modules",
        "database", "api_design", "deployment_target", "confidence_score"
    ],
    "Developer": [
        "project_name", "language_stack", "file_tree", "entrypoint",
        "dependencies", "implementation_notes", "coverage_mapping", "confidence_score"
        # "files" intentionally excluded — raw code is on disk
    ],
    "Environment": [
        "setup_script_name", "setup_commands", "execution_status"
    ],
    "QA": [
        "status", "execution_results", "bug_report",
        "requirement_coverage", "confidence_score"
    ],
    "DevOps": [
        "deployment_strategy", "deployment_contract",
        "assumptions", "confidence_score"
    ],
    "PM": [
        "project_status", "project_summary", "risk_analysis",
        "alignment_check", "confidence_score"
    ],
}

# ── Core helpers ───────────────────────────────────────────────────────────────

def _truncate_string(value: str, max_chars: int = MAX_STRING_CHARS) -> str:
    """Truncate a string and append a note if it was cut."""
    if len(value) <= max_chars:
        return value
    return value[:max_chars] + f"... [truncated, full length {len(value)} chars]"


def _compress_value(value: Any, depth: int = 0) -> Any:
    """Recursively compress a JSON-compatible value."""
    if value is None or value == "" or value == [] or value == {}:
        return None  # caller drops None values

    if isinstance(value, str):
        return _truncate_string(value)

    if isinstance(value, (int, float, bool)):
        return value

    if isinstance(value, list):
        total = len(value)
        kept = [_compress_value(item, depth + 1) for item in value[:MAX_LIST_ITEMS]]
        kept = [v for v in kept if v is not None]
        if total > MAX_LIST_ITEMS:
            kept.append(f"... [{total - MAX_LIST_ITEMS} more items not shown]")
        return kept or None

    if isinstance(value, dict):
        compressed = {}
        for k, v in value.items():
            # Skip code blobs — they are saved to disk separately
            if k in CODE_KEYS:
                compressed[k] = f"[code saved to disk — {len(str(v))} chars]"
                continue
            result = _compress_value(v, depth + 1)
            if result is not None:
                compressed[k] = result
        return compressed or None

    # Fallback — stringify and truncate
    return _truncate_string(str(value))


def compress(agent_name: str, data: Any) -> dict:
    """
    Entry point. Returns a compressed summary dict for the given agent's output.

    Args:
        agent_name: The name of the agent (used to apply keep-key rules).
        data:       The raw parsed output from that agent.

    Returns:
        A compressed dict ready to be stored as f"{agent_name}_summary"
        in the project context.
    """
    if not isinstance(data, dict):
        # Scalar or list output: just truncate
        return {"_summary": _truncate_string(str(data))}

    keep_keys = AGENT_KEEP_KEYS.get(agent_name)

    # Filter to allowed keys (drop keys not in keep list)
    if keep_keys:
        filtered = {k: v for k, v in data.items() if k in keep_keys}
    else:
        filtered = dict(data)  # keep everything, but still compress values

    # Deep-compress the values
    compressed = {}
    for key, value in filtered.items():
        result = _compress_value(value)
        if result is not None:
            compressed[key] = result

    # Always record metadata
    compressed["_agent"] = agent_name
    compressed["_compressed"] = True
    return compressed


def estimate_tokens(text: str) -> int:
    """Rough token estimate (1 token ≈ 4 chars)."""
    return len(text) // 4


def summary_to_str(agent_name: str, summary: dict) -> str:
    """Format a compressed summary as a readable string for prompt injection."""
    body = json.dumps(summary, indent=2, ensure_ascii=False)
    return f"--- {agent_name} (summary) ---\n{body}\n"

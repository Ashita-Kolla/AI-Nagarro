"""
tool_registry.py
----------------
MCP-style tool registry for Trixie's wellness agent.

In a real MCP setup, this is the "tool manifest" that an MCP server
publishes so that a client (the LLM agent) can discover available tools,
read their descriptions, and decide which one(s) to call.

Here we keep it simple: a plain Python registry that the recommendation
agent queries to select tools at runtime.
"""

from tools.wellness_tools import (
    get_breathing_exercise,
    lookup_wellness_resources,
    get_stress_tip,
)

# ---------------------------------------------------------------------------
# Tool Manifest  (mirrors what an MCP server's tools/list response looks like)
# ---------------------------------------------------------------------------

TOOL_MANIFEST = [
    {
        "name": "get_breathing_exercise",
        "description": (
            "Returns a step-by-step guided breathing exercise tailored to the "
            "user's stress severity level (low / medium / high). Use this when "
            "the user needs an immediate, in-the-moment calming technique."
        ),
        "parameters": {
            "severity": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Stress severity level detected by the emotion agent.",
            }
        },
        "callable": get_breathing_exercise,
    },
    {
        "name": "lookup_wellness_resources",
        "description": (
            "Looks up a curated set of wellness resources (techniques, habits, "
            "strategies) matched to the root cause of stress. Use this when "
            "the user needs longer-term actionable strategies."
        ),
        "parameters": {
            "cause": {
                "type": "string",
                "enum": ["workload", "meetings", "personal", "unclear"],
                "description": "Root cause of stress identified by the context agent.",
            }
        },
        "callable": lookup_wellness_resources,
    },
    {
        "name": "get_stress_tip",
        "description": (
            "Returns a single, context-aware motivational tip based on the "
            "cause and emotion. Use this as a quick insight to close the "
            "wellness response with a positive, empowering nudge."
        ),
        "parameters": {
            "cause": {
                "type": "string",
                "enum": ["workload", "meetings", "personal", "unclear"],
                "description": "Root cause of stress.",
            },
            "emotion": {
                "type": "string",
                "description": "Detected emotion (e.g. 'anxious', 'overwhelmed').",
            },
        },
        "callable": get_stress_tip,
    },
]

# Index by name for quick lookup
_TOOL_INDEX = {t["name"]: t for t in TOOL_MANIFEST}


# ---------------------------------------------------------------------------
# Agent-facing helpers
# ---------------------------------------------------------------------------

def list_tools() -> list[dict]:
    """Return the full tool manifest (name + description + parameters)."""
    return [
        {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}
        for t in TOOL_MANIFEST
    ]


def call_tool(name: str, **kwargs) -> dict:
    """
    Execute a tool by name with the given keyword arguments.

    This is the equivalent of an MCP client sending a tools/call request.
    Raises ValueError if the tool is not found.
    """
    tool = _TOOL_INDEX.get(name)
    if tool is None:
        raise ValueError(f"Unknown tool: '{name}'. Available tools: {list(_TOOL_INDEX.keys())}")
    return tool["callable"](**kwargs)


def select_tools_for(cause: str, severity: str) -> list[str]:
    """
    Agent decision function: given cause and severity, decide which tools to call.

    This is the 'tool selection' step — the part an LLM agent does when it
    reasons 'which of the available tools should I use right now?'

    Returns a list of tool names to call, in order.
    """
    tools_to_call = []

    # Always grab a breathing exercise — immediate relief for any severity
    tools_to_call.append("get_breathing_exercise")

    # Look up resources if we have a clear cause
    if cause in ("workload", "meetings", "personal"):
        tools_to_call.append("lookup_wellness_resources")

    # Add a motivational tip for high severity or when cause is unclear
    if severity == "high" or cause == "unclear":
        tools_to_call.append("get_stress_tip")

    return tools_to_call

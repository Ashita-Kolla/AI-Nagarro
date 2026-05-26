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
from tools.google_docs_tool import (
    save_journal_entry,
    get_journal_history,
)
from tools.calendar_tool import (
    create_calendar_reminder,
    get_calendar_reminders,
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
    {
        "name": "save_journal_entry",
        "description": (
            "Saves a daily wellness journal entry to Google Docs for reflection and record keeping."
        ),
        "parameters": {
            "content": {
                "type": "string",
                "description": "The content of the journal reflection.",
            },
            "emotion": {
                "type": "string",
                "description": "The user's detected emotion.",
            },
            "severity": {
                "type": "string",
                "description": "The user's stress severity level.",
            },
            "cause": {
                "type": "string",
                "description": "The identified root cause of stress.",
            },
        },
        "callable": save_journal_entry,
    },
    {
        "name": "get_journal_history",
        "description": (
            "Retrieves previous wellness journal entries from Google Docs to analyze emotional patterns."
        ),
        "parameters": {},
        "callable": get_journal_history,
    },
    {
        "name": "create_calendar_reminder",
        "description": (
            "Creates a wellness-related reminder in the calendar/reminder database."
        ),
        "parameters": {
            "activity": {
                "type": "string",
                "enum": ["meditation", "hydration", "sleep", "journaling", "exercise"],
                "description": "The wellness activity to remind the user about.",
            },
            "time": {
                "type": "string",
                "description": "The time of day in HH:MM format.",
            },
            "frequency": {
                "type": "string",
                "description": "How often the reminder should repeat (e.g. 'daily', 'every evening').",
            }
        },
        "callable": create_calendar_reminder,
    },
    {
        "name": "get_calendar_reminders",
        "description": (
            "Retrieves all scheduled calendar reminders from the persistent database."
        ),
        "parameters": {},
        "callable": get_calendar_reminders,
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


def select_tools_for(cause: str, severity: str, user_input: str = "") -> list[str]:
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

    # Automatically save check-ins as journal entries
    tools_to_call.append("save_journal_entry")

    # Dynamically select create_calendar_reminder if the user input contains reminder/schedule/calendar intent
    ui_lower = user_input.lower()
    if any(k in ui_lower for k in ["remind", "schedule", "calendar", "reminder", "alarm"]):
        tools_to_call.append("create_calendar_reminder")

    return tools_to_call

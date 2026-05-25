"""
wellness_tools.py
-----------------
MCP-style tool functions for Trixie's wellness agent.

Each tool:
  - Has a clear name and docstring (acts as the "tool description" an MCP server exposes)
  - Accepts structured input parameters
  - Returns a structured dict (the "tool result" an MCP client receives)

The recommendation agent calls these tools to enrich its response, exactly
the way an LLM agent would call an MCP tool server.
"""

import random


# ---------------------------------------------------------------------------
# Tool 1 – get_breathing_exercise
# ---------------------------------------------------------------------------

_BREATHING_EXERCISES = {
    "high": {
        "name": "4-7-8 Calming Breath",
        "description": "A clinically-backed technique that activates the parasympathetic nervous system to quickly reduce high anxiety.",
        "steps": [
            "Sit upright and close your eyes.",
            "Inhale quietly through your nose for 4 counts.",
            "Hold your breath for 7 counts.",
            "Exhale completely through your mouth for 8 counts.",
            "Repeat this cycle 4 times.",
        ],
        "duration_minutes": 3,
        "benefit": "Rapidly lowers cortisol and slows heart rate.",
    },
    "medium": {
        "name": "Box Breathing",
        "description": "Used by Navy SEALs to maintain calm under pressure. Simple and effective for moderate stress.",
        "steps": [
            "Breathe in through your nose for 4 counts.",
            "Hold for 4 counts.",
            "Breathe out slowly for 4 counts.",
            "Hold empty for 4 counts.",
            "Repeat 4–6 cycles.",
        ],
        "duration_minutes": 5,
        "benefit": "Resets your nervous system and restores focus.",
    },
    "low": {
        "name": "Mindful Belly Breathing",
        "description": "A gentle grounding exercise to maintain calm and mental clarity during mild stress.",
        "steps": [
            "Place one hand on your chest, one on your belly.",
            "Breathe in slowly through your nose — feel your belly rise.",
            "Exhale slowly through your mouth.",
            "Notice the rhythm for 5 full breaths.",
        ],
        "duration_minutes": 2,
        "benefit": "Anchors attention to the present moment and reduces mental noise.",
    },
}


def get_breathing_exercise(severity: str = "medium") -> dict:
    """
    MCP Tool: get_breathing_exercise
    Returns a structured breathing exercise tailored to the user's stress severity.

    Parameters:
        severity (str): One of 'low', 'medium', 'high'.

    Returns:
        dict with keys: tool_name, exercise (name, description, steps, duration_minutes, benefit)
    """
    key = severity.lower() if severity.lower() in _BREATHING_EXERCISES else "medium"
    exercise = _BREATHING_EXERCISES[key]
    return {
        "tool_name": "get_breathing_exercise",
        "severity_matched": key,
        "exercise": exercise,
    }


# ---------------------------------------------------------------------------
# Tool 2 – lookup_wellness_resources
# ---------------------------------------------------------------------------

_WELLNESS_RESOURCES = {
    "workload": [
        {
            "title": "Eat the Frog",
            "type": "Technique",
            "summary": "Tackle your hardest task first each morning. Brian Tracy's classic method prevents procrastination and reduces end-of-day overload.",
            "action": "Write tomorrow's 'frog' before you leave work today.",
        },
        {
            "title": "Pomodoro Technique",
            "type": "Productivity Method",
            "summary": "Work in focused 25-minute sprints separated by 5-minute breaks. Prevents decision fatigue from long unbroken work sessions.",
            "action": "Start your next task with a 25-minute timer — no interruptions.",
        },
        {
            "title": "Weekly Review",
            "type": "Habit",
            "summary": "Every Friday, spend 15 minutes reviewing what's done, what's pending, and what can be dropped.",
            "action": "Block 15 mins on Friday afternoon as a recurring calendar event.",
        },
    ],
    "meetings": [
        {
            "title": "No-Meeting Block",
            "type": "Calendar Strategy",
            "summary": "Reserve at least one 2-hour uninterrupted slot each day. Guard it as strictly as a client call.",
            "action": "Block 9–11 AM tomorrow as 'Deep Work – Do Not Schedule'.",
        },
        {
            "title": "3-Bullet Agenda Rule",
            "type": "Meeting Hack",
            "summary": "Before any meeting, write exactly 3 bullet-point goals. Meetings with a clear agenda finish 34% faster on average.",
            "action": "Send a 3-bullet agenda for your next scheduled meeting.",
        },
        {
            "title": "Async-First Communication",
            "type": "Team Practice",
            "summary": "Replace status-update meetings with a shared async doc (Notion, Confluence). Reserve live calls for decisions only.",
            "action": "Propose one recurring meeting to be replaced by an async update this week.",
        },
    ],
    "personal": [
        {
            "title": "5-Minute Journal",
            "type": "Mental Health Practice",
            "summary": "Write 3 things you're grateful for, 3 intentions for the day, and 1 affirmation. Proven to shift emotional baseline within 2 weeks.",
            "action": "Try the journal for just 5 minutes first thing tomorrow morning.",
        },
        {
            "title": "Walking Break",
            "type": "Physical Reset",
            "summary": "A 10-minute walk outside during lunch boosts mood by up to 20% and improves afternoon cognitive function.",
            "action": "Step outside for 10 minutes after lunch today.",
        },
        {
            "title": "EAP (Employee Assistance Program)",
            "type": "Professional Resource",
            "summary": "Most organisations offer free, confidential counselling sessions through their EAP. It's not just for crises.",
            "action": "Check your company intranet or HR portal for EAP contact details.",
        },
    ],
    "unclear": [
        {
            "title": "Body Scan Check-in",
            "type": "Mindfulness",
            "summary": "Close your eyes and slowly scan from head to toe noticing tension. Naming physical stress helps the mind process it.",
            "action": "Try a 3-minute body scan right now before your next task.",
        },
        {
            "title": "Stress Audit",
            "type": "Reflection Exercise",
            "summary": "Write down everything stressing you in two columns: 'In my control' and 'Out of my control'. Focus only on column 1.",
            "action": "Spend 5 minutes doing the stress audit — pen and paper works best.",
        },
    ],
}


def lookup_wellness_resources(cause: str = "unclear") -> dict:
    """
    MCP Tool: lookup_wellness_resources
    Returns a curated list of wellness resources for the identified stress cause.

    Parameters:
        cause (str): One of 'workload', 'meetings', 'personal', 'unclear'.

    Returns:
        dict with keys: tool_name, cause_matched, resources (list of resource dicts)
    """
    key = cause.lower() if cause.lower() in _WELLNESS_RESOURCES else "unclear"
    resources = _WELLNESS_RESOURCES[key]
    return {
        "tool_name": "lookup_wellness_resources",
        "cause_matched": key,
        "resources": resources,
    }


# ---------------------------------------------------------------------------
# Tool 3 – get_stress_tip
# ---------------------------------------------------------------------------

_STRESS_TIPS = {
    "workload": [
        "You can't do everything — choose the 3 tasks that move the needle most and let the rest wait.",
        "Multitasking reduces productivity by up to 40%. Serial focus — one task at a time — is always faster.",
        "Saying 'not right now' is a complete sentence. You don't need to justify every boundary at work.",
        "Progress, not perfection. Done and 80% right is almost always better than stuck at 100%.",
    ],
    "meetings": [
        "Standing meetings are 34% shorter on average. Suggest it for your next recurring sync.",
        "If a meeting doesn't have a clear agenda, it's okay to ask for one before accepting.",
        "Every meeting you skip that doesn't need you is time you give back to deep work.",
        "Batch your meetings on specific days — a 'meeting-heavy Tuesday' protects the rest of your week.",
    ],
    "personal": [
        "Compartmentalisation is a skill: create a small ritual (a walk, a coffee) that signals 'work starts now' and 'work ends now'.",
        "You perform better when you're honest about struggling. Vulnerability at work builds trust, not weakness.",
        "It's not your job to have everything figured out. Asking for support is a strength.",
        "Taking care of yourself isn't selfish — it's what keeps you able to show up for others.",
    ],
    "unclear": [
        "When stress feels vague, it usually means there are too many open loops. Write them all down and close one today.",
        "Movement is the fastest legal mood booster. Even 5 minutes of walking resets your nervous system.",
        "Stress shrinks our time horizon — try asking 'will this matter in 6 months?' to restore perspective.",
        "The antidote to overwhelm is always action, however small. Pick one tiny thing and do it now.",
    ],
}


def get_stress_tip(cause: str = "unclear", emotion: str = "stressed") -> dict:
    """
    MCP Tool: get_stress_tip
    Returns a single, context-aware motivational tip based on cause and emotion.

    Parameters:
        cause (str): Root cause category — 'workload', 'meetings', 'personal', 'unclear'.
        emotion (str): Detected emotion string (e.g. 'anxious', 'overwhelmed').

    Returns:
        dict with keys: tool_name, cause_matched, emotion_received, tip
    """
    key = cause.lower() if cause.lower() in _STRESS_TIPS else "unclear"
    tip = random.choice(_STRESS_TIPS[key])
    return {
        "tool_name": "get_stress_tip",
        "cause_matched": key,
        "emotion_received": emotion,
        "tip": tip,
    }

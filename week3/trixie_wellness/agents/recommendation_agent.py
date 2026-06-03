"""
recommendation_agent.py
-----------------------
Recommendation agent — now MCP-tool-aware.

Flow:
  1. Agent calls tool_registry.select_tools_for() to DECIDE which tools to invoke
  2. Agent calls tool_registry.call_tool() for each selected tool (MCP "tools/call")
  3. Tool results are injected into the final recommendations list
  4. LLM fallback is preserved as before
"""

import re
from llm.tinyllama import chat
from tools.tool_registry import select_tools_for, call_tool

FALLBACK_RECS: dict[str, list[str]] = {
    "workload": [
        "Write down your top 3 priorities for today and focus only on those — everything else can wait.",
        "Try the Pomodoro technique: work for 25 minutes, then take a 5-minute break. It protects focus and prevents burnout.",
        "At the end of the day, spend 2 minutes writing tomorrow's short task list so you can mentally switch off tonight.",
    ],
    "meetings": [
        "Block at least one 'no-meeting' focus slot on your calendar each day — protect it as you would a client call.",
        "Before your next meeting, write a 3-bullet agenda. Focused meetings finish faster and leave you with more energy.",
        "After back-to-back calls, take a 3-minute breathing break: inhale for 4 counts, hold for 4, exhale for 6. Repeat 3 times.",
    ],
    "personal": [
        "It is okay to acknowledge personal stress. Try writing your thoughts in a notebook for 5 minutes — it clears mental clutter.",
        "Take a short walk outside during your lunch break; even 10 minutes of fresh air and movement can shift your mood noticeably.",
        "If it feels right, let your manager know you are having a tough week. You do not have to share details — just asking for a lighter day helps.",
    ],
    "unclear": [
        "Right now, try a simple breathing exercise: inhale for 4 counts, hold for 4, exhale slowly for 6. Repeat 3 times.",
        "Drink a glass of water, stand up and stretch for 2 minutes. Small physical resets make a real difference.",
        "Write down the one thing that is weighing on you most today. Naming it takes away some of its power.",
    ],
}

SYSTEM_PROMPT = """You are a caring workplace wellness advisor.

Given an employee's emotional state and the cause of their stress, provide exactly 3 practical wellness recommendations.
If Relevant Knowledge Base Context is provided, strictly prioritize recommendations from that context. Ignore any parts of the context that are irrelevant to the employee's specific situation.

Format your response as a numbered list:
1. [First recommendation — 1 to 2 sentences, warm and actionable]
2. [Second recommendation — 1 to 2 sentences, warm and actionable]
3. [Third recommendation — 1 to 2 sentences, warm and actionable]

Be empathetic, specific, and realistic. Avoid generic advice."""


def _parse_numbered_list(text: str) -> list[str]:
    recs = []
    for line in text.strip().splitlines():
        line = line.strip()
        m = re.match(r'^[1-3][\.\)]\s+(.+)', line)
        if m:
            rec = m.group(1).strip()
            if len(rec) > 15:
                recs.append(rec)
    return recs


def _invoke_tools(cause: str, severity: str, emotion: str, user_input: str) -> tuple[list[dict], list[str]]:
    """
    MCP-style tool invocation step.

    1. Agent DECIDES which tools to call  (select_tools_for)
    2. Agent CALLS each tool              (call_tool)
    3. Returns (raw tool results, human-readable rec strings extracted from results)
    """
    tool_names = select_tools_for(cause, severity, user_input)
    tool_results = []
    recs_from_tools: list[str] = []

    for name in tool_names:
        try:
            if name == "get_breathing_exercise":
                result = call_tool(name, severity=severity)
                tool_results.append(result)
                ex = result["exercise"]
                steps_preview = " → ".join(ex["steps"][:3])
                recs_from_tools.append(
                    f"**{ex['name']}** ({ex['duration_minutes']} min): {steps_preview}… {ex['benefit']}"
                )

            elif name == "lookup_wellness_resources":
                result = call_tool(name, cause=cause)
                tool_results.append(result)
                # Pick the most actionable resource
                top = result["resources"][0]
                recs_from_tools.append(
                    f"**{top['title']}** [{top['type']}]: {top['summary']} — *Try this:* {top['action']}"
                )

            elif name == "get_stress_tip":
                result = call_tool(name, cause=cause, emotion=emotion)
                tool_results.append(result)
                recs_from_tools.append(f"{result['tip']}")

            elif name == "save_journal_entry":
                result = call_tool(name, content=user_input, emotion=emotion, severity=severity, cause=cause)
                tool_results.append(result)

            elif name == "create_calendar_reminder":
                from tools.calendar_tool import parse_reminder_from_text
                act, tm, freq = parse_reminder_from_text(user_input)
                result = call_tool(name, activity=act, time=tm, frequency=freq)
                tool_results.append(result)
                if result.get("status") == "success":
                    rem = result["reminder"]
                    recs_from_tools.append(
                        f"📅 **Calendar Reminder Scheduled:** I've scheduled a {rem['frequency']} reminder for **{rem['activity']}** at **{rem['time']}** to support your daily wellness journey!"
                    )

        except Exception:
            pass  # Never crash the pipeline due to a tool failure

    return tool_results, recs_from_tools


def run_recommendation_agent(state: dict) -> dict:
    emotion      = state.get("emotion", "stressed")
    severity     = state.get("severity", "medium")
    cause        = state.get("cause", "unclear")
    cause_summary = state.get("cause_summary", "")
    user_input   = state.get("user_input", "")
    rag_domain   = state.get("rag_domain", "")
    rag_context  = state.get("rag_context", "")

    # ── Step 1: MCP tool invocation ─────────────────────────────────────────
    tool_results, tool_recs = _invoke_tools(cause, severity, emotion, user_input)

    # ── Step 2: LLM for additional recommendations ──────────────────────────
    message = (
        f"Employee is feeling {emotion} with {severity} severity.\n"
        f"Root cause: {cause}.\n"
    )
    if cause_summary:
        message += f"Context: {cause_summary}\n"
        
    journal_history = state.get("journal_history", [])
    if journal_history:
        history_context = "\n\nHistorical journal entries for context:\n"
        for entry in journal_history[-3:]:
            history_context += f"- [{entry.get('timestamp')}] Emotion: {entry.get('emotion')}, Severity: {entry.get('severity')}, Cause: {entry.get('cause')}. Reflection: {entry.get('content')}\n"
        message += history_context

    if rag_context:
        message += f"\nRelevant Knowledge Base Context (Domain: {rag_domain}):\n{rag_context}\n"
        
    message += "\nPlease provide 3 wellness recommendations."

    llm_recs: list[str] = []
    try:
        raw = chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=message,
            max_new_tokens=380,
            temperature=0.65,
        )
        llm_recs = _parse_numbered_list(raw)
    except Exception:
        pass

    # ── Step 3: Merge — tool results take priority ───────────────────────────
    # Tool recs fill the first slots; LLM fills remaining up to 3 total
    merged: list[str] = list(tool_recs)
    for rec in llm_recs:
        if len(merged) >= 3:
            break
        merged.append(rec)

    # Final fallback if everything is empty
    if len(merged) < 2:
        merged = FALLBACK_RECS.get(cause, FALLBACK_RECS["unclear"])

    # ── Step 4: Expose tool call metadata back to the pipeline state ─────────
    tools_used = [r["tool_name"] for r in tool_results]

    from tools.calendar_tool import get_calendar_reminders
    latest_reminders = get_calendar_reminders().get("reminders", [])

    return {
        "recommendations": merged[:3],
        "tools_used": tools_used,
        "tool_results": tool_results,
        "reminders": latest_reminders,
    }

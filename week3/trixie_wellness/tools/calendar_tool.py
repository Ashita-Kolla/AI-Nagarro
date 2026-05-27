import os
import json
import re
import uuid
from datetime import datetime

# Define workspace root and calendar path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALENDAR_FILE = os.path.join(WORKSPACE_ROOT, "wellness_calendar.json")

VALID_ACTIVITIES = ["meditation", "hydration", "sleep", "journaling", "exercise"]

def get_calendar_reminders() -> dict:
    """
    Reads active reminders from the SQLite database.
    """
    try:
        from database import get_reminders
        reminders = get_reminders()
        return {"status": "success", "reminders": reminders}
    except Exception as e:
        return {"status": "error", "message": f"Failed to read reminders: {str(e)}", "reminders": []}

def save_reminders(reminders: list) -> bool:
    """
    Legacy helper (deprecated). Saves reminders list to wellness_calendar.json.
    """
    try:
        with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
            json.dump(reminders, f, indent=2)
        return True
    except Exception:
        return False

def create_calendar_reminder(activity: str, time: str, frequency: str = "daily") -> dict:
    """
    Validates the wellness category, creates a reminder, and persists it to SQLite.
    """
    activity = activity.lower().strip()
    # Normalize activity
    matched_activity = None
    for act in VALID_ACTIVITIES:
        if act in activity or activity in act:
            matched_activity = act
            break
    
    if not matched_activity:
        matched_activity = "meditation"  # Default fallback
    
    # Normalize time (expected HH:MM format, if invalid fallback to 08:00)
    time = time.strip()
    if not re.match(r"^\d{1,2}:\d{2}$", time):
        # Quick fallback normalize "8 PM" etc if passed in
        time_match = re.search(r"(\d{1,2})\s*(?::\s*(\d{2}))?\s*(am|pm)?", time, re.IGNORECASE)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            am_pm = time_match.group(3)
            if am_pm:
                if am_pm.lower() == "pm" and hour < 12:
                    hour += 12
                elif am_pm.lower() == "am" and hour == 12:
                    hour = 0
            time = f"{hour:02d}:{minute:02d}"
        else:
            time = "08:00"

    reminder_id = f"rem_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().isoformat()
    
    from database import create_reminder
    if create_reminder(reminder_id, matched_activity, time, frequency, active=True, timestamp=timestamp):
        reminder = {
            "id": reminder_id,
            "activity": matched_activity,
            "time": time,
            "frequency": frequency,
            "active": True,
            "timestamp": timestamp
        }
        return {
            "status": "success",
            "tool_name": "create_calendar_reminder",
            "message": f"Successfully created a {frequency} reminder for {matched_activity} at {time}.",
            "reminder": reminder
        }
    else:
        return {
            "status": "error",
            "tool_name": "create_calendar_reminder",
            "message": "Failed to save the reminder to the persistent database.",
            "reminder": None
        }


def parse_reminder_from_text(text: str) -> tuple[str, str, str]:
    """
    Parses wellness activity, time, and frequency from natural language.
    Examples:
      "Remind me to meditate every evening at 8 PM." -> ("meditation", "20:00", "every evening")
      "remind me to drink water daily at 2pm" -> ("hydration", "14:00", "daily")
    """
    text_lower = text.lower()
    
    # 1. Detect activity
    activity = "meditation"  # Default
    if "meditat" in text_lower:
        activity = "meditation"
    elif "water" in text_lower or "hydrat" in text_lower or "drink" in text_lower:
        activity = "hydration"
    elif "sleep" in text_lower or "bed" in text_lower:
        activity = "sleep"
    elif "journal" in text_lower or "reflect" in text_lower or "write" in text_lower:
        activity = "journaling"
    elif "exercise" in text_lower or "workout" in text_lower or "run" in text_lower or "walk" in text_lower or "stretch" in text_lower:
        activity = "exercise"
        
    # 2. Detect frequency/recurrence
    frequency = "daily"
    if "every evening" in text_lower:
        frequency = "every evening"
    elif "every morning" in text_lower:
        frequency = "every morning"
    elif "every day" in text_lower or "daily" in text_lower:
        frequency = "daily"
    elif "weekly" in text_lower:
        frequency = "weekly"
    elif "every night" in text_lower:
        frequency = "every night"
        
    # 3. Detect time
    time = "08:00"  # default
    # Search for e.g. "8 PM", "8:30 PM", "20:00", "at 8", "at 14"
    time_match = re.search(r"(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        am_pm = time_match.group(3)
        
        # Check context for evening/morning/night if am/pm is not specified
        if not am_pm:
            if "evening" in text_lower or "night" in text_lower or "pm" in text_lower:
                if hour < 12:
                    hour += 12
            elif "morning" in text_lower or "am" in text_lower:
                if hour == 12:
                    hour = 0
        else:
            if am_pm == "pm" and hour < 12:
                hour += 12
            elif am_pm == "am" and hour == 12:
                hour = 0
                
        time = f"{hour:02d}:{minute:02d}"
    else:
        # Set based on contextual time indicators if no digits found
        if "evening" in text_lower:
            time = "20:00"
        elif "morning" in text_lower:
            time = "08:00"
        elif "afternoon" in text_lower:
            time = "14:00"
        elif "night" in text_lower:
            time = "22:00"

    return activity, time, frequency

def toggle_calendar_reminder(reminder_id: str) -> dict:
    """
    Toggles the active state of a reminder in SQLite.
    """
    from database import toggle_reminder
    return toggle_reminder(reminder_id)

def delete_calendar_reminder(reminder_id: str) -> dict:
    """
    Deletes a reminder by its ID in SQLite.
    """
    from database import delete_reminder
    return delete_reminder(reminder_id)


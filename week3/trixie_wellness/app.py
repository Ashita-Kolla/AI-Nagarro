import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from graph.workflow import run_pipeline

app = FastAPI()

import uuid
import re

class CheckinRequest(BaseModel):
    user_input: str
    stress_level: str = ""
    sleep_hours: float = None

def extract_sleep_hours(text: str) -> float | None:
    """
    Extracts sleep hours from user input text using regular expressions.
    Examples:
        "slept 7 hours" -> 7.0
        "got 6.5 hrs of sleep" -> 6.5
        "slept 8h" -> 8.0
    """
    text_lower = text.lower()
    patterns = [
        r'(?:slept|sleep|got|had)\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:hours|hour|hrs|hr|h)\b',
        r'(\d+(?:\.\d+)?)\s*(?:hours|hour|hrs|hr|h)\s+(?:of\s+)?sleep\b',
        r'sleep\s*[:=-]\s*(\d+(?:\.\d+)?)\s*(?:hours|hour|hrs|hr|h)?\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
    return None

@app.post("/api/checkin")
def checkin(req: CheckinRequest):
    try:
        res = run_pipeline(req.user_input, req.stress_level)
        
        # Determine sleep hours
        sleep_hours = req.sleep_hours
        if sleep_hours is None:
            sleep_hours = extract_sleep_hours(req.user_input)
            
        # Save check-in result to SQLite mood_logs
        from database import save_mood_log
        log_id = f"mood_{uuid.uuid4().hex[:8]}"
        save_mood_log(
            log_id=log_id,
            user_input=req.user_input,
            stress_level=res.get("stress_level", req.stress_level),
            emotion=res.get("emotion", ""),
            severity=res.get("severity", ""),
            cause=res.get("cause", ""),
            sleep_hours=sleep_hours
        )
        
        # Include sleep_hours in the response
        response_data = dict(res)
        response_data["sleep_hours"] = sleep_hours
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class JournalEntryRequest(BaseModel):
    content: str
    emotion: str = "neutral"
    severity: str = "low"
    cause: str = "unclear"

@app.get("/api/journal")
def get_journal():
    try:
        from tools.google_docs_tool import get_journal_history
        return get_journal_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/journal")
def save_journal(req: JournalEntryRequest):
    try:
        from tools.google_docs_tool import save_journal_entry
        return save_journal_entry(req.content, req.emotion, req.severity, req.cause)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ReminderRequest(BaseModel):
    activity: str
    time: str
    frequency: str = "daily"

@app.get("/api/reminders")
def get_reminders():
    try:
        from tools.calendar_tool import get_calendar_reminders
        return get_calendar_reminders()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reminders")
def create_reminder(req: ReminderRequest):
    try:
        from tools.calendar_tool import create_calendar_reminder
        return create_calendar_reminder(req.activity, req.time, req.frequency)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reminders/toggle/{reminder_id}")
def toggle_reminder(reminder_id: str):
    try:
        from tools.calendar_tool import toggle_calendar_reminder
        return toggle_calendar_reminder(reminder_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/reminders/{reminder_id}")
def delete_reminder(reminder_id: str):
    try:
        from tools.calendar_tool import delete_calendar_reminder
        return delete_calendar_reminder(reminder_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AnalyticsRequest(BaseModel):
    question: str

@app.post("/api/analytics/query")
def run_analytics_query(req: AnalyticsRequest):
    try:
        from tools.sql_tool import run_text_to_sql
        return run_text_to_sql(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

os.makedirs(static_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

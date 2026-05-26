import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from graph.workflow import run_pipeline

app = FastAPI()

class CheckinRequest(BaseModel):
    user_input: str
    stress_level: str = ""

@app.post("/api/checkin")
def checkin(req: CheckinRequest):
    try:
        return run_pipeline(req.user_input, req.stress_level)
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

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

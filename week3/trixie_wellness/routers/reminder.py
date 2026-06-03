from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/reminders", tags=["reminder"])

class ReminderRequest(BaseModel):
    activity: str
    time: str
    frequency: str = "daily"

@router.get("")
def get_reminders():
    try:
        from tools.calendar_tool import get_calendar_reminders
        return get_calendar_reminders()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
def create_reminder(req: ReminderRequest):
    try:
        from tools.calendar_tool import create_calendar_reminder
        return create_calendar_reminder(req.activity, req.time, req.frequency)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/toggle/{reminder_id}")
def toggle_reminder(reminder_id: str):
    try:
        from tools.calendar_tool import toggle_calendar_reminder
        return toggle_calendar_reminder(reminder_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: str):
    try:
        from tools.calendar_tool import delete_calendar_reminder
        return delete_calendar_reminder(reminder_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

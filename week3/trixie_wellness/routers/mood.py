from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import re
from database import save_mood_log

router = APIRouter(prefix="/api/mood", tags=["mood"])

class MoodCheckinRequest(BaseModel):
    user_input: str
    stress_level: str = ""
    emotion: str = ""
    severity: str = ""
    cause: str = ""
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

@router.post("/")
def log_mood(req: MoodCheckinRequest):
    try:
        sleep_hours = req.sleep_hours
        if sleep_hours is None:
            sleep_hours = extract_sleep_hours(req.user_input)
            
        log_id = f"mood_{uuid.uuid4().hex[:8]}"
        save_mood_log(
            log_id=log_id,
            user_input=req.user_input,
            stress_level=req.stress_level,
            emotion=req.emotion,
            severity=req.severity,
            cause=req.cause,
            sleep_hours=sleep_hours
        )
        
        return {
            "status": "success",
            "log_id": log_id,
            "sleep_hours": sleep_hours,
            "message": "Mood logged successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

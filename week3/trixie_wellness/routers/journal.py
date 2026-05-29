from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/journal", tags=["journal"])

class JournalEntryRequest(BaseModel):
    content: str
    emotion: str = "neutral"
    severity: str = "low"
    cause: str = "unclear"

@router.get("/")
def get_journal():
    try:
        from tools.google_docs_tool import get_journal_history
        return get_journal_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def save_journal(req: JournalEntryRequest):
    try:
        from tools.google_docs_tool import save_journal_entry
        return save_journal_entry(req.content, req.emotion, req.severity, req.cause)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

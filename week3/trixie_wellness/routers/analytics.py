from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

class AnalyticsRequest(BaseModel):
    question: str

@router.post("/query")
def run_analytics_query(req: AnalyticsRequest):
    try:
        from tools.sql_tool import run_text_to_sql
        return run_text_to_sql(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

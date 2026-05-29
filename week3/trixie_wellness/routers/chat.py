from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from graph.workflow import run_pipeline

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    user_input: str
    stress_level: str = ""

@router.post("/")
def chat_with_agent(req: ChatRequest):
    try:
        res = run_pipeline(req.user_input, req.stress_level)
        return dict(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

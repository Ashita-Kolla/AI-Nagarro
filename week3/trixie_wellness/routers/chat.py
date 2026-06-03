from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from graph.workflow import run_pipeline
from database import log_safety_incident

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    user_input: str
    stress_level: str = ""

@router.post("")
@router.post("/")
def chat_with_agent(req: ChatRequest):
    try:
        res = dict(run_pipeline(req.user_input, req.stress_level))
        
        # Responsible AI Interception
        if res.get("is_flagged"):
            log_safety_incident(
                user_input=req.user_input,
                risk_level=res.get("risk_level", "unknown"),
                flag_reason=res.get("flag_reason", "unknown"),
                action_taken="intercepted and escalated"
            )
            # Override recommendations to show the safety response prominently
            res["recommendations"] = [
                f"🚨 URGENT SAFETY NOTICE: {res.get('safety_response', 'Please seek professional help immediately.')}"
            ]
        
        # Inject standard disclaimer into the recommendations
        disclaimer = "⚠️ DISCLAIMER: Trixie is an AI wellness assistant, not a medical or mental health professional. If you are in crisis, please call 988 or seek professional help."
        
        if "recommendations" not in res or not isinstance(res["recommendations"], list):
            res["recommendations"] = []
            
        res["recommendations"].append(disclaimer)
        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

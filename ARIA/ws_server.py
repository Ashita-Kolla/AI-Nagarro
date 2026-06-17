"""
ws_server.py — FastAPI WebSocket bridge for ARIA
Connects the React frontend to the Python agent pipeline.

Run with:
    uvicorn ws_server:app --reload --port 8000
"""

import asyncio
import json
import queue
import threading
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Ensure the ARIA root is in sys.path so core/ and agents/ resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

app = FastAPI(title="ARIA WebSocket Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# EVENT PROTOCOL
# ─────────────────────────────────────────────
# Frontend → Backend:
#   { "type": "start",        "brief": "..." }
#   { "type": "gate_action",  "action": "Approve"|"Edit"|"Regenerate"|"Quit",
#                             "agent": "BA", "correction": "..." }
#
# Backend → Frontend:
#   { "type": "log",            "message": "..." }
#   { "type": "supervisor_result", "data": {...} }
#   { "type": "agent_start",   "agent": "BA" }
#   { "type": "agent_output",  "agent": "BA", "data": {...}, "score": 85,
#                              "warning": null, "summary": "..." }
#   { "type": "gate_required", "agent": "BA" }
#   { "type": "agent_approved","agent": "BA" }
#   { "type": "pipeline_done" }
#   { "type": "error",         "message": "..." }
# ─────────────────────────────────────────────


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Thread-safe queues
    out_q: asyncio.Queue = asyncio.Queue()   # pipeline thread → WebSocket coroutine
    in_q:  queue.Queue   = queue.Queue()     # WebSocket coroutine → pipeline thread (blocking)

    loop = asyncio.get_event_loop()

    # ── Drain out_q and forward to client ──────────────────────────────────
    async def sender():
        while True:
            msg = await out_q.get()
            if msg is None:          # sentinel: pipeline finished / disconnected
                break
            try:
                await websocket.send_text(json.dumps(msg, ensure_ascii=False))
            except Exception:
                break

    sender_task = asyncio.create_task(sender())

    def push(event: dict):
        """Thread-safe helper called from the pipeline thread."""
        asyncio.run_coroutine_threadsafe(out_q.put(event), loop)

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            # ── Start a new pipeline run ────────────────────────────────────
            if msg.get("type") == "start":
                brief = msg.get("brief", "").strip()
                if not brief:
                    push({"type": "error", "message": "No brief provided."})
                    continue

                def run_pipeline(brief=brief):
                    try:
                        _execute_pipeline(brief, push, in_q)
                    except Exception as exc:
                        push({"type": "error", "message": f"Pipeline error: {exc}"})
                    finally:
                        asyncio.run_coroutine_threadsafe(out_q.put(None), loop)

                threading.Thread(target=run_pipeline, daemon=True).start()

            # ── Forward human-gate decision to the waiting pipeline thread ──
            elif msg.get("type") == "gate_action":
                in_q.put(msg)

    except WebSocketDisconnect:
        pass
    finally:
        sender_task.cancel()


# ─────────────────────────────────────────────
# PIPELINE EXECUTION (runs in a daemon thread)
# ─────────────────────────────────────────────
def _execute_pipeline(brief: str, push, in_q: queue.Queue):
    from core.context_manager import ContextManager
    from core.supervisor import Supervisor
    from core.ws_agent_runner import WSAgentRunner

    ctx = ContextManager()
    ctx.add_output("USER_BRIEF", brief)

    supervisor = Supervisor()

    push({"type": "log", "message": "Supervisor is evaluating the project brief..."})

    routing_data = supervisor.determine_routing(brief)
    if not routing_data:
        push({"type": "error", "message": "Supervisor failed to parse the brief. Check LLM connectivity."})
        return

    push({"type": "supervisor_result", "data": routing_data})
    push({"type": "log", "message": f"Supervisor summary: {routing_data.get('summary', '')}"})

    agents_required = routing_data.get("agents_required", [])
    if not agents_required:
        confidence = routing_data.get("confidence_score", 0)
        push({"type": "error", "message": f"Brief too vague to route (confidence: {confidence}). Please clarify."})
        return

    execution_queue = supervisor.build_execution_queue(agents_required)
    push({"type": "log", "message": f"Execution queue resolved: {' → '.join(execution_queue)}"})

    runner = WSAgentRunner(ctx, supervisor, push_event=push, hitl_queue=in_q)
    runner.run_queue(execution_queue)

    push({"type": "pipeline_done", "message": "All agents completed. Full context saved."})

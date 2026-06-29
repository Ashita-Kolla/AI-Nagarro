"""
ws_server.py — FastAPI WebSocket bridge for ARIA
Connects the React frontend to the Python agent pipeline.

Run with:
    uvicorn ws_server:app --port 8000

!! IMPORTANT: Do NOT use --reload. It kills the pipeline thread mid-run.
"""

import asyncio
import json
import queue
import threading
import os
import sys
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)

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


@app.get("/download/{agent_name}/{filename}")
async def download_artifact(agent_name: str, filename: str):
    """Serve any generated artifact for browser download."""
    import urllib.parse
    agent_name = urllib.parse.unquote(agent_name)
    filename = urllib.parse.unquote(filename)
    
    # Basic path traversal protection
    if ".." in agent_name or ".." in filename or "/" in filename or "\\" in filename:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid path")
        
    file_path = os.path.join(os.path.dirname(__file__), "outputs", agent_name, filename)
    if not os.path.exists(file_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found.")
        
    return FileResponse(
        path=file_path,
        filename=filename,
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
        pipeline_state = {"running": False}  # dict so it can be mutated by threads

        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            # ── Start a new pipeline run ────────────────────────────────────
            if msg.get("type") == "start":
                if pipeline_state["running"]:
                    push({"type": "log", "message": "Pipeline already running. Please wait or reconnect."})
                    continue

                brief = msg.get("brief", "").strip()
                if not brief:
                    push({"type": "error", "message": "No brief provided."})
                    continue

                pipeline_state["running"] = True
                run_thread_id = str(uuid.uuid4())   # unique per run — stored for resume
                push({"type": "pipeline_started", "thread_id": run_thread_id})

                def run_pipeline(brief=brief, thread_id=run_thread_id):
                    try:
                        _execute_pipeline(brief, push, in_q, thread_id)
                    except Exception as exc:
                        push({"type": "error", "message": f"Pipeline error: {exc}"})
                    finally:
                        pipeline_state["running"] = False
                        push({"type": "log", "message": "Pipeline thread finished."})

                threading.Thread(target=run_pipeline, daemon=True).start()

            # ── Resume a checkpointed run ──────────────────────────────────
            elif msg.get("type") == "resume":
                if pipeline_state["running"]:
                    push({"type": "log", "message": "Pipeline already running. Please wait."})
                    continue

                thread_id  = msg.get("thread_id", "")
                from_agent = msg.get("from_agent", None)
                if not thread_id:
                    push({"type": "error", "message": "resume requires a thread_id."})
                    continue

                pipeline_state["running"] = True
                push({"type": "log", "message": f"[Resume] Resuming run {thread_id[:8]}… from {from_agent or 'last checkpoint'}."})

                def run_resume(tid=thread_id, fa=from_agent):
                    try:
                        _resume_pipeline(push, in_q, tid, fa)
                    except Exception as exc:
                        push({"type": "error", "message": f"Resume error: {exc}"})
                    finally:
                        pipeline_state["running"] = False
                        push({"type": "log", "message": "Resume thread finished."})

                threading.Thread(target=run_resume, daemon=True).start()

            # ── Forward human-gate decision to the waiting pipeline thread ──
            elif msg.get("type") == "gate_action":
                in_q.put(msg)
                
            # ── Save Scripts (Safe UI approach) ──
            elif msg.get("type") == "save_scripts":
                agent_name = msg.get("agent")
                if agent_name == "Environment":
                    script_content = msg.get("script_content", "")
                    env_dir = os.path.join("outputs", "Environment")
                    os.makedirs(env_dir, exist_ok=True)
                    with open(os.path.join(env_dir, "setup.ps1"), "w", encoding="utf-8") as f:
                        f.write(script_content)
                elif agent_name == "QA":
                    test_suite = msg.get("test_suite", [])
                    qa_dir = os.path.join("outputs", "QA", "tests")
                    os.makedirs(qa_dir, exist_ok=True)
                    for test in test_suite:
                        filename = test.get("file")
                        code = test.get("code")
                        if filename and code:
                            with open(os.path.join(qa_dir, filename), "w", encoding="utf-8") as f:
                                f.write(code)

            # ── Execute Environment Script (Test Run) ──
            elif msg.get("type") == "test_run_script":
                script_content = msg.get("script_content", "")
                commands = script_content.split('\n')
                def do_test_run():
                    try:
                        from agents.environment import execute_setup_script
                        # Pass a dummy name and the content
                        result = execute_setup_script("setup.ps1", commands)
                        push({"type": "test_run_result", "status": result["status"], "log": result["log"]})
                    except Exception as e:
                        push({"type": "test_run_result", "status": "FAIL", "log": f"Server error: {e}"})
                threading.Thread(target=do_test_run, daemon=True).start()

            # ── Execute QA Playwright Scripts (Test Run) ──
            elif msg.get("type") == "test_run_qa":
                test_suite = msg.get("test_suite", [])
                def do_qa_test_run():
                    try:
                        from agents.qa import execute_local_tests
                        result = execute_local_tests(test_suite)
                        status = "PASS" if result.get("failed", 0) == 0 else "FAIL"
                        log = f"Total: {result.get('total_tests', 0)} | Passed: {result.get('passed', 0)} | Failed: {result.get('failed', 0)}\n\n{result.get('log', '')}"
                        push({"type": "test_run_result", "status": status, "log": log})
                    except Exception as e:
                        push({"type": "test_run_result", "status": "FAIL", "log": f"Server error: {e}"})
                threading.Thread(target=do_qa_test_run, daemon=True).start()

            # ── Execute Single QA Script (Playground) ──
            elif msg.get("type") == "test_run_single_qa":
                filename = msg.get("filename")
                code = msg.get("code")
                def do_single_qa_test_run():
                    try:
                        import subprocess
                        import sys
                        import os
                        from agents.qa import ensure_python_packages, fix_code_string

                        qa_dir = os.path.abspath(os.path.join("outputs", "QA", "tests"))
                        codebase_dir = os.path.abspath(os.path.join("outputs", "Developer", "codebase"))
                        codebase_tests_dir = os.path.join(codebase_dir, "tests")
                        os.makedirs(qa_dir, exist_ok=True)
                        os.makedirs(codebase_tests_dir, exist_ok=True)

                        # Ensure all Python package dirs have __init__.py before running
                        ensure_python_packages(codebase_dir)

                        # Enforce .py extension — safety net in case frontend sends .js name
                        safe_filename = filename
                        if safe_filename and not safe_filename.endswith(".py"):
                            safe_filename = os.path.splitext(safe_filename)[0] + ".py"

                        # Repair literal \n in code (LLM double-escape bug)
                        safe_code = fix_code_string(code)

                        # Save into Developer/codebase/tests (primary — imports resolve here)
                        test_path = os.path.join(codebase_tests_dir, safe_filename)
                        with open(test_path, "w", encoding="utf-8") as f:
                            f.write(safe_code)
                        # Also keep a copy in QA/tests for frontend artifact records
                        with open(os.path.join(qa_dir, safe_filename), "w", encoding="utf-8") as f:
                            f.write(safe_code)


                        # PYTHONPATH = codebase_dir so `from app.xyz import ...` resolves.
                        # Python adds the script's own dir (tests/) to sys.path[0] when run
                        # by absolute path — NOT the cwd — so we must set PYTHONPATH explicitly.
                        env = os.environ.copy()
                        env["PYTHONPATH"] = codebase_dir
                        result = subprocess.run(
                            [sys.executable, test_path],
                            cwd=codebase_dir,
                            env=env,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        status = "PASS" if result.returncode == 0 else "FAIL"
                        log = f"Exit code {result.returncode}\n{result.stdout}\n{result.stderr}"
                        push({"type": "test_run_single_result", "filename": safe_filename, "status": status, "log": log})
                    except Exception as e:
                        push({"type": "test_run_single_result", "filename": filename, "status": "FAIL", "log": f"Server error: {e}"})

                threading.Thread(target=do_single_qa_test_run, daemon=True).start()

    except WebSocketDisconnect:
        pass
    finally:
        sender_task.cancel()


# ─────────────────────────────────────────────
# PIPELINE EXECUTION (runs in a daemon thread)
# ─────────────────────────────────────────────
def _execute_pipeline(brief: str, push, in_q: queue.Queue, thread_id: str):
    from core.context_manager import ContextManager
    from core.supervisor import Supervisor
    from core.langgraph_runner import LangGraphRunner

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

    # Store supervisor output in context so downstream agents (e.g. BA) can read it
    ctx.add_output("Supervisor", routing_data)

    agents_required = routing_data.get("agents_required", [])
    if not agents_required:
        confidence = routing_data.get("confidence_score", 0)
        push({"type": "error", "message": f"Brief too vague to route (confidence: {confidence}). Please clarify."})
        return

    # Build the required agents sequence just for stable reference
    ordered_required = supervisor.build_execution_queue(agents_required)
    
    push({"type": "log", "message": f"Dynamic LangGraph routing configured for: {' -> '.join(ordered_required)}"})

    runner = LangGraphRunner(ctx, supervisor, push_event=push, hitl_queue=in_q)
    
    initial_state = {
        "brief": brief,
        "supervisor_routing": routing_data,
        "agents_required": ordered_required,
        "completed_agents": [],
        "current_agent": "",
        "agent_outputs": {},
        "human_correction": "",
        "human_action": {}
    }
    
    runner.run_graph(initial_state, thread_id=thread_id)

    push({"type": "pipeline_done", "message": "All agents completed. Full context saved."})


def _resume_pipeline(push, in_q: queue.Queue, thread_id: str, from_agent: str = None):
    """Resumes the pipeline from a saved checkpoint."""
    from core.context_manager import ContextManager
    from core.supervisor import Supervisor
    from core.langgraph_runner import LangGraphRunner

    # Note: State is loaded from SqliteSaver inside LangGraphRunner.
    # ContextManager should ideally re-hydrate from disk if it was saving there,
    # but since ARIA relies on the state passed through LangGraph, we can just
    # instantiate it and pass it to the runner. The agents use the state values.
    # If ContextManager holds critical global state, it should be serialized too,
    # but for ARIA's current design, the LangGraph state is sufficient for resuming.
    ctx = ContextManager()
    supervisor = Supervisor()
    runner = LangGraphRunner(ctx, supervisor, push_event=push, hitl_queue=in_q)
    
    runner.resume_graph(thread_id, from_agent=from_agent)
    push({"type": "pipeline_done", "message": "Resumed pipeline completed. Full context saved."})

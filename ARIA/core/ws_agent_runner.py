"""
core/ws_agent_runner.py
WebSocket-compatible agent runner.
Replaces blocking input() calls with thread-safe queue reads.
"""

import importlib
import json


class WSAgentRunner:
    def __init__(self, context_manager, supervisor, push_event, hitl_queue):
        self.context_manager = context_manager
        self.supervisor = supervisor
        self.push = push_event
        self.hitl_q = hitl_queue

    def run_queue(self, execution_queue, start_index=0):
        for i in range(start_index, len(execution_queue)):
            agent_name = execution_queue[i]
            self.push({"type": "agent_start", "agent": agent_name})
            self.push({"type": "log", "message": f"Starting {agent_name} agent..."})

            # Dynamic import of agent module
            try:
                agent_module = importlib.import_module(f"agents.{agent_name.lower()}")
            except ImportError as exc:
                self.push({"type": "error", "message": f"Could not load agent '{agent_name}': {exc}"})
                return

            human_note = None

            while True:
                # ── Call the agent ─────────────────────────────────────────
                result_data = agent_module.run(self.context_manager, correction=human_note)

                if not result_data:
                    self.push({"type": "error", "message": f"{agent_name} returned no parseable output. Stopping."})
                    return

                # ── Supervisor quality check ───────────────────────────────
                score, warning = self.supervisor.check_quality_ws(
                    agent_name, result_data, self.context_manager
                )

                # ── Push output to frontend ────────────────────────────────
                self.push({
                    "type":    "agent_output",
                    "agent":   agent_name,
                    "data":    result_data,
                    "score":   score,
                    "warning": warning,
                    "summary": _make_summary(agent_name, result_data),
                })

                if score is not None and score < 50:
                    self.push({"type": "log",
                               "message": f"WARNING: {agent_name} scored {score}/100 — {warning or 'low confidence'}."})
                else:
                    self.push({"type": "log",
                               "message": f"{agent_name} quality check passed. Score: {score}/100."})

                # ── Human gate ─────────────────────────────────────────────
                self.push({"type": "gate_required", "agent": agent_name})
                response = self.hitl_q.get()   # blocks until frontend responds

                action     = response.get("action", "")
                correction = response.get("correction", "")

                if action == "Approve":
                    self.context_manager.add_output(agent_name, result_data)
                    
                    if hasattr(agent_module, "post_approval"):
                        try:
                            self.push({"type": "log", "message": f"Running post-approval tasks for {agent_name}..."})
                            agent_module.post_approval(result_data, self.context_manager)
                            if agent_name == "BA":
                                self.push({"type": "brd_ready", "path": "outputs/BRD.docx",
                                           "message": "BRD document generated: outputs/BRD.docx"})
                        except Exception as e:
                            self.push({"type": "error", "message": f"Post-approval task failed: {e}"})
                            
                    self.push({"type": "agent_approved", "agent": agent_name})
                    self.push({"type": "log", "message": f"Human approved {agent_name}. Proceeding."})
                    break

                elif action == "Edit":
                    human_note = ((human_note + f"\n- {correction}") if human_note else correction)
                    self.push({"type": "log", "message": f"Human correction applied to {agent_name}. Rerunning..."})

                elif action == "Regenerate":
                    human_note = None
                    self.push({"type": "log", "message": f"Regenerating {agent_name} with no changes..."})

                elif action == "Quit":
                    self.push({"type": "log", "message": "User quit. Progress up to previous step is saved."})
                    return

                else:
                    self.push({"type": "log", "message": f"Unknown gate action '{action}'. Ignoring."})

        self.push({"type": "log", "message": "All agents completed successfully."})


def _make_summary(agent_name: str, data: dict) -> str:
    """Generate a one-liner summary for the frontend agent row."""
    if not isinstance(data, dict):
        return f"{agent_name} output received."
    top_keys = list(data.keys())[:3]
    return f"{agent_name} produced: {', '.join(top_keys)}."

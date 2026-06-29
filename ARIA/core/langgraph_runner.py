"""
core/langgraph_runner.py
LangGraph-based stateful agent runner for ARIA.
Replaces the linear ws_agent_runner.py loop.
"""

import importlib
import json
import os
import operator
import sqlite3
from typing import TypedDict, Annotated, Any, Dict, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# ── Checkpoint DB lives next to outputs/ so it survives backend restarts ──────
_CHECKPOINT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", ".checkpoints")
os.makedirs(_CHECKPOINT_DIR, exist_ok=True)
_CHECKPOINT_DB = os.path.join(_CHECKPOINT_DIR, "aria.db")

class AriaState(TypedDict):
    brief: str
    supervisor_routing: dict
    agents_required: list
    completed_agents: list
    current_agent: str
    agent_outputs: dict
    human_correction: str
    human_action: dict

class LangGraphRunner:
    def __init__(self, context_manager, supervisor, push_event, hitl_queue):
        self.context_manager = context_manager
        self.supervisor = supervisor
        self.push = push_event
        self.hitl_q = hitl_queue
        self.graph = None          # set by build_graph(); exposed for ws_server resume

    def _make_summary(self, agent_name: str, data: dict) -> str:
        if not isinstance(data, dict): return f"{agent_name} output received."
        top_keys = list(data.keys())[:3]
        return f"{agent_name} produced: {', '.join(top_keys)}."

    def build_graph(self):
        # 1. Routing node: Sets current_agent based on completion status
        def set_next_agent(state: AriaState):
            completed = state.get("completed_agents", [])
            required = state.get("agents_required", [])
            for agent in required:
                if agent not in completed:
                    return {"current_agent": agent, "human_correction": ""}
            return {"current_agent": ""}

        # 2. Main Agent Execution node
        def agent_node(state: AriaState):
            agent_name = state.get("current_agent")
            if not agent_name:
                return {}

            self.push({"type": "agent_start", "agent": agent_name})
            self.push({"type": "log", "message": f"Starting {agent_name} agent via LangGraph..."})

            try:
                agent_module = importlib.import_module(f"agents.{agent_name.lower()}")
            except ImportError as exc:
                self.push({"type": "error", "message": f"Could not load agent '{agent_name}': {exc}"})
                return {}

            correction = state.get("human_correction", "")
            result_data = agent_module.run(self.context_manager, correction=correction)

            if not result_data:
                self.push({"type": "error", "message": f"{agent_name} returned no parseable output. Stopping."})
                return {}

            score, warning = self.supervisor.check_quality_ws(
                agent_name, result_data, self.context_manager
            )

            self.push({
                "type":    "agent_output",
                "agent":   agent_name,
                "data":    result_data,
                "score":   score,
                "warning": warning,
                "summary": self._make_summary(agent_name, result_data),
            })

            if score is not None and score < 50:
                self.push({"type": "log", "message": f"WARNING: {agent_name} scored {score}/100 — {warning or 'low confidence'}."})
            else:
                self.push({"type": "log", "message": f"{agent_name} quality check passed. Score: {score}/100."})

            outputs = dict(state.get("agent_outputs", {}))
            outputs[agent_name] = result_data
            return {"agent_outputs": outputs}

        # 3. Human Gate (Interrupt) Node — LangGraph interrupts BEFORE this
        def human_gate_node(state: AriaState):
            return {}

        # 4. Process human action after resume
        def process_gate_action(state: AriaState):
            action_data = state.get("human_action", {})
            action = action_data.get("action", "")
            agent_name = state.get("current_agent")
            result_data = state.get("agent_outputs", {}).get(agent_name, {})

            if action == "Approve":
                self.context_manager.add_output(agent_name, result_data)
                try:
                    agent_module = importlib.import_module(f"agents.{agent_name.lower()}")
                    if hasattr(agent_module, "post_approval"):
                        self.push({"type": "log", "message": f"Running post-approval tasks for {agent_name}..."})
                        paths = agent_module.post_approval(result_data, self.context_manager)
                        if paths:
                            if isinstance(paths, str): paths = [paths]
                            self.push({"type": "artifacts_ready", "agent": agent_name, "paths": paths, "message": f"Artifacts generated for {agent_name}."})
                except Exception as e:
                    self.push({"type": "error", "message": f"Post-approval task failed: {e}"})

                self.push({"type": "agent_approved", "agent": agent_name})
                self.push({"type": "log", "message": f"Human approved {agent_name}. Proceeding."})

                completed = list(state.get("completed_agents", []))
                if agent_name not in completed:
                    completed.append(agent_name)
                return {"completed_agents": completed, "human_correction": "", "human_action": {}}

            elif action == "Edit":
                correction = action_data.get("correction", "")
                existing_correction = state.get("human_correction", "")
                new_correction = ((existing_correction + f"\n- {correction}") if existing_correction else correction)
                self.push({"type": "log", "message": f"Human correction applied to {agent_name}. Rerunning..."})
                return {"human_correction": new_correction, "human_action": {}}

            elif action == "Regenerate":
                self.push({"type": "log", "message": f"Regenerating {agent_name} with no changes..."})
                return {"human_correction": "", "human_action": {}}

            elif action == "LoopToDeveloper":
                self.push({"type": "log", "message": f"Looping back from {agent_name} to Developer to fix QA test failures..."})
                qa_output = state.get("agent_outputs", {}).get(agent_name, {})
                exec_results = qa_output.get("execution_results", {})
                failed = exec_results.get("failed", 0)
                log_out = exec_results.get("log", "No log provided.")
                bug_report = json.dumps(qa_output.get("bug_report", []), indent=2)

                auto_correction = (
                    f"AUTOMATED FEEDBACK FROM QA:\n"
                    f"Tests failed: {failed}\n"
                    f"Bug Reports:\n{bug_report}\n"
                    f"Execution Log:\n{log_out}\n"
                    f"Please update your output to resolve these issues."
                )

                completed = list(state.get("completed_agents", []))
                for a in ["Developer", "Environment", "QA"]:
                    if a in completed:
                        completed.remove(a)

                return {
                    "current_agent": "Developer",
                    "human_correction": auto_correction,
                    "human_action": {},
                    "completed_agents": completed
                }

            return {}

        # 5. Conditional routing after gate
        def route_after_gate(state: AriaState):
            agent_name = state.get("current_agent")
            completed = state.get("completed_agents", [])
            if agent_name in completed:
                required = state.get("agents_required", [])
                if len(completed) < len(required):
                    return "set_next_agent"
                else:
                    return "end"
            else:
                return "agent_node"

        # Build Graph
        workflow = StateGraph(AriaState)
        workflow.add_node("set_next_agent", set_next_agent)
        workflow.add_node("agent_node", agent_node)
        workflow.add_node("human_gate_node", human_gate_node)
        workflow.add_node("process_gate_action", process_gate_action)
        workflow.set_entry_point("set_next_agent")
        workflow.add_edge("set_next_agent", "agent_node")
        workflow.add_edge("agent_node", "human_gate_node")
        workflow.add_edge("human_gate_node", "process_gate_action")
        workflow.add_conditional_edges(
            "process_gate_action",
            route_after_gate,
            {"set_next_agent": "set_next_agent", "end": END, "agent_node": "agent_node"}
        )

        # SqliteSaver persists checkpoints to disk — survives backend restarts
        conn = sqlite3.connect(_CHECKPOINT_DB, check_same_thread=False)
        checkpointer = SqliteSaver(conn)
        checkpointer.setup() # ensure tables exist
        
        self.graph = workflow.compile(checkpointer=checkpointer, interrupt_before=["human_gate_node"])
        return self.graph

    def _poll_loop(self, config: dict):
        """Shared polling loop: blocks on human gates, drives graph to completion."""
        while True:
            state = self.graph.get_state(config)
            if not state.next:
                self.push({"type": "log", "message": "All agents completed successfully via LangGraph."})
                break

            if "human_gate_node" in state.next:
                current_state = state.values
                agent_name = current_state.get("current_agent")
                self.push({"type": "gate_required", "agent": agent_name})

                response = self.hitl_q.get()
                action = response.get("action", "")

                if action == "Quit":
                    self.push({"type": "log", "message": "User quit. Progress saved in LangGraph checkpoints."})
                    return

                self.graph.update_state(config, {"human_action": response})

                for event in self.graph.stream(None, config):
                    pass

    def run_graph(self, initial_state: dict, thread_id: str = "aria_run_001"):
        """Start a fresh pipeline run with a new thread_id."""
        self.build_graph()
        config = {"configurable": {"thread_id": thread_id}}

        for event in self.graph.stream(initial_state, config):
            pass

        self._poll_loop(config)

    def resume_graph(self, thread_id: str, from_agent: str = None):
        """
        Resume a checkpointed run without re-running preceding agents.

        Args:
            thread_id:  The UUID of the run to resume (sent as pipeline_started event).
            from_agent: If provided, rewind completed_agents so the pipeline
                        re-starts from this agent.  Agents BEFORE it are untouched.
        """
        if self.graph is None:
            self.build_graph()

        config = {"configurable": {"thread_id": thread_id}}

        if from_agent:
            state = self.graph.get_state(config)
            if state and state.values:
                required = state.values.get("agents_required", [])
                completed = list(state.values.get("completed_agents", []))
                if from_agent in required:
                    cutoff = required.index(from_agent)
                    # Keep only agents that appear before from_agent
                    completed = [a for a in completed if a in required and required.index(a) < cutoff]
                    self.graph.update_state(config, {
                        "completed_agents": completed,
                        "current_agent": from_agent,
                        "human_correction": "",
                        "human_action": {},
                    })
                    self.push({"type": "log", "message": f"[Resume] Rewound to {from_agent}. Agents before it are untouched — no token spend."})

        # stream(None) = continue from checkpoint, not from scratch
        for event in self.graph.stream(None, config):
            pass

        self._poll_loop(config)

"""
core/langgraph_runner.py
LangGraph-based stateful agent runner for ARIA.
Replaces the linear ws_agent_runner.py loop.
"""

import importlib
import json
import operator
from typing import TypedDict, Annotated, Any, Dict, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

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
        
    def _make_summary(self, agent_name: str, data: dict) -> str:
        if not isinstance(data, dict): return f"{agent_name} output received."
        top_keys = list(data.keys())[:3]
        return f"{agent_name} produced: {', '.join(top_keys)}."

    def build_graph(self):
        # 1. Routing node: Sets current_agent based on completion status
        def set_next_agent(state: AriaState):
            completed = state.get("completed_agents", [])
            required = state.get("agents_required", [])
            # Find the first required agent that is not yet completed
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

            # Supervisor quality check
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

        # 3. Human Gate (Interrupt) Node
        def human_gate_node(state: AriaState):
            # We don't need to do anything here. LangGraph will interrupt BEFORE executing this.
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
                
                # Extract execution results if available, else just a general message
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

        # 5. Conditional Routing logic
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
                # If not completed, it means the human hit Edit or Regenerate.
                # So we must route back to agent_node to re-run.
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
            {
                "set_next_agent": "set_next_agent",
                "end": END,
                "agent_node": "agent_node"
            }
        )
        
        # We need a memory saver to checkpoint and pause state
        checkpointer = MemorySaver()
        return workflow.compile(checkpointer=checkpointer, interrupt_before=["human_gate_node"])

    def run_graph(self, initial_state: dict):
        graph = self.build_graph()
        # Create a thread ID for statefulness
        config = {"configurable": {"thread_id": "aria_run_001"}}
        
        # 1. Start or Resume the graph
        for event in graph.stream(initial_state, config):
            pass
            
        # 2. Polling loop for interruptions
        while True:
            state = graph.get_state(config)
            if not state.next:
                # Graph fully completed
                self.push({"type": "log", "message": "All agents completed successfully via LangGraph."})
                break
                
            if "human_gate_node" in state.next:
                current_state = state.values
                agent_name = current_state.get("current_agent")
                self.push({"type": "gate_required", "agent": agent_name})
                
                # Block for human response over WebSocket queue
                response = self.hitl_q.get()
                action = response.get("action", "")
                
                if action == "Quit":
                    self.push({"type": "log", "message": "User quit. Progress saved in LangGraph checkpoints."})
                    return
                
                # Inject human decision into state
                graph.update_state(config, {"human_action": response})
                
                # Resume execution
                for event in graph.stream(None, config):
                    pass

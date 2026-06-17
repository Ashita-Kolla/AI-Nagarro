import os
import json
from .llm_utils import call_llm, parse_json_from_llm
from .agent_registry import resolve_execution_queue

class Supervisor:
    def __init__(self, prompts_dir="prompts"):
        self.prompts_dir = prompts_dir
        
    def determine_routing(self, brief):
        """
        Reads the brief, invokes the supervisor prompt,
        and returns the parsed JSON output.
        """
        prompt_path = os.path.join(self.prompts_dir, "step_01_supervisor.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        prompt = template.replace("{USER_BRIEF}", brief)
        
        print("Supervisor is evaluating the project brief...")
        response_text = call_llm(prompt)
        parsed = parse_json_from_llm(response_text)
        
        if not parsed:
            print("Error: Supervisor failed to return valid JSON.")
            return None
            
        return parsed
        
    def build_execution_queue(self, required_agents):
        """Resolves dependencies and returns an ordered list of agents."""
        return resolve_execution_queue(required_agents)
        
    def check_quality(self, agent_name, agent_output_data, context_manager):
        """
        Evaluates the output of an agent.
        Prints a warning if confidence < 50.
        """
        prompt_path = os.path.join(self.prompts_dir, "supervisor_quality_check.md")
        if not os.path.exists(prompt_path):
            return
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        # Convert output to string
        agent_output_str = json.dumps(agent_output_data, indent=2) if isinstance(agent_output_data, dict) else str(agent_output_data)
        context_str = context_manager.get_context_string()
        
        prompt = template.replace("{AGENT_NAME}", agent_name)
        prompt = prompt.replace("{CONTEXT}", context_str)
        prompt = prompt.replace("{AGENT_OUTPUT}", agent_output_str)
        
        print(f"\nSupervisor is performing a quality check on {agent_name}'s output...")
        response_text = call_llm(prompt)
        parsed = parse_json_from_llm(response_text)
        
        if parsed:
            score = parsed.get("confidence_score", 100)
            reason = parsed.get("confidence_reasoning", "")
            if score < 50:
                print(f"\n[SUPERVISOR WARNING] Confidence Score: {score}/100")
                print(f"Reason: {reason}")
                warnings = parsed.get("warnings", [])
                for w in warnings:
                    print(f" - {w}")
                print("The Human Gate will still run, but you may want to Edit or Regenerate.")
            else:
                print(f"[SUPERVISOR] Quality check passed (Score: {score}/100).")

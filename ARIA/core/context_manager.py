import os
import json

class ContextManager:
    def __init__(self, outputs_dir="outputs"):
        self.outputs_dir = outputs_dir
        self.full_context_file = os.path.join(outputs_dir, "full_project_context.json")
        self.project_context = {}
        
        if not os.path.exists(self.outputs_dir):
            os.makedirs(self.outputs_dir)
            
    def load_existing_context(self):
        """Loads existing context if resuming a session."""
        if os.path.exists(self.full_context_file):
            with open(self.full_context_file, "r", encoding="utf-8") as f:
                self.project_context = json.load(f)
        return self.project_context
        
    def add_output(self, agent_name, data):
        """Appends approved agent output under its key and saves to disk."""
        self.project_context[agent_name] = data
        self.save_context()
        
        # Save individual step output for legacy compatibility or debugging
        step_file = os.path.join(self.outputs_dir, f"{agent_name}.json")
        with open(step_file, "w", encoding="utf-8") as f:
            json.dump({"step": agent_name, "content": data}, f, indent=2, ensure_ascii=False)
            
    def get_context(self):
        """Returns the full project context as a dictionary."""
        return self.project_context
        
    def get_context_string(self):
        """Returns the context formatted as a string for injection into prompts."""
        combined = ""
        for agent, data in self.project_context.items():
            if agent == "USER_BRIEF":
                continue
            # Pretty-print JSON
            data_str = json.dumps(data, indent=2, ensure_ascii=False) if isinstance(data, dict) else str(data)
            combined += f"\n--- {agent} ---\n{data_str}\n"
        return combined

    def save_context(self):
        with open(self.full_context_file, "w", encoding="utf-8") as f:
            json.dump(self.project_context, f, indent=2, ensure_ascii=False)

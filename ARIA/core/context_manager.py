import os
import json
from .context_compressor import compress, summary_to_str, estimate_tokens

# Threshold in chars above which we compress an agent's output on save
COMPRESS_THRESHOLD_CHARS = 2000

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
        """
        Appends approved agent output under its key and saves to disk.
        If the output is large, also stores a compressed summary under
        f"{agent_name}_summary" for downstream agents to consume.
        """
        # Always store the full raw output
        self.project_context[agent_name] = data
        
        # Compress-on-save: create a summary when the output is large
        data_str = json.dumps(data, ensure_ascii=False) if isinstance(data, dict) else str(data)
        if len(data_str) > COMPRESS_THRESHOLD_CHARS:
            summary = compress(agent_name, data)
            self.project_context[f"{agent_name}_summary"] = summary
            summary_chars = len(json.dumps(summary, ensure_ascii=False))
            reduction_pct = round((1 - summary_chars / len(data_str)) * 100)
            print(
                f"[ContextCompressor] {agent_name}: "
                f"{len(data_str):,} chars → {summary_chars:,} chars "
                f"({reduction_pct}% reduction) | "
                f"~{estimate_tokens(data_str):,} → ~{estimate_tokens(json.dumps(summary)):,} tokens"
            )
        
        self.save_context()
        
        # Create agent-specific output directory
        agent_dir = os.path.join(self.outputs_dir, agent_name)
        os.makedirs(agent_dir, exist_ok=True)
        
        # Save individual step output for legacy compatibility or debugging
        step_file = os.path.join(agent_dir, f"{agent_name}.json")
        with open(step_file, "w", encoding="utf-8") as f:
            json.dump({"step": agent_name, "content": data}, f, indent=2, ensure_ascii=False)
            
    def get_context(self):
        """Returns the full project context as a dictionary."""
        return self.project_context

    def get_summary(self, agent_name: str) -> dict:
        """
        Returns the compressed summary for an agent if one exists,
        otherwise falls back to the full raw output.
        This is what downstream agents should use to build prompts.
        """
        summary_key = f"{agent_name}_summary"
        if summary_key in self.project_context:
            return self.project_context[summary_key]
        # No summary means output was small enough to use as-is
        return self.project_context.get(agent_name, {})
        
    def get_context_string(self):
        """
        Returns context formatted as a string for prompt injection.
        Prefers compressed summaries for large agents to keep prompts small.
        """
        combined = ""
        # Iterate only over real agent outputs (not summary keys or USER_BRIEF)
        for agent, data in self.project_context.items():
            if agent == "USER_BRIEF" or agent.endswith("_summary"):
                continue
            # Use summary if available, otherwise use raw data
            summary_key = f"{agent}_summary"
            if summary_key in self.project_context:
                combined += summary_to_str(agent, self.project_context[summary_key])
            else:
                data_str = json.dumps(data, indent=2, ensure_ascii=False) if isinstance(data, dict) else str(data)
                combined += f"\n--- {agent} ---\n{data_str}\n"
        return combined

    def save_context(self):
        with open(self.full_context_file, "w", encoding="utf-8") as f:
            json.dump(self.project_context, f, indent=2, ensure_ascii=False)

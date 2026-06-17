import os
from core.llm_utils import call_llm, parse_json_from_llm
from core.agent_registry import AGENT_REGISTRY
from core.utils import build_prompt

def run(context_manager, correction=None):
    agent_name = "Optimisation"
    prompt_file = AGENT_REGISTRY[agent_name]["prompt_file"]
    prompt_path = os.path.join("prompts", prompt_file)
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()
        
    prompt = build_prompt(template, context_manager)
    
    if correction:
        prompt += f"\n\nHUMAN CORRECTION: {correction}"
        
    response_text = call_llm(prompt)
    return parse_json_from_llm(response_text)

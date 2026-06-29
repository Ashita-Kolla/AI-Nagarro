import re
import json

from core.context_compressor import compress_context_for_agent

def build_prompt(template, context_manager, agent_name=None):
    prompt = template
    raw_context = context_manager.get_context()
    context = compress_context_for_agent(agent_name, raw_context) if agent_name else raw_context
    
    # Handle USER_BRIEF
    if "{USER_BRIEF}" in prompt and "USER_BRIEF" in context:
        prompt = prompt.replace("{USER_BRIEF}", str(context["USER_BRIEF"]))

    # Handle all "ALL APPROVED OUTPUTS" style placeholders (various phrasings used in .md files)
    all_outputs_str = context_manager.get_context_string()
    for placeholder in [
        "{ALL APPROVED OUTPUTS}",
        "{PASTE ALL APPROVED OUTPUTS}",
        "{ALL_APPROVED_OUTPUTS}",
    ]:
        if placeholder in prompt:
            prompt = prompt.replace(placeholder, all_outputs_str)

    placeholders = set(re.findall(r"\{([A-Za-z0-9_ ]+)\}", prompt))
    for p in placeholders:
        # Check if the placeholder matches an agent's output in context
        if p in context:
            prompt = prompt.replace("{" + p + "}", json.dumps(context[p], indent=2, ensure_ascii=False))
        # Legacy support: handle "PASTE STEP X" placeholders by injecting full context as fallback
        elif "PASTE" in p.upper() or "STEP" in p.upper():
            prompt = prompt.replace("{" + p + "}", all_outputs_str)

    return prompt

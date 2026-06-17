import re
import json

def build_prompt(template, context_manager):
    prompt = template
    context = context_manager.get_context()
    
    # Handle USER_BRIEF
    if "{USER_BRIEF}" in prompt and "USER_BRIEF" in context:
        prompt = prompt.replace("{USER_BRIEF}", str(context["USER_BRIEF"]))
        
    # Handle ALL APPROVED OUTPUTS if present
    if "{ALL APPROVED OUTPUTS}" in prompt:
        prompt = prompt.replace("{ALL APPROVED OUTPUTS}", context_manager.get_context_string())
        
    placeholders = set(re.findall(r"\{([A-Za-z0-9_ ]+)\}", prompt))
    for p in placeholders:
        # Check if the placeholder matches an agent's output in context
        if p in context:
            prompt = prompt.replace("{" + p + "}", json.dumps(context[p], indent=2, ensure_ascii=False))
        # Legacy support
        elif "STEP 0" in p.upper() or "STEP " in p.upper():
            # If the placeholder is trying to access a step, let's map it roughly to context
            # (In the new framework, we prefer directly passing context keys, but this adds resilience)
            pass
            
    return prompt

import os
import json
from core.llm_utils import call_llm, parse_json_from_llm
from core.agent_registry import AGENT_REGISTRY
from core.utils import build_prompt

def run(context_manager, correction=None):
    agent_name = "Optimisation"
    prompt_file = AGENT_REGISTRY[agent_name]["prompt_file"]
    prompt_path = os.path.join("prompts", prompt_file)
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()
        
    prompt = build_prompt(template, context_manager, agent_name=agent_name)
    
    if correction:
        prompt += f"\n\nHUMAN CORRECTION: {correction}"
        
    response_text = call_llm(prompt, agent_name=agent_name)
    return parse_json_from_llm(response_text)

def post_approval(data: dict, context_manager) -> list:
    out_dir = os.path.join("outputs", "Optimisation")
    os.makedirs(out_dir, exist_ok=True)
    generated_files = []

    json_path = os.path.join(out_dir, "optimisation_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    generated_files.append(json_path)

    # Write a readable markdown summary
    md_path = os.path.join(out_dir, "Optimisation_Report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Optimisation Report\n\n")
        f.write(f"**Estimated Effort Reduction:** {data.get('estimated_effort_reduction', 'N/A')}\n\n")

        f.write("## Duplicate / Overlapping Stories\n")
        for item in data.get("duplicate_stories", []):
            ids = ", ".join(item.get("story_ids", []))
            f.write(f"- **IDs:** {ids} — {item.get('reason', '')}\n")
        if not data.get("duplicate_stories"):
            f.write("- None found.\n")

        f.write("\n## Parallelisation Opportunities\n")
        for item in data.get("parallelisation_opportunities", []):
            tasks = ", ".join(item.get("tasks", []))
            f.write(f"- **Tasks:** {tasks} — {item.get('reason', '')}\n")
        if not data.get("parallelisation_opportunities"):
            f.write("- None found.\n")

        f.write("\n## Automation Opportunities\n")
        for item in data.get("automation_opportunities", []):
            f.write(f"- **{item.get('area', '')}:** {item.get('suggestion', '')}\n")
        if not data.get("automation_opportunities"):
            f.write("- None found.\n")

        summary = data.get("before_after_summary", {})
        f.write(f"\n## Before\n{summary.get('before', 'N/A')}\n")
        f.write(f"\n## After\n{summary.get('after', 'N/A')}\n")

    generated_files.append(md_path)
    print(f"Optimisation artifacts exported to {out_dir}.")
    return generated_files


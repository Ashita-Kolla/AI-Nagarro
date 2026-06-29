import os
import json
from core.llm_utils import call_llm, parse_json_from_llm
from core.context_compressor import compress_context_for_agent

def build_prompt(context_manager, correction: str = None) -> str:
    raw_context = context_manager.get_context()
    context = compress_context_for_agent("Planner", raw_context)
    
    ba_output = context.get("BA", {})
    architect_output = context.get("Architect", {})

    import json as _json
    ba_str = _json.dumps(ba_output, indent=2)
    arch_str = _json.dumps(architect_output, indent=2)
    
    tech_stack = architect_output.get("technology_stack", {}) if architect_output else {}
    frontend = tech_stack.get("frontend", "Not specified")
    backend = tech_stack.get("backend", "Not specified")
    database = tech_stack.get("database", "Not specified")
    infra = tech_stack.get("infrastructure", "Not specified")

    prompt = f"""You are the Developer Agent (Planner Phase) for ARIA, a multi-agent SDLC pipeline system.

You receive approved BA and Architect outputs and produce a complete development plan.

APPROVED BA OUTPUT:
{ba_str}

APPROVED ARCHITECT OUTPUT:
{arch_str}

---

YOUR JOB — PART 1: DEVELOPMENT PLANNING

Produce a complete breakdown of development work.

1. EPICS
   Group related user stories into epics.
   Each epic is a major feature area.
   Create the minimum number of epics necessary to complete the project. Do not overcomplicate or split simple tasks unnecessarily.
   Format: EP-001: [Epic name]

2. TASKS
   Break each epic into specific development tasks.
   Each task must be:
   - Specific enough for a developer to start immediately
   - Scoped to 1-3 days of work maximum
   - Linked to a user story ID where applicable
   - Assigned a story point value using Fibonacci only:
     1, 2, 3, 5, 8, 13
     1 = trivial, 2 = simple, 3 = small, 5 = medium,
     8 = large, 13 = very large or high uncertainty
   - Assigned a complexity: low / medium / high
   - Given explicit dependencies (which task IDs must complete before this one can start)

3. TECHNICAL NOTES
   For each epic, write technical implementation notes:
   - Which part of the tech stack handles this epic
   - Key libraries or packages needed
   - Any architectural patterns to follow
   - Any risks or complexity to flag

4. TOTAL SUMMARY
   - Total story points across all tasks
   - Estimated developer-days (assume 5 points per day)
   - Recommended team size
   - Suggested sprint breakdown (2-week sprints)

TECH STACK IN USE (from Architect — use this exactly):
Frontend: {frontend}
Backend: {backend}
Database: {database}
Infra: {infra}

CRITICAL RULES:
- Tasks must reference the approved tech stack. Do not suggest technologies not in the stack.
- Every user story from the BA output must be covered by at least one task.
- Do not write generic tasks like "implement feature". Every task must name the specific feature, endpoint, component, or function being built.
- Story points must be Fibonacci only. No 4s, 6s, 7s.
- Output ONLY raw valid JSON. No markdown. No backticks. No prose before or after.
"""
    if correction:
        prompt += f"\n\n=== HUMAN CORRECTION ===\n{correction}\n"

    prompt += """
OUTPUT FORMAT:
{
  "epics": [
    {
      "id": "EP-001",
      "title": "",
      "linked_stories": ["US-001", "US-002"],
      "technical_notes": "",
      "tasks": [
        {
          "id": "T-001",
          "title": "",
          "description": "",
          "linked_story": "US-001",
          "story_points": 0,
          "complexity": "low/medium/high",
          "depends_on": [],
          "tech_area": "frontend/backend/database/infra"
        }
      ]
    }
  ],
  "summary": {
    "total_story_points": 0,
    "estimated_developer_days": 0,
    "recommended_team_size": 0,
    "sprint_breakdown": [
      {
        "sprint": 1,
        "epics": [],
        "story_points": 0,
        "focus": ""
      }
    ]
  },
  "confidence_score": 0,
  "confidence_reasoning": ""
}
"""
    return prompt

def run(context_manager, correction: str = None) -> dict:
    context = context_manager.get_context()
    
    if not context.get("BA"):
        print("[Planner Agent Error] Cannot find BA output. Ensure BA agent has been approved before running the Planner agent.")
        return {}
    if not context.get("Architect"):
        print("[Planner Agent Error] Cannot find Architect output. Ensure Architect agent has been approved before running the Planner agent.")
        return {}

    try:
        prompt = build_prompt(context_manager, correction)
        response_text = call_llm(prompt, agent_name="Planner")
        parsed_data = parse_json_from_llm(response_text)

        if not parsed_data:
            print("Planner Agent Error: Failed to parse valid JSON from LLM.")
            return {}

        return parsed_data
    except Exception as e:
        print(f"Planner Agent Error: {str(e)}")
        return {}

def post_approval(data: dict, context_manager) -> list:
    out_dir = os.path.join("outputs", "Planner")
    os.makedirs(out_dir, exist_ok=True)
    
    generated_files = []
    
    # Write full JSON for downstream use
    full_json_path = os.path.join(out_dir, "development_plan.json")
    with open(full_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    generated_files.append(full_json_path)
    
    print(f"Planner artifacts exported to {out_dir}.")
    return generated_files

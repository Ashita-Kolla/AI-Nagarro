import os
import json
from core.llm_utils import call_llm, parse_json_from_llm

def build_prompt(context_manager, correction: str = None) -> str:
    context = context_manager.get_context()
    
    # Extract upstream outputs
    user_brief = context.get("USER_BRIEF", "")
    supervisor_output = context.get("Supervisor", {})
    ba_output = context.get("BA", {})
    architect_output = context.get("Architect", {})
    developer_output = context.get("Developer", {})
    qa_output = context.get("QA", {})
    devops_output = context.get("DevOps", {})

    prompt = f"""You are the PM Agent for ARIA, a multi-agent SDLC system.

You are responsible for final validation and delivery decisioning.
You DO NOT modify system design. You DO NOT generate code. You DO NOT generate infrastructure.
You ONLY analyze, validate, and decide.

=== CONTEXT ===
USER BRIEF:
{user_brief}

SUPERVISOR OUTPUT:
{json.dumps(supervisor_output, indent=2)}

BA OUTPUT:
{str(ba_output)[:1000]}

ARCHITECT OUTPUT:
{str(architect_output)[:1000]}

DEVELOPER OUTPUT:
{str(developer_output)[:1000]}

QA OUTPUT:
{str(qa_output)[:1000]}

DEVOPS OUTPUT:
{str(devops_output)[:1000]}

=== YOUR JOB ===
Perform full project governance.
1. Determine project status: READY / NEEDS_FIXES / BLOCKED
2. Generate PROJECT SUMMARY JSON: Must include complete system overview.
3. Perform alignment validation: Check consistency across all stages.
4. Identify risks and gaps: Be honest and explicit.
5. Generate GANTT CHART: Mermaid format and JSON task structure.
6. Generate JIRA CSV EXPORT: Must represent SDLC tasks clearly.
7. Provide final delivery recommendation.
"""

    if correction:
        prompt += f"\n\n=== HUMAN CORRECTION ===\nPlease apply the following corrections to your previous output:\n{correction}\n"

    prompt += """
=== OUTPUT REQUIREMENTS ===
You must return strictly valid JSON matching exactly this schema, with no additional markdown, text, or explanations outside the JSON:

{
  "project_status": "READY | NEEDS_FIXES | BLOCKED",
  "project_summary": {
    "project_name": "",
    "objective": "",
    "modules_built": [],
    "completion_status": "",
    "key_features_delivered": [],
    "unresolved_gaps": [],
    "technical_stack": [],
    "deployment_readiness": "",
    "risk_level": "",
    "confidence_score": 0
  },
  "alignment_check": {
    "ba_match": true,
    "architecture_match": true,
    "development_match": true,
    "qa_passed": true,
    "devops_ready": true
  },
  "risk_analysis": [
    "Risk 1",
    "Risk 2"
  ],
  "gantt_mermaid": "",
  "gantt_json": {
    "tasks": []
  },
  "jira_csv": "",
  "delivery_recommendation": "",
  "confidence_score": 0,
  "confidence_reasoning": ""
}
"""
    return prompt

def run(context_manager, correction: str = None) -> dict:
    try:
        prompt = build_prompt(context_manager, correction)
        response_text = call_llm(prompt, agent_name="PM")
        parsed_data = parse_json_from_llm(response_text)

        if not parsed_data:
            print("PM Agent Error: Failed to parse valid JSON from LLM.")
            return {}

        return parsed_data
    except Exception as e:
        print(f"PM Agent Error: {str(e)}")
        return {}

def post_approval(data: dict, context_manager) -> list:
    """
    Hook called by the LangGraph runner after human approval.
    Exports the PM artifacts to the file system.
    """
    out_dir = os.path.join("outputs", "PM")
    os.makedirs(out_dir, exist_ok=True)
    
    generated_files = []

    # 1. Save Full Output JSON
    full_json_path = os.path.join(out_dir, "PM_Report.json")
    with open(full_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    generated_files.append(full_json_path)

    # 2. Save Project Summary isolated
    summary = data.get("project_summary")
    if summary:
        summary_path = os.path.join(out_dir, "Project_Summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        generated_files.append(summary_path)

    # 3. Save Gantt Mermaid
    mermaid_raw = data.get("gantt_mermaid", "")
    if mermaid_raw:
        # Clean mermaid code if wrapped in markdown
        mermaid_clean = mermaid_raw.strip()
        if mermaid_clean.startswith("```mermaid"):
            mermaid_clean = mermaid_clean[10:]
        elif mermaid_clean.startswith("```"):
            mermaid_clean = mermaid_clean[3:]
        if mermaid_clean.endswith("```"):
            mermaid_clean = mermaid_clean[:-3]
            
        mmd_path = os.path.join(out_dir, "project_timeline.mmd")
        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(mermaid_clean.strip())
        generated_files.append(mmd_path)

    # 4. Save Jira CSV
    jira_csv = data.get("jira_csv", "")
    if jira_csv:
        csv_path = os.path.join(out_dir, "Jira_Import.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(jira_csv)
        generated_files.append(csv_path)

    print(f"PM artifacts exported to {out_dir}.")
    return generated_files

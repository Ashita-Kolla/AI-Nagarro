import os
import json
from core.llm_utils import call_llm, parse_json_from_llm

def build_prompt(context_manager, correction: str = None) -> str:
    context = context_manager.get_context()
    import json as _json
    
    # Extract upstream outputs via summaries
    user_brief = context.get("USER_BRIEF", "")
    supervisor_output = context_manager.get_summary("Supervisor")
    architect_output = context_manager.get_summary("Architect")
    developer_output = context_manager.get_summary("Developer")
    qa_output = context_manager.get_summary("QA")

    prompt = f"""You are the DevOps Agent for the ARIA multi-agent SDLC system.

Your job is to turn the completed software (architecture + code + QA results) into deployment-ready infrastructure artifacts.
You are NOT an orchestrator. You are NOT a code generator. You are NOT an architecture modifier.

=== CONTEXT ===
User Brief: {user_brief}
Supervisor Strategy (summary): {_json.dumps(supervisor_output, indent=2)}
Architect Design (summary): {_json.dumps(architect_output, indent=2)}
Developer Output (summary): {_json.dumps(developer_output, indent=2)}
QA Results (summary): {_json.dumps(qa_output, indent=2)}

=== RESPONSIBILITIES ===
1. Generate Docker configuration (Dockerfile and docker-compose.yml if multi-service)
2. Generate CI/CD pipeline (GitHub Actions .github/workflows/ci.yml)
3. Generate environment configuration (.env.example - NO SECRETS)
4. Define deployment strategy (container / VM / serverless, scaling, runtime constraints)
5. Generate a deployment contract JSON
6. List infrastructure assumptions and limitations
7. Generate a Local Deployment Guide (Markdown). You MUST provide NATIVE run commands (e.g., `python -m uvicorn main:app`, `npm start`) to run the app directly on the host machine without Docker. Native run commands are MANDATORY.
8. Provide a confidence score (0-100) with reasoning
"""

    if correction:
        prompt += f"\n\n=== HUMAN CORRECTION ===\nPlease apply the following corrections to your previous output:\n{correction}\n"

    prompt += """
=== OUTPUT REQUIREMENTS ===
You must return strictly valid JSON matching exactly this schema, with no additional markdown, text, or explanations outside the JSON:

{
  "docker": {
    "dockerfile": "",
    "docker_compose": ""
  },
  "ci_cd": {
    "github_actions": ""
  },
  "environment": {
    "env_example": []
  },
  "deployment_strategy": "",
  "deployment_contract": {
    "entrypoint": "",
    "exposed_ports": [],
    "build_artifacts": [],
    "runtime": "",
    "health_check": ""
  },
  "local_deployment_guide": "# Local Deployment Guide\\n\\nRun `docker-compose up`...",
  "assumptions": [],
  "limitations": [],
  "confidence_score": 0,
  "confidence_reasoning": ""
}
"""
    return prompt

def run(context_manager, correction: str = None) -> dict:
    try:
        prompt = build_prompt(context_manager, correction)
        # Using standard call_llm from core.llm_utils
        response_text = call_llm(prompt, agent_name="DevOps")
        parsed_data = parse_json_from_llm(response_text)

        if not parsed_data:
            print("DevOps Agent Error: Failed to parse valid JSON from LLM.")
            return {}

        return parsed_data
    except Exception as e:
        print(f"DevOps Agent Error: {str(e)}")
        return {}

def post_approval(data: dict, context_manager) -> list:
    """
    Hook called by the LangGraph runner after human approval.
    Exports the DevOps artifacts to the file system.
    """
    out_dir = os.path.join("outputs", "DevOps")
    os.makedirs(out_dir, exist_ok=True)
    
    generated_files = []

    # 1. Save Full JSON
    json_path = os.path.join(out_dir, "devops_strategy.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    generated_files.append(json_path)

    # 2. Dockerfile
    docker_data = data.get("docker", {})
    dockerfile = docker_data.get("dockerfile", "")
    if dockerfile:
        df_path = os.path.join(out_dir, "Dockerfile")
        with open(df_path, "w", encoding="utf-8") as f:
            f.write(dockerfile)
        generated_files.append(df_path)

    # 3. docker-compose.yml
    docker_compose = docker_data.get("docker_compose", "")
    if docker_compose:
        dc_path = os.path.join(out_dir, "docker-compose.yml")
        with open(dc_path, "w", encoding="utf-8") as f:
            f.write(docker_compose)
        generated_files.append(dc_path)

    # 4. GitHub Actions
    ci_cd = data.get("ci_cd", {})
    gh_actions = ci_cd.get("github_actions", "")
    if gh_actions:
        workflows_dir = os.path.join(out_dir, ".github", "workflows")
        os.makedirs(workflows_dir, exist_ok=True)
        ci_path = os.path.join(workflows_dir, "ci.yml")
        with open(ci_path, "w", encoding="utf-8") as f:
            f.write(gh_actions)
        generated_files.append(ci_path)

    # 5. .env.example
    env_data = data.get("environment", {})
    env_example = env_data.get("env_example", [])
    if env_example:
        env_path = os.path.join(out_dir, ".env.example")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("\n".join(env_example) if isinstance(env_example, list) else str(env_example))
        generated_files.append(env_path)

    # 6. Deployment Contract
    contract = data.get("deployment_contract", {})
    if contract:
        contract_path = os.path.join(out_dir, "deployment_contract.json")
        with open(contract_path, "w", encoding="utf-8") as f:
            json.dump(contract, f, indent=2, ensure_ascii=False)
        generated_files.append(contract_path)

    # 7. Local Deployment Guide
    local_guide = data.get("local_deployment_guide", "")
    if local_guide:
        guide_path = os.path.join(out_dir, "LOCAL_DEPLOYMENT.md")
        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(local_guide)
        generated_files.append(guide_path)

    print(f"DevOps artifacts exported to {out_dir}.")
    return generated_files

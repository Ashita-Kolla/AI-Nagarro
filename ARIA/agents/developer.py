import os
import json
from core.llm_utils import call_llm, parse_json_from_llm

def build_prompt(context_manager, correction: str = None) -> str:
    context = context_manager.get_context()
    
    user_brief = context.get("USER_BRIEF", "")
    ba_output = context_manager.get_summary("BA")
    architect_output = context_manager.get_summary("Architect")
    qa_feedback = context_manager.get_summary("QA")

    import json as _json
    prompt = f"""You are the Developer Agent for ARIA.

You are the CORE IMPLEMENTATION ENGINE.
You are a FULL SYSTEM BUILDER responsible for generating a COMPLETE WORKING CODEBASE based on the Architect's design and BA's requirements.

=== CONTEXT ===
USER BRIEF:
{user_brief}

BA REQUIREMENTS (SUMMARY):
{_json.dumps(ba_output, indent=2, ensure_ascii=False)}

ARCHITECTURE DESIGN (SUMMARY):
{_json.dumps(architect_output, indent=2, ensure_ascii=False)}
"""
    
    if qa_feedback:
        import json as _json2
        prompt += f"\nQA FEEDBACK (PREVIOUS RUN):\n{_json2.dumps(qa_feedback, indent=2, ensure_ascii=False)}\nFix ONLY reported issues. Regenerate corrected codebase while preserving structure.\n"

    prompt += """
=== RESPONSIBILITIES & STRICT RULES ===
1. EXTREME SIMPLICITY: You must keep the codebase as simple as humanly possible. Put all backend logic into a single `main.py` file if possible. DO NOT create complex folder structures (like `src/api/`, `src/database/`) unless explicitly requested.
2. NO UNNECESSARY DEPENDENCIES: Do not import complex external libraries (like `bcrypt`, `sqlalchemy`) unless strictly requested. Use simple in-memory dictionaries or standard libraries if a database is requested but no specific DB is mandated.
3. RUNNABLE CODE: The generated code MUST be fully runnable instantly.
4. CORRECT IMPORTS: Ensure all imports match the exact file paths provided in the `file_tree`.
5. PYTHON PACKAGES: If you must create folders, you MUST include `__init__.py` files in any directories that act as Python packages.
6. NO PLACEHOLDERS: Provide complete, working code for the MVP. Do not leave "TODO" or "pass" for critical functionality.
7. Output must be testable, deterministic, and stable.
8. CRITICAL: You are bound by a strict token output limit. You MUST write ONLY the absolute Minimum Viable Product (MVP) files. Keep it concise.
"""

    if correction:
        prompt += f"\n=== HUMAN CORRECTION ===\nPlease apply the following corrections:\n{correction}\n"

    prompt += """
=== OUTPUT REQUIREMENTS ===
You must return strictly valid JSON matching EXACTLY this schema.
Do NOT output any markdown blocks outside the JSON.
The structure shown below is just an EXAMPLE. You must output the CORRECT structure dynamically based on the technology stack chosen.

{
  "project_name": "example_project",
  "language_stack": ["python", "fastapi"],
  "file_tree": [
    "src/",
    "src/__init__.py",
    "src/main.py"
  ],
  "files": [
    {
      "path": "src/__init__.py",
      "content": ""
    },
    {
      "path": "src/main.py",
      "content": "print('Hello World')"
    }
  ],
  "entrypoint": "",
  "dependencies": [],
  "implementation_notes": [
    "Note 1"
  ],
  "coverage_mapping": {
    "requirements_covered": [],
    "missing_requirements": []
  },
  "runtime_assumptions": [
    "Assumption 1"
  ],
  "confidence_score": 0,
  "confidence_reasoning": ""
}
"""
    return prompt

def run(context_manager, correction: str = None) -> dict:
    try:
        prompt = build_prompt(context_manager, correction)
        response_text = call_llm(prompt, agent_name="Developer", max_tokens=8000)
        parsed_data = parse_json_from_llm(response_text)

        if not parsed_data:
            print("Developer Agent Error: Failed to parse valid JSON from LLM.")
            return {}

        return parsed_data
    except Exception as e:
        print(f"Developer Agent Error: {str(e)}")
        return {}

def post_approval(data: dict, context_manager) -> list:
    """
    Exports the Developer artifacts (the full generated codebase) to the file system.
    """
    out_dir = os.path.join("outputs", "Developer")
    codebase_dir = os.path.join(out_dir, "codebase")
    os.makedirs(codebase_dir, exist_ok=True)
    
    generated_files = []

    # 1. Save Full Output JSON for reference
    full_json_path = os.path.join(out_dir, "developer_summary.json")
    with open(full_json_path, "w", encoding="utf-8") as f:
        # Save summary without the massive files array to save space
        summary_data = {k: v for k, v in data.items() if k != "files"}
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    generated_files.append(full_json_path)

    # 2. Extract and physically save the codebase files
    files = data.get("files", [])
    for file_obj in files:
        path = file_obj.get("path", "")
        content = file_obj.get("content", "")
        if path and content:
            # Prevent directory traversal vulnerabilities
            safe_path = os.path.normpath(path).lstrip("\\/")
            if ".." in safe_path:
                continue
                
            full_path = os.path.join(codebase_dir, safe_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            generated_files.append(full_path)

    print(f"Developer artifacts exported to {out_dir}.")
    return generated_files

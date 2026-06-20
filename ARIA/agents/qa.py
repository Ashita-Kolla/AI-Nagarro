import os
import json
import subprocess
from core.llm_utils import call_llm, parse_json_from_llm

def build_prompt(context_manager, correction: str = None) -> str:
    context = context_manager.get_context()
    
    user_brief = context.get("USER_BRIEF", "")
    ba_output = context.get("BA", {})
    architect_output = context.get("Architect", {})
    developer_output = context.get("Developer", {})

    prompt = f"""You are the QA Agent for ARIA.

You are a FIRST-CLASS agent responsible for VALIDATION and GATE DECISIONING.
Your job is to generate real Playwright test cases from the BA and Developer output.

=== CONTEXT ===
USER BRIEF: {user_brief}
BA REQUIREMENTS: {str(ba_output)[:1500]}
ARCHITECTURE: {str(architect_output)[:1500]}
DEVELOPER CODE SUMMARY: {str(developer_output)[:1500]}

=== RESPONSIBILITIES ===
1. Generate test cases from BA + Developer output.
2. Convert test cases into Playwright test files (.spec.ts).
3. Validate requirement coverage (every feature must be tested).
4. Provide a bug report identifying any obvious logical flaws in the developer output.

"""

    if correction:
        prompt += f"\n\n=== HUMAN CORRECTION ===\nPlease apply the following corrections:\n{correction}\n"

    prompt += """
=== OUTPUT REQUIREMENTS ===
You must return strictly valid JSON matching EXACTLY this schema. 
Provide the actual Playwright TypeScript code in the `test_suite[].code` field.

{
  "status": "PASS | FAIL",
  "test_suite": [
    {
      "file": "login.spec.ts",
      "code": "import { test, expect } from '@playwright/test';\\n\\ntest('example', async ({ page }) => { ... });"
    }
  ],
  "execution_results": {
    "total_tests": 0,
    "passed": 0,
    "failed": 0
  },
  "bug_report": [
    {
      "severity": "CRITICAL | MAJOR | MINOR",
      "issue": "",
      "reproduction": "",
      "suggested_fix": ""
    }
  ],
  "requirement_coverage": {
    "total": 0,
    "covered": 0,
    "missing": []
  },
  "artifacts_saved_to": "outputs/QA/test_results.json",
  "confidence_score": 0,
  "confidence_reasoning": ""
}
"""
    return prompt

def execute_playwright_tests(test_suite: list) -> dict:
    """
    Attempts to physically execute the generated Playwright tests.
    Fails safely if the environment is missing.
    """
    qa_dir = os.path.join("outputs", "QA", "tests")
    os.makedirs(qa_dir, exist_ok=True)
    
    # 1. Write tests to disk
    for test in test_suite:
        filename = test.get("file", "test.spec.ts")
        code = test.get("code", "")
        if filename and code:
            with open(os.path.join(qa_dir, filename), "w", encoding="utf-8") as f:
                f.write(code)
                
    if not test_suite:
        return {"total_tests": 0, "passed": 0, "failed": 0, "log": "No tests generated."}
            
    # 2. Try to run npx playwright test
    try:
        # Running in the tests directory
        print("QA Agent: Executing Playwright tests locally...")
        result = subprocess.run(
            ["npx", "playwright", "test"], 
            cwd=qa_dir, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        passed = (result.returncode == 0)
        log_output = result.stdout + "\n" + result.stderr
        
        # If npx runs but playwright isn't initialized, it usually returns an error code
        if "No tests found" in log_output or "playwright" not in log_output.lower():
            passed = False
            
        return {
            "total_tests": len(test_suite),
            "passed": len(test_suite) if passed else 0,
            "failed": 0 if passed else len(test_suite),
            "log": log_output
        }
    except Exception as e:
        # Fallback if npx or node is completely missing
        return {
            "total_tests": len(test_suite),
            "passed": 0,
            "failed": len(test_suite),
            "log": f"Execution Environment Error: {str(e)}\n\n(Playwright/Node.js might not be installed or configured in this environment. Tests were saved to disk but could not run.)"
        }

def run(context_manager, correction: str = None) -> dict:
    try:
        # 1. Generate Tests via LLM
        prompt = build_prompt(context_manager, correction)
        response_text = call_llm(prompt, agent_name="QA")
        parsed_data = parse_json_from_llm(response_text)

        if not parsed_data:
            print("QA Agent Error: Failed to parse valid JSON from LLM.")
            return {}

        # 2. Extract tests but do NOT execute them automatically.
        # Execution is triggered by the human via "Test Run Scripts" in the frontend.
        test_suite = parsed_data.get("test_suite", [])
        
        parsed_data["execution_results"] = {
            "total_tests": len(test_suite),
            "passed": 0,
            "failed": 0,
            "status": "PENDING_APPROVAL",
            "log": "Waiting for human test run or approval."
        }
        
        return parsed_data
    except Exception as e:
        print(f"QA Agent Error: {str(e)}")
        return {}

def post_approval(data: dict, context_manager) -> list:
    """
    Exports the QA artifacts (test cases and results) to the file system.
    Injects human-edited test suites from disk if available.
    """
    out_dir = os.path.join("outputs", "QA")
    qa_tests_dir = os.path.join(out_dir, "tests")
    os.makedirs(qa_tests_dir, exist_ok=True)
    
    generated_files = []
    
    # 1. Update data with human edits from disk (if the WS handler saved them)
    test_suite = data.get("test_suite", [])
    for test in test_suite:
        filename = test.get("file")
        if filename:
            file_path = os.path.join(qa_tests_dir, filename)
            if os.path.exists(file_path):
                # If human edited it and it was saved to disk
                with open(file_path, "r", encoding="utf-8") as f:
                    test["code"] = f.read()
                generated_files.append(file_path)
            else:
                # If no human edit, write the LLM's original code to disk
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(test.get("code", ""))
                generated_files.append(file_path)

    # Inject the updated test_suite into context so downstream agents see edits
    context_manager.add_output("QA", data)

    # 2. Save Full Output JSON
    full_json_path = os.path.join(out_dir, "test_results.json")
    with open(full_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    generated_files.append(full_json_path)

    print(f"QA artifacts exported to {out_dir}.")
    return generated_files

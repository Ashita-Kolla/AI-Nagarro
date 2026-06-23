import os
import json
import subprocess
import sys
from core.llm_utils import call_llm, parse_json_from_llm


# ── Helpers ───────────────────────────────────────────────────────────────────

def read_developer_summary() -> dict:
    """Read developer_summary.json to get the real language stack and file tree."""
    path = os.path.abspath(os.path.join("outputs", "Developer", "developer_summary.json"))
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def scan_codebase_with_contents(max_file_bytes: int = 1200) -> tuple[str, str]:
    """
    Walks Developer/codebase, returns:
      - file_tree: sorted list of relative paths (one per line)
      - file_contents: concatenated snippet of each file (for LLM context)
    Skips __pycache__, .pyc, hidden dirs, and the tests/ folder itself.
    """
    codebase_root = os.path.abspath(os.path.join("outputs", "Developer", "codebase"))
    if not os.path.isdir(codebase_root):
        return "(Developer codebase not yet generated)", ""

    tree_lines = []
    content_snippets = []
    skip_dirs = {"__pycache__", "tests", "node_modules", ".git"}

    for dirpath, dirnames, filenames in os.walk(codebase_root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in skip_dirs]
        rel_dir = os.path.relpath(dirpath, codebase_root)

        for fname in filenames:
            if fname.endswith((".pyc", ".png", ".jpg", ".ico", ".gz")):
                continue
            rel_path = fname if rel_dir == "." else f"{rel_dir.replace(os.sep, '/')}/{fname}"
            tree_lines.append(rel_path)

            full_path = os.path.join(dirpath, fname)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(max_file_bytes)
                if len(content) == max_file_bytes:
                    content += "\n... (truncated)"
                content_snippets.append(f"\n### {rel_path} ###\n{content}")
            except Exception:
                pass

    file_tree = "\n".join(sorted(tree_lines)) if tree_lines else "(no files found)"
    file_contents = "\n".join(content_snippets)
    return file_tree, file_contents


def read_environment_deps() -> dict:
    """Read environment_setup.json to get the list of install commands."""
    path = os.path.abspath(os.path.join("outputs", "Environment", "environment_setup.json"))
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def install_python_deps(codebase_dir: str):
    """
    Reads requirements.txt from the codebase root and installs missing packages
    into the current Python environment using pip.
    Also reads the environment setup commands for any pip install lines.
    """
    logs = []

    # 1. requirements.txt inside codebase
    req_path = os.path.join(codebase_dir, "requirements.txt")
    if os.path.exists(req_path):
        print("QA Agent: Installing packages from requirements.txt...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", req_path, "--quiet"],
            capture_output=True, text=True, timeout=120
        )
        logs.append(f"pip -r requirements.txt → exit {result.returncode}\n{result.stderr}")

    # 2. pip install lines from environment setup
    env_data = read_environment_deps()
    for cmd in env_data.get("setup_commands", []):
        cmd_s = cmd.strip()
        if cmd_s.startswith("pip install"):
            print(f"QA Agent: Running '{cmd_s}'...")
            result = subprocess.run(
                [sys.executable, "-m"] + cmd_s.replace("pip", "pip", 1).split(),
                capture_output=True, text=True, timeout=120
            )
            logs.append(f"{cmd_s} → exit {result.returncode}\n{result.stderr}")

    return "\n".join(logs)


def build_prompt(context_manager, correction: str = None) -> str:
    context = context_manager.get_context()

    user_brief = context.get("USER_BRIEF", "")
    ba_output = context.get("BA", {})
    architect_output = context.get("Architect", {})
    developer_output = context.get("Developer", {})

    # ── Dynamic codebase intelligence ─────────────────────────────────────────
    dev_summary = read_developer_summary()
    language_stack = dev_summary.get("language_stack", ["Python"])   # e.g. ["HTML","CSS","JS"]
    project_name   = dev_summary.get("project_name", "Project")
    file_tree, file_contents = scan_codebase_with_contents()
    env_data = read_environment_deps()
    env_deps = env_data.get("setup_commands", [])

    # Decide test strategy based on detected language stack
    is_python = any(lang.lower() == "python" for lang in language_stack)
    lang_label = ", ".join(language_stack)

    if is_python:
        test_strategy = """PYTHON PROJECT:
- Use `import unittest` and the standard library only (no external test runner needed).
- Import modules EXACTLY as shown in the file tree (cwd = codebase root).
  e.g. if `app/calculator.py` exists → `from app.calculator import Calculator`
- Use `unittest.mock.patch` for database/HTTP/file dependencies."""
    else:
        test_strategy = f"""NON-PYTHON PROJECT ({lang_label}):
- The project is NOT a Python server project. Do NOT try to import Python modules.
- Instead, write Python test files that validate the project FILES directly:
  * For HTML files: use `html.parser` (stdlib) to parse and assert structure/content.
  * For JS files: read the file as text and assert presence of key functions/strings.
  * For CSS files: read the file as text and assert style rules exist.
  * For JSON/config files: parse with `json` and assert required keys exist.
- Use `open(path)` with a path RELATIVE to cwd (codebase root) e.g. `open('app/index.html')`.
- Every test class still uses `unittest.TestCase`."""

    prompt = f"""You are the QA Agent for ARIA — a STRICT, senior-level QA engineer.

Project: {project_name}
Language Stack: {lang_label}

=== CONTEXT ===
USER BRIEF: {user_brief}
BA REQUIREMENTS: {str(ba_output)[:1200]}
ARCHITECTURE: {str(architect_output)[:1200]}
DEVELOPER SUMMARY: {str(developer_output)[:1200]}

=== ACTUAL CODEBASE FILE TREE (on disk right now) ===
{file_tree}

=== ACTUAL FILE CONTENTS (read from disk) ===
{file_contents[:4000]}

=== TEST STRATEGY ===
{test_strategy}

=== RULES ===
1. Generate ONE test file per logical feature/module. Name it `test_<feature>.py`.
2. NEVER fabricate import paths. Only use paths that appear in the FILE TREE above.
3. NEVER write dummy tests like `self.assertTrue(True)`. Every test must make a real assertion.
4. Tests run with cwd = codebase root. File paths must be relative to that root.
5. ALL test files must end with:
   if __name__ == '__main__':
       unittest.main()
6. Provide a bug_report for any real issues found in the code.

"""

    if correction:
        prompt += f"\n\n=== HUMAN CORRECTION ===\n{correction}\n"

    prompt += """
=== OUTPUT REQUIREMENTS ===
Return ONLY valid JSON. No markdown fences, no extra text.

{
  "status": "PASS | FAIL",
  "test_suite": [
    {
      "file": "test_<feature>.py",
      "code": "<complete runnable Python test code as a single escaped string>"
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

def execute_local_tests(test_suite: list) -> dict:
    """
    1. Installs Python dependencies from requirements.txt and environment setup.
    2. Writes test files into Developer/codebase/tests (so imports resolve natively).
    3. Also copies tests to outputs/QA/tests for artifact records.
    4. Runs each test with cwd = codebase root.
    """
    qa_dir = os.path.abspath(os.path.join("outputs", "QA", "tests"))
    codebase_dir = os.path.abspath(os.path.join("outputs", "Developer", "codebase"))
    codebase_tests_dir = os.path.join(codebase_dir, "tests")
    os.makedirs(qa_dir, exist_ok=True)
    os.makedirs(codebase_tests_dir, exist_ok=True)

    if not test_suite:
        return {"total_tests": 0, "passed": 0, "failed": 0, "log": "No tests generated."}

    # ── Step 1: Install dependencies ──────────────────────────────────────────
    dep_log = install_python_deps(codebase_dir)
    if dep_log:
        print(f"QA Agent: Dependency install log:\n{dep_log}")


    # 1. Write tests into the Developer codebase (primary) and QA dir (copy)
    for test in test_suite:
        filename = test.get("file", "test.py")
        code = test.get("code", "")
        if filename and code:
            # Primary: inside codebase so imports work
            with open(os.path.join(codebase_tests_dir, filename), "w", encoding="utf-8") as f:
                f.write(code)
            # Copy: QA artifact record
            with open(os.path.join(qa_dir, filename), "w", encoding="utf-8") as f:
                f.write(code)

    # 2. Execute each test from the codebase root so relative imports work
    log_output = ""
    passed_count = 0
    failed_count = 0

    print("QA Agent: Executing Python tests from Developer codebase...")

    for test in test_suite:
        filename = test.get("file", "test.py")
        test_path = os.path.join(codebase_tests_dir, filename)
        try:
            result = subprocess.run(
                [sys.executable, test_path],
                cwd=codebase_dir,       # run from codebase root
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                passed_count += 1
                log_output += f"✅ {filename} passed.\n{result.stdout}"
            else:
                failed_count += 1
                log_output += f"❌ {filename} failed:\n{result.stdout}\n{result.stderr}\n"
        except Exception as e:
            failed_count += 1
            log_output += f"❌ {filename} error: {e}\n"

    return {
        "total_tests": len(test_suite),
        "passed": passed_count,
        "failed": failed_count,
        "log": log_output
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

    # 3. Generate Markdown Report
    report_path = os.path.join(out_dir, "QA_Report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# QA Execution Report\n\n")
        
        exec_res = data.get("execution_results", {})
        f.write("## Summary\n")
        f.write(f"- **Total Tests:** {exec_res.get('total_tests', 0)}\n")
        f.write(f"- **Passed:** {exec_res.get('passed', 0)}\n")
        f.write(f"- **Failed:** {exec_res.get('failed', 0)}\n")
        f.write(f"- **Status:** {exec_res.get('status', 'UNKNOWN')}\n\n")
        
        f.write("## Bug Report\n")
        bug_reports = data.get("bug_report", [])
        if bug_reports:
            for bug in bug_reports:
                f.write(f"### [{bug.get('severity', 'BUG')}] {bug.get('issue', '')}\n")
                f.write(f"**Reproduction:** {bug.get('reproduction', '')}\n\n")
                f.write(f"**Suggested Fix:** {bug.get('suggested_fix', '')}\n\n")
        else:
            f.write("No bugs reported.\n\n")
            
        f.write("## Execution Log\n")
        f.write(f"```text\n{exec_res.get('log', 'No log available.')}\n```\n")
        
    generated_files.append(report_path)

    print(f"QA artifacts exported to {out_dir}.")
    return generated_files

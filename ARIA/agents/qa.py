import os
import json
import subprocess
import sys
from core.llm_utils import call_llm, parse_json_from_llm


def fix_code_string(code: str) -> str:
    """
    Repair code strings where the LLM double-escaped newlines.
    This happens when the LLM outputs literal backslash-n (\\n) inside
    its JSON string instead of a proper JSON newline escape (\n).
    The symptom is: the saved .py file has the entire test on one line.
    """
    if code and '\\n' in code:
        # Replace literal backslash-n with real newlines
        code = code.replace('\\n', '\n')
    # Also fix literal \t -> real tab, and \' -> '
    if code and '\\t' in code:
        code = code.replace('\\t', '\t')
    return code


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


def scan_codebase_with_contents(max_file_bytes: int = 1500) -> tuple[str, str]:
    """
    Walks Developer/codebase, returns:
      - file_tree: annotated list showing EXACTLY how each file should be accessed in tests
      - file_contents: concatenated snippet of each file (for LLM context)

    Annotation key:
      [PY-IMPORT]  → Python file importable as a module (e.g. from app.calculator import Calculator)
      [READ-TEXT]  → Non-Python file; must be read with open() as text
      [SKIP]       → Binary/generated file, do not test directly
    Skips __pycache__, .pyc, hidden dirs, and the tests/ folder itself.
    """
    codebase_root = os.path.abspath(os.path.join("outputs", "Developer", "codebase"))
    if not os.path.isdir(codebase_root):
        return "(Developer codebase not yet generated)", ""

    tree_lines = []
    content_snippets = []
    skip_dirs = {"__pycache__", "tests", "node_modules", ".git", ".venv", "venv", "dist", "build"}
    skip_exts = {".pyc", ".png", ".jpg", ".jpeg", ".ico", ".gz", ".zip", ".woff", ".woff2", ".ttf", ".eot", ".map"}
    python_exts = {".py"}
    text_exts = {".js", ".ts", ".jsx", ".tsx", ".html", ".htm", ".css", ".scss", ".json", ".yaml", ".yml", ".toml", ".txt", ".md", ".env", ".xml", ".csv"}

    for dirpath, dirnames, filenames in os.walk(codebase_root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in skip_dirs]
        rel_dir = os.path.relpath(dirpath, codebase_root)

        for fname in sorted(filenames):
            ext = os.path.splitext(fname)[1].lower()
            if ext in skip_exts:
                continue

            rel_path = fname if rel_dir == "." else f"{rel_dir.replace(os.sep, '/')}/{fname}"

            # Determine annotation
            if ext in python_exts:
                # Derive Python import path: e.g. app/calculator.py -> app.calculator
                module_path = rel_path.replace("/", ".").removesuffix(".py")
                annotation = f"[PY-IMPORT: from {module_path} import <ClassName>]"
            elif ext in text_exts:
                annotation = f"[READ-TEXT: open('{rel_path}', 'r').read()]"
            else:
                annotation = "[SKIP: binary/unknown]"

            tree_lines.append(f"{rel_path}  {annotation}")

            full_path = os.path.join(dirpath, fname)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(max_file_bytes)
                if len(content) == max_file_bytes:
                    content += "\n... (truncated)"
                content_snippets.append(f"\n### {rel_path} ###\n{content}")
            except Exception:
                pass

    file_tree = "\n".join(tree_lines) if tree_lines else "(no files found)"
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


def ensure_python_packages(codebase_dir: str):
    """
    Walk the codebase and ensure every directory containing .py files has an
    __init__.py so they are proper Python packages (importable via `from pkg.module import ...`).
    This is infrastructure setup, not test logic.
    """
    for dirpath, dirnames, filenames in os.walk(codebase_dir):
        dirnames[:] = [d for d in dirnames if d not in {"__pycache__", "tests", "node_modules", ".git"}]
        has_python = any(f.endswith(".py") and f != "__init__.py" for f in filenames)
        if has_python:
            init_path = os.path.join(dirpath, "__init__.py")
            if not os.path.exists(init_path):
                open(init_path, "w").close()
                print(f"QA Agent: Created missing __init__.py in {os.path.relpath(dirpath, codebase_dir)}")


def install_python_deps(codebase_dir: str):
    """
    Reads requirements.txt from the codebase root and installs missing packages
    into the current Python environment using pip.
    Also reads the environment setup commands for any pip install lines.
    """
    logs = []

    # Ensure all Python packages have __init__.py
    ensure_python_packages(codebase_dir)

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
            # Strip npm/yarn-style flags that are invalid for pip (e.g. -D, --save-dev)
            tokens = cmd_s.split()
            cleaned = [t for t in tokens if t not in {"-D", "--save-dev", "--save", "-g", "--global"}]
            if len(cleaned) <= 2:
                # Nothing left to install after stripping bad flags — skip
                continue
            print(f"QA Agent: Running '{' '.join(cleaned)}'...")
            result = subprocess.run(
                [sys.executable, "-m"] + cleaned,
                capture_output=True, text=True, timeout=120
            )
            logs.append(f"{' '.join(cleaned)} → exit {result.returncode}\n{result.stderr}")

    return "\n".join(logs)


def build_prompt(context_manager, correction: str = None) -> str:
    context = context_manager.get_context()

    user_brief = context.get("USER_BRIEF", "")
    ba_output = context.get("BA", {})
    architect_output = context.get("Architect", {})
    developer_output = context.get("Developer", {})

    # ── Dynamic codebase intelligence ─────────────────────────────────────────
    dev_summary = read_developer_summary()
    language_stack = dev_summary.get("language_stack", ["Python"])
    project_name   = dev_summary.get("project_name", "Project")
    file_tree, file_contents = scan_codebase_with_contents()
    env_data = read_environment_deps()

    lang_label = ", ".join(language_stack)
    is_python = any(lang.lower() == "python" for lang in language_stack)

    # ── Build concrete test pattern examples from the actual file tree ─────────
    py_import_examples = []
    text_read_examples = []
    for line in file_tree.splitlines():
        if "[PY-IMPORT" in line and len(py_import_examples) < 3:
            py_import_examples.append(line.strip())
        elif "[READ-TEXT" in line and len(text_read_examples) < 3:
            text_read_examples.append(line.strip())

    examples_block = ""
    if py_import_examples:
        examples_block += "\nPython modules you CAN import directly:\n"
        for ex in py_import_examples:
            examples_block += f"  {ex}\n"
    if text_read_examples:
        examples_block += "\nNon-Python files you MUST read as text (NEVER import):\n"
        for ex in text_read_examples:
            examples_block += f"  {ex}\n"

    prompt = f"""You are the QA Agent for ARIA. Your ONLY output is a single valid JSON object. Nothing else.

⚠️ ABSOLUTE OUTPUT RULES — VIOLATIONS WILL BREAK THE PIPELINE:
1. Do NOT write any text before or after the JSON. No explanations, no headers, no "Here is the test suite".
2. Do NOT wrap the JSON in markdown fences. No ```python, no ```json, no ```. Just raw JSON.
3. ALL Python code inside JSON string values MUST use \\n for newlines (escaped backslash-n), NEVER raw newlines.
   CORRECT: "code": "import unittest\\nclass TestFoo(unittest.TestCase):\\n    def test_bar(self):\\n        self.assertEqual(1,1)"
   WRONG:   "code": "import unittest
class TestFoo..."
4. ALL double quotes inside code strings MUST be escaped as \\".
5. Start your response with {{ and end with }}. No other characters outside the JSON.

Project: {project_name}
Language Stack: {lang_label}

=== PROJECT CONTEXT ===
USER BRIEF: {user_brief[:800]}
BA REQUIREMENTS: {str(ba_output)[:800]}

=== CODEBASE FILE TREE ===
{file_tree}

=== ACTUAL FILE CONTENTS ===
{file_contents[:3500]}

=== EXECUTION ENVIRONMENT ===
  - cwd = codebase root, PYTHONPATH = codebase root
  - Runner: python <test_file_absolute_path>
  - Python version: {sys.version.split()[0]}

=== DEMO COVERAGE RULES ===
Generate a SHORT and SIMPLE test suite for demo purposes.
Do NOT write dozens of tests. Focus only on the absolute most critical paths:
1. One basic positive test for the main API endpoint (e.g. GET list or POST create).
2. One basic test for the frontend HTML (e.g. checking if the title or a form field exists).
3. If there is a validation rule, write exactly one test for it (e.g. missing required field).

Keep the tests extremely short. This is a demo, not a production suite.

=== HOW TO WRITE FASTAPI TESTS ===
 (WITHOUT markdown fences — just write it as the code string value):

 
=== RULES ===
- 1 or 2 test files max (e.g. test_api.py, test_frontend.py)
- Keep it under 5 total test methods across all files.
- NEVER write self.assertTrue(True) or dummy assertions. Assert something real.
- Always use sqlite:///:memory: for the test database — never write to app.db
- Set os.environ BEFORE imports that read environment variables.
- Keep bug reports concise. Identify the issue and provide a short fix.

"""

    if correction:
        prompt += f"\n\n=== HUMAN CORRECTION ===\n{correction}\n"

    prompt += """
OUTPUT FORMAT — output ONLY this JSON, nothing else, starting NOW:
{
  "status": "PASS",
  "test_suite": [
    {
      "file": "test_api.py",
      "code": "import os, sys, unittest\\nsys.path.insert(0, ...)\\n..."
    },
    {
      "file": "test_validation.py",
      "code": "import os, sys, unittest\\n..."
    },
    {
      "file": "test_frontend.py",
      "code": "import unittest\\n..."
    }
  ],
  "execution_results": {"total_tests": 0, "passed": 0, "failed": 0},
  "bug_report": [{"severity": "MINOR", "issue": "", "reproduction": "", "suggested_fix": ""}],
  "requirement_coverage": {"total": 10, "covered": 9, "missing": []},
  "artifacts_saved_to": "outputs/QA/test_results.json",
  "confidence_score": 90,
  "confidence_reasoning": "All CRUD, validation, and frontend tests covered."
}
"""
    return prompt


def execute_local_tests(test_suite: list) -> dict:
    """
    1. Installs Python dependencies from requirements.txt and environment setup.
    2. Ensures all Python package dirs have __init__.py (so imports resolve).
    3. Writes test files into Developer/codebase/tests (primary execution location)
       AND outputs/QA/tests (artifact record for frontend display).
    4. Runs each test with cwd = codebase root AND PYTHONPATH = codebase root.
    """
    qa_dir = os.path.abspath(os.path.join("outputs", "QA", "tests"))
    codebase_dir = os.path.abspath(os.path.join("outputs", "Developer", "codebase"))
    codebase_tests_dir = os.path.join(codebase_dir, "tests")
    os.makedirs(qa_dir, exist_ok=True)
    os.makedirs(codebase_tests_dir, exist_ok=True)

    if not test_suite:
        return {"total_tests": 0, "passed": 0, "failed": 0, "log": "No tests generated."}

    # ── Step 1: Install dependencies + ensure __init__.py files exist ─────────
    dep_log = install_python_deps(codebase_dir)
    if dep_log:
        print(f"QA Agent: Dependency install log:\n{dep_log}")

    # ── Step 2: Write tests to BOTH locations ─────────────────────────────────
    for test in test_suite:
        filename = test.get("file", "test.py")
        code = test.get("code", "")
        if filename and code:
            # Enforce .py extension — LLM should never produce .js test files,
            # but as a safety net we correct the filename here.
            if not filename.endswith(".py"):
                filename = os.path.splitext(filename)[0] + ".py"
                test["file"] = filename

            # Primary: inside codebase so imports work natively
            with open(os.path.join(codebase_tests_dir, filename), "w", encoding="utf-8") as f:
                f.write(code)
            # Copy: QA artifact record (shown in frontend)
            with open(os.path.join(qa_dir, filename), "w", encoding="utf-8") as f:
                f.write(code)

    # ── Step 3: Execute each test ─────────────────────────────────────────────
    log_output = ""
    passed_count = 0
    failed_count = 0

    print("QA Agent: Executing Python tests from Developer codebase...")

    # Set PYTHONPATH so `from app.xyz import ...` resolves.
    # When Python runs a script by absolute path it adds the script's own directory
    # (tests/) to sys.path[0] — NOT the cwd — so we must set PYTHONPATH explicitly.
    env = os.environ.copy()
    env["PYTHONPATH"] = codebase_dir

    for test in test_suite:
        filename = test.get("file", "test.py")
        test_path = os.path.join(codebase_tests_dir, filename)
        try:
            result = subprocess.run(
                [sys.executable, test_path],
                cwd=codebase_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=30
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

        # 2. Sanitize test suite: fix filenames and repair any escaped code strings
        test_suite = parsed_data.get("test_suite", [])
        for test in test_suite:
            # Enforce .py extension
            filename = test.get("file", "test.py")
            if filename and not filename.endswith(".py"):
                test["file"] = os.path.splitext(filename)[0] + ".py"
            # Repair literal \n in code (LLM double-escape bug)
            code = test.get("code", "")
            test["code"] = fix_code_string(code)

        # 3. AUTO-EXECUTE tests immediately so user sees results before approving.
        #    Tests are written to both codebase/tests (execution) and QA/tests (display).
        print("QA Agent: Auto-executing generated tests before gate...")
        exec_results = execute_local_tests(test_suite)

        status = "PASS" if exec_results.get("failed", 0) == 0 and exec_results.get("total_tests", 0) > 0 else "FAIL"
        parsed_data["status"] = status
        parsed_data["execution_results"] = {
            "total_tests": exec_results.get("total_tests", 0),
            "passed": exec_results.get("passed", 0),
            "failed": exec_results.get("failed", 0),
            "status": status,
            "log": exec_results.get("log", "")
        }

        return parsed_data
    except Exception as e:
        print(f"QA Agent Error: {str(e)}")
        return {}


def post_approval(data: dict, context_manager) -> list:
    """
    Exports the QA artifacts (test cases and results) to the file system.
    Writes tests to BOTH QA/tests (frontend display) AND Developer/codebase/tests
    (execution location) so the "Run Code" button works immediately after approval.
    """
    out_dir = os.path.join("outputs", "QA")
    qa_tests_dir = os.path.join(out_dir, "tests")
    codebase_dir = os.path.abspath(os.path.join("outputs", "Developer", "codebase"))
    codebase_tests_dir = os.path.join(codebase_dir, "tests")
    os.makedirs(qa_tests_dir, exist_ok=True)
    os.makedirs(codebase_tests_dir, exist_ok=True)

    # Ensure __init__.py exists for all Python packages before tests run
    ensure_python_packages(codebase_dir)

    generated_files = []

    # 1. Update data with human edits from disk; write all tests to both locations
    test_suite = data.get("test_suite", [])
    for test in test_suite:
        filename = test.get("file")
        if not filename:
            continue

        # Safety: enforce .py extension
        if not filename.endswith(".py"):
            filename = os.path.splitext(filename)[0] + ".py"
            test["file"] = filename

        qa_file_path = os.path.join(qa_tests_dir, filename)
        codebase_file_path = os.path.join(codebase_tests_dir, filename)

        if os.path.exists(qa_file_path):
            # Human edited the file — read edited version and sync to codebase
            with open(qa_file_path, "r", encoding="utf-8") as f:
                edited_code = f.read()
            test["code"] = edited_code
        else:
            # Write LLM's original code to QA/tests
            with open(qa_file_path, "w", encoding="utf-8") as f:
                f.write(test.get("code", ""))

        # Always sync to Developer/codebase/tests (execution location)
        with open(codebase_file_path, "w", encoding="utf-8") as f:
            f.write(test.get("code", ""))

        generated_files.append(qa_file_path)

    # Inject updated test_suite into context so downstream agents see edits
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

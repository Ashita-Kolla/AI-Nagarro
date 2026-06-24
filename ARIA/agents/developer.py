import os
import json
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from core.llm_utils import call_llm, parse_json_from_llm

def build_prompt(context_manager, correction: str = None) -> str:
    context = context_manager.get_context()
    
    architect_output = context_manager.get_summary("Architect")
    planner_output = context_manager.get_summary("Planner")

    import json as _json
    planner_str = _json.dumps(planner_output, indent=2) if planner_output else "{}"
    full_ctx_str = _json.dumps(context, indent=2)
    
    tech_stack = architect_output.get("technology_stack", {}) if architect_output else {}
    frontend = tech_stack.get("frontend", "Not specified")
    backend = tech_stack.get("backend", "Not specified")
    database = tech_stack.get("database", "Not specified")

    prompt = f"""You are the Developer Agent for ARIA. Your ONLY job is to output a single valid JSON object. Nothing else.

⚠️ ABSOLUTE OUTPUT RULES — VIOLATIONS WILL BREAK THE PIPELINE:
1. Do NOT write any text before or after the JSON. No greetings, no explanations, no "Here is the code".
2. Do NOT wrap the JSON in markdown fences. No ```json, no ```. Just raw JSON starting with {{ and ending with }}.
3. ALL code inside JSON string values MUST use \\n for newlines (escaped backslash-n), NEVER raw newlines.
   CORRECT:   "main.py": "from fastapi import FastAPI\\napp = FastAPI()\\n"
   WRONG:     "main.py": "from fastapi import FastAPI\napp = FastAPI()\n"
4. ALL double quotes inside code strings MUST be escaped as \\".
5. Keep the total codebase MINIMAL. 3-5 files max. Short code. Every extra line risks truncation.

PROJECT CONTEXT:
{full_ctx_str[:2000]}

APPROVED TECH STACK:
Frontend: {frontend}
Backend: {backend}
Database: {database}

APPROVED EPICS AND TASKS:
{planner_str[:1500]}

---

CODE REQUIREMENTS:
1. FRONTEND: Generate a single `index.html` using CDN imports (React via Babel, Tailwind via CDN). No build step.
2. BACKEND: Single `main.py` using FastAPI + SQLite (`sqlite:///./app.db`).
   - MUST include: `Base.metadata.create_all(bind=engine)` so tables auto-create on startup.
   - MUST include: `CORSMiddleware` with `allow_origins=["*"]`.
   - MUST serve `index.html` as a static file on the GET "/" route using FileResponse.
3. DATABASE: SQLite only. No Postgres, no MySQL.
4. AUTH: None unless explicitly required.
5. SEED DATA: Insert 3-5 realistic example rows directly in `main.py` using a startup event.
"""
    if correction:
        prompt += f"\n\n=== HUMAN/QA CORRECTION ===\n{correction}\n"
        prompt += "\n⚠️ CRITICAL: You are implementing a correction. Keep your fix short and precise. Output the full updated codebase, but DO NOT add unnecessary bloat or you will hit the token limit.\n"

    prompt += """
OUTPUT FORMAT — output ONLY this JSON, nothing else:
{
  "files": {
    "requirements.txt": "fastapi\\nuvicorn\\nsqlalchemy\\n",
    "main.py": "from fastapi import FastAPI\\nfrom fastapi.middleware.cors import CORSMiddleware\\nfrom fastapi.responses import FileResponse\\nfrom sqlalchemy import create_engine, Column, Integer, String\\nfrom sqlalchemy.orm import declarative_base, sessionmaker\\nfrom pydantic import BaseModel\\n\\napp = FastAPI()\\napp.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])\\nengine = create_engine('sqlite:///./app.db')\\nBase = declarative_base()\\n# ... full code here ...",
    "index.html": "<!DOCTYPE html>\\n<html>\\n<head>\\n<title>App</title>\\n</head>\\n<body>\\n<!-- full React+Tailwind frontend via CDN here -->\\n</body>\\n</html>"
  },
  "setup_instructions": {
    "steps": ["1. pip install -r requirements.txt", "2. python -m uvicorn main:app --reload", "3. Open http://localhost:8000 in your browser"],
    "environment_variables": []
  }
}
"""
    return prompt

def run(context_manager, correction: str = None) -> dict:
    context = context_manager.get_context()
    
    if not context.get("Architect"):
        print("[Developer Agent Error] Cannot find Architect output. Ensure Architect agent has been approved before running Developer.")
        return {}
    if not context.get("Planner"):
        print("[Developer Agent Error] Cannot find Planner output. Ensure Planner agent has been approved before running Developer.")
        return {}

    try:
        prompt = build_prompt(context_manager, correction)
        # Using 8000 max_tokens to accommodate the massive JSON structure
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
    out_dir = os.path.join("outputs", "Developer")
    codebase_dir = os.path.join(out_dir, "codebase")
    os.makedirs(codebase_dir, exist_ok=True)
    
    generated_files = []

    # 1. Save Full Output JSON (exclude files to save space)
    full_json_path = os.path.join(out_dir, "developer_summary.json")
    with open(full_json_path, "w", encoding="utf-8") as f:
        summary_data = {k: v for k, v in data.items() if k != "files"}
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    generated_files.append(full_json_path)

    # 2. Extract and physically save the codebase files
    files = data.get("files", {})
    failed_writes = []
    
    for file_path, content in files.items():
        if file_path and content:
            safe_path = os.path.normpath(file_path).lstrip("\\/")
            if ".." in safe_path:
                continue
                
            full_path = os.path.join(codebase_dir, safe_path)
            try:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                generated_files.append(full_path)
            except Exception as e:
                failed_writes.append(f"{safe_path}: {e}")

    if failed_writes:
        print(f"✗ Failed to write {len(failed_writes)} files:")
        for err in failed_writes:
            print(f"  {err}")

    # 3. Generate .docx document using python-docx
    docx_path = os.path.join(out_dir, "developer_tasks.docx")
    try:
        generate_developer_tasks_docx(docx_path, context_manager, data)
        generated_files.append(docx_path)
    except Exception as e:
        print(f"Failed to generate developer_tasks.docx: {e}")

    print(f"Developer artifacts exported to {out_dir}.")
    return generated_files

def generate_developer_tasks_docx(docx_path, context_manager, dev_data):
    doc = Document()
    planner_data = context_manager.get_summary("Planner") or {}
    supervisor_data = context_manager.get_summary("Supervisor") or {}
    project_name = supervisor_data.get("project_name", "Unknown Project")
    summary = planner_data.get("summary", {})

    # Styles matching BRD
    style_h1 = doc.styles['Heading 1']
    font_h1 = style_h1.font
    font_h1.name = 'Calibri'
    font_h1.size = Pt(16)
    font_h1.bold = True
    font_h1.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    
    style_h2 = doc.styles['Heading 2']
    font_h2 = style_h2.font
    font_h2.name = 'Calibri'
    font_h2.size = Pt(13)
    font_h2.bold = True
    font_h2.color.rgb = RGBColor(0x2F, 0x2F, 0x2F)
    
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Calibri'
    font_normal.size = Pt(11)

    # Cover Page
    title = doc.add_paragraph("Developer Task Breakdown")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.size = Pt(24)
    title.runs[0].bold = True

    doc.add_paragraph(f"Project: {project_name}")
    import datetime
    doc.add_paragraph(f"Date: {datetime.date.today().strftime('%Y-%m-%d')}")
    doc.add_paragraph(f"Total Story Points: {summary.get('total_story_points', 0)}")
    doc.add_paragraph(f"Estimated Duration: {summary.get('estimated_developer_days', 0)} days")
    doc.add_page_break()

    # 1. Executive Summary
    doc.add_heading("1. Executive Summary", level=1)
    doc.add_paragraph(f"This document outlines the development tasks required to complete {project_name}. "
                      f"It includes a total of {summary.get('total_story_points', 0)} story points spanning "
                      f"across {len(planner_data.get('epics', []))} epics. The recommended team size is "
                      f"{summary.get('recommended_team_size', 1)} developers.")

    # 2. Sprint Plan
    doc.add_heading("2. Sprint Plan", level=1)
    for sprint in summary.get("sprint_breakdown", []):
        doc.add_heading(f"Sprint {sprint.get('sprint', 1)}", level=2)
        doc.add_paragraph(f"Focus: {sprint.get('focus', '')} ({sprint.get('story_points', 0)} pts)")
        
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Epic ID'
        hdr_cells[1].text = 'Task ID'
        hdr_cells[2].text = 'Story Points'
        hdr_cells[3].text = 'Complexity'
        
        for epic_id in sprint.get('epics', []):
            for e in planner_data.get('epics', []):
                if e.get('id') == epic_id:
                    for t in e.get('tasks', []):
                        row_cells = table.add_row().cells
                        row_cells[0].text = epic_id
                        row_cells[1].text = t.get('id', '')
                        row_cells[2].text = str(t.get('story_points', ''))
                        row_cells[3].text = t.get('complexity', '')

    # 3. Epic Breakdown
    doc.add_heading("3. Epic Breakdown", level=1)
    for epic in planner_data.get("epics", []):
        doc.add_heading(f"{epic.get('id', '')}: {epic.get('title', '')}", level=2)
        doc.add_paragraph(f"Technical Notes: {epic.get('technical_notes', '')}")
        
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Task ID'
        hdr_cells[1].text = 'Title'
        hdr_cells[2].text = 'Points'
        hdr_cells[3].text = 'Tech Area'
        
        for task in epic.get("tasks", []):
            row_cells = table.add_row().cells
            row_cells[0].text = task.get("id", "")
            row_cells[1].text = task.get("title", "")
            row_cells[2].text = str(task.get("story_points", ""))
            row_cells[3].text = task.get("tech_area", "")

    # 4. Setup Instructions
    doc.add_heading("4. Setup Instructions", level=1)
    setup = dev_data.get("setup_instructions", {})
    for step in setup.get("steps", []):
        doc.add_paragraph(step, style='List Number')

    # 5. Environment Variables
    doc.add_heading("5. Environment Variables", level=1)
    envs = setup.get("environment_variables", [])
    if envs:
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Variable'
        hdr_cells[1].text = 'Description'
        hdr_cells[2].text = 'Example'
        
        for env in envs:
            row_cells = table.add_row().cells
            row_cells[0].text = env.get("key", "")
            row_cells[1].text = env.get("description", "")
            row_cells[2].text = env.get("example", "")

    doc.save(docx_path)

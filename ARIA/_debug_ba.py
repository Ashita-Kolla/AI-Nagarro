import json
from dotenv import load_dotenv
load_dotenv()
from core.llm_utils import call_llm

user_brief = open("outputs/USER_BRIEF/USER_BRIEF.json", encoding="utf-8").read()
user_brief = json.loads(user_brief)["content"]

supervisor_output = {
    "project_type": "new_application",
    "agents_required": ["BA", "Architect", "Developer", "QA", "DevOps", "PM", "Optimisation"],
    "confidence_score": 90,
    "summary": "A simple web-based Contact Management application for individual users, freelancers, and small business owners."
}

prompt_template = """
You are the BA Agent for ARIA, a multi-agent SDLC
system. You perform deep business analysis on a
project brief and produce structured, professional
business analysis artifacts.

SUPERVISOR OUTPUT:
{supervisor_output}

USER BRIEF:
{user_brief}
{human_correction}
---

YOUR JOB:

Produce a complete business analysis. Be specific.
Be thorough. Do not be vague. Every item you produce
will be used by 6 downstream agents -- Architect,
Developer, QA, DevOps, PM, and Optimisation.

1. BUSINESS REQUIREMENTS
   Write 5-7 high-level business requirements.
   Format: "BR-001: The system must..."
   These are business needs, not technical specs.
   Cover: core purpose, user needs, performance, security, scalability.

2. USER STORIES
   Write one user story per major feature.
   Minimum 4 stories, maximum 6.

   Format exactly:
   - id: US-001
   - role: specific type of user
   - action: what they want to do (be concise)
   - benefit: measurable outcome
   - acceptance_criteria: list of 2-3 measurable, testable conditions.

3. FUNCTIONAL REQUIREMENTS
   One requirement per major system behaviour. Maximum 8.
   Format: "FR-001: The system must..."

4. NON-FUNCTIONAL REQUIREMENTS
   Cover only the most relevant categories (max 2 items each):
   - Performance, Security, Scalability, Availability

5. ASSUMPTIONS
   List up to 5 key assumptions.

6. OUT OF SCOPE
   List up to 4 explicitly excluded items.

7. CONFIDENCE SCORE
   Score 0-100 with one sentence of reasoning.

---

CRITICAL RULES:
- Output ONLY raw valid JSON. No markdown.
  No backticks. No prose before or after.
- Do not invent features not in the brief or
  implied by it.
- Every acceptance criterion must be testable
  by a QA engineer without asking questions.
- If the brief mentions compliance (GDPR, HIPAA,
  PCI-DSS, WCAG), create dedicated requirements
  for it -- do not just mention it in passing.

---

OUTPUT FORMAT:

{{
  "business_requirements": [
    "BR-001: ...",
    "BR-002: ..."
  ],
  "user_stories": [
    {{
      "id": "US-001",
      "role": "",
      "action": "",
      "benefit": "",
      "acceptance_criteria": [
        "criterion 1",
        "criterion 2",
        "criterion 3"
      ]
    }}
  ],
  "functional_requirements": [
    "FR-001: ...",
    "FR-002: ..."
  ],
  "non_functional_requirements": {{
    "performance": [],
    "security": [],
    "scalability": [],
    "accessibility": [],
    "availability": [],
    "compatibility": []
  }},
  "assumptions": [
    "Assumption 1: ..."
  ],
  "out_of_scope": [
    "Feature or capability not included"
  ],
  "confidence_score": 0,
  "confidence_reasoning": ""
}}
"""

prompt = prompt_template.format(
    supervisor_output=json.dumps(supervisor_output),
    user_brief=user_brief,
    human_correction=""
)

for i in range(8):
    print(f"=== Attempt {i+1} ===")
    response_text = call_llm(prompt, agent_name='BA')
    print("Raw length:", len(response_text or ""))
    try:
        json.loads(response_text)
        print("VALID JSON")
    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)
        print("At position:", e.pos)
        start = max(0, e.pos - 200)
        end = min(len(response_text), e.pos + 100)
        print("--- context around error ---")
        print(response_text[start:end])
        with open("_debug_ba_raw.txt", "w", encoding="utf-8") as f:
            f.write(response_text or "")
        print("Saved failing response to _debug_ba_raw.txt")
        break

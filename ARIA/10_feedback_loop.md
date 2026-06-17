# ARIA — Feedback Loop (Workflow 2)

## What is the feedback loop?

After the full pipeline completes and the client 
receives their project artifacts, they will request 
changes. This is Workflow 2.

Instead of rerunning all 8 agents from scratch, 
the feedback loop:
1. Takes the change request
2. Identifies which artifacts are affected
3. Reruns only those agents
4. Produces a versioned update (v2, v3, etc.)

Everything untouched stays at its current version.

---

## How it works — step by step

### Step 1 — Client submits a change request
Via the chatbot. Plain language.

EXAMPLE:
"Add a multilingual support feature. 
The site needs to work in English and Spanish."

---

### Step 2 — Impact Analysis Agent runs
This is a new agent that only runs in Workflow 2.
It reads the full_project_context.json and the 
change request, then outputs which artifacts 
are affected and why.

Prompt file: 12_prompts/step_09_feedback.md

OUTPUT EXAMPLE:
{
  "change_request": "Add multilingual support 
                     for English and Spanish",
  "affected_artifacts": [
    {
      "artifact": "user_stories",
      "agent": "BA",
      "reason": "New user stories needed for 
                 language selection and content 
                 switching behaviour"
    },
    {
      "artifact": "architecture",
      "agent": "Architect",
      "reason": "i18n library (next-intl) must be 
                 added to the tech stack. 
                 Translation file storage needed."
    },
    {
      "artifact": "test_cases",
      "agent": "QA",
      "reason": "New test cases needed for 
                 language toggle, content accuracy 
                 in Spanish, and fallback behaviour"
    },
    {
      "artifact": "timeline",
      "agent": "PM",
      "reason": "Multilingual adds estimated 1 week 
                 of effort. Timeline and budget 
                 must be reassessed."
    }
  ],
  "not_affected": [
    {
      "artifact": "cicd_pipeline",
      "agent": "DevOps",
      "reason": "No infrastructure changes required 
                 for i18n implementation"
    }
  ],
  "version": "v2"
}

---

### Step 3 — Human approves the impact list
The human reviews which agents will rerun.
They can remove agents from the list if they 
disagree with the impact assessment.

---

### Step 4 — Selective regeneration
Only the affected agents rerun.
Each affected agent receives:
- Their original approved output (as baseline)
- The change request
- The impact analysis output
- Instruction to update only what is affected 
  and preserve everything else

---

### Step 5 — Version comparison
The dashboard shows v1 vs v2 side by side 
for each affected artifact only.
Unaffected artifacts are not shown — they 
have not changed.

---

## Versioning convention

outputs/
├── v1/
│   ├── step_01_supervisor.json
│   ├── step_02_ba.json
│   └── full_project_context.json
├── v2/
│   ├── step_02_ba.json        ← only affected agents
│   ├── step_03_architect.json
│   ├── step_05_qa.json
│   ├── step_07_pm.json
│   └── full_project_context.json
└── latest -> v2/              ← symlink to current version

---

## Feedback loop prompt file to create

File: 12_prompts/step_09_feedback.md

It must:
- Accept the change request as {CHANGE_REQUEST}
- Accept the full context as {FULL_PROJECT_CONTEXT}
- Accept the current version number as {CURRENT_VERSION}
- Output the affected_artifacts list with agent 
  names matching the ARIA fixed list exactly
- Not regenerate anything itself — only analyse impact

---

## When to use the feedback loop vs a full rerun

| Situation | Use |
|---|---|
| Client adds a new feature | Feedback loop |
| Client changes the tech stack entirely | Full rerun from Architect |
| Client changes the business type | Full rerun from BA |
| Client adds a minor copy change | No rerun — manual edit |
| Client changes the timeline or budget | Feedback loop — PM only |
| Client adds a new integration | Feedback loop — Architect, Developer, QA |
# ARIA — Project Context Schema

## What is the project context?

project_context is a single growing JSON object that 
is built up as each agent completes and is approved.

Every agent receives the full project_context as input 
so it has complete awareness of all previous decisions.

The final version is saved as:
outputs/full_project_context.json

---

## How it grows

After Step 1 approved:
{
  "version": "v1",
  "user_brief": "...",
  "supervisor": { ...step 1 output... }
}

After Step 2 approved:
{
  "version": "v1",
  "user_brief": "...",
  "supervisor": { ...step 1 output... },
  "ba": { ...step 2 output... }
}

And so on until all 8 steps are complete.

Each new agent appends its key.
Nothing is overwritten.
The context only grows.

---

## Full schema — what the complete object looks like

{
  "version": "v1",
  "run_id": "unique identifier for this run",
  "created_at": "ISO timestamp",
  "last_updated": "ISO timestamp",
  "user_brief": "The original brief as typed by the user",

  "supervisor": {
    "project_type": "",
    "secondary_types": [],
    "agents_required": [],
    "routing_rationale": "",
    "brief_quality": {
      "present": [],
      "missing": []
    },
    "clarifications_needed": [],
    "assumptions_made": [],
    "confidence_score": 0,
    "confidence_reasoning": "",
    "summary": ""
  },

  "ba": {
    "business_requirements": [],
    "user_stories": [
      {
        "id": "",
        "role": "",
        "action": "",
        "benefit": "",
        "acceptance_criteria": []
      }
    ],
    "assumptions": [],
    "out_of_scope": [],
    "confidence_score": 0,
    "confidence_reasoning": ""
  },

  "architect": {
    "tech_stack": {
      "frontend": "",
      "backend": "",
      "database": "",
      "infra": "",
      "justification": ""
    },
    "architecture_overview": "",
    "database_schema": [
      {
        "table": "",
        "fields": [],
        "relationships": ""
      }
    ],
    "integrations": [],
    "deviations_from_brief": [],
    "confidence_score": 0,
    "confidence_reasoning": ""
  },

  "developer": {
    "epics": [
      {
        "id": "",
        "title": "",
        "tasks": [
          {
            "id": "",
            "title": "",
            "story_points": 0,
            "complexity": "",
            "depends_on": []
          }
        ]
      }
    ],
    "total_story_points": 0,
    "confidence_score": 0,
    "confidence_reasoning": ""
  },

  "qa": {
    "test_cases": [
      {
        "id": "",
        "linked_story": "",
        "description": "",
        "preconditions": [],
        "steps": [
          {
            "step": 0,
            "action": "",
            "test_data": "",
            "expected_result": ""
          }
        ],
        "environment": "",
        "type": "",
        "automation_tool": ""
      }
    ],
    "edge_cases": [
      {
        "id": "",
        "scenario": "",
        "input": "",
        "expected_behaviour": ""
      }
    ],
    "manual_test_count": 0,
    "automated_test_count": 0,
    "confidence_score": 0,
    "confidence_reasoning": ""
  },

  "devops": {
    "cicd_pipeline": {
      "stages": [],
      "tool": ""
    },
    "environments": [],
    "containerisation": "",
    "deployment_strategy": "",
    "infra_checklist": [],
    "confidence_score": 0,
    "confidence_reasoning": ""
  },

  "pm": {
    "timeline_weeks": 0,
    "milestones": [
      {
        "milestone": "",
        "week": "",
        "deliverable": "",
        "owner": "",
        "acceptance": ""
      }
    ],
    "risks": [
      {
        "risk": "",
        "likelihood": "",
        "impact": "",
        "mitigation": "",
        "owner": "",
        "deadline": ""
      }
    ],
    "dependencies": [
      {
        "task": "",
        "blocks": "",
        "reason": ""
      }
    ],
    "resource_plan": [
      {
        "role": "",
        "headcount": 0,
        "days_allocated": 0,
        "day_rate_usd": 0,
        "total_cost_usd": 0
      }
    ],
    "total_budget_used_usd": 0,
    "budget_remaining_usd": 0,
    "trade_offs": [],
    "confidence_score": 0,
    "confidence_reasoning": ""
  },

  "optimisation": {
    "duplicate_stories": [],
    "parallelisation_opportunities": [],
    "automation_opportunities": [],
    "estimated_effort_reduction": "",
    "effort_reduction_basis": "",
    "before_after_summary": {
      "before": {
        "timeline": "",
        "total_tasks": 0,
        "total_story_points": 0,
        "estimated_days": 0
      },
      "after": {
        "timeline": "",
        "total_tasks": 0,
        "total_story_points": 0,
        "estimated_days": 0
      }
    }
  },

  "hitl_log": [
    {
      "step": "",
      "action": "approved / edited / regenerated",
      "human_note": "correction text if edited, null otherwise",
      "timestamp": "ISO timestamp"
    }
  ]
}

---

## Key rules for aria.py

1. Load the context file at the start of every run
2. After each approval, append the agent output 
   under its key and save immediately
3. Never overwrite an existing key — if BA already 
   exists and you are rerunning BA, save as ba_v2
4. Always pass the full context to each agent prompt
   not just the immediately previous step
5. The hitl_log must be updated on every gate action
   including regenerations and edits
6. On a feedback loop run, increment the version field:
   "version": "v1" becomes "version": "v2"

---

## Why this matters

The project_context is the single source of truth 
for the entire ARIA run. 

If it is incomplete, agents hallucinate missing context.
If it is overwritten, you lose the audit trail.
If it is not passed in full, downstream agents make 
decisions that contradict upstream decisions.

Every bug you have seen in the ARIA test runs 
(wrong business type in BA, PM ignoring the timeline, 
architect deviating from the stack silently) happened 
because the context was not passed correctly.

Fix the context, fix the outputs.
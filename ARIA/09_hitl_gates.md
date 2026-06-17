# ARIA — Human-in-the-Loop Gates

## What is a HITL gate?

After every agent completes its output, ARIA pauses 
and presents the result to the human operator before 
the next agent runs. The human decides what happens next.

This means no agent ever runs on unreviewed input.
Every step is human-approved before it becomes context 
for the next step.

---

## The three gate options

### [A] Approve
The output is accepted as-is.
It is saved to outputs/step_XX_agentname.json.
It is added to the running project_context.
The next agent runs immediately.

Use when: Output is accurate, complete, and fits 
the project brief.

### [E] Edit
The human types a correction or addition.
The correction is appended to the original prompt as:
HUMAN CORRECTION: {your note here}
The agent reruns with this extra context.
The human must approve before moving on.

Use when: Output is mostly right but has specific 
errors, wrong assumptions, or missing details.

EXAMPLE:
"The timeline should be 6 weeks not 12. 
Budget is $8,000. Adjust the plan accordingly."

### [R] Regenerate
The agent reruns with no changes to the prompt.
Use sparingly — if the output was bad, Regenerate 
alone rarely fixes it. Use Edit instead.

Use when: Output was cut off, malformed JSON, 
or clearly incomplete due to a technical error 
not a prompt quality issue.

### [Q] Quit
Saves all progress up to the last approved step.
On next run, ARIA detects completed steps and 
offers to resume from where you left off.

Use when: You need to stop mid-run and continue later.

---

## What the gate checks for

Before approving any step, verify:

SUPERVISOR (Step 1)
- [ ] Project type is correctly classified
- [ ] Agent list only contains ARIA agents
- [ ] Confidence score is honest — not inflated
- [ ] Clarifications are specific, not generic

BA (Step 2)
- [ ] Business type matches the approved brief
- [ ] User stories use As a / I want / So that format
- [ ] Every acceptance criterion is measurable
- [ ] Assumptions are explicitly stated

ARCHITECT (Step 3)
- [ ] Tech stack matches what was specified in brief
- [ ] Any deviation from brief is flagged with reason
- [ ] Database schema covers all entities from user stories
- [ ] Integrations list is complete

DEVELOPER (Step 4)
- [ ] Epics map to user stories from BA output
- [ ] Story points use Fibonacci scale only
- [ ] Dependencies between tasks are explicit
- [ ] No tasks reference entities not in the architecture

QA (Step 5)
- [ ] Every test case has preconditions
- [ ] Steps have specific test data, not "check that X works"
- [ ] At least 8 edge cases present
- [ ] Automated/manual classification is justified

DEVOPS (Step 6)
- [ ] CI/CD tool matches the architecture tech stack
- [ ] No contradictions (e.g. Docker + serverless Vercel)
- [ ] All three environments defined: dev, staging, prod
- [ ] Confidence score is not 0

PM (Step 7)
- [ ] Timeline matches the client-approved timeline exactly
- [ ] Budget breakdown sums to the approved budget or less
- [ ] Every risk has an owner and a deadline
- [ ] Milestone format uses strings not number ranges

OPTIMISATION (Step 8)
- [ ] Parallelisation suggestions are technically valid
- [ ] Effort reduction percentage has a stated basis
- [ ] Before/after summary is specific not vague
- [ ] Duplicate stories list is not empty by default 
      — verify manually

---

## Common failure patterns and fixes

| What you see | What it means | Fix |
|---|---|---|
| Agent ignores the business context | Context injection failed — placeholder not replaced | Check aria.py placeholder replacement logic |
| Output cut off mid-JSON | max_tokens too low | Raise max_tokens to 2000-3000 |
| JSON wrapped in backticks | Model ignored raw JSON instruction | Select R to regenerate, or add "no backticks" to prompt |
| Timeline doubled from brief | PM agent ignored constraints | Select E, restate the constraint explicitly |
| Confidence score is 0 | Model skipped that field | Select E, ask it to reassess and score honestly |
| Agent invents new agent types | Supervisor prompt not locking agent list | Check step_01_supervisor.md for the fixed list rule |
| Wrong business type in BA | Supervisor output not injected into BA prompt | Check {STEP_01_OUTPUT} placeholder in step_02_ba.md |
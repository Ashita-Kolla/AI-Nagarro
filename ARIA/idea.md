
# AI Impact Measurement MVP — what it is and how it works

## The problem

* [ ] Organizations roll out AI tools (Copilot, etc.) into engineering work and then can't credibly prove whether it helped. Leadership doesn't trust self-reported gains, and the core insight driving this whole project is:  **estimates presented as measurements destroy trust** . Today the only fix that works is a spreadsheet plus a consultant sitting next to the team enforcing discipline — manual, slow, not repeatable. This app encodes that discipline as software, so the rules can't be fudged by whoever's using it.

## What V1 proves

One thing: **an unstructured, free-text description of an AI use case can become a provenance-graded, calculation-backed measurement register in minutes.**

## The end-to-end journey

1. **Create a use case** — title, free-text description, the unit of work involved, which SDLC lifecycle stage(s) it touches.
2. **LLM proposes candidate KPIs** — given the description plus a fixed contract (the five families, the instrument schema, baseline-treatment rules), the LLM returns candidate child KPIs. Each candidate must map to exactly one family or it's rejected outright.
3. **User keeps/drops candidates** — human judgment call, not automatic.
4. **Kept candidates become the KPI register** for that use case.
5. **Manual measurement entry** — baseline value, AI-assisted value, unit, sample size `n`, and an evidence grade. Which fields even show up depends on the instrument's baseline treatment.
6. **Deterministic Python computes deltas** — never the LLM.
7. **Engineering view** — the full register with computed values, each carrying its evidence grade.
8. **Leadership view** — five family cards as ranges (never a blended average) with total `n`, plus one derived € value scenario.

This is exactly the thread you and I were just poking at: step 5 is manual by deliberate design in V1 — not because nobody thought to automate it.

## The domain model, in brief

**Five fixed KPI families** (never modified — use cases extend by adding instruments, not new families):

* **Productivity** — net effort reduction (negative = good)
* **Speed** — time-to-outcome (negative = good)
* **Quality & acceptance** — includes a safety gate (positive = good)
* **Adoption & fidelity** — level only, no baseline
* **Value released** — always derived, never directly measured

 **Four baseline treatments** , spelled exactly like the workbook: `Reduction`, `Level`, `Estimated-baseline`, `Derived`. Each determines which fields appear and how (or whether) a delta is computed — e.g. a `Level` metric must never get an invented baseline; a `Derived` metric never accepts manual entry at all.

**Three separate provenance axes** (this is the trust mechanism, and it's the load-bearing idea in the whole product):

* **Evidence grade** : `illustrative < estimated < team_stated < measured` — how strong is the evidence.
* **Value origin** : `observed` vs `derived` — was this typed in or calculated.
* **Value maturity** (scenario/€ outputs only): `identified → validated → implementation_ready → realized` — only `realized` may ever be called an actual booked saving.

Nothing renders anywhere in the UI without its evidence grade. A heading over a set of values can't claim a grade stronger than the weakest value inside it.

## How the numbers stay honest

There's a real spreadsheet (`ENGAGEMENT_MASTER_WORKBOOK`, kept local, never committed) that is the actual numeric spec — every formula in `docs/architecture/calculation-contract.md` was read off a cell, not written from memory. Percent handling, delta math, the "no blended average" rule, the zero-baseline guard, the scenario chain with its double-count guard — all traced back to specific cells. The LLM is explicitly barred from ever touching arithmetic; it only proposes instrument definitions.

## Stack

React + Vite + TypeScript SPA · Python 3.11+/FastAPI/Pydantic v2 · SQLite via SQLAlchemy (Postgres-portable schema) · calculation engine as pure, framework-free Python functions · pytest with heavy coverage on the calculation logic. Single container, no auth, no cloud dependency for the first demo.

## What's explicitly out of scope for V1 (this is where your earlier question lands)

Auth/RBAC, any connector (work-tracker, code-platform, AI-assistant usage, LLM-gateway telemetry), automated SDLC telemetry ingestion, MCP server, multi-tenancy, exemplar library. **Manual entry is intentional** — V1 is validating the measurement  *product* , not building automated evidence collection yet. That's named as Phase 2 work.

## How the work itself is governed

* [ ] `AGENTS.md` is the operating constitution for any agent (human or AI) touching this repo. Key rules: the workbook outranks prose for anything numeric; accepted ADRs outrank the PRD; the PRD outranks everything else. Claims made during analysis get tagged `FACT`/`REQUIREMENT`/`DECISION`/`INFERENCE`/`ASSUMPTION`/`CONFLICT`/`OPEN QUESTION` so nothing unsupported passes as settled. GitHub Issues are the backlog of record. There are three repo-specific skills (`analyze-requirement`, `implement-issue`, `review-change`) that encode the working procedure for scoping, building, and reviewing a change.

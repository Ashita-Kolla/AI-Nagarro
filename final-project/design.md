# Phase 1 — Problem Definition & System Design

## Goal

Define system behavior, decision boundaries, and information flow for an autonomous multi-agent service desk that routes, executes actions, and handles uncertainty safely.

---

## 1. System Scope

The system:

- Accepts natural language user requests
- Classifies intent with a confidence score
- Routes to specialized agents (HR / IT / Finance / QA / PM / BA)
- Executes actions via tools (tickets, emails, invoices, etc.)
- Handles uncertainty explicitly — no silent failures
- Maintains session-level context memory

---

## 2. User Categories

**Human users**

| Actor | Role |
|-------|------|
| Employee | General staff — submits HR, IT, or Finance requests |
| QA Engineer | Submits bug reports and system errors — assumed technical context |
| Business Analyst | Submits requirement and process queries — assumed domain context |
| PM / Other Staff | Submits project status and task-related requests |

**External systems**

| Actor | Role |
|-------|------|
| HR System | Simulated or external — receives HR-related actions |
| IT Support System | Receives IT tickets and access requests |
| Finance / Billing System | Receives invoices and reimbursement requests |
| Project Management System | Receives status updates and task assignments |

---

## 3. Intent Taxonomy

| Domain | Intents |
|--------|---------|
| HR | `salary_issue` · `leave_request` · `payslip_request` |
| IT | `laptop_issue` · `vpn_issue` · `software_installation` |
| Finance | `invoice_request` · `reimbursement_request` |
| QA / Dev | `bug_report` · `system_error` |
| PM / BA | `project_status` · `requirement_clarification` |
| Fallback | `unknown_intent` |

---

## 4. Output Types

The system produces **structured outcomes**, not just conversational replies.

| Output | Description |
|--------|-------------|
| `ticket_creation` | Creates a support or bug ticket |
| `email_generation` | Drafts and sends a structured email |
| `invoice_generation` | Generates an invoice document |
| `status_update` | Posts a status update to the relevant system |
| `human_escalation` | Routes to a human agent — first-class output, not a fallback hack |

---

## 5. Confidence Threshold Policy

The classifier outputs an intent **and** a confidence score (0–1). Routing is decided as follows:

| Confidence | Action |
|------------|--------|
| ≥ 0.80 | Auto-route to specialist agent |
| 0.60 – 0.80 | Ask clarification question |
| < 0.60 | Human escalation |

This is a core safety rule. The system **never guesses** below threshold.

---

## 6. Unknown Intent Handling

If the classifier cannot confidently map a request:

```
User Query
   ↓
Classifier confidence < threshold
   ↓
Unknown Intent Handler
   ↓
Clarification Question  OR  Human Escalation
```

Prevents wrong department routing, wrong automated actions, and silent failures — especially critical in Finance and HR.

---

## 7. Context / Memory Layer

Sits alongside the classifier and router. Maintains session-level state only.

**Stores:**
- User role (if known)
- Department (if known)
- Conversation history (current session)
- Previous intent(s)

**Purpose:** Avoids repeated questions, improves routing accuracy, enables multi-step workflows.

**Example session state:**
```json
{
  "user": "QA Engineer",
  "department": "Engineering",
  "previous_intent": "bug_report",
  "history": ["..."]
}
```

---

## 8. Agent Mapping

| Intent Domain | Specialist Agent |
|---------------|-----------------|
| HR | HR Agent |
| IT | IT Agent |
| Finance | Finance Agent |
| QA / Dev | QA Agent |
| PM / BA | PM Agent |
| Unknown | Unknown Intent Handler → Escalation |

---

## 9. System Architecture

```
User Input
   ↓
Context Memory Layer
   ↓
Intent Classifier + Confidence Score
   ↓
   ├── ≥ 0.80  →  Router Agent  →  Specialist Agent
   ├── 0.60–0.80  →  Clarification Prompt
   └── < 0.60  →  Human Escalation

Specialist Agent
   ↓
Tool Executor Layer
   ↓
Output Generator
   ↓
Response to User
```

---

## 10. System Behavior Rules

1. Never guess intent below confidence threshold
2. Always compute and store confidence score internally
3. Human escalation is a valid, first-class system output
4. Context must be reused within the session — never ask repeated questions
5. Agents cannot override the unknown intent handler
6. Tool execution only occurs after validated routing

---

## 11. Deliverables

| Deliverable | Description | Status |
|-------------|-------------|--------|
| System Design Document | Architecture, rules, flow | ✅ This document |
| Intent Taxonomy | Structured intent list per domain | ✅ Section 3 |
| Output Type Schema | Ticket / email / invoice / escalation | ✅ Section 4 |
| Confidence & Fallback Policy | Thresholds and decision rules | ✅ Section 5–6 |
| Context Memory Design | Session state definition | ✅ Section 7 |

## 12. Workflow Mapping (n8n Design)

Workflow	Purpose
Router Workflow	Intent classification and routing
HR Workflow	Salary, leave, payroll requests
IT Workflow	Laptop, VPN, access requests
Finance Workflow	Invoices and reimbursements
QA Workflow	Bug reporting and issue tracking
PM Workflow	Project status and planning requests
Escalation Workflow	Human handoff and unresolved requests

This will make Phase 2 implementation much easier because you'll already know exactly which n8n workflows need to exist.

What I would do next

After finalizing Phase 1:

Build only ONE n8n workflow first
Chat Input
    ↓
OpenAI Node
    ↓
Intent Classification
    ↓
Confidence Check
    ↓
Switch Node
    ↓
HR / IT / Finance / Unknown

Don't build all six agents yet.

Start with:

HR Agent
IT Agent
Finance Agent
Unknown Intent Handler

Those four workflows are enough to prove the architecture works before expanding to QA and PM.

---

*Phase 1 complete. This defines a controlled autonomous workflow system with uncertainty handling and safety boundaries — not just a chatbot.*
# Project Management Operations Manual

**Document Owner:** Project Management Office (PMO)  
**Last Updated:** June 2026  
**Version:** 2.8  
**Classification:** Internal Use Only

---

## Overview

This manual serves as the definitive guide for project management practices at Nagarro. It is intended for Project Managers, Delivery Leads, Scrum Masters, and senior contributors working on client-facing or internal projects. All processes described here are aligned with the Nagarro Delivery Framework (NDF) and industry best practices (PMBOK, Agile/Scrum, SAFe).

For PMO support: **pmo@nagarro.com** | PM Community Slack: **#pm-community**

---

## 1. Project Status Reporting

### 1.1 Overview

Regular, transparent status reporting is a cornerstone of Nagarro's delivery culture. Status reports maintain stakeholder confidence, surface risks early, and provide a formal record of project performance. All active client engagements must produce a Weekly Status Report (WSR) unless the client explicitly waives this requirement in writing.

### 1.2 Required Reporting Cadence

| Report Type | Frequency | Audience |
|---|---|---|
| Weekly Status Report (WSR) | Every Friday by 4 PM | Client + Internal leadership |
| Monthly Executive Summary | Last working day of month | C-suite + Account Manager |
| Milestone Report | On milestone completion | Client stakeholders |
| Risk Register Update | Bi-weekly | Delivery Head + PMO |
| Financial Report | Monthly | Finance BP + Account Manager |

### 1.3 Weekly Status Report Structure

Every WSR must follow the Nagarro standard template and include:

**Section 1 – Executive Summary (2–3 sentences)**
A concise, client-friendly summary of the week's progress. Avoid technical jargon. Focus on business outcomes delivered.

**Section 2 – RAG Status**
Rate the project across three dimensions using Red/Amber/Green:
- **Schedule:** Are we on track against the approved project plan?
- **Budget:** Is actual spend within 5% of the planned budget?
- **Quality:** Are defect rates and test pass rates within acceptable thresholds?

**Section 3 – Accomplishments This Week**
Bulleted list of completed deliverables, milestones achieved, and decisions made.

**Section 4 – Planned for Next Week**
Clear list of what will be delivered in the next reporting period, with owners named.

**Section 5 – Risks and Issues**
Any new or updated risks, along with the current mitigation strategy. Do not omit risks from the WSR — it protects both Nagarro and the client.

**Section 6 – Decisions Required**
Any pending decisions from the client that are blocking progress. Include the deadline by which the decision is needed.

### 1.4 Generating the Status Report

**Step 1 – Access the Project Hub**
Navigate to Project Hub → [Your Project] → Reports → New Status Report. The system auto-populates metrics from Jira (velocity, bug counts), Time & Expense (budget utilisation), and the project schedule.

**Step 2 – Review and edit the draft**
Review auto-populated data for accuracy. The Jira sync may lag by 2 hours — refresh if needed. Add narrative context that the data alone cannot convey.

**Step 3 – Internal review**
Share the draft with your Delivery Head for review at least 2 hours before the client-facing deadline.

**Step 4 – Distribute**
Use the Project Hub's distribution feature to send to the configured recipient list. Do not send project reports from personal email or as raw attachments — use the portal to maintain a version history.

### 1.5 Escalation Policy

**Escalation Policy:** If a project turns Red on Schedule or Budget, you must notify your Delivery Head and Account Manager immediately — do not wait for the next WSR. A recovery plan must be drafted within 48 hours of a Red status being declared.

---

## 2. Resource Allocation

### 2.1 Overview

Effective resource allocation ensures the right people with the right skills are working on the right activities at the right time. At Nagarro, resource management is a collaborative responsibility between Project Managers, Resource Managers, and the PMO.

### 2.2 Staffing a New Project

**Step 1 – Raise a Resource Request**
Once a SOW is signed and a project code is created, raise a Resource Request in the Resource Management System (RMS) at rms.nagarro.com. Provide:
- Required skill sets and seniority levels
- Number of resources needed
- Start date and expected duration
- Preferred location/timezone (if applicable)

**Step 2 – Resource Manager review**
The Resource Manager will match your requirements against the internal availability pool within 3 business days. You will receive a list of proposed candidates with skill profiles.

**Step 3 – Profile review and selection**
Review proposed profiles. You may request brief 30-minute introductory calls with candidates. Selection must be communicated within 2 business days.

**Step 4 – Onboarding initiation**
Once selected, the Resource Manager initiates the project onboarding process: system access, induction, project documentation sharing, and team introductions.

### 2.3 Managing Resource Changes Mid-Project

Requesting a resource change mid-project requires careful management to avoid delivery disruption:

- **Planned rotation:** Submit a Change Request in RMS at least 4 weeks in advance. The outgoing resource must complete a knowledge transfer document before departure.
- **Unplanned departure (illness, resignation):** Notify the Resource Manager immediately. An interim replacement will be identified within 3 business days. Document the risk in your Risk Register.
- **Skill gap identified:** If a resource's skills are insufficient for project needs, discuss with your Delivery Head before initiating any formal process. Training, pairing, or role adjustment may resolve the issue without a full replacement.

### 2.4 Escalation Policy

**Escalation Policy:** If a critical skill gap cannot be filled from the internal pool within 5 business days, the Resource Manager will escalate to the Global Resource Allocation Committee, which may engage contractors or partner organisations as a fallback.

---

## 3. Requirement Clarification

### 3.1 Overview

Ambiguous or incomplete requirements are among the leading causes of project overruns and client dissatisfaction. Nagarro's delivery methodology mandates formal requirement validation before any development work begins, and a structured change process for any modifications thereafter.

### 3.2 Requirements Baseline Process

**Step 1 – Review the PRD/BRD**
Thoroughly review the Product Requirements Document (PRD) or Business Requirements Document (BRD) provided by the client. Log all assumptions and questions in the Requirements Tracker.

**Step 2 – Identify ambiguities and gaps**
Analyse the document for:
- Missing acceptance criteria
- Conflicting requirements between sections
- Undefined edge cases or error handling
- Unclear ownership or sign-off authority

**Step 3 – Requirements Clarification Session**
Schedule a focused 1–2 hour session with the client's product owner and key SMEs. Use the prepared question log as the agenda. Document all answers in real-time and share the meeting minutes within 24 hours for client confirmation.

**Step 4 – Update and baseline the requirements**
Incorporate all clarifications into the PRD. Have the client formally sign off on the updated document. This signed version becomes the "baseline" — any future changes are subject to the Change Management process.

### 3.3 Living Requirements in Agile Projects

For Agile/Scrum engagements, requirements evolve through the product backlog. Best practices:
- Every User Story must have a Definition of Ready (DoR) before sprint planning: clear acceptance criteria, estimated by the team, dependencies identified
- Ensure the product backlog is groomed at least 2 sprints ahead
- Any story that cannot be refined due to missing information should be flagged as a blocker with the client PO immediately

### 3.4 Escalation Policy

**Escalation Policy:** If the client's product owner is unavailable for clarification for more than 3 business days and this is blocking sprint work, escalate via the Account Manager. The delay must be logged as a risk in the project Risk Register.

---

## 4. Scope Creep Management

### 4.1 Overview

Scope creep is the gradual expansion of a project's scope beyond the original agreement, often without corresponding adjustments to timeline, budget, or resources. It is one of the most common reasons projects fail to deliver on time or on budget. Proactive scope management is a critical project management skill.

### 4.2 Identifying Scope Creep

Scope creep can be subtle. Watch for:
- Client casually mentioning "can you also add..." or "while you're at it..."
- New requirements appearing in sprint planning that were not in the original PRD
- The team working on features not covered by any approved User Story
- Timeline slipping without any formally logged change requests

### 4.3 The Change Control Process

**Step 1 – Document the change request**
When a new requirement or scope addition is identified, capture it formally using the Change Request (CR) Template in the Project Hub. Include a clear description of what is being requested, why it is needed, and who is requesting it.

**Step 2 – Impact analysis**
Estimate the impact of the change on:
- **Schedule:** How many additional days/sprints will this require?
- **Budget:** What is the cost in person-days at the agreed rate card?
- **Quality:** Does this change introduce risk to existing functionality?
- **Resources:** Does this require skills not currently on the team?

**Step 3 – Client presentation and approval**
Present the CR and its impact analysis to the client stakeholder. Do not begin work on the change until formal written approval (email confirmation is acceptable) is received.

**Step 4 – Update project documents**
Once approved, update the SOW amendment (if commercial impact), project plan, and product backlog. Notify all team members of the change.

### 4.4 Escalation Policy

**Escalation Policy:** If a client insists on proceeding with an unapproved change or refuses to acknowledge scope additions, escalate immediately to the Delivery Head and Account Manager. Do not allow the team to begin work on unapproved changes.

---

## 5. Risk Escalation

### 5.1 Risk Management Framework

Nagarro follows a structured risk management approach based on a 5×5 probability-impact matrix. All project risks must be logged in the Risk Register from project initiation and reviewed at least bi-weekly.

### 5.2 Risk Categories

- **Schedule Risk:** Threats to the delivery timeline (e.g., dependency delays, underestimation)
- **Budget Risk:** Threats to financial performance (e.g., scope creep, FX fluctuation)
- **Resource Risk:** Threats to team continuity (e.g., attrition, skill gaps)
- **Technical Risk:** Threats from technical complexity, third-party APIs, or legacy systems
- **Client Risk:** Threats from client-side factors (e.g., delayed approvals, change in sponsor)
- **Compliance Risk:** Regulatory, data privacy, or contractual compliance threats

### 5.3 Risk Assessment and Response

**Step 1 – Log the risk**
In Project Hub → Risk Register → Add Risk. Assign an ID, description, category, owner, and initial probability/impact scores.

**Step 2 – Score the risk**
Rate Probability (1=Very Low to 5=Almost Certain) and Impact (1=Negligible to 5=Critical). The Risk Score = Probability × Impact. Scores of 15+ are High risks requiring immediate escalation.

**Step 3 – Define a response strategy**
Choose one of four strategies:
- **Avoid:** Eliminate the cause of the risk (change approach)
- **Mitigate:** Take actions to reduce probability or impact
- **Transfer:** Shift the risk to a third party (e.g., insurance, contractual clause)
- **Accept:** Acknowledge the risk and prepare a contingency plan

**Step 4 – Monitor and update**
Review the Risk Register every 2 weeks during the project team meeting. Update status, probability, and impact as the project progresses.

### 5.4 Escalation Thresholds

| Risk Score | Action Required |
|---|---|
| 1–6 (Low) | Monitor; update bi-weekly |
| 7–14 (Medium) | Active mitigation plan; PM owns |
| 15–19 (High) | Immediate escalation to Delivery Head |
| 20–25 (Critical) | Escalation to VP + Client escalation; daily tracking |

### 5.5 Escalation Policy

**Escalation Policy:** Any risk that materialises into an active issue causing project impact must be reported to the Delivery Head and Account Manager within 24 hours. An emergency response call must be scheduled within 48 hours.

---

## 6. Stakeholder Meeting Scheduling

### 6.1 Overview

Effective meetings are purposeful, time-bound, and result in clear action items. Nagarro's meeting culture emphasises quality over quantity. This section covers how to schedule, prepare, and run stakeholder-level meetings for maximum effectiveness.

### 6.2 Planning a Stakeholder Meeting

**Step 1 – Define the objective**
Before scheduling any meeting, answer: What decision needs to be made? What information needs to be shared? Could this be resolved via email? If no clear objective can be stated, do not call a meeting.

**Step 2 – Identify required attendees**
Only invite people who are essential to the meeting's objective. Every unnecessary attendee reduces the meeting's efficiency and increases the collective cost in person-hours. Separate "Required" from "Optional" in your invite.

**Step 3 – Check availability**
Use the Scheduling Assistant in Microsoft Outlook or Google Calendar to find a time when all required attendees are free. For international attendees, use a Time Zone Converter to ensure you do not schedule at unsociable hours for any participant.

**Step 4 – Create and send the calendar invite**
The invite must include:
- **Meeting title:** Clear and specific (e.g., "Project Alpha — Q2 Milestone Review" not "Meeting")
- **Duration:** Be realistic but concise. Default to 30 or 45 minutes rather than 60
- **Agenda:** Attach a bullet-point agenda with time allocations for each item
- **Pre-read materials:** Share at least 24 hours before the meeting
- **Video call link:** Always include a conference link even for in-person meetings in case of remote participants
- **Dial-in details:** For clients who prefer phone

**Step 5 – Send a reminder**
Send a brief reminder email the day before with the agenda and any materials. This significantly improves attendance and preparation quality.

### 6.3 Running the Meeting

- Start on time. Do not wait more than 2–3 minutes for latecomers.
- Designate a note-taker if you are facilitating.
- Keep to the agenda. Park off-topic discussions in a "Parking Lot" for follow-up.
- Close each agenda item with a clear decision or action item (who, what, when).
- End 5 minutes early to allow transition time between meetings.

### 6.4 Post-Meeting Follow-Up

Within 24 hours of the meeting, distribute the meeting minutes via the Project Hub → Meeting Minutes → New. The minutes must capture:
- Attendees
- Key decisions made
- Action items with owners and due dates
- Parking lot items

All action item owners should acknowledge receipt. Track open actions in the Project Hub until closed.

### 6.5 Escalation Policy

**Escalation Policy:** If a key decision-maker is repeatedly unavailable or meetings are consistently unproductive, raise this as a Client Risk in the Risk Register and escalate to the Account Manager. Persistent unavailability of the client sponsor is a high-severity risk to delivery.

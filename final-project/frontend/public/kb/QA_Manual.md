# Quality Assurance Operations Manual

**Document Owner:** QA Centre of Excellence (QA CoE)  
**Last Updated:** June 2026  
**Version:** 3.5  
**Classification:** Internal Use Only

---

## Overview

This manual is the authoritative reference for all Quality Assurance processes at Nagarro. It covers the full QA lifecycle from test strategy and environment management to defect reporting, automation, and release governance. It is intended for QA Engineers, Test Leads, SDETs, and Project Managers working on any Nagarro engagement.

QA CoE contact: **qa-coe@nagarro.com** | QA Community Slack: **#qa-community**

---

## 1. Bug Report

### 1.1 Overview

Effective bug reporting is a professional skill. A well-written bug report provides developers with everything they need to reproduce, understand, and fix a defect without back-and-forth. Poor bug reports waste time and erode team trust. At Nagarro, all bugs must be reported via Jira using the standard defect template.

### 1.2 Bug Severity Classification

All bugs must be classified by severity at the time of reporting:

| Severity | Definition | Example | Expected Fix Time |
|---|---|---|---|
| Sev-1 (Critical) | System crash, data loss, security breach | Checkout crashes, user data exposed | Same day |
| Sev-2 (High) | Major feature broken, no workaround | Login fails, payments not processing | Within 24 hours |
| Sev-3 (Medium) | Feature partially broken, workaround exists | Filter doesn't sort correctly | Next sprint |
| Sev-4 (Low) | Minor UI issues, cosmetic defects | Button colour off-spec, typo | Backlog |

### 1.3 Writing a High-Quality Bug Report

**Step 1 – Reproduce the bug at least twice**
Before logging, reproduce the issue at least twice to confirm it is consistent and not a one-off glitch. Note the exact conditions under which it occurs.

**Step 2 – Open Jira → Create Issue → Bug**
Navigate to your project in Jira. Click **Create** → Select Issue Type: **Bug**. Fill in all mandatory fields.

**Step 3 – Write a clear summary**
The summary should follow the format: **[Feature] [What is broken] [Context]**
- ✅ Good: "Checkout – Payment confirmation email not sent when paying by Visa"
- ❌ Bad: "Email doesn't work"

**Step 4 – Fill in all required fields**

- **Environment:** Specify the exact environment (e.g., Staging v2.3.1, Chrome 115, Windows 11)
- **Steps to Reproduce:** Numbered list — be as precise as possible. Include test account credentials if needed (use the test credentials sheet — never production credentials).
- **Expected Result:** What should have happened according to the requirement/acceptance criteria?
- **Actual Result:** What actually happened? Describe precisely — do not just say "it broke."
- **Severity:** Assign per the classification table above.
- **Priority:** How urgently should this be fixed? (May differ from severity — e.g., a cosmetic bug on the homepage might be high priority)

**Step 5 – Attach evidence**
Always attach:
- Screenshots (annotated with arrows or highlights where relevant)
- Screen recording video (for intermittent or complex interaction bugs)
- Browser console logs (F12 → Console → right-click → Save as)
- Network trace if the issue involves API calls (F12 → Network tab → Export HAR)

**Step 6 – Assign and notify**
Assign to the relevant developer or leave in the Triage queue. Tag the relevant module lead. For Sev-1 and Sev-2 bugs, send a Slack notification to the #project-[name] channel immediately — do not rely on Jira notifications alone.

### 1.4 Bug Lifecycle

New → Triage → In Progress → Fixed → Re-test → Verified/Closed

If a bug is re-opened after being marked Fixed, add a comment explaining why it was not actually resolved. Track re-open rates — high re-open rates indicate a quality issue in the fix process.

### 1.5 Escalation Policy

**Escalation Policy:** Any Sev-1 bug discovered in a Production environment must be reported immediately to the QA Lead, Project Manager, and the on-call engineer. Do not wait for the next daily standup. The P1 Incident Management process must be initiated within 30 minutes of discovery.

---

## 2. Test Data Request

### 2.1 Overview

Quality test data is a prerequisite for meaningful testing. Using production data for testing is strictly prohibited at Nagarro due to GDPR, data privacy regulations, and client contractual obligations. All test data must be synthetically generated or anonymised before use in any non-production environment.

### 2.2 Types of Test Data

| Type | Use Case | Source |
|---|---|---|
| Synthetic Data | Functional and regression testing | Mock data generation scripts |
| Anonymised Production Data | Performance testing with realistic volumes | Data masking tool (automated) |
| Seed Data | Initial environment setup | Configuration scripts in the repository |
| Edge Case Data | Boundary testing | Manually crafted or parameterised |

### 2.3 Requesting Test Data

**Step 1 – Define your data requirements**
Before submitting a request, document:
- What type of data is needed (users, transactions, products, etc.)
- Volume required (e.g., 1,000 user accounts, 10,000 order records)
- Specific attribute constraints (e.g., users aged 18–65, orders in USD only)
- Environment it is needed for (Dev, QA, Staging, UAT)

**Step 2 – Submit a Test Data Request**
Access IT Portal → Test Data Management → New Request. Fill in the data specification form and attach any example data templates.

**Step 3 – Run the generation script**
For standard data types, the self-service data generation tool at **testdata.nagarro.com** can generate and load data directly into the QA or Staging environment within 30 minutes. Follow the instructions on the portal.

**Step 4 – Validate the generated data**
After generation, validate a sample of the data against your specifications. Common issues: date format mismatches, referential integrity violations, or missing required fields.

**Step 5 – Data cleanup after testing**
After your test cycle is complete, use the data cleanup tool to purge test data from shared environments. This prevents data pollution for other teams.

### 2.4 Sensitive Data Handling

If your testing requires data that resembles sensitive information (e.g., national IDs, payment card numbers), you must:
- Use only format-preserving but entirely synthetic values (e.g., valid-format but non-real credit card numbers)
- Never use real personal data
- Store all test credentials in the team's password manager — not in spreadsheets or plain text files

### 2.5 Escalation Policy

**Escalation Policy:** If the data generation script fails to produce valid data after two attempts, raise an IT Priority 2 ticket. If test data is blocking a sprint, flag it as a dependency risk in the daily standup and notify the PM immediately.

---

## 3. Environment Down

### 3.1 Environment Overview

Nagarro uses a multi-environment delivery pipeline to ensure code quality at every stage before production:

| Environment | Purpose | Owner | Access |
|---|---|---|---|
| Development (Dev) | Feature development and unit testing | Dev team | Dev team only |
| QA / SIT | System integration testing | QA team | QA + Dev |
| Staging / Pre-Prod | Full regression, performance, UAT | QA + PM | All project team |
| UAT | Client-driven user acceptance testing | Client + QA | Client + QA |
| Production | Live system | DevOps | Restricted |

### 3.2 Diagnosing an Environment Outage

**Step 1 – Confirm the issue is environment-wide**
Ask at least one other team member if they can access the environment. If it's only you, the issue may be local (VPN, firewall, browser). Try a different browser, clear cache, or reconnect VPN.

**Step 2 – Check the IT Status Page**
Visit **status.nagarro.com** for active incident notifications. If a maintenance window or known outage is listed, this is already being handled — subscribe to updates and wait.

**Step 3 – Check the environment health dashboard**
Each environment has a health dashboard accessible at **envhealth.nagarro.com/[project-code]**. Look for failed services, unhealthy containers, or database connectivity issues.

**Step 4 – Attempt a service restart**
If you have DevOps access and the issue is a failed application service (not infrastructure):
1. SSH into the environment (credentials in the team vault)
2. Run `sudo systemctl restart [service-name]` or use the environment management console in AWS/Azure
3. Monitor logs: `sudo journalctl -u [service-name] -f`

**Step 5 – Log a DevOps support ticket**
If you cannot resolve it yourself within 30 minutes, raise a ticket in IT Portal → DevOps → Environment Issue. Include: environment name, symptoms, steps already attempted, and urgency level. Attach log snippets.

### 3.3 Minimising Impact During Downtime

- Redirect the team to local development, code reviews, test planning, or documentation work
- Communicate the outage proactively to the PM so client commitments can be reassessed
- Log the incident with start time, end time, root cause, and resolution in the Incident Log

### 3.4 Escalation Policy

**Escalation Policy:** If the QA or Staging environment is down for more than 2 hours during a sprint and the DevOps team is unresponsive, escalate to the IT Manager and your Delivery Head. Persistent environment instability should be logged as a project risk.

---

## 4. Automation Failure

### 4.1 Overview

Nagarro's automated testing pipelines are a critical part of our continuous delivery capability. Automated test failures in the CI/CD pipeline must be investigated promptly. Every pipeline failure is a potential quality signal — do not dismiss failures without investigation.

### 4.2 CI/CD Pipeline Overview

Nagarro uses the following stack for test automation:

| Tool | Purpose |
|---|---|
| GitHub Actions / Azure DevOps | CI/CD pipeline orchestration |
| Cypress | End-to-end (E2E) web testing |
| Playwright | Cross-browser E2E testing |
| Jest / Vitest | Unit and integration testing (JavaScript) |
| JUnit / TestNG | Unit testing (Java) |
| Selenium Grid | Legacy browser compatibility testing |
| k6 / JMeter | Performance and load testing |

### 4.3 Diagnosing a Pipeline Failure

**Step 1 – Review the pipeline logs**
In GitHub Actions or Azure DevOps, navigate to the failed run. Click on the failed job and expand the step that failed. Read the full error message carefully before taking any action.

**Step 2 – Categorise the failure**

| Failure Type | Characteristics | Action |
|---|---|---|
| Functional failure | Test assertion fails consistently | Likely a real bug — log a defect |
| Flaky test | Passes sometimes, fails sometimes | Investigate timing/async issues |
| Environment failure | Connection timeout, service unavailable | Retry the pipeline; check environment health |
| Configuration failure | Missing environment variable, wrong credentials | Fix config; do not ignore |
| Infrastructure failure | Pipeline agent down, resource exhaustion | Contact DevOps |

**Step 3 – Reproduce locally**
Run the failing test(s) locally using the same environment variables as the pipeline. If it passes locally, the issue is likely environment or configuration-related. If it fails locally, you have a reproducible failure — debug from there.

**Step 4 – Check for recent code changes**
Use `git log` or the PR history to identify what changed in the last commit that triggered the failure. A targeted diff review often reveals the root cause quickly.

**Step 5 – Fix and verify**
Once the root cause is identified:
- If it's a real bug: Log a defect in Jira and notify the dev team
- If it's a flaky test: Add retry logic and fix race conditions
- If it's a selector change due to UI updates: Update the locators
- If it's a config issue: Update the pipeline environment variables and notify the team

**Step 6 – Document the fix**
Add a comment to the pipeline failure run explaining what was wrong and how it was fixed. Update the team runbook if this is a recurring pattern.

### 4.4 Managing Flaky Tests

Flaky tests undermine confidence in the test suite. Nagarro's policy:
- Any test with a failure rate >10% over a 2-week period must be quarantined (tagged `@quarantine` and excluded from the main pipeline) and fixed within the next sprint.
- The QA Lead maintains a Flaky Test Register — log all flaky tests there.
- Zero-tolerance for known flaky tests blocking CI/CD on the main branch.

### 4.5 Escalation Policy

**Escalation Policy:** If the main branch pipeline is consistently red for more than 24 hours and the team cannot identify the root cause, escalate to the QA Lead and Tech Lead simultaneously. Blocking the main branch is a Sev-2 issue.

---

## 5. Release Sign-Off

### 5.1 Overview

The QA sign-off is the formal gate that authorises deployment of a software release to Production. No deployment to Production should occur without a documented QA sign-off, except in emergency hotfix scenarios (which follow a separate Expedited Release process).

### 5.2 Release Readiness Checklist

Before issuing sign-off, the QA Lead must confirm the following:

**Functional Testing**
- ☐ All user stories in the release scope have been tested against acceptance criteria
- ☐ No open Sev-1 or Sev-2 bugs. All Sev-3+ bugs have been triaged and deferred with client acknowledgement.
- ☐ Regression suite has been executed — pass rate ≥ 98%
- ☐ Exploratory testing has been performed on high-risk areas

**Non-Functional Testing**
- ☐ Performance tests executed — response times within SLA (typically <2s for 95th percentile)
- ☐ Security scan completed — no Critical or High vulnerabilities unmitigated
- ☐ Accessibility scan completed (WCAG 2.1 AA) for public-facing features

**Process and Documentation**
- ☐ All bugs found in this cycle have been logged and have a resolution status
- ☐ Test execution report generated and stored in the Project Hub
- ☐ Release notes reviewed and approved
- ☐ Rollback plan confirmed with DevOps

### 5.3 Sign-Off Process

**Step 1 – Generate the QA Test Execution Report**
From the Test Management tool (TestRail / Zephyr), generate the Test Execution Summary Report. Export as PDF and upload to Project Hub → Releases → [Release Name] → QA Report.

**Step 2 – Complete the Release Readiness Checklist**
Fill in the checklist in the Project Hub release record. Each item requires a Yes/No and a comment for any Nos.

**Step 3 – Confirm with Stakeholders**
For major releases, hold a brief (30-min) Release Readiness Review with the PM, Tech Lead, and DevOps Lead. For minor releases, an email confirmation is sufficient.

**Step 4 – Issue Formal Sign-Off**
In the Project Hub, click **Approve Release for Deployment**. This timestamps the approval and notifies the DevOps team to proceed with the deployment window.

### 5.4 Escalation Policy

**Escalation Policy:** If there is pressure to sign off on a release with known open Sev-1 or Sev-2 bugs, the QA Lead must formally document the risk and obtain written sign-off from both the client and the Nagarro Delivery Head accepting the risk. The QA team should not be pressured into signing off on a defective release.

---

## 6. Production Bug Reported

### 6.1 Overview

Production bugs are the highest-priority issues in the QA world. A bug in production means real users are affected right now. Speed, accuracy, and clear communication are essential. This section covers the P1 Incident Response process for production bugs.

### 6.2 Immediate Response (First 30 Minutes)

**Minute 0–5: Triage**
- Reproduce the issue on the production environment (using a test/canary account — never disturb live user data)
- Assess the blast radius: How many users are affected? What data/transactions are impacted?
- Assign a severity level immediately (default to Sev-1 until you can confirm otherwise)

**Minute 5–15: Notify**
- Post in the #incidents Slack channel immediately with: What is broken, How many users affected, Steps to reproduce, Initial severity
- Tag: Project PM, Tech Lead, QA Lead, DevOps Lead, Account Manager
- For Sev-1 issues: Phone the on-call engineer. Do not rely on Slack alone.

**Minute 15–30: Contain**
- Assess whether an immediate rollback is safer than a hotfix
- If the bug involves data corruption or security, disable the affected feature immediately (feature flag, firewall rule, or full rollback)
- Communicate to the client's technical contact — do not let them find out from their end users

### 6.3 Investigation and Resolution

**Step 1 – Create a Sev-1 Jira ticket**
Even in a crisis, proper documentation must be maintained. Create the Jira ticket concurrently with the response — it serves as the incident log.

**Step 2 – Root cause analysis**
Pull application logs, database logs, and deployment records for the time window when the bug first appeared. Correlate with recent deployments using the deployment history in the DevOps pipeline.

**Step 3 – Fix strategy decision**
- **Hotfix:** A minimal targeted fix deployed directly to production. Requires expedited QA validation (smoke test on staging minimum) and Delivery Head approval.
- **Rollback:** Revert to the last known-good version. Faster, but may lose recent legitimate changes.

**Step 4 – Deploy and validate**
After the fix is deployed, the QA team must immediately run a smoke test on production to confirm the fix is working and no new issues have been introduced.

**Step 5 – Post-Incident Review (PIR)**
Within 5 business days of resolution, conduct a blameless PIR with all involved parties. Document:
- Timeline of events
- Root cause
- Why existing tests didn't catch it
- What process changes will prevent recurrence

The PIR report must be filed in the Project Hub and shared with the client.

### 6.4 Escalation Policy

**Escalation Policy:** Any production incident involving personal data exposure, financial loss, or regulatory implications must be escalated to the CISO and Legal team within 1 hour of discovery. Depending on the jurisdiction, a mandatory breach notification may be required within 72 hours (GDPR Article 33). Do not delay this escalation.

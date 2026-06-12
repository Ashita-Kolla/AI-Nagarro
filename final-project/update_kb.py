import json, sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open('My workflow.json', encoding='utf-8'))

# Full expanded KB with comprehensive, natural-language symptoms for every entry
EXPANDED_KB = [
  # ── FINANCE ─────────────────────────────────────────────────────────────
  {
    "id": "fin-001",
    "reference_link": "/kb/Finance_Manual.html#invoice-generation",
    "issue": "Invoice generation",
    "symptoms": [
      "invoice", "generate invoice", "create invoice", "how to invoice",
      "billing", "send bill", "raise invoice", "how do i invoice",
      "billing request", "make invoice", "invoice customer", "issue invoice",
      "how to generate invoice", "how to create invoice"
    ],
    "steps": [
      "Collect customer details",
      "Validate billing information",
      "Generate invoice in ERP system",
      "Send invoice via email"
    ],
    "escalate_if": "Customer information incomplete",
    "domain": "FINANCE"
  },
  {
    "id": "fin-002",
    "reference_link": "/kb/Finance_Manual.html#reimbursement-request",
    "issue": "Reimbursement request",
    "symptoms": [
      "reimbursement", "expense claim", "claim expense", "travel expense",
      "how to claim", "get reimbursed", "submit expense", "expense report",
      "out of pocket", "travel reimbursement", "expense refund",
      "paid out of pocket", "expenses not paid", "need reimbursement"
    ],
    "steps": [
      "Upload receipts to the Expense Portal",
      "Validate policy compliance for limits",
      "Submit for manager approval",
      "Wait for next payment cycle"
    ],
    "escalate_if": "Required documentation missing",
    "domain": "FINANCE"
  },
  {
    "id": "fin-003",
    "reference_link": "/kb/Finance_Manual.html#payment-status-inquiry",
    "issue": "Payment status inquiry",
    "symptoms": [
      "payment status", "check payment", "payment pending", "where is my payment",
      "vendor payment", "invoice paid", "when will i get paid", "payment not received"
    ],
    "steps": [
      "Check payment records in ERP",
      "Verify payment schedule (Net 30/60)",
      "Provide status update to vendor"
    ],
    "escalate_if": "Payment discrepancy detected",
    "domain": "FINANCE"
  },
  {
    "id": "fin-004",
    "reference_link": "/kb/Finance_Manual.html#corporate-credit-card",
    "issue": "Corporate credit card",
    "symptoms": [
      "credit card", "corporate card", "company card", "card limit",
      "lost card", "new credit card", "request card", "card request"
    ],
    "steps": [
      "Fill out the corporate card request form",
      "Obtain VP approval",
      "Submit to Finance operations",
      "Card will be mailed in 7-10 days"
    ],
    "escalate_if": "Card lost or stolen (report immediately)",
    "domain": "FINANCE"
  },
  {
    "id": "fin-005",
    "reference_link": "/kb/Finance_Manual.html#budget-approval",
    "issue": "Budget approval",
    "symptoms": [
      "budget", "budget approval", "spend limit", "capex", "opex",
      "get budget approved", "request budget", "budget request"
    ],
    "steps": [
      "Review department budget allocation",
      "Verify requested spend against remaining budget",
      "Route to Finance Director for sign-off"
    ],
    "escalate_if": "Budget limit exceeded",
    "domain": "FINANCE"
  },

  # ── HR ───────────────────────────────────────────────────────────────────
  {
    "id": "hr-001",
    "reference_link": "/kb/HR_Manual.html#salary-not-credited",
    "issue": "Salary not credited",
    "symptoms": [
      "salary", "salary not received", "salary missing", "no salary",
      "pay not received", "paycheck missing", "salary not credited",
      "salary issue", "did not receive salary", "where is my salary",
      "haven't received salary", "salary not in account"
    ],
    "steps": [
      "Verify today is the exact payroll date",
      "Check registered bank account in HR portal",
      "Review payroll records",
      "Create payroll investigation case"
    ],
    "escalate_if": "Salary still missing after payroll verification",
    "domain": "HR"
  },
  {
    "id": "hr-002",
    "reference_link": "/kb/HR_Manual.html#payslip-request",
    "issue": "Payslip request",
    "symptoms": [
      "payslip", "salary slip", "pay stub", "paystub", "download payslip",
      "get payslip", "view payslip", "payslip not available",
      "need payslip", "salary document"
    ],
    "steps": [
      "Log in to the HR Self-Service Portal",
      "Navigate to the 'Compensation' tab",
      "Select the desired month and click 'Download PDF'"
    ],
    "escalate_if": "Payslip unavailable in system",
    "domain": "HR"
  },
  {
    "id": "hr-003",
    "reference_link": "/kb/HR_Manual.html#leave-request",
    "issue": "Leave request",
    "symptoms": [
      "leave", "apply for leave", "apply leave", "leave application",
      "request leave", "how do i apply for leave", "how to apply for leave",
      "how to apply leave", "take leave", "take a day off", "day off",
      "vacation", "annual leave", "sick leave", "pto", "time off",
      "holiday request", "leave request", "half day", "medical leave",
      "request time off", "apply for time off", "casual leave",
      "how to take leave", "how to request leave"
    ],
    "steps": [
      "Check leave balance in the portal",
      "Select requested dates in the calendar",
      "Submit manager approval request",
      "Update leave records"
    ],
    "escalate_if": "Leave balance insufficient",
    "domain": "HR"
  },
  {
    "id": "hr-004",
    "reference_link": "/kb/HR_Manual.html#benefits-and-insurance",
    "issue": "Benefits and Insurance",
    "symptoms": [
      "benefits", "insurance", "health insurance", "dental", "enrollment",
      "401k", "medical benefits", "how to enroll", "employee benefits"
    ],
    "steps": [
      "Go to the Benefits portal",
      "Check active enrollments",
      "Review open enrollment period guidelines",
      "Contact provider for direct queries"
    ],
    "escalate_if": "Enrollment period missed due to technical error",
    "domain": "HR"
  },
  {
    "id": "hr-005",
    "reference_link": "/kb/HR_Manual.html#performance-review",
    "issue": "Performance review",
    "symptoms": [
      "performance review", "appraisal", "feedback cycle", "goals",
      "performance feedback", "how does review work", "performance appraisal"
    ],
    "steps": [
      "Access the Performance Management system",
      "Complete your self-evaluation",
      "Schedule a 1-on-1 with your manager",
      "Sign off on the final review"
    ],
    "escalate_if": "Manager is on long-term leave",
    "domain": "HR"
  },
  {
    "id": "hr-006",
    "reference_link": "/kb/HR_Manual.html#workplace-harassment-or-conflict",
    "issue": "Workplace harassment or conflict",
    "symptoms": [
      "harassment", "conflict", "toxic workplace", "report manager",
      "dispute", "workplace issue", "hostile environment", "bullying"
    ],
    "steps": [
      "File a confidential report via the Employee Relations portal",
      "HR Business Partner will contact you within 24 hours",
      "Mediation or formal investigation will be initiated"
    ],
    "escalate_if": "Immediate safety concern",
    "domain": "HR"
  },

  # ── IT ───────────────────────────────────────────────────────────────────
  {
    "id": "it-001",
    "reference_link": "/kb/IT_Manual.html#password-reset",
    "issue": "Password reset",
    "symptoms": [
      "password", "reset password", "forgot password", "can't login",
      "locked out", "account locked", "password expired", "change password",
      "how to reset password", "login issue", "access denied"
    ],
    "steps": [
      "Go to the IT self-service portal",
      "Click 'Forgot Password'",
      "Verify your identity via MFA",
      "Set a new password"
    ],
    "escalate_if": "Account locked after multiple failed attempts",
    "domain": "IT"
  },
  {
    "id": "it-002",
    "reference_link": "/kb/IT_Manual.html#vpn-issues",
    "issue": "VPN issues",
    "symptoms": [
      "vpn", "vpn not working", "can't connect vpn", "vpn error",
      "remote access", "vpn disconnects", "vpn slow", "connect to vpn"
    ],
    "steps": [
      "Restart the VPN client",
      "Check your internet connection",
      "Reinstall the VPN client if issue persists",
      "Contact IT if VPN certificate is expired"
    ],
    "escalate_if": "VPN certificate expired",
    "domain": "IT"
  },
  {
    "id": "it-003",
    "reference_link": "/kb/IT_Manual.html#software-installation",
    "issue": "Software installation",
    "symptoms": [
      "install software", "need software", "request software",
      "software request", "new application", "install app",
      "software access", "how to install"
    ],
    "steps": [
      "Submit a software request via the IT portal",
      "IT will verify license availability",
      "Software pushed remotely to your machine within 24h"
    ],
    "escalate_if": "No license available",
    "domain": "IT"
  },
  {
    "id": "it-004",
    "reference_link": "/kb/IT_Manual.html#wifi-connectivity",
    "issue": "Wifi connectivity",
    "symptoms": [
      "wifi", "no wifi", "wifi not working", "internet not working",
      "network issue", "can't connect to internet", "no internet",
      "wifi slow", "network down", "connectivity issue"
    ],
    "steps": [
      "Restart your device",
      "Forget and reconnect to the corporate WiFi (NagarroNet)",
      "Check if other devices have the same issue",
      "Contact IT if issue persists"
    ],
    "escalate_if": "Network-wide outage",
    "domain": "IT"
  },
  {
    "id": "it-005",
    "reference_link": "/kb/IT_Manual.html#hardware-request",
    "issue": "Hardware request",
    "symptoms": [
      "hardware", "new laptop", "broken mouse", "new monitor",
      "keyboard broken", "headset", "docking station", "equipment request",
      "request hardware", "need equipment"
    ],
    "steps": [
      "Fill out the hardware request form on the intranet",
      "Wait for manager approval",
      "Hardware will be shipped within 3-5 business days"
    ],
    "escalate_if": "Urgent replacement needed",
    "domain": "IT"
  },
  {
    "id": "it-006",
    "reference_link": "/kb/IT_Manual.html#blue-screen",
    "issue": "Blue screen",
    "symptoms": [
      "blue screen", "bsod", "system crash", "windows crashed",
      "computer crashed", "laptop crashed", "death screen"
    ],
    "steps": [
      "Take a photo of the error code on the blue screen",
      "Hold the power button to force shutdown",
      "Turn the laptop back on",
      "Check for Windows updates"
    ],
    "escalate_if": "Blue screen happens repeatedly",
    "domain": "IT"
  },

  # ── PM ───────────────────────────────────────────────────────────────────
  {
    "id": "pm-001",
    "reference_link": "/kb/PM_Manual.html#project-status-request",
    "issue": "Project status request",
    "symptoms": [
      "project status", "project update", "status report",
      "progress update", "project timeline", "where is the project"
    ],
    "steps": [
      "Retrieve project metrics from the dashboard",
      "Check milestone completion status",
      "Generate weekly status summary",
      "Share PDF report with requester"
    ],
    "escalate_if": "Project data unavailable or corrupt",
    "domain": "PM"
  },
  {
    "id": "pm-002",
    "reference_link": "/kb/PM_Manual.html#resource-allocation",
    "issue": "Resource allocation",
    "symptoms": [
      "resource", "resource allocation", "assign task", "allocate work",
      "need developer", "resource shortage", "team capacity"
    ],
    "steps": [
      "Review current team capacity map",
      "Identify available resources with matching skills",
      "Re-prioritize lower impact tasks if necessary",
      "Assign owner to the task"
    ],
    "escalate_if": "No suitable resource available globally",
    "domain": "PM"
  },
  {
    "id": "pm-003",
    "reference_link": "/kb/PM_Manual.html#requirement-clarification",
    "issue": "Requirement clarification",
    "symptoms": [
      "requirements", "unclear requirement", "need clarification",
      "scope definition", "requirements not clear"
    ],
    "steps": [
      "Review requirement document (PRD)",
      "Identify ambiguities and edge cases",
      "Schedule clarification meeting with product owner",
      "Update requirements and notify team"
    ],
    "escalate_if": "Business owner unavailable for > 3 days",
    "domain": "PM"
  },
  {
    "id": "pm-004",
    "reference_link": "/kb/PM_Manual.html#scope-creep",
    "issue": "Scope creep",
    "symptoms": [
      "scope creep", "scope change", "change request", "new feature added",
      "timeline impact", "requirements changing", "project scope changing"
    ],
    "steps": [
      "Document the new requested changes",
      "Estimate the impact on timeline and budget",
      "Submit formal Change Request to stakeholders",
      "Wait for approval before starting work"
    ],
    "escalate_if": "Client refuses to adjust timeline",
    "domain": "PM"
  },
  {
    "id": "pm-005",
    "reference_link": "/kb/PM_Manual.html#risk-escalation",
    "issue": "Risk escalation",
    "symptoms": [
      "project risk", "risk", "blocker", "critical delay", "dependency failed",
      "project blocker", "risk escalation"
    ],
    "steps": [
      "Log the risk in the project risk register",
      "Assess probability and impact (High/Med/Low)",
      "Formulate a mitigation plan",
      "Notify the project sponsor immediately"
    ],
    "escalate_if": "Risk materializes into an issue",
    "domain": "PM"
  },
  {
    "id": "pm-006",
    "reference_link": "/kb/PM_Manual.html#stakeholder-meeting-scheduling",
    "issue": "Stakeholder meeting scheduling",
    "symptoms": [
      "schedule meeting", "meeting", "stakeholder call", "book meeting",
      "set up call", "align stakeholders", "meeting invite", "calendar invite"
    ],
    "steps": [
      "Identify all required attendees and their time zones",
      "Check calendar availability using the scheduling tool",
      "Create and send the calendar invite with an agenda",
      "Share pre-read materials at least 24 hours before",
      "Send a reminder the day before the meeting"
    ],
    "escalate_if": "Key decision-maker is unavailable for more than 1 week",
    "domain": "PM"
  },

  # ── QA ───────────────────────────────────────────────────────────────────
  {
    "id": "qa-001",
    "reference_link": "/kb/QA_Manual.html#bug-report",
    "issue": "Bug report",
    "symptoms": [
      "bug", "report bug", "application bug", "unexpected behavior",
      "error", "broken feature", "glitch", "how to report bug",
      "found a bug", "something is broken", "it's not working"
    ],
    "steps": [
      "Capture issue description",
      "Collect screenshots and browser console logs",
      "Record step-by-step reproduction instructions",
      "Create bug ticket in Jira"
    ],
    "escalate_if": "Critical production issue",
    "domain": "QA"
  },
  {
    "id": "qa-002",
    "reference_link": "/kb/QA_Manual.html#test-data-request",
    "issue": "Test data request",
    "symptoms": [
      "test data", "need test data", "dummy accounts", "mock data",
      "sandbox data", "fake data", "sample data"
    ],
    "steps": [
      "Identify required data parameters",
      "Run the mock data generation script",
      "Verify data loads in the sandbox environment",
      "Provide data set IDs to requester"
    ],
    "escalate_if": "Script fails to generate valid data",
    "domain": "QA"
  },
  {
    "id": "qa-003",
    "reference_link": "/kb/QA_Manual.html#environment-down",
    "issue": "Environment down",
    "symptoms": [
      "environment down", "staging down", "staging broken",
      "test environment down", "can't access uat", "server is down",
      "uat not working", "test server down"
    ],
    "steps": [
      "Check environment health dashboard",
      "Restart the staging server instances",
      "Clear the environment cache",
      "Notify the DevOps team if unresolved"
    ],
    "escalate_if": "Environment remains down after 30 mins",
    "domain": "QA"
  },
  {
    "id": "qa-004",
    "reference_link": "/kb/QA_Manual.html#automation-failure",
    "issue": "Automation failure",
    "symptoms": [
      "automation failure", "automation script failed", "cypress failing",
      "ci/cd pipeline red", "tests failing", "pipeline failed"
    ],
    "steps": [
      "Review the CI/CD pipeline logs",
      "Check for flakiness or network timeouts",
      "Run the specific failing test locally",
      "Update selectors if UI changed"
    ],
    "escalate_if": "Core functionality is actually broken",
    "domain": "QA"
  },
  {
    "id": "qa-005",
    "reference_link": "/kb/QA_Manual.html#release-sign-off",
    "issue": "Release sign-off",
    "symptoms": [
      "release sign-off", "release", "production deployment", "qa approval",
      "sign off release", "ready to release", "go live"
    ],
    "steps": [
      "Review all test run results for the release branch",
      "Verify no open Sev-1 or Sev-2 bugs",
      "Generate the QA summary report",
      "Provide formal sign-off in the release channel"
    ],
    "escalate_if": "Blocking bugs remain open",
    "domain": "QA"
  },
  {
    "id": "qa-006",
    "reference_link": "/kb/QA_Manual.html#production-bug-reported",
    "issue": "Production bug reported",
    "symptoms": [
      "production bug", "bug in production", "prod is broken",
      "live site error", "customer reported bug", "critical bug",
      "p1 bug", "production is down"
    ],
    "steps": [
      "Confirm reproduction on production environment",
      "Assess severity and customer impact",
      "Create a Sev-1 Jira ticket and notify the on-call engineer",
      "Implement hotfix or roll back the last deployment",
      "Post a status update in the #incidents channel"
    ],
    "escalate_if": "Revenue or data loss is occurring",
    "domain": "QA"
  }
]

# Now inject into the workflow
for n in data['nodes']:
    if n['name'] == 'Knowledge Resolver Vector Search':
        js = n['parameters']['jsCode']
        
        # Replace the entire kb array
        start = js.index('const kb = [')
        end = js.index('];', start) + 2
        
        new_kb = 'const kb = ' + json.dumps(EXPANDED_KB, indent=2, ensure_ascii=False) + ';'
        js = js[:start] + new_kb + js[end:]
        
        # Also lower the threshold from 0.75 to 0.40 for strict kb-first behaviour
        js = js.replace('const MATCH_THRESHOLD = 0.75', 'const MATCH_THRESHOLD = 0.40')
        # Also handle if threshold is inline
        import re
        js = re.sub(r'score\s*>=\s*0\.75', 'score >= 0.40', js)
        js = re.sub(r'const MATCH_THRESHOLD\s*=\s*[\d.]+', 'const MATCH_THRESHOLD = 0.40', js)
        
        n['parameters']['jsCode'] = js
        print('KB updated successfully!')
        print(f'Total entries: {len(EXPANDED_KB)}')
        break

json.dump(data, open('My workflow.json', 'w', encoding='utf-8'), indent=2)
print('workflow.json saved.')

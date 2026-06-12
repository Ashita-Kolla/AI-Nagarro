# Finance Operations Manual

**Document Owner:** Finance Operations Team  
**Last Updated:** June 2026  
**Version:** 3.2  
**Classification:** Internal Use Only

---

## Overview

This manual provides comprehensive guidance for all finance-related processes at Nagarro. It is intended for employees, managers, and finance team members who need to understand, initiate, or process financial transactions, approvals, and inquiries. All policies described herein are aligned with Nagarro's internal financial controls and regulatory compliance requirements.

For urgent finance matters outside business hours, contact the Finance on-call team at **finance-oncall@nagarro.com**.

---

## 1. Invoice Generation

### 1.1 Purpose and Scope

Invoice generation is a critical business process used to formally request payment from clients for services rendered or goods delivered. Every invoice issued by Nagarro must comply with local tax regulations, client contract terms, and Nagarro's internal billing policies. Incorrect or incomplete invoices can delay payment cycles and negatively impact cash flow.

This section applies to all client-facing project managers, delivery leads, and finance business partners who participate in the billing lifecycle.

### 1.2 Prerequisites Before Raising an Invoice

Before initiating an invoice, you must verify the following:

- **Contract or SOW is active:** Confirm the signed Statement of Work (SOW) or Master Service Agreement (MSA) is on file and within the valid date range.
- **Deliverables confirmed:** Obtain written confirmation from the client (email or project tool) that the milestone or deliverable has been accepted.
- **Billing schedule alignment:** Ensure the invoice date falls within the agreed billing cycle (e.g., monthly retainer on the 1st, milestone on completion).
- **PO Number available:** Most enterprise clients require a valid Purchase Order number on each invoice. Obtain this from the client's procurement contact in advance.

### 1.3 Step-by-Step Invoice Process

**Step 1 – Collect and validate customer details**
Access the client profile in the ERP system (SAP / Oracle). Verify the legal entity name, billing address, tax identification number (TIN/VAT), and designated accounts payable contact. Any discrepancy between the ERP record and the client's current details must be resolved before proceeding.

**Step 2 – Confirm billable amounts**
Pull the approved timesheets and/or expense reports for the billing period. Cross-reference against the agreed rate card in the SOW. Ensure no unbilled amounts from prior periods are outstanding without a formal amendment.

**Step 3 – Create the invoice in the ERP system**
Navigate to the Billing module in SAP/Oracle. Select the correct project code and cost center. Enter the invoice lines, including description, quantity, rate, currency, and applicable taxes. Use the standard Nagarro invoice template — do not create ad-hoc documents in Word or Excel.

**Step 4 – Internal review and approval**
All invoices above $10,000 USD require approval from the Delivery Head before sending. Invoices above $50,000 USD require Finance Controller sign-off. Route the invoice draft via the Workflow Approval system, not via email.

**Step 5 – Send the invoice to the client**
Once approved, the system will auto-generate a PDF and send it to the client's designated AP email. Retain a copy of the sent confirmation. For clients requiring portal submission (e.g., Ariba, Coupa), upload manually and record the portal reference number in the ERP.

**Step 6 – Track and follow up**
Set a payment follow-up reminder for T+5 days before the invoice due date. Log all client communication regarding the invoice in the ERP activity log.

### 1.4 Common Issues and Resolutions

| Issue | Resolution |
|---|---|
| Client requests invoice correction | Issue a Credit Note and re-raise the corrected invoice within 2 business days |
| PO number not yet issued | Hold the invoice and notify the client PM; do not send without a PO |
| Tax rate discrepancy | Consult the Tax team at tax@nagarro.com before issuing |
| ERP system error | Contact IT Helpdesk and cc finance-ops@nagarro.com |

### 1.5 Escalation Policy

**Escalation Policy:** Escalate to the Finance Controller if: (1) the client disputes the invoice and no resolution is reached within 5 business days; (2) the invoice amount exceeds the project PO by more than 5%; or (3) the client is more than 45 days overdue without a payment plan in place.

---

## 2. Reimbursement Requests

### 2.1 Policy Overview

Nagarro reimburses employees for legitimate, pre-approved business expenses incurred while performing their duties. Reimbursement is governed by the **Global Expense Policy v5.1**, available on the intranet. Employees are responsible for ensuring their expenses comply with the policy before submitting. Non-compliant expenses will be rejected without exception.

Reimbursements are processed in the bi-weekly payroll cycle. Submissions received by the 10th of the month will be processed in that month's second payroll run.

### 2.2 Eligible Expenses

The following categories are eligible for reimbursement with proper documentation:

- **Travel:** Flights (economy class for trips under 8 hours), trains, taxis, and car rentals. First or business class requires VP-level pre-approval.
- **Accommodation:** Hotels up to the regional per-diem rate. See Appendix A for current per-diem limits by city.
- **Meals:** Up to $75/day for international travel, $40/day for domestic travel, with itemized receipts.
- **Client entertainment:** Up to $150/person with business purpose noted and manager approval.
- **Home office:** Monthly internet stipend up to $50 for approved remote workers.
- **Training and certifications:** Up to $2,000/year per employee with manager pre-approval.

### 2.3 Submission Process

**Step 1 – Collect all receipts**
Receipts must be itemized and legible. Credit card statements alone are not accepted. For cash expenses, a self-certification form is required for amounts over $25.

**Step 2 – Log into the Expense Portal**
Access via intranet → Finance → Expense Management → New Claim. Select the correct expense category, project code, and cost center for each line item.

**Step 3 – Upload receipts and complete all mandatory fields**
Attach original receipts (PDF or JPEG, max 5MB each). Fill in the business purpose field with a specific description (e.g., "Client dinner with Accenture team during Q2 business review" — not just "dinner").

**Step 4 – Submit for manager approval**
The system routes the claim to your direct manager. Managers must approve or reject within 3 business days. If unapproved after 5 business days, it auto-escalates to the Manager's manager.

**Step 5 – Finance audit and processing**
The Finance team conducts a sample audit of 10% of all claims. Selected claims may require additional documentation. Payment is issued via payroll or a separate bank transfer for larger amounts.

### 2.4 Policy Limits Reference Table

| Category | Domestic Limit | International Limit |
|---|---|---|
| Flights | Economy, any amount | Economy under 8h / Business over 8h with approval |
| Hotel | $150/night | $250/night |
| Meals per day | $40 | $75 |
| Ground transport | Actual cost | Actual cost |
| Client entertainment | $150/person | $200/person |

### 2.5 Escalation Policy

**Escalation Policy:** Escalate to HR/Finance Business Partner if: (1) your manager is unresponsive for over 5 business days; (2) your claim is rejected and you believe it was wrongfully denied; or (3) the expense is related to a sensitive matter such as a confidential client engagement.

---

## 3. Payment Status Inquiry

### 3.1 Overview

This section covers how to check the status of an outgoing vendor payment or an employee reimbursement. Nagarro's standard payment terms are Net-30 for most vendors, unless otherwise specified in the contract.

### 3.2 Checking Payment Status

**Step 1 – Access the Finance Portal**
Navigate to Finance Portal → Payments → Search. Enter the invoice number, vendor name, or payment reference.

**Step 2 – Review payment schedule**
Check the scheduled payment date. Payments are processed on the 15th and 28th of each month. If the invoice was approved after the cutoff, it will be included in the next cycle.

**Step 3 – Confirm bank details are correct**
If a payment is overdue, verify that the vendor's bank details on file are correct and match the invoice. Incorrect account numbers are the most common cause of payment delays.

**Step 4 – Contact Finance if still unresolved**
Log a query via the Finance Helpdesk portal with the invoice number, amount, and expected payment date. You will receive a response within 2 business days.

### 3.3 Escalation Policy

**Escalation Policy:** If payment is more than 15 days past the due date with no communication from Finance, escalate to the Finance Controller with full invoice documentation.

---

## 4. Corporate Credit Card

### 4.1 Eligibility and Purpose

Nagarro corporate credit cards are issued to employees who regularly incur business expenses of $500/month or more. Cards are issued in the employee's name and are for business use only. Personal charges are strictly prohibited and will result in disciplinary action.

### 4.2 Application Process

**Step 1 – Submit the request form**
Download the Corporate Card Request Form from the intranet. Complete all sections including your employee ID, department, cost center, and justification for the card.

**Step 2 – Obtain VP-level approval**
Have your Vice President or department head sign the form digitally via DocuSign.

**Step 3 – Submit to Finance Operations**
Email the signed form to corporate-cards@nagarro.com. Processing takes 5–7 business days.

**Step 4 – Card activation**
Your card will be mailed to your registered office address. Activate online using the link in the welcome email. Set up your online account and enroll in the spend management portal (Concur/SAP Concur).

### 4.3 Usage Policies

- All transactions must be reconciled in Concur within 5 business days of the transaction.
- Receipts must be attached to each transaction record.
- Cards must not be shared under any circumstances.
- Cash advances on the corporate card are not permitted.

### 4.4 Escalation Policy

**Escalation Policy:** For lost or stolen cards, call the card issuer's emergency hotline immediately (number on back of card) and notify Security at security@nagarro.com within 1 hour.

---

## 5. Budget Approval

### 5.1 Overview

All departmental expenditures not covered by pre-approved operating budgets require a formal Budget Approval before commitment. This ensures financial controls are maintained and spending is aligned with company strategy.

### 5.2 Budget Types

- **OPEX (Operating Expenditure):** Day-to-day operational costs such as software subscriptions, travel, and contractor fees.
- **CAPEX (Capital Expenditure):** Long-term investments such as hardware purchases, office equipment, or infrastructure upgrades above $5,000.
- **Project Budget:** Dedicated budgets tied to a specific client or internal project, governed by the approved Project Financial Plan.

### 5.3 Approval Process

**Step 1 – Review your department's current budget**
Access the Budget Dashboard in the Finance Portal. Review remaining budget against planned spend for the quarter.

**Step 2 – Complete the Budget Request Form**
Fill in the request amount, business justification, vendor details, and expected ROI or cost benefit. Attach supporting quotes or proposals.

**Step 3 – Route for approval**
- Up to $5,000: Manager approval
- $5,001–$25,000: Department VP approval
- $25,001–$100,000: CFO approval
- Over $100,000: Board approval required

**Step 4 – Procurement**
Once approved, forward the approval confirmation to procurement@nagarro.com to begin the vendor onboarding and purchase order process.

### 5.4 Escalation Policy

**Escalation Policy:** If a budget request is urgent and approval is delayed beyond 5 business days, escalate to your Finance Business Partner. Committing expenditure without approval is a serious policy violation.

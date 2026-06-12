# IT Support Operations Manual

**Document Owner:** IT Operations & Infrastructure Team  
**Last Updated:** June 2026  
**Version:** 5.0  
**Classification:** Internal Use Only

---

## Overview

This manual is the primary reference for all IT-related support requests, self-service procedures, and escalation paths at Nagarro. It covers the most common issues employees encounter with hardware, software, network connectivity, and access management. Following the procedures in this document will ensure the fastest possible resolution of your IT issues.

For critical production incidents, contact the IT Service Desk immediately: **+1 800 NAGARRO** | **it-helpdesk@nagarro.com** | Ticket Portal: **it.nagarro.com**

**SLA Overview:**
- Priority 1 (Critical): 1-hour response, 4-hour resolution
- Priority 2 (High): 4-hour response, 8-hour resolution
- Priority 3 (Medium): 8-hour response, 2-day resolution
- Priority 4 (Low): 24-hour response, 5-day resolution

---

## 1. Password Reset

### 1.1 Overview

Account access issues are among the most common IT requests. Nagarro uses a Single Sign-On (SSO) system powered by Okta, which means a single set of credentials provides access to all integrated applications including email, Jira, Confluence, HR Portal, ERP, and VPN.

Passwords expire every **90 days**. You will receive reminder emails at 14 days, 7 days, and 1 day before expiry. Resetting your password promptly prevents account lockout.

### 1.2 Self-Service Password Reset

**Step 1 – Navigate to the password reset portal**
Open a browser and go to **password.nagarro.com** (accessible without VPN). Click **"Forgot Password / Reset Password"**.

**Step 2 – Verify your identity**
You will be prompted to verify via one of the following:
- **Authenticator App (Okta Verify):** Approve the push notification on your mobile device.
- **SMS OTP:** A 6-digit code will be sent to your registered mobile number.
- **Security Questions:** Answer 2 of your 3 pre-set security questions.

**Step 3 – Set your new password**
Your new password must meet the following requirements:
- Minimum 12 characters
- At least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character
- Cannot be the same as your last 10 passwords
- Cannot contain your name or employee ID

**Step 4 – Re-authenticate all active sessions**
After resetting, you will be signed out of all active sessions. Re-login to all applications using your new credentials. If your VPN client doesn't accept the new password immediately, wait 5 minutes and try again.

### 1.3 Account Lockout

Your account will be locked after **5 consecutive failed login attempts**. To unlock:

1. Go to password.nagarro.com and click "Unlock Account"
2. Verify your identity using MFA (as above)
3. Your account will be unlocked instantly

If MFA is also unavailable (e.g., lost phone), contact the IT Service Desk with your employee ID and a photo ID for identity verification.

### 1.4 MFA Device Management

To add, remove, or replace an MFA device:
1. Log in to accounts.nagarro.com
2. Navigate to Security → Authenticators
3. Add a new authenticator or remove an existing one

If you lose your MFA device before adding a backup, contact the IT Service Desk — they will perform identity verification and temporarily disable MFA for one login to allow you to set up a new device.

### 1.5 Escalation Policy

**Escalation Policy:** If the self-service reset portal fails or your account cannot be unlocked via self-service, contact the IT Service Desk immediately (Priority 2). Do not share your credentials with anyone, including IT staff — legitimate IT will never ask for your password.

---

## 2. VPN Issues

### 2.1 Overview

Nagarro uses **GlobalProtect VPN** (Palo Alto Networks) for secure remote access to internal systems, development environments, and corporate applications. VPN connectivity is required for all remote work involving access to sensitive systems or internal tools.

### 2.2 System Requirements

| OS | Minimum Version |
|---|---|
| Windows | Windows 10 version 1909 or later |
| macOS | macOS 11 (Big Sur) or later |
| Linux | Ubuntu 20.04 LTS or later |

### 2.3 Common VPN Issues and Solutions

**Issue: VPN client will not connect — "Gateway not responding"**
1. Check your internet connection by opening a public website (e.g., google.com)
2. Restart your router if on home WiFi
3. Disable any third-party firewall or antivirus temporarily to test
4. Try connecting via mobile hotspot to isolate a network-level block
5. Restart the GlobalProtect service: Task Manager → Services → PanGPS → Restart

**Issue: VPN connects but cannot access internal sites**
1. Disconnect and reconnect the VPN
2. Flush DNS cache: Open Command Prompt as Administrator → `ipconfig /flushdns`
3. Try accessing by IP address instead of hostname to rule out DNS issues
4. Check if a specific service is down via the IT Status Page (status.nagarro.com)

**Issue: VPN certificate expired**
This requires IT intervention. Do not attempt to install certificates manually. Contact the IT Service Desk with your device serial number. A technician will remotely push the updated certificate.

**Issue: VPN disconnects repeatedly**
1. Disable auto-sleep settings for your network adapter: Control Panel → Device Manager → Network Adapters → Right-click your adapter → Power Management → Uncheck "Allow the computer to turn off this device to save power"
2. Set VPN reconnect timer: GlobalProtect Settings → Advanced → Connection → Enable "Auto-reconnect"
3. If on corporate WiFi, try switching to a different access point

### 2.4 VPN Client Installation

For new devices or after OS reinstalls:
1. Navigate to **vpn-download.nagarro.com** (internal network or MDM-managed device)
2. Download the GlobalProtect installer for your OS
3. Install and enter the gateway address: **vpn.nagarro.com**
4. Log in with your corporate SSO credentials
5. Approve the MFA prompt

### 2.5 Escalation Policy

**Escalation Policy:** If VPN is completely inaccessible and you need to work remotely on a business-critical task, contact the IT Service Desk (Priority 1). Temporary access via a jump server can be provisioned within 2 hours.

---

## 3. Software Installation

### 3.1 Overview

Nagarro manages software through a centralised MDM (Mobile Device Management) system using **Microsoft Intune** (Windows) and **Jamf Pro** (macOS). Standard software is pre-approved and available via the Software Centre. Non-standard software requires a formal request and approval.

### 3.2 Approved Software Catalogue

The following software is pre-approved and available for self-installation via Software Centre without additional approval:

- **Development:** VS Code, IntelliJ IDEA CE, Git, Node.js, Python, Docker Desktop
- **Productivity:** Microsoft 365 (Office), Slack, Zoom, Google Chrome, Firefox
- **Collaboration:** Confluence, Jira, Miro, Figma (viewer)
- **Security:** Antivirus (auto-deployed), LastPass

### 3.3 Self-Service Installation (Approved Software)

**Step 1 – Open Software Centre**
Windows: Start Menu → Microsoft Intune Company Portal  
macOS: Applications → Managed Software Centre

**Step 2 – Browse or search**
Find the application in the catalogue. Click **Install**. The software will be downloaded and installed silently in the background — no administrator password required.

**Step 3 – Confirm installation**
Most installations complete within 15 minutes. You may need to restart the application or your machine afterward.

### 3.4 Non-Standard Software Request

For software not in the approved catalogue:

**Step 1 – Submit a Software Request**
IT Portal → Software Requests → New Request. Provide the software name, version, vendor, business justification, and estimated number of users.

**Step 2 – Security and compliance review**
The IT Security team will review the software for licensing compliance, data handling, and security vulnerabilities. This takes 3–5 business days.

**Step 3 – Manager approval**
If the security review passes, your manager will be asked to formally approve the business need.

**Step 4 – Deployment**
Approved software is added to the managed catalogue and deployed to your device within 2 business days.

### 3.5 Escalation Policy

**Escalation Policy:** If a software request has been pending for more than 10 business days without update, escalate to your IT Business Partner. Emergency software requests for client-critical needs can be expedited to 24-hour processing — flag this clearly in the request.

---

## 4. WiFi Connectivity

### 4.1 Nagarro Network Infrastructure

Nagarro offices use enterprise-grade WiFi with three available networks:

| Network Name | Purpose | Authentication |
|---|---|---|
| NagarroNet | Primary corporate network for work devices | SSO (Okta) |
| NagarroGuest | Visitor and personal device internet access | Daily access code |
| NagarroIOT | Smart devices, printers, AV equipment | Auto-provisioned |

**All work-related activity must use NagarroNet.** Using personal hotspots for work activity involving sensitive data is a security policy violation.

### 4.2 Troubleshooting WiFi Issues

**Issue: Cannot see NagarroNet in the WiFi list**
1. Toggle your device's WiFi off and on
2. Move closer to an access point (AP). Office maps showing AP locations are in the IT portal
3. Forget all saved Nagarro networks and rediscover them
4. Restart your device's network adapter: Right-click WiFi icon → Network troubleshooter

**Issue: Connected to NagarroNet but no internet**
1. Disconnect and reconnect
2. Open a command prompt: `ping 8.8.8.8` — if you get replies, the issue is DNS; run `ipconfig /flushdns`
3. Check the IT Status Page for network outage announcements
4. Try a different physical location in the office

**Issue: Slow WiFi speeds**
1. Run a speed test at fast.com while connected to NagarroNet
2. Check how many devices you are connected to (most people only need 1–2)
3. Avoid streaming personal media on the corporate network
4. High congestion areas: Move away from large meeting rooms or auditoriums during peak hours

**Issue: Repeatedly dropping connection**
1. Forget NagarroNet and reconnect with fresh credentials
2. Update your device's WiFi driver (Device Manager → Network Adapters → Update Driver)
3. Check if your device's power-saving mode is aggressively turning off the WiFi adapter

### 4.3 Home Network for Remote Work

For reliable remote work:
- Use a wired ethernet connection where possible
- Minimum requirement: 25 Mbps download / 10 Mbps upload
- If your home internet is insufficient, Nagarro provides a monthly mobile data stipend — apply via HR Portal → Benefits → Remote Work Allowance

### 4.4 Escalation Policy

**Escalation Policy:** Report complete network outages at an office location as Priority 1 immediately. Widespread outages will trigger Nagarro's Business Continuity Plan with backup connectivity solutions deployed within 2 hours.

---

## 5. Hardware Request

### 5.1 Standard Hardware Entitlements

Every Nagarro employee is entitled to a standard hardware kit based on their role. The following table outlines the standard kit:

| Role Category | Standard Kit |
|---|---|
| Developer / Engineer | 15" laptop, external monitor (24"), keyboard, mouse, headset |
| Designer | 15" laptop, 27" 4K display, stylus tablet |
| Manager / Lead | 14" laptop, monitor, keyboard, mouse |
| Remote Worker | Same as above + desk stand, webcam, and ring light |

Upgrades beyond the standard kit require business justification and manager approval.

### 5.2 Requesting New or Replacement Hardware

**Step 1 – Submit a Hardware Request**
IT Portal → Hardware Requests → New Request. Select whether this is for a New Joiner, Replacement (damaged/end-of-life), or Upgrade.

**Step 2 – Justification**
For upgrades or non-standard items, provide a clear business justification. "I prefer a different keyboard" is not sufficient — "The existing keyboard causes repetitive strain injury (RSI) symptoms" with a medical note is acceptable.

**Step 3 – Manager approval**
For items valued above $500, manager approval is automatically requested.

**Step 4 – Procurement and delivery**
Standard items are dispatched from the IT equipment inventory within 2 business days. Non-stock items require 5–10 business days for procurement. All hardware is delivered to your registered office address unless otherwise specified.

### 5.3 Returning Hardware

Hardware must be returned upon offboarding or when replacing an item. Unreturned assets will be deducted from the final paycheck. Use the pre-paid return label provided in the offboarding email. Ensure all data is wiped from personal storage devices before return.

### 5.4 Escalation Policy

**Escalation Policy:** For urgent hardware failures that prevent you from working (e.g., laptop completely dead), contact the IT Service Desk as a Priority 2 request. A loaner device can typically be arranged within 4 hours at major office locations.

---

## 6. Blue Screen (BSOD) / System Crash

### 6.1 Overview

A Blue Screen of Death (BSOD) on Windows indicates a critical system error — usually a driver conflict, hardware failure, or corrupted system file. A single BSOD is often not cause for major concern, but repeated crashes require immediate investigation.

### 6.2 Immediate Steps

**Step 1 – Photograph the error screen**
Before the machine restarts, photograph the error code and hex value shown (e.g., `DRIVER_IRQL_NOT_LESS_OR_EQUAL 0x000000D1`). This is essential for diagnostics.

**Step 2 – Allow automatic restart**
Modern Windows will restart automatically after a BSOD. If it does not restart within 2 minutes, hold the power button for 5 seconds to force shutdown, then restart.

**Step 3 – Check for immediate recurrence**
If the system crashes again within 10 minutes of restart, do not continue attempting to use it. Proceed to escalation immediately.

**Step 4 – Run Windows Memory Diagnostic**
Start → Search → "Windows Memory Diagnostic" → Restart now and check for problems. A failing RAM module is a common cause of BSODs.

**Step 5 – Check for recent changes**
Think: did the crash start after a Windows Update, new driver installation, or new peripheral? If so, roll back the specific change:
- Windows Update: Settings → Update & Security → View Update History → Uninstall Updates
- Driver: Device Manager → Right-click device → Properties → Driver → Roll Back

**Step 6 – Export crash dump logs**
Open Event Viewer (search in Start menu) → Windows Logs → System → Filter by Error and Critical. Export the last 10 entries and attach to your IT support ticket.

### 6.3 Prevention

- Keep Windows updated (Updates are pushed automatically on NagarroNet overnight)
- Never install unsigned or cracked software on corporate devices
- Avoid physically moving the laptop while the hard drive is actively writing data
- Use surge protectors for power

### 6.4 Escalation Policy

**Escalation Policy:** If a BSOD occurs more than twice within a 7-day period, or if the machine fails to boot after a crash, raise an urgent IT support ticket (Priority 2). The device may require OS reinstall or hardware replacement.

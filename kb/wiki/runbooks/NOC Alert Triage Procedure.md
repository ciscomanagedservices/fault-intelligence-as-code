---
type: runbook
title: "NOC Alert Triage Procedure"
created: 2026-05-06
updated: 2026-05-06
status: active
severity_scope: ["SEV-1", "SEV-2", "SEV-3", "SEV-4"]
tags:
  - runbook
  - noc
  - triage
  - incident-response
related:
  - "[[Global Network Operations Center]]"
  - "[[Incident Severity SLAs]]"
  - "[[ServiceNow]]"
  - "[[Splunk]]"
  - "[[ThousandEyes]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# NOC Alert Triage Procedure

## Purpose

This runbook describes the standard Tier 1 (T1) alert triage process for the [[Global Network Operations Center]]. Every alert received must be triaged using this process before escalation or closure.

---

## Step 1 — Acknowledge the Alert (< 2 minutes)

1. Acknowledge the alert in the monitoring dashboard to prevent duplicate notifications
2. Identify the alert source: [[Splunk]], [[ThousandEyes]], [[Kentik]], or manual report
3. Identify the affected device, site, or service

---

## Step 2 — Initial Diagnosis (< 5 minutes for SEV-1/2)

Run these checks in order:

**A. Connectivity test**
```
ping <device management IP> -c 10
traceroute <device management IP>
```

**B. Interface status**
- Check interface status in NOC dashboard or pull from [[Splunk]]: search for `host=<device> "line protocol is down"` in last 15 minutes

**C. Check for known issues**
- Search `wiki/known-issues/` for the symptom pattern
- If a known workaround exists, apply it and document in the ticket

**D. ThousandEyes check**
- Open [[ThousandEyes]] dashboard for the affected site
- Check: HTTP availability, DNS health, network path packet loss

---

## Step 3 — Open a Ticket in ServiceNow

1. Log into [[ServiceNow]] and open a new Incident
2. Set severity per the [[Incident Severity SLAs]] matrix
3. Record: alert source, affected device/service, symptoms observed, initial diagnosis results
4. Set the assignment group to **NOC-Tier1**

---

## Step 4 — Escalation Decision

| Condition | Action |
|-----------|--------|
| Issue matches a known runbook (SEV-3/4) | Follow the specific runbook; close if resolved |
| SEV-1 or SEV-2 detected | Immediately escalate to T2; page T3 if SEV-1 |
| No known runbook; issue persists | Escalate to T2 after 15 minutes |
| Issue auto-resolves | Document in ticket, mark resolved, note as transient |

---

## Step 5 — SEV-1 Bridge Call

If this is a SEV-1:
1. Open a bridge call immediately (bridge number in NOC operations guide)
2. Notify: T2 on-call, T3 on-call, NOC Manager
3. Update the [[ServiceNow]] ticket every 15 minutes with status
4. Notify stakeholders per the escalation matrix in [[Incident Severity SLAs]]

---

## Notes

- Do NOT attempt to make changes without T2 or T3 approval
- All commands run on production devices must be read-only during triage (show commands only)
- If you need Break-Glass CLI access, request it from a T3 engineer

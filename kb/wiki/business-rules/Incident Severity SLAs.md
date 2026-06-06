---
type: business-rule
title: "Incident Severity SLAs"
created: 2026-05-06
updated: 2026-05-06
status: active
tags:
  - business-rule
  - sla
  - incident-management
  - escalation
related:
  - "[[Global Network Operations Center]]"
  - "[[ServiceNow]]"
  - "[[Change Management Policy]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Incident Severity SLAs

## Purpose

This document defines the incident severity levels, response time SLAs, escalation paths, and communication requirements for all network incidents at [[ACME Corp]]. All [[Global Network Operations Center]] personnel must follow these SLAs.

---

## Severity Matrix

| Severity | Label | Definition | NOC Response Time | Bridge Call |
|----------|-------|-----------|-------------------|-------------|
| **SEV-1** | Critical | Global or regional outage impacting revenue or life-safety systems | **5 minutes** | Immediate — T1, T2, T3, Management |
| **SEV-2** | High | Significant performance degradation or loss of redundancy for a critical service | **15 minutes** | T2 + T3 on-call |
| **SEV-3** | Medium | Localized branch outage or non-critical service disruption | **2 hours** | T2 on-call notified |
| **SEV-4** | Low | Minor glitches, configuration requests, single-user access issues | **24 hours** | None required |

---

## SEV-1 Escalation Procedure

1. T1 acknowledges alert and immediately opens [[ServiceNow]] ticket
2. T1 calls the T2 on-call hotline within **5 minutes** of alert acknowledgement
3. T2 opens bridge call and pages T3 on-call within **5 minutes** of T2 notification
4. T3 must join bridge call within **10 minutes** of being paged
5. NOC Manager must be notified within **15 minutes** of bridge call open
6. Executive escalation (VP of Infrastructure) if outage exceeds **30 minutes** with no ETR

### SEV-1 Communications

| Time Since Outage | Action |
|-------------------|--------|
| T+0 | [[ServiceNow]] ticket opened, bridge call initiated |
| T+15min | First status update to stakeholder distribution list |
| T+30min | Escalate to VP of Infrastructure if unresolved |
| T+30min (recurring) | Status update every 30 minutes until resolved |

---

## SEV-2 Escalation Procedure

1. T1 opens ticket and notifies T2 on-call within **15 minutes**
2. T2 leads investigation; escalates to T3 if not resolved within **1 hour**
3. Status updates to stakeholders every **1 hour**

---

## SEV-3 / SEV-4 Procedure

- SEV-3: T1 works the ticket; escalates to T2 if not resolved within **4 hours**
- SEV-4: T1 queues the ticket for next business day response; escalates to T2 if not resolved within **3 business days**

---

## Severity Downgrade / Upgrade

- Any NOC team member may **upgrade** a severity if conditions worsen (e.g., SEV-3 branch outage spreads to regional core)
- Severity **downgrade** requires T3 or NOC Manager approval
- Document all severity changes in the [[ServiceNow]] ticket with justification

---

## Post-Incident Review

- **SEV-1:** Post-mortem required within **48 hours** of resolution. T3 leads. Output: RCA document filed in `wiki/incidents/`
- **SEV-2:** Post-mortem required within **1 week** of resolution. T2/T3 leads.
- **SEV-3/4:** No post-mortem required unless pattern indicates a recurring issue

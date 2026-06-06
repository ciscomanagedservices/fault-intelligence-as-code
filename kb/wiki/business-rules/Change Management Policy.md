---
type: business-rule
title: "Change Management Policy"
created: 2026-05-06
updated: 2026-05-06
status: active
tags:
  - business-rule
  - change-management
  - itil
  - cab
related:
  - "[[ServiceNow]]"
  - "[[Network Architecture and Engineering]]"
  - "[[Infrastructure as Code]]"
  - "[[Incident Severity SLAs]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Change Management Policy

## Purpose

This document defines the rules governing all planned network changes at [[ACME Corp]]. All changes must comply with this policy regardless of size or urgency. Policy is ITIL-aligned.

---

## Core Requirements

Every network change, without exception, must:

1. **Have a [[ServiceNow]] change ticket** opened before any work begins
2. **Include a documented rollback procedure** — tested, verified, and executable within the maintenance window
3. **Be deployed via the CI/CD pipeline** — no manual CLI changes except Break-Glass (see [[Infrastructure as Code]])
4. **Be scheduled within an approved maintenance window** unless it is an emergency change

---

## Change Types

| Type | Approval Required | Example |
|------|------------------|---------|
| **Standard** | Pre-approved template (no individual approval needed) | Add VLAN at branch, update static route |
| **Normal – Minor** | Team lead / manager approval | Firmware upgrade on branch switch, prefix-list update |
| **Normal – Major** | Full CAB review and approval | Core routing topology change, firewall policy rebuild, NGFW upgrade |
| **Emergency** | ECAB (Emergency CAB) — two T3 + NOC Manager | SEV-1 mitigation requiring a config change |

---

## Change Advisory Board (CAB)

- **Scope:** Any change affecting Tier-1 services or core routing infrastructure
- **Meeting schedule:** Every **Tuesday at 14:00 UTC**
- **Submission deadline:** Change request must be submitted to ServiceNow by **Friday 17:00 UTC** the week before the meeting
- **Attendees:** T3 engineers, NAE leads, NetSecOps lead, NOC Manager, representatives from affected business units

---

## Maintenance Windows

| Scope | Window |
|-------|--------|
| Global standard | Saturday 22:00 UTC — Sunday 04:00 UTC |
| APAC regional | Wednesday 14:00 UTC — Wednesday 18:00 UTC |
| EMEA regional | Sunday 01:00 UTC — Sunday 05:00 UTC |
| AMER regional | Sunday 06:00 UTC — Sunday 10:00 UTC |

Changes must complete and be verified within the window. If a change cannot be completed, the rollback must be executed before the window closes.

---

## Rollback Mandate

All change tickets must include a rollback section containing:
- Step-by-step rollback commands/procedure
- Expected outcome after rollback
- Rollback decision criteria: "Rollback if X condition is not met by Y minutes after change"
- Person responsible for executing rollback

> [!note] Enforcement
> Changes submitted without a documented rollback procedure will be **rejected by CAB** and returned to the requester.

---

## Emergency Change (ECAB) Process

1. Open an emergency [[ServiceNow]] change ticket immediately
2. Get verbal approval from two T3 engineers AND the NOC Manager
3. Execute the change; document every command run and its output
4. Within 24 hours of the emergency change: update the change ticket with full documentation and schedule a CAB retrospective review

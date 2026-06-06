---
type: folder-index
title: "Business Rules Index"
created: 2026-05-06
updated: 2026-05-06
tags:
  - index
  - business-rules
status: seed
page_count: 3
related: []
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Business Rules

## What Belongs Here

**Purpose:** Organizational policies, constraints, and rules that govern how network operations are conducted — the "must", "must not", and "only if" layer for a troubleshooting agent.

**Types of content that belong here:**
- Escalation paths and contact trees (who to call, when, in what order)
- SLA definitions and breach thresholds
- Change management policies (change windows, approval requirements, freeze periods)
- Regulatory and compliance constraints (what can't be touched without approval)
- Customer-facing commitments (uptime guarantees, notification requirements)
- Internal prioritization rules (which circuits are critical, which can wait)
- On-call schedules and rotation logic
- Authorization boundaries (what NOC can do vs. what requires Network Engineering)

**Boundary:** This folder contains *organizational rules*, not technical procedures (those are in `runbooks/`). A business rule says "always notify the customer within 15 minutes of a P1 outage." The runbook says "here are the steps to diagnose a P1 outage."

**Agent usage:** A troubleshooting agent must consult this folder before taking any action that could impact customers or require escalation. Business rules constrain *what* the agent may do and *who* it must involve.

## Pages

<!-- Updated by wiki-ingest and wiki-lint -->

- [[Incident Severity SLAs]] — SEV-1 through SEV-4 definitions, response times, escalation paths, and post-mortem requirements
- [[Change Management Policy]] — ITIL change types, CAB schedule (Tues 14:00 UTC), maintenance windows, rollback mandate
- [[Security Zero Trust Mandates]] — 5 non-negotiable security mandates: MACsec DCI, BGP hardening, OOB isolation, device hardening, default-deny firewall

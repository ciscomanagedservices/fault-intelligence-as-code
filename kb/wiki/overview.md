---
type: overview
title: "Network Operations Knowledge Base — Overview"
created: 2026-05-06
updated: 2026-05-06
tags:
  - meta
  - overview
status: draft
related: []
sources: []
---

# Network Operations Knowledge Base

> **Status:** Draft — scaffolded, awaiting ingestion of source material.

## Purpose

This wiki is a persistent, compounding knowledge base for network operations. Its primary audience is a **network troubleshooting agent** — an AI system that uses this wiki to diagnose issues, retrieve relevant procedures, apply business constraints, and escalate appropriately.

Human operators also use this wiki directly for reference, runbook lookup, and incident post-mortem review.

## How the Troubleshooting Agent Uses This Wiki

The agent follows a standard lookup sequence:

1. **Read `wiki/hot.md`** — get recent context (fast, ~500 tokens)
2. **Check `known-issues/`** — does a known workaround apply? If yes, apply it and stop.
3. **Search `incidents/`** — has this symptom pattern occurred before? What resolved it?
4. **Pull the relevant `runbooks/` procedure** — execute the appropriate steps
5. **Consult `business-rules/`** — check escalation requirements, SLAs, change constraints before acting
6. **Reference `entities/` and `concepts/`** as needed for device-specific context or protocol details

## Folder Map

```
wiki/
├── entities/        — Devices, vendors, teams, tools, people
├── concepts/        — Protocols, technologies, terminology
├── sources/         — Ingested doc summaries
├── incidents/       — Past outages and degradation events
├── runbooks/        — Step-by-step troubleshooting and change procedures
├── known-issues/    — Recurring bugs, workarounds, vendor quirks
├── business-rules/  — SLAs, escalation paths, change policies
├── comparisons/     — Tool and protocol side-by-side analyses
├── questions/       — Filed Q&A pairs
└── meta/            — Dashboards and lint reports
```

## Coverage Status

> [!gap] Coverage
> No sources have been ingested yet. All folders are empty stubs.
> Priority first sources: existing runbooks, recent incident post-mortems, escalation contact list.

## Key Pages to Create First

- **Runbooks:** BGP troubleshooting, link flap diagnosis, VLAN provisioning, incident response (P1/P2)
- **Business Rules:** Escalation matrix, SLA definitions, change window policy
- **Known Issues:** Start with any recurring vendor bugs or monitoring false positives
- **Entities:** Core routers, switches, firewalls; NOC team roster; key vendor contacts

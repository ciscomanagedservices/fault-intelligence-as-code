---
type: folder-index
title: "Runbooks Index"
created: 2026-05-06
updated: 2026-05-29
tags:
  - index
  - runbooks
status: active
page_count: 4
related: []
sources:
  - "[[ACME Corp Network Operations Handbook]]"
  - "[[INC-20260509 — Persistent CRC Errors xr-43 (source)]]"
---

# Runbooks

## What Belongs Here

**Purpose:** Step-by-step operational procedures for common network tasks, troubleshooting workflows, and incident response actions.

**Types of content that belong here:**
- Troubleshooting procedures (e.g., "How to diagnose BGP session flapping")
- Configuration change procedures (e.g., "How to add a VLAN to a trunk port")
- Incident response playbooks (e.g., "DDoS response procedure")
- Maintenance procedures (e.g., "How to perform a rolling IOS upgrade")
- Health check and verification procedures
- Escalation procedures

**Boundary:** Runbooks are *procedural how-to guides* with ordered steps. They reference entities from `entities/` and concepts from `concepts/`, but do not define them. Business rules about *when* to escalate belong in `business-rules/`. Historical records of *specific executions* belong in `incidents/`.

**Agent usage:** A troubleshooting agent should use runbooks as the primary action source — match symptom → check `incidents/` and `known-issues/` for pattern → execute steps from the relevant runbook.

## Pages

<!-- Updated by wiki-ingest and wiki-lint -->

- [[NOC Alert Triage Procedure]] — Standard T1 first-response triage for any alert; leads to escalation or specific runbooks
- [[BGP Adjacency Troubleshooting]] — T2/T3 guide for diagnosing down or flapping BGP sessions
- [[Circuit Outage Response]] — WAN circuit failure response; includes carrier trouble ticket procedure
- [[Interface CRC Error Troubleshooting]] — Diagnostic procedure for CRC input errors on router/switch interfaces; covers optics, connectors, and SFP replacement

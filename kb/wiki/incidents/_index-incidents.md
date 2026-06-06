---
type: folder-index
title: "Incidents Index"
created: 2026-05-06
updated: 2026-05-29
tags:
  - index
  - incidents
status: active
page_count: 3
related: []
sources:
  - "[[INC-20260314 — BGP Session Flap xr-43 (source)]]"
  - "[[INC-20260421 — Process Memory Exhaustion xr-43 (source)]]"
  - "[[INC-20260509 — Persistent CRC Errors xr-43 (source)]]"
---

# Incidents

## What Belongs Here

**Purpose:** One page per significant network incident — outages, degradations, security events, and near-misses — with enough detail for a troubleshooting agent to recognize recurrence patterns.

**Types of content that belong here:**
- Major and minor outage records
- Performance degradation events
- Security incidents with network impact
- Post-mortem summaries
- Near-misses and avoided outages
- Recurring flapping or instability events

**Boundary:** This folder records *what happened* in specific past events. Generalizable lessons from incidents get promoted to `known-issues/` (for recurring patterns) or `runbooks/` (for response procedures). Business response and escalation decisions go in `decisions/` or `business-rules/`.

**Key fields for agent use:** `symptoms`, `root_cause`, `affected_systems`, `resolution_steps` — a troubleshooting agent should check these first when matching a current symptom to historical patterns.

## Pages

<!-- Updated by wiki-ingest and wiki-lint -->

- [[INC-20260314 — BGP Session Flap xr-43]] — SEV-2 | BGP flap to ISP-A from far-end degraded SFP; BFD failover held; 47 min
- [[INC-20260421 — Process Memory Exhaustion xr-43]] — SEV-1 | IaC prefix-set push OOM-killed BGP process; 23 branches, 4m12s outage
- [[INC-20260509 — Persistent CRC Errors xr-43]] — SEV-3 | Silent SFP failure; CRC errors below BFD threshold; VoIP degradation; 77 min

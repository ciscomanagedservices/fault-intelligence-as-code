---
type: folder-index
title: "Entities Index"
created: 2026-05-06
updated: 2026-05-29
tags:
  - index
  - entities
status: active
page_count: 18
related: []
sources:
  - "[[ACME Corp Network Operations Handbook]]"
  - "[[INC-20260314 — BGP Session Flap xr-43 (source)]]"
  - "[[INC-20260421 — Process Memory Exhaustion xr-43 (source)]]"
  - "[[INC-20260509 — Persistent CRC Errors xr-43 (source)]]"
---

# Entities

## What Belongs Here

**Purpose:** One page per discrete, named thing that exists in the network operations environment.

**Types of content that belong here:**
- Network devices (routers, switches, firewalls, load balancers, access points)
- Vendors and manufacturers (Cisco, Juniper, Palo Alto, etc.)
- Software platforms and tools (SolarWinds, Splunk, Ansible, etc.)
- Teams and organizational units (NOC, Security Ops, Network Engineering)
- People — key contacts, SMEs, on-call owners
- External services and ISPs

**Boundary:** This folder contains *who and what* — not *how* (that's `runbooks/`) and not *why* (that's `decisions/`). Relationships between entities are documented here via wikilinks, but the logic of those relationships lives elsewhere.

## Pages

<!-- Updated by wiki-ingest and wiki-lint -->

### Organizations
- [[ACME Corp]]

### ISPs / Upstream Providers
- [[ISP-A]] — Primary upstream BGP peer for xr-43; AS 65001

### Devices
- [[xr-43]] — Cisco ASR-9904 edge router; 16GB RAM; 3 incidents in 2026

### Teams
- [[Global Network Operations Center]]
- [[Network Architecture and Engineering]]
- [[Network Security Operations]]

### Vendors
- [[Cisco]]
- [[Juniper Networks]]
- [[Arista Networks]]
- [[Palo Alto Networks]]
- [[Fortinet]]
- [[F5 Networks]]

### Tools & Platforms
- [[NetBox]]
- [[Splunk]]
- [[ServiceNow]]
- [[ThousandEyes]]
- [[Kentik]]
- [[Oxidized]]

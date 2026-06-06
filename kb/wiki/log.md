---
type: meta
title: "Operation Log"
created: 2026-05-06
updated: 2026-05-29
tags:
  - meta
  - log
status: evergreen
---

# Operation Log

Append-only. New entries go at the TOP. Never edit past entries.

---

## 2026-05-29 — batch ingest | 3 Incident Records (xr-43)

- Sources: `.raw/INC-20260314T082217Z-xr43-bgp-flap.md`, `.raw/INC-20260421T031544Z-xr43-memory-exhaustion.md`, `.raw/INC-20260509T143322Z-xr43-interface-crc.md`
- Pages created (11 total):
  - **incidents/** [[INC-20260314 — BGP Session Flap xr-43]], [[INC-20260421 — Process Memory Exhaustion xr-43]], [[INC-20260509 — Persistent CRC Errors xr-43]]
  - **sources/** [[INC-20260314 — BGP Session Flap xr-43 (source)]], [[INC-20260421 — Process Memory Exhaustion xr-43 (source)]], [[INC-20260509 — Persistent CRC Errors xr-43 (source)]]
  - **entities/** [[xr-43]], [[ISP-A]]
  - **known-issues/** [[SFP+ Silent Degradation — CRC Below BFD Threshold]], [[ASR-9904 BGP Process OOM — Large Prefix-Sets]]
  - **runbooks/** [[Interface CRC Error Troubleshooting]]
- Pages updated: [[_index-incidents]], [[_index-entities]], [[_index-sources]], [[_index-runbooks]], [[_index-known-issues]], [[index]], [[hot]]
- Key insight: xr-43 (ASR-9904, 16GB) had 3 incidents in under 2 months — two optic/SFP related, one IaC memory limit. Device warrants elevated monitoring and proactive SFP lifecycle review.

---

## 2026-05-06 — ingest | ACME Corp Network Operations Handbook

- Source: `.raw/acme_corp_netops_handbook.md`
- Summary: [[ACME Corp Network Operations Handbook]]
- Pages created (31 total):
  - **sources/** [[ACME Corp Network Operations Handbook]]
  - **entities/** [[ACME Corp]], [[Global Network Operations Center]], [[Network Architecture and Engineering]], [[Network Security Operations]], [[Cisco]], [[Juniper Networks]], [[Arista Networks]], [[Palo Alto Networks]], [[Fortinet]], [[F5 Networks]], [[NetBox]], [[Splunk]], [[ServiceNow]], [[ThousandEyes]], [[Kentik]], [[Oxidized]]
  - **concepts/** [[BGP]], [[IS-IS]], [[EVPN-VXLAN]], [[Spine-Leaf Architecture]], [[SD-WAN]], [[Zero Trust]], [[VRRP]], [[BFD]], [[MACsec]], [[RPKI]], [[Infrastructure as Code]]
  - **runbooks/** [[NOC Alert Triage Procedure]], [[BGP Adjacency Troubleshooting]], [[Circuit Outage Response]]
  - **business-rules/** [[Incident Severity SLAs]], [[Change Management Policy]], [[Security Zero Trust Mandates]]
  - **known-issues/** [[Shadow IT — Unapproved Network Hardware]]
- Pages updated: [[_index-entities]], [[_index-sources]], [[_index-concepts]], [[_index-runbooks]], [[_index-business-rules]], [[_index-known-issues]], [[index]], [[hot]]
- Key insight: First ingest establishes full organizational, hardware, protocol, and policy coverage for ACME Corp network operations.

---

## 2026-05-06 — Vault scaffolded

- Mode: B/C hybrid — Network Operations Knowledge Base (agent-optimized)
- Folders created: `entities/`, `concepts/`, `sources/`, `incidents/`, `runbooks/`, `known-issues/`, `business-rules/`, `comparisons/`, `questions/`, `meta/`
- Templates created: `concept.md`, `entity.md`, `source.md`, `question.md`, `comparison.md`, `incident.md`, `runbook.md`, `known-issue.md`, `business-rule.md`
- Purpose: Knowledge base optimized for a network troubleshooting agent
- Content depth: Full proposals (draft content, marked status: draft)

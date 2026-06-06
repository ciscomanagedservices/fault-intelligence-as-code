---
type: meta
title: "Wiki Index"
created: 2026-05-06
updated: 2026-05-29
tags:
  - index
  - meta
status: seed
---

# Network Operations Knowledge Base — Master Index

This is the master catalog of all pages in the wiki. Updated on every ingest and lint operation.

## Folders

| Folder | Purpose | Index | Count |
|--------|---------|-------|-------|
| `entities/` | Devices, vendors, teams, tools, people | [[_index-entities]] | 18 |
| `concepts/` | Protocols, patterns, technologies, terminology | [[_index-concepts]] | 11 |
| `sources/` | Ingested doc summaries | [[_index-sources]] | 4 |
| `incidents/` | Past outages, degradations, post-mortems | [[_index-incidents]] | 3 |
| `runbooks/` | Step-by-step procedures and playbooks | [[_index-runbooks]] | 4 |
| `known-issues/` | Recurring bugs, workarounds, environmental quirks | [[_index-known-issues]] | 3 |
| `business-rules/` | SLAs, escalation paths, change policies | [[_index-business-rules]] | 3 |
| `comparisons/` | Tool, vendor, protocol analyses | [[_index-comparisons]] | 0 |
| `questions/` | Filed Q&A pairs | [[_index-questions]] | 0 |
| `meta/` | Dashboards, lint reports, conventions | [[_index-meta]] | 0 |

## Infrastructure Pages

- [[overview]] — executive summary of the wiki
- [[log]] — chronological operation log
- [[hot]] — recent context cache (~500 words)

## All Pages

<!-- wiki-ingest appends pages here -->

### Sources
- [[ACME Corp Network Operations Handbook]]
- [[INC-20260314 — BGP Session Flap xr-43 (source)]] · [[INC-20260421 — Process Memory Exhaustion xr-43 (source)]] · [[INC-20260509 — Persistent CRC Errors xr-43 (source)]]

### Entities
- [[ACME Corp]] · [[ISP-A]] · [[xr-43]]
- [[Global Network Operations Center]] · [[Network Architecture and Engineering]] · [[Network Security Operations]]
- [[Cisco]] · [[Juniper Networks]] · [[Arista Networks]] · [[Palo Alto Networks]] · [[Fortinet]] · [[F5 Networks]]
- [[NetBox]] · [[Splunk]] · [[ServiceNow]] · [[ThousandEyes]] · [[Kentik]] · [[Oxidized]]

### Concepts
- [[BGP]] · [[IS-IS]] · [[EVPN-VXLAN]] · [[Spine-Leaf Architecture]] · [[SD-WAN]]
- [[Zero Trust]] · [[VRRP]] · [[BFD]] · [[MACsec]] · [[RPKI]] · [[Infrastructure as Code]]

### Incidents
- [[INC-20260314 — BGP Session Flap xr-43]] · [[INC-20260421 — Process Memory Exhaustion xr-43]] · [[INC-20260509 — Persistent CRC Errors xr-43]]

### Runbooks
- [[NOC Alert Triage Procedure]] · [[BGP Adjacency Troubleshooting]] · [[Circuit Outage Response]] · [[Interface CRC Error Troubleshooting]]

### Business Rules
- [[Incident Severity SLAs]] · [[Change Management Policy]] · [[Security Zero Trust Mandates]]

### Known Issues
- [[Shadow IT — Unapproved Network Hardware]] · [[SFP+ Silent Degradation — CRC Below BFD Threshold]] · [[ASR-9904 BGP Process OOM — Large Prefix-Sets]]

---
type: entity
entity_type: tool
title: "Kentik"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - tool
  - monitoring
  - flow-analysis
  - capacity-planning
related:
  - "[[Global Network Operations Center]]"
  - "[[Splunk]]"
  - "[[ThousandEyes]]"
  - "[[BGP]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Kentik

## Role at ACME Corp

Kentik is the **network flow analytics** platform at [[ACME Corp]]. It ingests NetFlow v9 and IPFIX data from all major transit boundaries and provides traffic visibility for capacity planning and security forensics.

## Data Collection

| Protocol | Collected At |
|----------|------------|
| NetFlow v9 | All major transit boundaries (WAN edge, DC core, branch SD-WAN) |
| IPFIX | Supplemental flow data from modern platforms |

## Key Use Cases

### Capacity Planning
- Trend analysis on top-talkers, busiest interfaces, and WAN circuit utilization
- Helps NAE identify links approaching saturation before users are impacted
- Informs annual bandwidth procurement decisions

### Security Forensics
- DDoS detection: identifies sudden traffic volume spikes by source/destination IP, ASN, or protocol
- Lateral movement detection: unusual east-west flows within the data center
- Complements [[Splunk]] syslog for full-scope incident investigations

### Traffic Engineering
- Visibility into BGP traffic paths (which peering / transit carries which prefix)
- Supports route policy optimization for [[BGP]] traffic steering

## Alerting

Kentik can generate threshold-based alerts (e.g., "interface X is at 90% utilization") that feed into [[ServiceNow]] or the NOC monitoring dashboard.

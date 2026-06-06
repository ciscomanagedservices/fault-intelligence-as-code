---
type: entity
entity_type: team
title: "Global Network Operations Center"
aliases: ["NOC", "Global NOC"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - team
  - noc
  - acme-corp
related:
  - "[[ACME Corp]]"
  - "[[Network Architecture and Engineering]]"
  - "[[Network Security Operations]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Global Network Operations Center (NOC)

## Overview

The NOC is the first line of defense and operational heart of [[ACME Corp]]'s network. It operates **24/7/365** and is organized into three tiers.

## Tier Structure

### Tier 1 (T1) — Analysts
- Alert triage
- Basic diagnostics: ping, traceroute, interface status
- Initial ticket generation in [[ServiceNow]]
- Follow standard [[runbooks]] for known issues

### Tier 2 (T2) — Technicians
- Complex escalations from T1
- Packet capture analysis ([[Wireshark]])
- Routing protocol adjacency troubleshooting ([[BGP]] / [[OSPF]])
- Firewall rule validation
- ISP/carrier coordination for circuit outages

### Tier 3 (T3) — Escalation Engineers
- Deep Subject Matter Experts (SMEs)
- Sev-1 global outage command
- Zero-day mitigation
- Core routing loop resolution
- Critical hardware failure response
- Bridge between Operations and [[Network Architecture and Engineering]]

## Escalation SLAs

| Severity | Condition | Response Time |
|----------|-----------|---------------|
| SEV-1 | Global/regional outage, revenue or life-safety impact | **5 minutes** + immediate bridge call |
| SEV-2 | Significant degradation or loss of redundancy | **15 minutes** |
| SEV-3 | Localized branch outage or non-critical disruption | **2 hours** |
| SEV-4 | Minor glitch, config request, single-user issue | **24 hours** |

See [[Incident Severity SLAs]] for full details.

## Key Tools

- [[Splunk]] — SNMP/syslog aggregation and alerting
- [[ThousandEyes]] — synthetic probing and user-experience monitoring
- [[Kentik]] — NetFlow/IPFIX flow analysis
- [[ServiceNow]] — ticketing and change management
- Slack NOC channel — real-time config diff alerts from [[Oxidized]]

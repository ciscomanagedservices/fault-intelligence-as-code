---
type: entity
entity_type: tool
title: "Splunk"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - tool
  - monitoring
  - siem
  - syslog
related:
  - "[[Global Network Operations Center]]"
  - "[[ThousandEyes]]"
  - "[[Kentik]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Splunk

## Role at ACME Corp

Splunk is the central aggregation platform for **SNMP traps and Syslog data** from legacy and all network devices. It serves as the primary alerting engine for the [[Global Network Operations Center]].

## Data Sources

| Source | Protocol | Details |
|--------|---------|---------|
| Network devices (legacy) | SNMPv3 | Interface counters, CPU/memory, hardware alarms |
| All network devices | Syslog | Authentication events, config changes, link state changes, routing events |
| Config diff alerts | [[Oxidized]] integration | Triggers alert if unauthorized config change detected |

## Key Use Cases at ACME Corp

1. **NOC alerting:** Dashboards and correlation searches alert T1 analysts to threshold breaches (high CPU, interface errors, BGP flaps)
2. **Security forensics:** Log correlation for detecting unauthorized access, port scans, or suspicious routing changes
3. **Config change audit:** Oxidized diffs streamed to Splunk; unauthorized changes trigger immediate NOC Slack alert

## Relationship to Other Monitoring Tools

| Tool | Focus |
|------|-------|
| Splunk | SNMP/syslog — legacy devices, event correlation |
| [[ThousandEyes]] | Synthetic probing — end-user experience simulation |
| [[Kentik]] | Flow data — NetFlow/IPFIX traffic analysis |
| Prometheus/Grafana | Streaming telemetry — modern Arista/Cisco sub-second metrics |

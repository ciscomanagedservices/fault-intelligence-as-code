---
type: entity
entity_type: tool
title: "ThousandEyes"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - tool
  - monitoring
  - synthetic
  - end-user-experience
related:
  - "[[Global Network Operations Center]]"
  - "[[Splunk]]"
  - "[[Kentik]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# ThousandEyes

## Role at ACME Corp

ThousandEyes provides **synthetic probing** from agents deployed in every branch and data center, simulating the end-user experience for key application paths.

## Deployment

- Agents deployed at: every branch office, every data center
- Total coverage: 150+ branch agents + 12 data center agents + 3 cloud hub agents

## What It Monitors

| Test Type | Metric | Use Case |
|-----------|--------|---------|
| HTTP Server | Availability, response time | Web app health from user perspective |
| DNS | Resolution time, NXDOMAIN errors | DNS infrastructure health |
| VoIP | Jitter, packet loss, MOS score | Unified communications quality |
| Network Path | Hop-by-hop latency, packet loss | ISP / WAN path visibility |
| BGP Route | Prefix visibility, route changes | Internet routing health |

## Importance to NOC

ThousandEyes is the primary tool for answering: **"Is this a network problem or an application problem?"**

- If a user reports slowness, the ThousandEyes dashboard can confirm whether latency is in the WAN, the ISP, the data center, or the application server
- Correlates with [[Splunk]] (device events) and [[Kentik]] (traffic flows) for full-stack triage

## Alerting

ThousandEyes alerts feed into the NOC monitoring dashboard. Threshold breaches (e.g., HTTP availability < 99%, jitter > 30ms) generate tickets in [[ServiceNow]].

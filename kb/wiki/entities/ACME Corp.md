---
type: entity
entity_type: organization
title: "ACME Corp"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - organization
  - acme-corp
related:
  - "[[Global Network Operations Center]]"
  - "[[Network Architecture and Engineering]]"
  - "[[Network Security Operations]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# ACME Corp

## Overview

ACME Corp is a multinational logistics and manufacturing company. The corporate network is central to all operations.

## Network Scale

| Metric | Value |
|--------|-------|
| Employees | 45,000+ |
| Regional Data Centers | 12 |
| Global Cloud Hubs | 3 |
| Branch Offices | 150+ |
| Continents | 4 |

## Availability Target

**99.999% ("Five Nines")** for core transport and data center infrastructure.

## Network Teams

- [[Global Network Operations Center]] — 24/7/365 operational monitoring and incident response
- [[Network Architecture and Engineering]] — design, scaling, and IaC automation
- [[Network Security Operations]] — perimeter security and access control

## Key Tools & Platforms

| Role | Tool |
|------|------|
| IPAM / Inventory SSoT | [[NetBox]] |
| Config backup & diff | [[Oxidized]] |
| ITSM / Change Management | [[ServiceNow]] |
| Log & SNMP aggregation | [[Splunk]] |
| Flow analysis | [[Kentik]] |
| Synthetic monitoring | [[ThousandEyes]] |

## Vendor Standards

ACME Corp maintains a strict approved-vendor list. Unapproved ("Shadow IT") hardware is actively isolated by NAC policies.

- Core routing: [[Cisco]] ASR 9000, [[Juniper Networks]] MX Series
- DC fabric: [[Arista Networks]] 7300X3 / 7050X3
- Firewalls: [[Palo Alto Networks]] PA-5200 / PA-800
- SD-WAN edge: [[Fortinet]] FortiGate
- Load balancers: [[F5 Networks]] BIG-IP iSeries, NGINX Plus

---
type: entity
entity_type: tool
title: "NetBox"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - tool
  - ipam
  - inventory
  - ssot
related:
  - "[[Network Architecture and Engineering]]"
  - "[[Infrastructure as Code]]"
  - "[[Ansible]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# NetBox

## Role at ACME Corp

NetBox is the **Single Source of Truth (SSoT)** for all network intent at [[ACME Corp]]. Every configuration push, VLAN assignment, and IP address allocation originates from NetBox. It is the authoritative record of truth for the entire network.

## Responsibilities

| Function | Details |
|----------|---------|
| IPAM | IP address management — all subnets, prefixes, and IP assignments |
| VLAN Management | VLAN IDs and names defined and owned in NetBox |
| Device Inventory | All network devices catalogued with make, model, site, role, and status |
| Rack Layout | Physical rack units mapped per data center |
| Circuit Tracking | ISP circuits and WAN links documented here |

## Integration

NetBox feeds directly into the [[Ansible]] CI/CD pipeline managed by [[Network Architecture and Engineering]]. Templates render device configurations dynamically from NetBox data. This means:

- No device gets a configuration that isn't reflected in NetBox first
- IPAM discrepancies detected during pipeline runs are flagged as errors before deployment
- Provides the "intent" layer in the [[Infrastructure as Code]] workflow

## Policy

All VLAN, IP, and device changes must be committed to NetBox **before** a change ticket is opened in [[ServiceNow]]. NetBox state is the reference for CAB review.

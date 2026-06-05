---
type: source
title: "ACME Corp Network Operations & Architecture Master Handbook"
created: 2026-05-06
updated: 2026-05-06
status: ingested
version: "3.4.1"
classification: INTERNAL/CONFIDENTIAL
raw_file: ".raw/acme_corp_netops_handbook.md"
tags:
  - source
  - network-operations
  - acme-corp
  - architecture
  - best-practices
related:
  - "[[ACME Corp]]"
  - "[[Global Network Operations Center]]"
  - "[[Network Architecture and Engineering]]"
  - "[[Network Security Operations]]"
---

# ACME Corp Network Operations & Architecture Master Handbook

## Summary

The authoritative internal reference for ACME Corp's global network operations. Covers organizational structure, standardized hardware profiles, operational best practices, monitoring strategy, redundancy requirements, and security mandates. Governs all teams responsible for a network spanning 45,000+ employees, 12 regional data centers, 3 cloud hubs, and 150+ branch offices across 4 continents.

**Availability target:** 99.999% ("Five Nines") on core transport and data center infrastructure.

---

## Key Sections

| Section | Topics |
|---------|--------|
| §2 — Roles & Responsibilities | NOC tiers (T1/T2/T3), NAE, NetSecOps |
| §3 — Device Types & Hardware | Core routing, DC fabric, firewalls, SD-WAN, ADC/LB |
| §4 — Best Practices / SOPs | IaC/config mgmt, change management, monitoring, HA, incident SLAs |
| §5 — Security Mandates | MACsec, BGP hardening, OOB management, device hardening |

---

## Entities Extracted

**Teams:** [[Global Network Operations Center]], [[Network Architecture and Engineering]], [[Network Security Operations]]

**Vendors:** [[Cisco]], [[Juniper Networks]], [[Arista Networks]], [[Palo Alto Networks]], [[Fortinet]], [[F5 Networks]]

**Tools:** [[NetBox]], [[Splunk]], [[ServiceNow]], [[ThousandEyes]], [[Kentik]], [[Oxidized]]

---

## Concepts Extracted

[[BGP]], [[IS-IS]], [[EVPN-VXLAN]], [[Spine-Leaf Architecture]], [[SD-WAN]], [[Zero Trust]], [[VRRP]], [[BFD]], [[MACsec]], [[RPKI]], [[Infrastructure as Code]]

---

## Notable Policies & Rules

- No manual CLI changes to production — all config via Ansible/GitLab CI/CD
- Break-Glass SSH access only; all OOB via MFA jump hosts
- CAB approval required for Tier-1 / core routing changes (meets Tuesdays 14:00 UTC)
- Every change ticket must include a verified rollback procedure
- BFD tuned to 50ms failure detection on all core links
- MACsec mandatory on all DCI links (dark fiber / metro ethernet)

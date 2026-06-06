---
type: entity
entity_type: vendor
title: "Palo Alto Networks"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - vendor
  - palo-alto
  - firewall
  - security
related:
  - "[[Network Security Operations]]"
  - "[[Zero Trust]]"
  - "[[Fortinet]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Palo Alto Networks

## Role at ACME Corp

Palo Alto Networks is the **primary Next-Gen Firewall (NGFW) vendor** for all security zones at [[ACME Corp]]. All firewalls are managed by [[Network Security Operations]].

## Deployed Hardware

| Model | Deployment Location | Role |
|-------|-------------------|------|
| PA-5200 Series | Data Center Edge | High-throughput NGFW — DMZ, inter-zone, PCI segmentation |
| PA-800 Series | Branch Edge | Remote branch perimeter NGFW |

## Configuration Baseline

- **App-ID** enabled by default — all traffic classified by application, not just port/protocol
- **User-ID** enabled — traffic tied to authenticated user identity
- **Default Deny** posture — [[Zero Trust]] architecture; all traffic denied unless explicitly permitted
- **TLS Decryption** — enabled on designated DMZ inbound flows for deep inspection
- **IPS/IDS** — active on all inbound and lateral traffic flows

## Security Zones

Standard zones enforced across all PA deployments:

| Zone | Description |
|------|-------------|
| DMZ | Internet-facing services |
| Internal | Corporate LAN segments |
| PCI | Cardholder data environment (isolated) |
| OOB | Out-of-band management (isolated) |

## Related

- [[Network Security Operations]] — team that manages all Palo Alto deployments
- [[Zero Trust]] — security model all PA firewalls enforce
- [[Fortinet]] — SD-WAN edge vendor (FortiGate also provides branch firewall capability)

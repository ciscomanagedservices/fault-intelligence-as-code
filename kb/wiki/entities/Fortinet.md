---
type: entity
entity_type: vendor
title: "Fortinet"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - vendor
  - fortinet
  - sd-wan
  - branch
related:
  - "[[Palo Alto Networks]]"
  - "[[SD-WAN]]"
  - "[[Cisco]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Fortinet

## Role at ACME Corp

Fortinet **FortiGate** is the standard SD-WAN edge device for all ACME Corp branch offices. It handles WAN path selection, application-aware routing, and branch-edge security.

## Deployed Hardware

| Model | Role |
|-------|------|
| FortiGate (branch-appropriate SKU) | SD-WAN edge + branch firewall |

## Configuration Baseline

- **Dual WAN links active/active** — both links carry traffic simultaneously; path selection is application-aware
- **Application-aware routing** — latency-sensitive apps (VoIP, video) prefer low-latency WAN; bulk traffic can use cheaper broadband
- **WAN transport options:** MPLS, Broadband (DSL/cable/fiber), 5G/LTE (failover or active)
- **802.1X** — not handled by FortiGate (handled by [[Cisco]] Catalyst 9300 access switches downstream)

## Integration

FortiGate branch SD-WAN overlays tunnel back to ACME Corp's core network, which then distributes traffic to data centers and cloud hubs via [[BGP]] routing. See [[SD-WAN]] for full architecture details.

## Related

- [[SD-WAN]] — technology concept this device implements
- [[Cisco]] Catalyst 9300 — downstream access switches at each branch
- [[Palo Alto Networks]] PA-800 — deployed at larger branches alongside FortiGate for dedicated NGFW

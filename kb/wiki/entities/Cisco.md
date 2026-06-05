---
type: entity
entity_type: vendor
title: "Cisco"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - vendor
  - cisco
related:
  - "[[Juniper Networks]]"
  - "[[Arista Networks]]"
  - "[[BGP]]"
  - "[[IS-IS]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Cisco

## Role at ACME Corp

Cisco is a primary hardware vendor for [[ACME Corp]]'s **core routing, WAN transit, and branch access** layers.

## Deployed Hardware

### Core Routing & WAN Transit
| Model | Role |
|-------|------|
| ASR-9904 | Core edge/WAN router |
| ASR-9910 | Core edge/WAN router (higher density) |

**Configuration:** IS-IS IGP + MP-BGP overlay. RPKI validation on all external peerings.

### Branch Access
| Model | Role |
|-------|------|
| Catalyst 9300 Series | Branch wired access switches (802.1X enforced on all ports) |
| Catalyst 9100 Series | Wi-Fi 6 Access Points (802.1X wireless) |

## Key Protocols Used
- [[IS-IS]] — interior gateway protocol on ASR 9000 platforms
- [[BGP]] — MP-BGP overlay for WAN and cloud routing
- [[BFD]] — fast failure detection on core routing links

## Related Vendors
- [[Juniper Networks]] — co-deployed at core routing layer
- [[Arista Networks]] — DC fabric (separate layer from Cisco)

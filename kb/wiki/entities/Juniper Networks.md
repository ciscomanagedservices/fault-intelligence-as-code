---
type: entity
entity_type: vendor
title: "Juniper Networks"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - vendor
  - juniper
related:
  - "[[Cisco]]"
  - "[[BGP]]"
  - "[[IS-IS]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Juniper Networks

## Role at ACME Corp

Juniper is a co-primary vendor for [[ACME Corp]]'s **core routing and WAN transit** layer, deployed alongside [[Cisco]] ASR 9000 platforms.

## Deployed Hardware

| Model | Role |
|-------|------|
| MX480 | Core routing / WAN edge |
| MX960 | Core routing / WAN edge (high density chassis) |

**Configuration:** IS-IS IGP + MP-BGP overlay. Strict Prefix-List filtering and RPKI validation on all external BGP peerings.

## Key Protocols Used
- [[IS-IS]] — interior gateway protocol
- [[BGP]] — MP-BGP for overlay WAN and cloud interconnect
- [[BFD]] — 50ms failure detection on all core links

## Notes

The MX Series is deployed in the same routing tier as [[Cisco]] ASR 9000 routers. Multi-vendor IGP interoperability is achieved via IS-IS. Both platforms must comply with the same BFD and RPKI configuration baseline.

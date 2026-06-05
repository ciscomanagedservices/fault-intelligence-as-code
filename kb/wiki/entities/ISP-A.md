---
type: entity
entity_type: organization
title: "ISP-A"
created: 2026-05-29
updated: 2026-05-29
tags:
  - entity
  - isp
  - upstream-provider
  - bgp
status: active
related:
  - "[[xr-43]]"
  - "[[BGP]]"
  - "[[INC-20260314 — BGP Session Flap xr-43]]"
  - "[[SFP+ Silent Degradation — CRC Below BFD Threshold]]"
---

# ISP-A

## Profile

| Field | Value |
|-------|-------|
| Type | Upstream Internet Service Provider |
| BGP AS | AS 65001 |
| Peering IP | 198.51.100.1 |
| Peering interface on xr-43 | GigabitEthernet0/0/0/1 |
| NOC contact | Engaged via standard TAC bridge |

## Relationship to ACME Corp Network

- Primary upstream BGP peer for edge router [[xr-43]]
- Failover path via xr-44 (BFD-triggered in <50ms)
- BGP session uses MD5 authentication and max-prefix guard

## Incident History

| Incident | Date | Issue | Resolution |
|----------|------|-------|------------|
| [[INC-20260314 — BGP Session Flap xr-43]] | 2026-03-14 | Degraded SFP transceiver on ISP-A's PE caused CRC errors → BGP hold timer expiry | ISP-A replaced PE SFP |

## Notes

- ISP-A's PE-side optic degradation is **invisible to ACME's local SNMP monitoring** — only visible via CRC input error counters on xr-43's uplink interface
- When engaging ISP-A NOC, present CRC error evidence from `show interfaces GigabitEthernet0/0/0/1` alongside local optic readings to demonstrate far-end causation

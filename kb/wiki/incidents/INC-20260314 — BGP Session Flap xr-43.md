---
type: incident
title: "INC-20260314 — BGP Session Flap xr-43"
incident_id: INC-20260314T082217Z
created: 2026-03-14
updated: 2026-03-15
status: resolved
severity: SEV-2
tags:
  - incident
  - bgp
  - flap
  - xr-43
  - core-routing
  - optics
  - isp-a
affected_systems:
  - xr-43
  - BGP peering to ISP-A (AS 65001)
duration_minutes: 47
sla_breached: false
related:
  - "[[BGP]]"
  - "[[BFD]]"
  - "[[xr-43]]"
  - "[[ISP-A]]"
  - "[[Incident Severity SLAs]]"
  - "[[BGP Adjacency Troubleshooting]]"
  - "[[INC-20260509 — Persistent CRC Errors xr-43]]"
  - "[[SFP+ Silent Degradation — CRC Below BFD Threshold]]"
source: "[[INC-20260314 — BGP Session Flap xr-43 (source)]]"
---

# INC-20260314 — BGP Session Flap to Upstream PE (xr-43)

## Summary

Edge router [[xr-43]] (Cisco ASR-9904) experienced **3 repeated BGP session flaps** to upstream provider [[ISP-A]] (peer 198.51.100.1, AS 65001) over a 47-minute window. [[BFD]] fast-failover to xr-44 maintained connectivity, but route churn caused ~200ms elevated latency across 6 branch sites per flap event. **Root cause: degraded SFP transceiver on ISP-A's PE** (far-end, not local).

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 08:22:17 | First BGP NOTIFICATION — Hold Timer Expired |
| 08:22:18 | BFD session DOWN on GigabitEthernet0/0/0/1 |
| 08:23:02 | BGP session re-established |
| 08:27:41 | Second flap — same peer, same NOTIFICATION |
| 08:35:19 | Third flap — NOC escalates to SEV-2 |
| 08:48:00 | TAC engaged; CRC errors identified on interface |
| 09:02:00 | ISP-A confirms degraded optic on their PE side |
| 09:09:14 | ISP-A replaces SFP; session stabilizes |
| 09:22:00 | 15-min stability confirmed; incident resolved |

## Symptoms (Agent Pattern Matching)

| Symptom | Syslog / Observable |
|---------|---------------------|
| BGP session down | `%ROUTING-BGP-5-ADJCHANGE: neighbor 198.51.100.1 Down - Hold Timer Expired` |
| Interface state | `%PKT_INFRA-LINK-3-UPDOWN: Interface GigabitEthernet0/0/0/1, changed state to Down` |
| BFD flap | BFD session down on core-facing interface |
| Branch impact | 5–12% packet loss on 6 branch sites during convergence |
| CRC errors | Input CRC errors incrementing on GigabitEthernet0/0/0/1 |
| Flow | Route churn visible in Kentik flow analysis |

> [!key-insight] Distinguishing marker
> The BGP flap was caused by **CRC errors on the uplink interface** — not a BGP misconfiguration or policy error. When BGP sessions flap with Hold Timer Expired, always check `show interfaces` for CRC input errors before assuming a routing issue.

## Root Cause

Degraded SFP transceiver on ISP-A's PE router (far-end). CRC error rate exceeded BFD detection threshold, causing link-layer drops and BGP hold timer expiry. xr-43's own optics were within spec. This is a **far-end optic degradation** scenario — invisible to local SNMP polling until it causes link events.

See: [[SFP+ Silent Degradation — CRC Below BFD Threshold]]

## Resolution Steps

1. `show controllers optics 0/0/0/1` — confirmed xr-43 interface optics within spec
2. `show interfaces GigabitEthernet0/0/0/1` — observed CRC input errors incrementing
3. Engaged ISP-A NOC with evidence of far-end CRC errors
4. ISP-A replaced degraded SFP on their PE router
5. Monitored 15 minutes post-fix — zero CRC errors, BGP stable

## Impact

| Metric | Value |
|--------|-------|
| Duration | 47 min (08:22–09:09 UTC) |
| Traffic | Minimal — BFD failover to xr-44 maintained connectivity |
| Branch sites | ~200ms elevated latency on 6 sites per flap event |
| SLA breach | No (SEV-2 responded within 15 min) |

## Lessons Learned / Patterns Extracted

- Far-end optic degradation is **invisible to local SNMP** until it causes link events
- CRC errors are the key diagnostic indicator — check before escalating to ISP
- BFD + ECMP failover worked as designed; no topology changes needed
- Consider proactive optical power monitoring via NETCONF/gNMI streaming telemetry
- See [[SFP+ Silent Degradation — CRC Below BFD Threshold]] for the general pattern
- Related later incident (local SFP failure): [[INC-20260509 — Persistent CRC Errors xr-43]]

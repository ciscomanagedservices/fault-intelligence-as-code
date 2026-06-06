---
type: incident
title: "INC-20260509 — Persistent CRC Errors xr-43"
incident_id: INC-20260509T143322Z
created: 2026-05-09
updated: 2026-05-10
status: resolved
severity: SEV-3
tags:
  - incident
  - crc-errors
  - hardware
  - xr-43
  - interface
  - optics
  - sfp
affected_systems:
  - xr-43
  - TenGigE0/0/0/3 (inter-DC link to DC-West)
duration_minutes: 77
sla_breached: false
related:
  - "[[BFD]]"
  - "[[xr-43]]"
  - "[[Cisco]]"
  - "[[Splunk]]"
  - "[[Oxidized]]"
  - "[[Incident Severity SLAs]]"
  - "[[INC-20260314 — BGP Session Flap xr-43]]"
  - "[[SFP+ Silent Degradation — CRC Below BFD Threshold]]"
  - "[[Interface CRC Error Troubleshooting]]"
source: "[[INC-20260509 — Persistent CRC Errors xr-43 (source)]]"
---

# INC-20260509 — Persistent CRC Errors on Fabric Interface (xr-43)

## Summary

Edge router [[xr-43]] (Cisco ASR-9904) interface TenGigE0/0/0/3 (inter-DC link to DC-West) accumulated CRC input errors at ~40/min. **The link stayed UP** — [[BFD]] did not trigger, no BGP flap — but latency-sensitive traffic (VoIP, trading feeds) experienced quality degradation. Detected by Splunk threshold alert (>500 CRC errors in 15 min). **Root cause: failing SFP+ with degraded signal integrity despite power within spec.** Resolved by local SFP replacement.

> [!key-insight] Silent degradation
> This is a **"silent" hardware failure** — the interface remained UP, BFD did not fire, no BGP flaps. The only indicators were CRC counter increments (not logged by default) and VoIP quality complaints. Without the Splunk CRC threshold alert, this could have persisted indefinitely.

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 14:33:22 | Splunk alert: "CRC error threshold exceeded on xr-43 TenGigE0/0/0/3" |
| 14:35:00 | NOC acknowledges; assigns SEV-3 (2-hour response for non-outage degradation) |
| 14:42:00 | `show interfaces TenGigE0/0/0/3` — 2,847 input CRC errors (counter reset 6h prior) |
| 14:45:00 | `show controllers optics 0/0/0/3` — Rx power -2.1 dBm (within spec, trending low) |
| 14:50:00 | Checked far-end (DC-West spine-02) — Tx power normal |
| 15:10:00 | Cleaned fiber patch panel at xr-43 MMR |
| 15:15:00 | CRC rate unchanged — dirty connector ruled out |
| 15:30:00 | Replaced SFP+ transceiver on TenGigE0/0/0/3 |
| 15:35:00 | CRC errors stopped immediately |
| 15:50:00 | 15-min zero-error window confirmed; incident resolved |

## Symptoms (Agent Pattern Matching)

| Symptom | Syslog / Observable |
|---------|---------------------|
| CRC counter | `show interfaces TenGigE0/0/0/3` — input CRC errors incrementing steadily (~40/min) |
| Link state | Interface remains UP — `%PKT_INFRA-LINEPROTO-5-UPDOWN` NOT triggered |
| BFD | No BFD flap (error rate below BFD detection sensitivity) |
| BGP | No BGP session drop |
| Monitoring | Splunk threshold alert: >500 CRC errors in 15-min window |
| User reports | VoIP quality degradation — jitter spikes correlated |
| Optics | Rx power within spec (-2.1 dBm) but signal integrity degraded |

## Root Cause

Failing SFP+ transceiver in slot 0/0/0/3 on xr-43. Power levels remained within acceptable range but the module was producing **bit errors at the physical layer** — a known end-of-life failure mode for SFP+ optics. Far-end (DC-West spine-02) Tx power was normal, ruling out the cable or far-end issue.

**Pattern:** SFP+ modules can fail gracefully — optical power stays acceptable while signal integrity degrades. This produces CRC errors **below the threshold that triggers BFD or interface state changes** — making it a "silent" degradation.

See: [[SFP+ Silent Degradation — CRC Below BFD Threshold]]

## Resolution Steps

1. `show interfaces summary` — isolated CRC errors to single interface
2. `show interfaces TenGigE0/0/0/3` — confirmed counter incrementing, interface UP
3. `show controllers optics 0/0/0/3` — Rx power within spec; no obvious optic failure
4. Verified far-end optics healthy (ruled out cable or far-end issue)
5. Cleaned fiber connectors at MMR — no improvement
6. Replaced SFP+ transceiver with spare from on-site stock
7. Monitored 15 minutes — zero CRC errors post-swap
8. Opened RMA for failed SFP+ (serial: FNS23410R7M)

## Impact

| Metric | Value |
|--------|-------|
| Duration | 1 hr 17 min (detection to resolution) |
| Traffic | No packet loss; quality degradation on latency-sensitive flows |
| User impact | 3 VoIP quality complaints from UC team |
| SLA breach | No (SEV-3, 2-hour response met) |

## Lessons Learned / Patterns Extracted

- SFP+ modules can fail **gracefully** — power in-spec but signal integrity degraded
- CRC errors below BFD threshold = "silent degradation" — only caught by counter polling
- Standard diagnostic sequence: interface counters → optics → far-end → connectors → SFP replacement
- Added Oxidized alert: CRC error delta > 100 between 4-hour config snapshots
- Recommend lifecycle replacement of SFP+ modules >5 years in edge router slots
- See [[SFP+ Silent Degradation — CRC Below BFD Threshold]] for general pattern and proactive measures
- See [[Interface CRC Error Troubleshooting]] for the full diagnostic runbook
- Related incident (far-end optic degradation causing BGP flap): [[INC-20260314 — BGP Session Flap xr-43]]

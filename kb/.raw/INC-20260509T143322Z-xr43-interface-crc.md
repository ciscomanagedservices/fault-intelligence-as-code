---
type: incident
title: "Persistent CRC Errors on Fabric Interface — xr-43"
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
affected_systems:
  - xr-43
  - TenGigE0/0/0/3 (inter-DC link to DC-West)
related:
  - "[[Cisco]]"
  - "[[BFD]]"
  - "[[Incident Severity SLAs]]"
sources: []
---

# INC-20260509T143322Z — Persistent CRC Errors on Fabric Interface (xr-43)

## Summary

Edge router **xr-43** (Cisco ASR-9904) interface TenGigE0/0/0/3 (inter-DC link to DC-West) began accumulating CRC input errors at a rate of ~40/minute. The link remained UP and BFD did not trigger, but quality-of-service degradation was observed on latency-sensitive traffic (VoIP, trading feeds). Splunk threshold alert fired after 500 CRC errors in 15 minutes.

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 14:33:22 | Splunk alert: "CRC error threshold exceeded on xr-43 TenGigE0/0/0/3" |
| 14:35:00 | NOC acknowledges; assigns SEV-3 per SLA (2-hour response for non-outage degradation) |
| 14:42:00 | `show interfaces TenGigE0/0/0/3` confirms 2,847 input CRC errors (counter reset 6h ago) |
| 14:45:00 | `show controllers optics 0/0/0/3` — Rx power -2.1 dBm (within spec but trending low) |
| 14:50:00 | Checked far-end (DC-West switch spine-02) — Tx power normal |
| 15:10:00 | Cleaned fiber patch panel at xr-43 MMR |
| 15:15:00 | CRC rate unchanged — ruled out dirty connector |
| 15:30:00 | Swapped SFP+ transceiver on xr-43 TenGigE0/0/0/3 |
| 15:35:00 | CRC errors stopped immediately |
| 15:50:00 | 15-min zero-error window confirmed; incident resolved |

## Symptoms

- Syslog: `%PKT_INFRA-LINEPROTO-5-UPDOWN` NOT triggered (link stayed UP)
- Splunk alert on CRC threshold (>500 in 15 min)
- VoIP quality degradation reports from UC team (jitter spikes correlated)
- No BFD flap — error rate below BFD detection sensitivity
- `show interfaces` CRC counter incrementing steadily

## Root Cause

Failing SFP+ transceiver in slot 0/0/0/3 on xr-43. The optic was within spec on power readings but producing bit errors at the physical layer. This is a known failure mode for SFP+ modules approaching end-of-life — power levels remain acceptable while signal integrity degrades.

## Resolution Steps

1. Confirmed CRC errors isolated to single interface via `show interfaces summary`
2. Verified far-end optics healthy (ruled out cable or far-end issue)
3. Cleaned fiber connectors — no improvement
4. Replaced SFP+ transceiver with spare from on-site stock
5. Monitored 15 minutes — zero CRC errors post-swap
6. Opened RMA for failed SFP+ (serial: FNS23410R7M)

## Impact

- Duration: 1 hour 17 minutes (detection to resolution)
- Traffic impact: No packet loss, but quality degradation on latency-sensitive flows
- 3 VoIP quality complaints from UC team during the event
- No SLA breach (SEV-3, 2-hour response met)

## Lessons Learned

- SFP+ transceivers can fail gracefully — power within spec but signal integrity degraded
- CRC errors below BFD threshold are a "silent degradation" — only caught by counter polling
- Added Oxidized config diff check: alert if CRC error delta > 100 between 4-hour snapshots
- Recommend lifecycle replacement of SFP+ modules older than 5 years in edge router slots

---
type: known-issue
title: "SFP+ Silent Degradation — CRC Below BFD Threshold"
created: 2026-05-29
updated: 2026-05-29
status: active
severity: medium
tags:
  - known-issue
  - hardware
  - optics
  - sfp
  - crc-errors
  - bfd
  - silent-degradation
affected_platforms:
  - Cisco ASR-9904
  - Cisco ASR-9910
  - Any router/switch with SFP/SFP+ interfaces
related:
  - "[[BFD]]"
  - "[[INC-20260314 — BGP Session Flap xr-43]]"
  - "[[INC-20260509 — Persistent CRC Errors xr-43]]"
  - "[[xr-43]]"
  - "[[Interface CRC Error Troubleshooting]]"
  - "[[BGP Adjacency Troubleshooting]]"
sources:
  - "[[INC-20260314 — BGP Session Flap xr-43 (source)]]"
  - "[[INC-20260509 — Persistent CRC Errors xr-43 (source)]]"
workaround_available: true
---

# SFP+ Silent Degradation — CRC Below BFD Threshold

## Problem Description

SFP+ transceivers can fail **gracefully** — optical Tx/Rx power levels remain within acceptable thresholds while signal integrity at the physical layer degrades. This produces **CRC input errors** at a rate that is:

- High enough to cause **quality degradation** (VoIP jitter, packet retransmissions, latency on latency-sensitive flows)
- Low enough that **BFD does not trigger** (interface stays UP, no link-state change)
- Low enough that **BGP hold timers may not expire** (unless rate is very high)

**Result:** The fault is invisible to standard monitoring (SNMP, BFD, BGP state) and can persist indefinitely without a CRC-specific alert.

## Affected Scenarios

| Scenario | Visibility |
|----------|-----------|
| Local SFP+ failing | Not visible via SNMP optic polling until late-stage; caught by CRC counters |
| Far-end SFP failing | Invisible locally — only visible as CRC errors on the local interface |
| Dirty/damaged fiber | Produces identical symptom; rule out with cleaning before SFP swap |

## Detection

| Method | Detail |
|--------|--------|
| Splunk CRC threshold alert | Alert if CRC delta > 500 in 15-min window (implemented post INC-20260509) |
| Oxidized config diff | Alert if CRC error delta > 100 between 4-hour snapshots (implemented post INC-20260509) |
| Manual | `show interfaces <int>` — check input errors / CRC counter |
| Optic readings | `show controllers optics <slot>` — may NOT show anomaly even with failing SFP |

> [!warning] Do not rely on optical power readings alone
> A failing SFP+ may show Rx power at -2.1 dBm (within spec) while producing hundreds of CRC errors per minute. Optical power within spec does **not** rule out SFP failure.

## Diagnostic Steps

See [[Interface CRC Error Troubleshooting]] for the full procedure. Quick summary:

1. Isolate interface via `show interfaces summary`
2. Check CRC counter on target interface
3. Read optics — note even if in-spec
4. Verify far-end optics
5. Clean fiber patch panel
6. If CRC rate unchanged after cleaning → replace SFP

## Workaround / Fix

**Immediate:** Replace SFP+ transceiver with a known-good spare from on-site stock.

**Proactive:**
- Implement Splunk alert: CRC errors > 500 in 15 minutes on any interface
- Implement Oxidized alert: CRC delta > 100 per 4-hour snapshot
- Lifecycle: replace SFP+ modules **older than 5 years** in edge router slots proactively

## Incident References

| Incident                                       | Device               | Details                                                                          |
| ---------------------------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| [[INC-20260509 — Persistent CRC Errors xr-43]] | xr-43 TenGigE0/0/0/3 | Local SFP+ failing; ~40 CRC/min; link UP; VoIP degradation; resolved by SFP swap |
| [[INC-20260314 — BGP Session Flap xr-43]]      | xr-43 GigE0/0/0/1    | Far-end (ISP-A PE) SFP degraded; CRC → BFD trigger → BGP flap; resolved by ISP-A |

## Agent Short-Circuit Rule

> When a troubleshooting agent detects CRC input errors incrementing on any interface — even with the interface UP and no BGP/BFD events — treat this as a potential SFP failure. Immediately check far-end optics and proceed to the [[Interface CRC Error Troubleshooting]] runbook rather than the [[BGP Adjacency Troubleshooting]] runbook.

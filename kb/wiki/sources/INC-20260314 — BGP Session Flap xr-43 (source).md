---
type: source
title: "INC-20260314 — BGP Session Flap xr-43 (source)"
raw_file: ".raw/INC-20260314T082217Z-xr43-bgp-flap.md"
ingested: 2026-05-29
incident_id: INC-20260314T082217Z
created: 2026-03-14
tags:
  - source
  - incident
  - bgp
  - xr-43
status: ingested
related:
  - "[[INC-20260314 — BGP Session Flap xr-43]]"
---

# Source: INC-20260314 — BGP Session Flap xr-43

**Raw file:** `kb/.raw/INC-20260314T082217Z-xr43-bgp-flap.md`
**Incident page:** [[INC-20260314 — BGP Session Flap xr-43]]

## Document Summary

Internal incident record for a SEV-2 BGP session flap event on edge router xr-43 (Cisco ASR-9904) on 2026-03-14. The BGP session to upstream [[ISP-A]] (AS 65001) flapped 3 times over 47 minutes. Root cause was a degraded SFP transceiver on ISP-A's PE — a far-end optic issue invisible to local monitoring. BFD fast-failover to xr-44 maintained connectivity. Resolved by ISP-A replacing the SFP.

## Pages Created from This Source

| Page | Folder |
|------|--------|
| [[INC-20260314 — BGP Session Flap xr-43]] | `incidents/` |
| [[xr-43]] | `entities/` |
| [[ISP-A]] | `entities/` |
| [[SFP+ Silent Degradation — CRC Below BFD Threshold]] | `known-issues/` |

## Key Extractions

- **Diagnostic technique:** Check `show interfaces` CRC errors when BGP flaps with Hold Timer Expired
- **Known issue pattern:** Far-end optic degradation → CRC errors → BFD trigger → BGP hold timer expiry
- **Lesson:** Local optic readings being in-spec does NOT rule out a physical-layer issue

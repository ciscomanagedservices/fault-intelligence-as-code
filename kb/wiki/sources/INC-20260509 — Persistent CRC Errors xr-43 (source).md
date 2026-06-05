---
type: source
title: "INC-20260509 — Persistent CRC Errors xr-43 (source)"
raw_file: ".raw/INC-20260509T143322Z-xr43-interface-crc.md"
ingested: 2026-05-29
incident_id: INC-20260509T143322Z
created: 2026-05-09
tags:
  - source
  - incident
  - crc-errors
  - xr-43
  - hardware
status: ingested
related:
  - "[[INC-20260509 — Persistent CRC Errors xr-43]]"
---

# Source: INC-20260509 — Persistent CRC Errors xr-43 (source)

**Raw file:** `kb/.raw/INC-20260509T143322Z-xr43-interface-crc.md`
**Incident page:** [[INC-20260509 — Persistent CRC Errors xr-43]]

## Document Summary

Internal incident record for a SEV-3 silent hardware degradation on xr-43 (Cisco ASR-9904) on 2026-05-09. Interface TenGigE0/0/0/3 (inter-DC link to DC-West) accumulated CRC input errors at ~40/min while staying UP — no BFD trigger, no BGP flap. Detected via Splunk CRC threshold alert. Caused VoIP quality degradation. Root cause: failing SFP+ with power within spec but degraded signal integrity. Resolved by local SFP replacement in 77 minutes.

## Pages Created from This Source

| Page | Folder |
|------|--------|
| [[INC-20260509 — Persistent CRC Errors xr-43]] | `incidents/` |
| [[xr-43]] | `entities/` (updated) |
| [[SFP+ Silent Degradation — CRC Below BFD Threshold]] | `known-issues/` (updated) |
| [[Interface CRC Error Troubleshooting]] | `runbooks/` |

## Key Extractions

- **Silent failure mode:** SFP+ can fail with power in-spec but signal integrity degraded
- **Detection gap:** CRC errors below BFD threshold won't trigger interface state changes — requires counter polling or Splunk threshold alert
- **Diagnostic sequence:** interface counters → optics → far-end → connectors → SFP replacement
- **Lifecycle recommendation:** Replace SFP+ modules older than 5 years in edge router slots

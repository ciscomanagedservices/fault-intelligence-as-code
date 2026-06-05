---
type: source
title: "INC-20260421 — Process Memory Exhaustion xr-43 (source)"
raw_file: ".raw/INC-20260421T031544Z-xr43-memory-exhaustion.md"
ingested: 2026-05-29
incident_id: INC-20260421T031544Z
created: 2026-04-21
tags:
  - source
  - incident
  - memory
  - xr-43
  - iac
status: ingested
related:
  - "[[INC-20260421 — Process Memory Exhaustion xr-43]]"
---

# Source: INC-20260421 — Process Memory Exhaustion xr-43 (source)

**Raw file:** `kb/.raw/INC-20260421T031544Z-xr43-memory-exhaustion.md`
**Incident page:** [[INC-20260421 — Process Memory Exhaustion xr-43]]

## Document Summary

Internal incident record for a SEV-1 BGP process OOM kill on xr-43 (Cisco ASR-9904, IOS-XR 7.9.2, 16GB RAM) on 2026-04-21. An [[Infrastructure as Code|IaC]] pipeline push deployed a route-policy referencing 12,847 prefixes, causing `bgp_policy_reg` to be OOM-killed. All 14 BGP sessions dropped simultaneously; 23 branch sites lost connectivity for 4m12s. The pipeline had been tested on xr-44 (32GB) without issue — platform memory difference was the root gap.

## Pages Created from This Source

| Page | Folder |
|------|--------|
| [[INC-20260421 — Process Memory Exhaustion xr-43]] | `incidents/` |
| [[xr-43]] | `entities/` (updated) |
| [[ASR-9904 BGP Process OOM — Large Prefix-Sets]] | `known-issues/` |

## Key Extractions

- **Platform limit:** ASR-9904 (16GB) cannot safely compile prefix-sets > 8,000 entries in a single commit
- **Diagnostic:** All BGP sessions drop simultaneously → process crash, not link issue
- **Correlation rule:** Config commit by `netauto` followed by memory warning within 30s
- **Mitigation:** Split large prefix-sets; add platform-aware memory check to Ansible playbooks

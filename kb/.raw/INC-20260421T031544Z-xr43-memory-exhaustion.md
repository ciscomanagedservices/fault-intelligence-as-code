---
type: incident
title: "Process Memory Exhaustion — xr-43"
incident_id: INC-20260421T031544Z
created: 2026-04-21
updated: 2026-04-22
status: resolved
severity: SEV-1
tags:
  - incident
  - memory
  - process-crash
  - xr-43
  - core-routing
affected_systems:
  - xr-43
  - All BGP peers on xr-43
  - 23 branch sites (primary uplink via xr-43)
related:
  - "[[BGP]]"
  - "[[Cisco]]"
  - "[[Incident Severity SLAs]]"
  - "[[NOC Alert Triage Procedure]]"
sources: []
---

# INC-20260421T031544Z — Process Memory Exhaustion (xr-43)

## Summary

Edge router **xr-43** (Cisco ASR-9904, IOS-XR 7.9.2) experienced memory exhaustion in the BGP process (`bgp_policy_reg`) leading to a BGP process restart. All 14 BGP sessions dropped simultaneously. Full convergence took 4 minutes 12 seconds. 23 branch sites lost connectivity for the duration.

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 03:15:44 | Syslog: `%MGBL-CONFIG-6-DB_COMMIT: Configuration committed by user 'netauto'` |
| 03:15:46 | Syslog: `%MEM-4-MEMORY_LOW: Memory for node 0/RSP0/CPU0 is running low` |
| 03:15:51 | Syslog: `%ROUTING-BGP-5-KILL: BGP process bgp_policy_reg killed due to out-of-memory` |
| 03:15:52 | All 14 BGP peers: `ADJCHANGE: Down - Process restart` |
| 03:16:00 | SEV-1 bridge opened per SLA (5-minute response) |
| 03:17:30 | BGP process restarted automatically (IOS-XR process restart) |
| 03:18:22 | First BGP peer re-established (iBGP to xr-44) |
| 03:19:56 | All iBGP peers recovered; route convergence complete |
| 03:22:10 | All eBGP peers re-established; branch traffic restored |
| 03:45:00 | Root cause identified: route-policy compilation spike from config push |
| 04:00:00 | Incident closed after 30-min stability window |

## Symptoms

- Syslog: `%MEM-4-MEMORY_LOW: Memory for node 0/RSP0/CPU0 is running low`
- Syslog: `%ROUTING-BGP-5-KILL: BGP process bgp_policy_reg killed due to out-of-memory`
- All BGP sessions DOWN simultaneously (not sequential flap)
- Splunk alert: "xr-43 BGP peer count dropped below threshold"
- ThousandEyes: 23 branch probes reporting 100% packet loss

## Root Cause

An automated config push by the IaC pipeline (`netauto` user via Ansible) deployed a route-policy change that referenced a large prefix-set (12,847 prefixes). The `bgp_policy_reg` process attempted to recompile all affected policies in-memory simultaneously, exceeding the configured memory limit for the process group. This triggered the OOM kill.

The same config change had been tested on xr-44 (ASR-9910, 32GB RAM) without issue. xr-43 (ASR-9904, 16GB RAM) has half the memory — the pipeline did not account for platform memory differences.

## Resolution Steps

1. BGP process auto-restarted via IOS-XR process supervision (no manual intervention for recovery)
2. Verified all peers re-established and routes converged
3. Identified triggering commit via `show configuration history last 5 detail`
4. Rolled back route-policy change to previous version
5. Added memory guard: split large prefix-set into 3 smaller sets applied incrementally
6. Added pre-deployment memory check to Ansible playbook for ASR-9904 targets

## Impact

- Duration: 4 minutes 12 seconds (total outage), 45 minutes (incident lifecycle)
- Traffic impact: **Complete loss** for 23 branch sites relying on xr-43 as primary path
- SLA breach: No (SEV-1 allows 5-min response; bridge opened at 03:16:00, 16 seconds post-event)

## Lessons Learned

- IaC pipeline must include **platform-aware memory validation** before deploying policy changes
- ASR-9904 (16GB) cannot safely compile prefix-sets > 8,000 entries in a single commit
- Consider IOS-XR BGP Graceful Restart to reduce convergence time on process crashes
- Added Splunk alert: "config commit on xr-43 followed by memory warning within 30s"

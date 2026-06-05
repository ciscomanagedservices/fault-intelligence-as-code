---
type: incident
title: "INC-20260421 — Process Memory Exhaustion xr-43"
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
  - iac
  - bgp
  - oom
affected_systems:
  - xr-43
  - All BGP peers on xr-43 (14 sessions)
  - 23 branch sites (primary uplink)
duration_minutes: 4
incident_lifecycle_minutes: 45
sla_breached: false
related:
  - "[[BGP]]"
  - "[[xr-43]]"
  - "[[Cisco]]"
  - "[[Splunk]]"
  - "[[ThousandEyes]]"
  - "[[Infrastructure as Code]]"
  - "[[Incident Severity SLAs]]"
  - "[[NOC Alert Triage Procedure]]"
  - "[[ASR-9904 BGP Process OOM — Large Prefix-Sets]]"
source: "[[INC-20260421 — Process Memory Exhaustion xr-43 (source)]]"
---

# INC-20260421 — Process Memory Exhaustion (xr-43)

## Summary

Edge router [[xr-43]] (Cisco ASR-9904, IOS-XR 7.9.2, **16GB RAM**) experienced BGP process OOM kill (`bgp_policy_reg`) after an [[Infrastructure as Code|IaC]] pipeline pushed a route-policy referencing a 12,847-entry prefix-set. All **14 BGP sessions dropped simultaneously**. BGP auto-restarted; convergence completed in 4m 12s. **23 branch sites lost connectivity** for the full convergence window. IaC pipeline did not account for memory differences between xr-43 (16GB) and xr-44 (32GB).

> [!key-insight] SEV-1 characteristic
> Unlike a flapping BGP session, ALL peers dropped simultaneously — this is the signature of a process crash, not a link issue. The triggering commit was visible in `show configuration history`.

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 03:15:44 | `%MGBL-CONFIG-6-DB_COMMIT: Configuration committed by user 'netauto'` |
| 03:15:46 | `%MEM-4-MEMORY_LOW: Memory for node 0/RSP0/CPU0 is running low` |
| 03:15:51 | `%ROUTING-BGP-5-KILL: BGP process bgp_policy_reg killed due to out-of-memory` |
| 03:15:52 | All 14 BGP peers: `ADJCHANGE: Down - Process restart` |
| 03:16:00 | SEV-1 bridge opened (within 5-min SLA) |
| 03:17:30 | BGP process auto-restarted via IOS-XR process supervision |
| 03:18:22 | First peer re-established (iBGP to xr-44) |
| 03:19:56 | All iBGP recovered; route convergence complete |
| 03:22:10 | All eBGP peers re-established; branch traffic restored |
| 03:45:00 | Root cause identified: route-policy compilation spike |
| 04:00:00 | Closed after 30-min stability window |

## Symptoms (Agent Pattern Matching)

| Symptom | Syslog / Observable |
|---------|---------------------|
| Memory warning | `%MEM-4-MEMORY_LOW: Memory for node 0/RSP0/CPU0 is running low` |
| BGP process killed | `%ROUTING-BGP-5-KILL: BGP process bgp_policy_reg killed due to out-of-memory` |
| All BGP sessions down | `ADJCHANGE: Down - Process restart` (all 14 peers simultaneously) |
| Monitoring alert | Splunk: "xr-43 BGP peer count dropped below threshold" |
| Synthetic probes | ThousandEyes: 23 branch probes reporting 100% packet loss |
| Preceding event | Config commit by `netauto` user 7 seconds before memory warning |

> [!key-insight] Key distinguishing marker
> All BGP sessions drop **simultaneously** within 1 second — this is a process crash, not interface-level flapping. Cross-correlate with a config commit immediately prior.

## Root Cause

IaC pipeline (`netauto` user, Ansible) pushed a route-policy referencing a **12,847-entry prefix-set**. The `bgp_policy_reg` process attempted to recompile all affected policies in-memory simultaneously, exceeding the configured memory limit. OOM kill triggered.

**Platform memory disparity:** Same config change tested on xr-44 (ASR-9910, **32GB RAM**) without issue. xr-43 (ASR-9904, **16GB RAM**) has half the memory — the Ansible playbook had no platform-aware memory validation.

**Limit:** ASR-9904 (16GB) cannot safely compile prefix-sets > 8,000 entries in a single commit.

See: [[ASR-9904 BGP Process OOM — Large Prefix-Sets]]

## Resolution Steps

1. BGP process auto-restarted via IOS-XR process supervision (no manual intervention needed)
2. Verified all 14 peers re-established and routes converged
3. Identified triggering commit: `show configuration history last 5 detail`
4. Rolled back route-policy change to previous version
5. Split large prefix-set into 3 smaller sets applied incrementally
6. Added pre-deployment memory check to Ansible playbook for ASR-9904 targets
7. Added Splunk alert: "config commit on xr-43 followed by memory warning within 30s"

## Impact

| Metric | Value |
|--------|-------|
| Outage duration | 4 min 12 sec (full BGP loss) |
| Incident lifecycle | 45 min |
| Affected branches | 23 sites (100% packet loss) |
| SLA breach | No (SEV-1 bridge at 03:16:00 — 16s after event) |
| Recovery | Automatic (no manual restart needed) |

## Lessons Learned / Patterns Extracted

- IaC pipelines **must include platform-aware memory validation** before deploying policy changes
- ASR-9904 (16GB): safe prefix-set compile limit ~8,000 entries per commit
- Config commit + memory warning within 30s = strong OOM indicator → add Splunk correlation rule
- Consider IOS-XR BGP Graceful Restart to reduce convergence impact on process crashes
- All-sessions-simultaneous drop = process crash, not link issue — diagnose differently
- See [[ASR-9904 BGP Process OOM — Large Prefix-Sets]] for the generalized known issue and workaround

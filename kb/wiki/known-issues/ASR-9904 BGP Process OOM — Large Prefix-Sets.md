---
type: known-issue
title: "ASR-9904 BGP Process OOM — Large Prefix-Sets"
created: 2026-05-29
updated: 2026-05-29
status: active
severity: critical
tags:
  - known-issue
  - memory
  - oom
  - asr-9904
  - ios-xr
  - bgp
  - iac
  - prefix-set
affected_platforms:
  - Cisco ASR-9904 (16GB RAM)
not_affected:
  - Cisco ASR-9910 (32GB RAM) — tested without issue
related:
  - "[[xr-43]]"
  - "[[BGP]]"
  - "[[Infrastructure as Code]]"
  - "[[INC-20260421 — Process Memory Exhaustion xr-43]]"
  - "[[NOC Alert Triage Procedure]]"
sources:
  - "[[INC-20260421 — Process Memory Exhaustion xr-43 (source)]]"
workaround_available: true
---

# ASR-9904 BGP Process OOM — Large Prefix-Sets

## Problem Description

On Cisco ASR-9904 routers with **16GB RAM** running IOS-XR 7.9.2+, deploying a BGP route-policy that references a large prefix-set triggers the `bgp_policy_reg` process to recompile all affected policies simultaneously. If the prefix-set exceeds the safe threshold, the process group exceeds its memory limit and is **OOM-killed by the kernel**.

**Consequence:** All BGP sessions on the device drop simultaneously. IOS-XR process supervision auto-restarts the BGP process, but convergence takes ~4 minutes — enough to cause a full outage for downstream branch sites.

## Platform Memory Contrast

| Platform | RAM | Safe prefix-set limit per commit | Notes |
|----------|-----|----------------------------------|-------|
| ASR-9904 | 16 GB | **~8,000 entries** | Subject of INC-20260421 |
| ASR-9910 | 32 GB | > 12,847 entries tested OK | No issue observed |
| ASR-9920+ | 64+ GB | N/A (no incidents) | — |

> [!warning] Do not test on ASR-9910 and deploy to ASR-9904
> The same configuration change passed QA on xr-44 (ASR-9910, 32GB) and caused a SEV-1 outage on xr-43 (ASR-9904, 16GB). Platform memory differences are not automatically accounted for by Ansible without explicit platform checks.

## Triggering Condition

An [[Infrastructure as Code|IaC]] pipeline (`netauto` user, Ansible) commits a route-policy referencing a single prefix-set with more than ~8,000 entries to an ASR-9904 target.

**Syslog signature (in order):**
```
%MGBL-CONFIG-6-DB_COMMIT: Configuration committed by user 'netauto'
%MEM-4-MEMORY_LOW: Memory for node 0/RSP0/CPU0 is running low
%ROUTING-BGP-5-KILL: BGP process bgp_policy_reg killed due to out-of-memory
%ROUTING-BGP-5-ADJCHANGE: neighbor X.X.X.X Down - Process restart (×14)
```

**Time window:** Memory warning appears within 2–7 seconds of config commit.

## Detection / Monitoring

| Alert | Description |
|-------|-------------|
| Splunk correlation rule | "Config commit on xr-43 followed by memory warning within 30s" — added post INC-20260421 |
| Splunk BGP peer count | "xr-43 BGP peer count dropped below threshold" (existing) |
| ThousandEyes | Branch probe 100% packet loss (confirms blast radius) |

## Workaround

**Immediate recovery:** No manual action needed — IOS-XR process supervision auto-restarts `bgp_policy_reg`. Monitor peers and verify all BGP sessions re-establish (~4 min).

**Preventive (implemented post INC-20260421):**

1. **Split large prefix-sets.** Divide any prefix-set > 6,000 entries into multiple sets of ≤ 3,000 entries each. Apply via incremental commits.

2. **Add platform-aware memory check to Ansible playbooks** targeting ASR-9904:
   ```yaml
   - name: Pre-deploy memory check (ASR-9904)
     ios_command:
       commands: show platform resources
     register: mem_output
   - name: Fail if memory < 4GB free
     fail:
       msg: "Insufficient free memory on ASR-9904 — aborting route-policy deploy"
     when: "'<4096' in mem_output.stdout[0]"
   ```

3. **Graceful Restart consideration.** Enable BGP Graceful Restart on xr-43 to reduce convergence impact if an OOM kill occurs despite preventive measures.

## Incident Reference

| Incident | Date | Details |
|----------|------|---------|
| [[INC-20260421 — Process Memory Exhaustion xr-43]] | 2026-04-21 | SEV-1; 23 branch sites, 4m12s full outage; root cause IaC prefix-set push |

## Agent Short-Circuit Rule

> When the troubleshooting agent sees simultaneous BGP session drops (all peers down within 1–2 seconds) on xr-43 AND a config commit by `netauto` in the preceding 30 seconds AND a `%MEM-4-MEMORY_LOW` syslog: classify immediately as IaC-triggered OOM. Do NOT investigate BGP configuration or link layer. Monitor process auto-restart and peer re-establishment. Verify rollback of the triggering commit.

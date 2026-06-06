# Remediation Guide: BGP Neighbor Down — Neighbor's Maximum Prefix Limit Exceeded by Local Advertisement (IOS XR)

> **Source:** `ia-drafts/AD000003-bgp-max-prefix-adjchange-xr/docs/RG000003-bgp-max-prefix-adjchange-questionnaire.md`
> **Generated:** 2026-05-29
> **Status:** Final
> **Alert Definition:** AD000003
> **Guide ID:** RG000003
> **Linked Fault Signature:** FS000003
> **Linked Repair Action Workflow:** RAW000003

---

## Overview

This guide addresses IOS XR BGP peering failures where the neighbor sends a CEASE
notification because the local router advertised more prefixes than the neighbor's
configured inbound maximum-prefix limit allows. The key clue is the syslog text
`BGP Notification received, maximum number of prefixes reached`, which means the
neighbor initiated the teardown. The intended repair path is deliberately simple:
confirm the fault, identify a recent export policy or prefix-set change, roll back a
clearly offending recent commit when it is safe to do so, restore the BGP session,
and verify that the peering remains stable.

## Applicability

- **Products:** Cisco ASR 9000 Series; Cisco 8000 Series; Cisco NCS 5000, 5500,
  5700 Series; Cisco NCS 540, 560 Series; other IOS XR platforms using the BGP
  routing process
- **Operating Systems:** IOS XR
- **Component:** Route Processor / BGP process
- **Severity:** Warning
- **Related Defects:** None identified for this guide

## Triggering Events

### Event 1: Neighbor-Sent BGP CEASE for Maximum Prefixes

- **Type:** Syslog
- **Message ID:** ROUTING-BGP-5-ADJCHANGE
- **Example Message:**
  ```
  bgp[1090]: %ROUTING-BGP-5-ADJCHANGE : neighbor 172.20.20.17 Down - BGP Notification received, maximum number of prefixes reached (VRF: default) (AS: 65535)
  ```
- **Key Values to Extract:** `{{ neighbor_ip }}` from the text after `neighbor`,
  `{{ vrf_name }}` from the `VRF:` field, and `{{ asn }}` from the `AS:` field

### Recovery Indicator

- **Recovery Event:**
  ```
  bgp[1090]: %ROUTING-BGP-5-ADJCHANGE : neighbor 172.20.20.17 Up (VRF: default) (AS: 65535)
  ```
- **Recovery Window:** The session should return to `Established` within
  **120 seconds** after the rollback is applied and `clear bgp` is issued.

## Symptoms

- BGP neighbor `{{ neighbor_ip }}` is `Idle` or `Active`, not `Established`
- Routes learned through `{{ neighbor_ip }}` are withdrawn from the RIB and traffic
  may black-hole or move to a less preferred path
- `show bgp neighbors {{ neighbor_ip }}` reports a last reset reason referencing
  `Maximum Number of Prefixes Reached`
- The session does not recover on its own after the offending advertisement change
- The outage often lines up with a recent route-policy, prefix-set, or related export
  policy change on the local router

## Diagnosis & Repair Steps

### Step 1: Confirm This Is the Correct BGP Failure Mode

**Commands:**
```
show bgp neighbors {{ neighbor_ip }} | include State|reset
```

**What to Look For:** Confirm the neighbor is not `Established` and that the last
reset reason explicitly references a neighbor-sent notification for maximum prefixes.
If the session is down for another reason, this guide does not apply.

**Sample Output — Healthy:**
```
RP/0/RP0/CPU0:router# show bgp neighbors 172.20.20.17 | include State|reset
  BGP state = Established, up for 2d14h33m
```

**Sample Output — Fault Confirmed:**
```
RP/0/RP0/CPU0:router# show bgp neighbors 172.20.20.17 | include State|reset
  BGP state = Idle
  Last reset 00:08:42 ago, due to BGP Notification received (Maximum Number of Prefixes Reached)
```

**Decision Point:**
- If the session is `Idle` or `Active` and the reset reason shows maximum prefixes,
  proceed to Step 2.
- If the session is already `Established`, stop — the fault is no longer active.
- If the session is down for a different reason, stop and use a different BGP guide.
- If the output is incomplete or the reset reason cannot be determined, escalate per
  the Escalation section.

---

### Step 2: Check Recent Commit History for an Export Policy Change

**Commands:**
```
show configuration commit list
show configuration commit changes last 1
show configuration commit changes last 5
show bgp neighbors {{ neighbor_ip }} | include policy
```

**What to Look For:** Use a simple search window: inspect commits from the last
**4 hours** and review up to the **last 5 commits** first. Look for changes to the
neighbor's attached export route-policy, referenced prefix-set, or obvious related
redistribution / policy attachment changes.

**Sample Output — Healthy:**
```
RP/0/RP0/CPU0:router# show configuration commit changes last 1
Building configuration...
!! IOS XR Configuration 7.9.1
router bgp 64512
 neighbor 172.20.20.8
  description MGMT_LINK
 !
!
end

RP/0/RP0/CPU0:router# show bgp neighbors 172.20.20.17 | include policy
  Outbound route policy: PEER_65535_EXPORT
```

**Sample Output — Fault Confirmed:**
```
RP/0/RP0/CPU0:router# show configuration commit changes last 1
Building configuration...
!! IOS XR Configuration 7.9.1
route-policy PEER_65535_EXPORT
  if destination in ANY_PREFIX then
    pass
  else
    drop
  endif
end-policy
!
end

RP/0/RP0/CPU0:router# show bgp neighbors 172.20.20.17 | include policy
  Outbound route policy: PEER_65535_EXPORT
```

**Decision Point:**
- If you find a recent export route-policy or prefix-set change that clearly aligns
  with the outage, proceed to Step 3.
- If the most recent commit is unrelated, inspect up to the last 5 commits. If still
  unclear, extend to 10 commits maximum within the last 4 hours.
- If no relevant change is found, do one quick sanity check for obvious redistribution
  or policy attachment changes affecting `{{ neighbor_ip }}`. If still no clear cause
  is found, escalate.
- If commit history is unavailable or cannot be trusted, escalate.

---

### Step 3: Preview the Rollback and Confirm It Is Safe

**Commands:**
```
show configuration rollback changes last 1
show rpl route-policy {{ policy_name }}
```

**What to Look For:** The rollback preview must clearly restore the export policy or
prefix-set to a more restrictive version and must not include unacceptable unrelated
changes. This simplified guide only supports a clean rollback of a clearly offending
recent commit.

**Sample Output — Healthy:**
```
RP/0/RP0/CPU0:router# show configuration rollback changes last 1
Building configuration...
!! IOS XR Configuration 7.9.1
route-policy PEER_65535_EXPORT
  if destination in ALLOWED_TO_65535 then
    pass
  else
    drop
  endif
end-policy
!
end

RP/0/RP0/CPU0:router# show rpl route-policy PEER_65535_EXPORT
route-policy PEER_65535_EXPORT
  if destination in ANY_PREFIX then
    pass
  else
    drop
  endif
end-policy
```

**Sample Output — Fault Confirmed:**
```
RP/0/RP0/CPU0:router# show configuration rollback changes last 1
Building configuration...
!! IOS XR Configuration 7.9.1
interface HundredGigE0/0/0/1
 description CORE_LINK
!
route-policy PEER_65535_EXPORT
  if destination in ANY_PREFIX then
    pass
  else
    drop
  endif
end-policy
!
end
```

**Decision Point:**
- If the preview cleanly restores the intended restrictive policy and the rollback
  scope is acceptable, proceed to Step 4.
- If the preview does not meaningfully restore the export policy, review 1–2 older
  commits within the Step 2 search window to confirm whether the true policy change is
  older than the current rollback candidate. If it is not a clean last-commit rollback,
  stop this simplified path and escalate.
- If the preview includes mixed changes with unclear blast radius, do not apply the
  rollback without local approval or routing SME review.
- If only the policy should be reverted but unrelated changes must be preserved,
  treat manual policy surgery as out of scope for this guide and escalate / hand off.

**Caution:** `rollback configuration last 1` reverses the entire most recent commit.
Only use this during an active incident if the preview shows that the commit is
clearly the cause and mainly affects the relevant BGP export policy or prefix-set.

---

### Step 4: Apply the Rollback and Verify the Policy State

**Commands:**
```
rollback configuration last 1
show rpl route-policy {{ policy_name }}
```

**What to Look For:** The rollback should complete successfully and the policy should
now reflect the prior restrictive state.

**Sample Output — Healthy:**
```
RP/0/RP0/CPU0:router# rollback configuration last 1
Loading Rollback Changes.
Loaded Rollback Changes in 1 sec
Committing.
1 items committed in 1 sec (0)items/sec
Updating.
Updated Commit database in 1 sec
Configuration successfully rolled back 1 commits.

RP/0/RP0/CPU0:router# show rpl route-policy PEER_65535_EXPORT
route-policy PEER_65535_EXPORT
  if destination in ALLOWED_TO_65535 then
    pass
  else
    drop
  endif
end-policy
```

**Sample Output — Fault Confirmed:**
```
RP/0/RP0/CPU0:router# rollback configuration last 1
% Failed to complete rollback operation

RP/0/RP0/CPU0:router# show rpl route-policy PEER_65535_EXPORT
route-policy PEER_65535_EXPORT
  if destination in ANY_PREFIX then
    pass
  else
    drop
  endif
end-policy
```

**Decision Point:**
- If rollback succeeds and the policy is restored, proceed to Step 5.
- If rollback fails, escalate.
- If rollback succeeds but the policy still looks overly broad, do not continue with
  repeated rollback attempts under this guide; escalate.
- If output is inconsistent or the route-policy object cannot be verified, escalate.

**Caution:** This step can affect live routing behavior. Confirm local incident or
change-control expectations before proceeding when the commit affects more than the
targeted BGP peer.

---

### Step 5: Restore the BGP Session

**Commands:**
```
clear bgp ipv4 unicast {{ neighbor_ip }}
clear bgp vrf {{ vrf_name }} ipv4 unicast {{ neighbor_ip }}
show bgp neighbors {{ neighbor_ip }} | include State|reset
show logging last 100 | include {{ neighbor_ip }}
```

**What to Look For:** After the correct `clear bgp` command is issued for the
neighbor's VRF, the session should progress to `Established` within **120 seconds**.
If it returns to `Idle` with the same CEASE reason, the prefix problem remains. If it
stays stuck in `Active` for the full 120-second window, treat that as a different BGP
adjacency issue.

**Sample Output — Healthy:**
```
RP/0/RP0/CPU0:router# show bgp neighbors 172.20.20.17 | include State|reset
  BGP state = Established, up for 00:00:47

RP/0/RP0/CPU0:router# show logging last 100 | include 172.20.20.17
bgp[1090]: %ROUTING-BGP-5-ADJCHANGE : neighbor 172.20.20.17 Up (VRF: default) (AS: 65535)
```

**Sample Output — Fault Confirmed:**
```
RP/0/RP0/CPU0:router# show bgp neighbors 172.20.20.17 | include State|reset
  BGP state = Idle
  Last reset 00:00:18 ago, due to BGP Notification received (Maximum Number of Prefixes Reached)
```

**Decision Point:**
- If the session reaches `Established` within 120 seconds, proceed to Post-Repair
  Verification.
- If the session drops again with the same max-prefix CEASE, escalate.
- If the session remains `Active` or otherwise fails to reach `Established` within
  120 seconds, treat this as a different adjacency problem and escalate / hand off to
  standard BGP adjacency troubleshooting.
- If the wrong VRF command was used, correct it and retry once. If still unresolved,
  escalate.

**Caution:** `clear bgp` resets the live peering session. Expect transient routing
impact while the session is re-established.

## Escalation

**When to Escalate:**
- No relevant route-policy, prefix-set, redistribution, or policy attachment change is
  found after reviewing the last 5 commits and, if needed, up to 10 commits within the
  last 4 hours
- The rollback preview does not cleanly restore the intended restrictive policy
- The commit is mixed and the rollback blast radius is unclear
- Rollback fails or the policy remains overly broad after rollback
- The session drops again with the same CEASE after rollback and session reset
- The session does not reach `Established` within 120 seconds after `clear bgp`

**Who to Contact:**
- Internal routing SME / on-call routing engineer first, if available
- Cisco TAC for platform support, targeting **IOS XR Routing / BGP** or equivalent

**Severity Guidance:**
- **S2** default: production BGP peering is down and traffic is impacted
- **S3**: redundancy exists and service impact is low
- **S1**: major or widespread business-critical outage

**Case / Ticket Format:**
- Suggested SR summary: `IOS XR BGP max-prefix CEASE from neighbor {{ neighbor_ip }} in VRF {{ vrf_name }}`

**Evidence to Collect Before Escalating:**
```
show bgp neighbors {{ neighbor_ip }}
show bgp neighbors {{ neighbor_ip }} | include policy
show configuration commit list
show configuration commit changes last 5
show configuration rollback changes last 1
show rpl route-policy {{ policy_name }}
show bgp ipv4 unicast summary | include {{ neighbor_ip }}
show logging last 500 | include {{ neighbor_ip }}
show version
```

## Post-Repair Verification

**Commands:**
```
show bgp neighbors {{ neighbor_ip }} | include State|reset|Prefix
show bgp ipv4 unicast summary | include {{ neighbor_ip }}
show logging last 100 | include {{ neighbor_ip }}
show bgp neighbors {{ neighbor_ip }} routes
show route ipv4 unicast
```

**Expected Healthy Output:**
```
RP/0/RP0/CPU0:router# show bgp neighbors 172.20.20.17 | include State|reset|Prefix
  BGP state = Established, up for 00:04:22
  Prefix advertised 3820, suppressed 0, withdrawn 4700
  Prefix accepted 4210, suppressed 0, withdrawn 40

RP/0/RP0/CPU0:router# show bgp ipv4 unicast summary | include 172.20.20.17
172.20.20.17       65535    4   4   4210    3820   0       0   00:04:22 Established
```

The session should remain `Established`, the advertised prefix count should be back at
the expected lower level, and no new `ADJCHANGE Down` message should appear for
`{{ neighbor_ip }}`.

## References

- [Cisco BGP Maximum-Prefix Feature](https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/25160-bgp-maximum-prefix.html)
- [ASR 9000 Routing Configuration Guide — Implementing BGP](https://www.cisco.com/c/en/us/td/docs/routers/asr9000/software/26xx/routing/configuration/guide/b-routing-cg-asr9000-26xx/implementing-bgp.html)
- [IOS XR Configuration Management — Rollback and Commit](https://www.cisco.com/c/en/us/td/docs/routers/asr9000/software/asr9k-r7-9/system-management/configuration/guide/b-system-mgmt-cg-asr9000-79x/configuration-management.html)
- RFC 4486 — Subcodes for BGP Cease Notification Message

---

## Summary of Optimizations

- Added explicit numeric thresholds from the answered questionnaire:
  **4-hour / 5-commit default search window** in Step 2 and **120-second recovery
  threshold** in Step 5.
- Added a simple intermediate sanity check in Step 2 so the guide can confirm the
  neighbor's attached export policy before escalating, without expanding into deep
  `advertised-routes` analysis.
- Tightened the rollback scope so this guide only supports a **clean, recent rollback**.
  Mixed commits, unclear rollback previews, and manual policy surgery are now treated
  as escalation / handoff cases instead of adding extra complexity.
- Added explicit handling for the case where the session stays **Active** but does not
  reach `Established` within 120 seconds; this is now treated as a different adjacency
  problem.
- Added practical escalation guidance, including who to contact, default TAC severity,
  and a suggested SR summary format.
- These optimizations were informed primarily by the answered optimization
  questionnaire and the original source guide. No additional research was required in
  this optimization pass.

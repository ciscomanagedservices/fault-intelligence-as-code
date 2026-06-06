# Remediation Guide: BGP Neighbor Administrative Shutdown

> **Alert Definition:** AD000002
> **Guide ID:** RG000002
> **Linked Fault Signature:** FS000002
> **Linked Repair Action Workflow:** RAW000002

## Overview

This guide provides step-by-step instructions to diagnose and resolve a BGP neighbor
session that has been placed in administrative shutdown on an IOS XR router. When an
operator applies the `neighbor shutdown` configuration command, the BGP process tears
down the session, sends a CEASE notification to the remote peer, and stops all route
exchange. This guide covers the local router where the shutdown is applied and provides
the steps to restore the session.

## Applicability

- **Products:** ASR 9000 Series; also applicable to Cisco 8000 Series, NCS 5500/5700, NCS 540
- **Operating Systems:** IOS XR 7.x and later
- **Component:** Routing
- **Severity:** Warning
- **Related Defects:** None identified

## Triggering Events

### Event 1: BGP Neighbor Down — Administrative Shutdown (Local Router)

- **Type:** Syslog
- **Message ID:** ROUTING-BGP-5-ADJCHANGE
- **Example Message:**
  ```
  RP/0/RP0/CPU0:router: bgp[1056]: %ROUTING-BGP-5-ADJCHANGE : neighbor 10.1.1.1 Down - Admin. shutdown (VRF: default) (AS: 65001)
  ```
- **Key Values to Extract:** The neighbor IP address — the IPv4 (or IPv6) address
  appearing immediately after "neighbor" in the message (e.g., `10.1.1.1`). The VRF
  name appearing in the `(VRF: <name>)` field (e.g., `default`). The neighbor AS number
  appearing in the `(AS: <asn>)` field (e.g., `65001`).

### Correlation

- **Logic:** Event 1 triggers this guide. It is logged on the router where
  `neighbor shutdown` is applied.

### Recovery Indicator

- **Recovery Event:** BGP neighbor returns to Up state after `no shutdown` is applied.
  ```
  RP/0/RP0/CPU0:router: bgp[1056]: %ROUTING-BGP-5-ADJCHANGE : neighbor 10.1.1.1 Up (VRF: default) (AS: 65001)
  ```
- **Recovery Window:** Within 60 seconds of `no shutdown` being applied (BGP session
  re-establishment time depends on hold timer and keepalive interval).

## Symptoms

- BGP neighbor is in `Idle (Admin)` state — the `(Admin)` qualifier distinguishes
  administrative shutdown from fault-induced idle states
- All routes learned from the affected neighbor are withdrawn from the RIB
- Traffic that relied on routes from this neighbor may be black-holed or rerouted
  through a less-preferred path
- `show bgp summary` shows the neighbor with state `Idle` and uptime `00:00:00`
- `show bgp neighbors <ip>` shows `BGP state = Idle (Admin)`
- Running configuration contains `shutdown` under the neighbor stanza

## Diagnosis & Repair Steps

### Step 1: Confirm the Neighbor Is in Administrative Shutdown

Verify that the BGP session is down specifically due to administrative shutdown (not a
fault-induced failure such as hold timer expiry or interface down).

**Commands:**
```
show bgp neighbors {{ neighbor_ip }}
show bgp neighbors {{ neighbor_ip }} | include "BGP state\|Last reset\|shutdown"
```

**What to Look For:** The `BGP state` field should show `Idle (Admin)`. The `(Admin)`
qualifier is the definitive indicator that the session is administratively shut down.
If the state is `Idle` without `(Admin)`, the session is down for a different reason
and this guide does not apply.

**Sample Output — Healthy (session up):**
```
BGP state = Established, up for 3d14h
```

**Sample Output — Fault Confirmed (admin shutdown):**
```
BGP state = Idle (Admin)
Last reset 00:15:32, due to Admin. shutdown
```

**Decision Point:** If `BGP state = Idle (Admin)` is confirmed, proceed to Step 2.
If the state is `Idle` without `(Admin)`, or if the last reset reason is not
`Admin. shutdown`, this guide does not apply — investigate the specific reset reason.

### Step 2: Confirm the Shutdown Is in the Running Configuration

Verify that the `shutdown` command is present in the running configuration for this
neighbor. This confirms the shutdown is persistent (not a transient state from a
previous `clear bgp` command).

**Commands:**
```
show running-config router bgp | include -A 5 "neighbor {{ neighbor_ip }}"
```

**What to Look For:** The `shutdown` keyword should appear under the neighbor stanza.

**Sample Output — Shutdown Configured:**
```
 neighbor 10.1.1.1
  remote-as 65001
  shutdown
  address-family ipv4 unicast
```

**Sample Output — No Shutdown in Config (transient state):**
```
 neighbor 10.1.1.1
  remote-as 65001
  address-family ipv4 unicast
```

**Decision Point:** If `shutdown` is present in the running configuration, proceed to
Step 3 to remove the shutdown. If `shutdown` is not in the running configuration, the
session may be recovering from a transient event — monitor for re-establishment and
investigate the original reset reason.

### Step 3: Remove the Administrative Shutdown

Remove the `shutdown` command from the neighbor stanza to restore the BGP session.

**Commands:**
```
configure terminal
router bgp {{ local_as }}
 neighbor {{ neighbor_ip }}
  no shutdown
 commit
end
```

**What to Look For:** The commit should succeed without errors. The BGP process will
immediately begin re-establishing the session.

**Sample Output — Commit Successful:**
```
RP/0/RP0/CPU0:router(config-bgp-nbr)#no shutdown
RP/0/RP0/CPU0:router(config-bgp-nbr)#commit
```

**Decision Point:** After committing, proceed to Step 4 to verify the session
re-establishes. If the commit fails (e.g., due to a configuration conflict), review
the error message and resolve the conflict before retrying.

**Caution:** On a production router, removing the shutdown will immediately trigger
BGP session re-establishment and route advertisement. Ensure this is the intended
action before committing. If this neighbor carries a large routing table, the
re-establishment may cause a brief CPU spike during route processing.

### Step 4: Verify BGP Session Re-Establishment

Confirm the BGP session has returned to the Established state and routes are being
exchanged normally.

**Commands:**
```
show bgp neighbors {{ neighbor_ip }} | include "BGP state"
show bgp summary
show logging | include "ADJCHANGE.*{{ neighbor_ip }}"
```

**What to Look For:** The `BGP state` should return to `Established`. The `show bgp
summary` output should show the neighbor with a non-zero uptime and a prefix count
matching the expected route count from this peer. The syslog should show a
`ROUTING-BGP-5-ADJCHANGE` Up event for the neighbor.

**Sample Output — Healthy (recovered):**
```
BGP state = Established, up for 00:01:15

Neighbor        Spk  AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down  St/PfxRcd
10.1.1.1          0 65001    1250    1248        1    0    0 00:01:15       8500
```

**Sample Output — Still Faulted:**
```
BGP state = Idle
```

**Decision Point:** If the session is Established with a non-zero prefix count, the
repair is complete — proceed to Post-Repair Verification. If the session remains Idle
or Active after 60 seconds, proceed to the Escalation section.

## Escalation

**When to Escalate:**
- BGP session remains Idle or Active more than 60 seconds after `no shutdown` is applied
- Session briefly reaches Active or OpenSent then drops again (possible authentication
  mismatch, capability negotiation failure, or remote peer also has the neighbor shut down)
- `show bgp neighbors` shows a reset reason other than `Admin. shutdown` after the
  `no shutdown` is applied (indicates a secondary fault)
- The remote peer is not under your control and may also have the session shut down on
  their side

**Evidence to Collect Before Escalating:**
```
show bgp neighbors {{ neighbor_ip }}
show bgp summary
show running-config router bgp
show logging | include ADJCHANGE
show bgp neighbors {{ neighbor_ip }} | include "BGP state\|Last reset\|Hold\|Keepalive\|Notification"
show tcp brief | include {{ neighbor_ip }}
```

## Post-Repair Verification

After removing the shutdown and confirming the session is Established:

**Commands:**
```
show bgp neighbors {{ neighbor_ip }} | include "BGP state"
show bgp summary
show bgp neighbors {{ neighbor_ip }} | include "Prefixes Current"
show logging | include "ADJCHANGE.*{{ neighbor_ip }}"
```

**Expected Healthy Output:**
```
BGP state = Established, up for 00:05:00

Neighbor        Spk  AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down  St/PfxRcd
10.1.1.1          0 65001    2500    2498        1    0    0 00:05:00       8500
```

BGP state is Established, uptime is increasing, prefix count matches the expected
route count from this peer, and the syslog shows a `ROUTING-BGP-5-ADJCHANGE` Up event
with no subsequent Down events.

## References

- [Cisco IOS XR BGP Command Reference — shutdown (BGP)](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/bgp/cumulative/command/reference/b-bgp-cr-cisco8000/m-bgp-commands-8k.html)
- RFC 4486 — Subcodes for BGP Cease Notification Message
- RFC 8203 / RFC 9003 — BGP Administrative Shutdown Communication
- BGP Graceful Maintenance (GSHUT) — preferred alternative for planned maintenance:
  use `graceful-maintenance activate` under the neighbor stanza to drain traffic before
  tearing down the session

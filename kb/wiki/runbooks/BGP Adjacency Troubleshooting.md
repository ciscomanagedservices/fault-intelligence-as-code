---
type: runbook
title: "BGP Adjacency Troubleshooting"
created: 2026-05-06
updated: 2026-05-06
status: active
severity_scope: ["SEV-1", "SEV-2"]
tags:
  - runbook
  - bgp
  - routing
  - troubleshooting
related:
  - "[[BGP]]"
  - "[[BFD]]"
  - "[[RPKI]]"
  - "[[Cisco]]"
  - "[[Juniper Networks]]"
  - "[[Arista Networks]]"
  - "[[Global Network Operations Center]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# BGP Adjacency Troubleshooting

## Purpose

This runbook guides T2/T3 engineers through diagnosing and restoring a down or flapping [[BGP]] session. Applies to all platforms: [[Cisco]] ASR 9000, [[Juniper Networks]] MX Series, [[Arista Networks]] DC fabric.

---

## Pre-Checks

Before diving into BGP, confirm:
- [ ] Physical interface is up/up
- [ ] [[IS-IS]] adjacency (if applicable) is up — BGP next-hop reachability depends on IS-IS
- [ ] [[BFD]] session status (a bad BFD timer is a common cause of BGP flapping)

---

## Step 1 — Identify the BGP Session State

**Cisco IOS-XR (ASR 9000):**
```
show bgp neighbors <neighbor-ip>
show bgp summary
```

**Juniper (MX Series):**
```
show bgp neighbor <neighbor-ip>
show bgp summary
```

**Arista EOS:**
```
show bgp neighbors <neighbor-ip>
show bgp summary
```

Expected state: **Established**. Any other state (Idle, Active, Connect, OpenSent, OpenConfirm) indicates a problem.

---

## Step 2 — Check BFD Status

```
# Cisco IOS-XR
show bfd session destination <neighbor-ip>

# Juniper
show bfd session address <neighbor-ip>

# Arista
show bfd peers
```

If BFD is down, BGP will also be down. Fix BFD first.

**Common BFD Issues:**
- Timer mismatch between peers → align TX/RX intervals and detection multiplier
- Hardware resource exhaustion → check BFD scale limits on platform

---

## Step 3 — TCP / Authentication Check

BGP runs over TCP port 179 with MD5/TCP-AO authentication.

```
# Verify TCP session exists
show tcp brief | include 179

# Check for auth failures in syslog
# Search Splunk: host=<router> "BGP MD5" OR "authentication failure" earliest=-1h
```

**If MD5 mismatch:**
- Verify the pre-shared key matches on both ends
- Common cause: device replacement where the new device has a different password configured
- Key must be updated on BOTH sides simultaneously during a maintenance window

---

## Step 4 — Check Prefix-List / Route Policy

If session is **Established** but no prefixes are being exchanged:

```
# Cisco IOS-XR — check inbound/outbound policy
show bgp neighbors <neighbor-ip> | include "Policy|prefix"

# Arista
show bgp neighbors <neighbor-ip> | grep -A 5 "Route map"
```

Verify that the configured prefix-list or route-map permits the expected prefixes. Check [[NetBox]] for the documented expected prefix list.

---

## Step 5 — Check RPKI Validation

If prefixes are received but not installed:

```
# Cisco IOS-XR
show bgp <prefix/len>
# Look for: "Received from <neighbor>", "ROV state: invalid"

# Check RPKI cache connectivity
show rpki server summary
```

If RPKI validator is unreachable, sessions may default to "unknown" — check [[RPKI]] page for validator IPs and expected behavior. An Invalid prefix being rejected is **correct behavior** per ACME Corp policy.

---

## Step 6 — Escalation

If the issue is not resolved after completing all steps:
1. Update [[ServiceNow]] ticket with all findings
2. Escalate to T3 engineer
3. For external peer issues (ISP), open a carrier trouble ticket; provide: circuit ID, BGP session IPs, AS numbers, symptom description, and time of failure

---

## Related Runbooks
- [[Circuit Outage Response]] — if the underlying WAN circuit is down
- [[NOC Alert Triage Procedure]] — initial triage before this runbook

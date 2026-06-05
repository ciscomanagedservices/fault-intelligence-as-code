# Optimization Questionnaire: BGP Neighbor Down — Neighbor's Maximum Prefix Limit Exceeded by Local Advertisement (IOS XR)

> **Source:** `ia-drafts/AD000003-bgp-max-prefix-adjchange-xr/RG000003-bgp-max-prefix-adjchange-guide.md`
> **Generated:** 2026-05-29
> **Status:** Questionnaire — Best-Effort Draft Answers Added

---

## Analysis Summary

The source guide covers BGP session failures on IOS XR where a neighbor-sent CEASE
notification ("BGP Notification received, maximum number of prefixes reached") brings
down the session. The guide's remediation flow is clean and operationally focused:
confirm the fault, locate the offending route-policy commit in IOS XR configuration
history, roll it back, restore the session, and verify. The platform and trigger are
well-specified. The primary gaps are undefined time thresholds (lookback window for
commits, session recovery wait time), missing branches for edge-case outcomes in
Steps 2–4, service impact qualification for the rollback step, and an underspecified
escalation procedure.

---

## Clarifying Questions

The following questions must be answered before the optimized Remediation Guide can be
generated. Replace `<your answer here>` in each **Answer** block. Partial answers are
accepted — unanswered questions will become `[GAP]` placeholders in the guide.

### Undefined Thresholds

**T1.** Step 2 states to check "commits made within the last few hours" and suggests
inspecting "last 5" commits if the most recent shows no change. What is the
appropriate lookback window (in time or number of commits) before the engineer
concludes no relevant config change exists and escalates?

> **Answer:** Use a simple operational default: review commits from the last **4 hours** and inspect up to the **last 5 commits** first.

**T2.** Step 4 states the session should recover "within 30–120 seconds" after
`clear bgp`. At what specific point (elapsed time or number of BGP open attempts)
should the engineer conclude the session is not recovering and escalate?

> **Answer:** Use **120 seconds** as the main threshold. After `clear bgp`, if the session is still not **Established** within **2 minutes**, or if it clearly fails through **2–3 open attempts**, stop waiting and escalate.

### Missing Decision Branches

**D1.** Step 2 Decision Point: if no route-policy or prefix-set change is found in
the commit history, the guide immediately escalates. Should there be an intermediate
check before escalating — for example, verifying whether the prefix count grew due to
a new peer being established or a redistribution policy change rather than a local
route-policy edit? Or is "no config change found → escalate immediately" the intended
path?

> **Answer:** Keep this simple. Do **one quick sanity check** before escalating: confirm which export route-policy / prefix-set is attached to the neighbor and confirm there was no obvious recent redistribution or policy change affecting that neighbor. If there is still no clear recent config change, **escalate**. Do **not** expand this guide into deep `advertised-routes` troubleshooting.

**D2.** Step 3 Decision Point: the rollback preview (`show configuration rollback
changes last 1`) might show a policy that is already identical to the current running
config — meaning the commit that was found in Step 2 changed something else but the
policy content itself did not actually change. In that case, what should the engineer
do? Roll back anyway? Look further back in the commit history? Escalate?

> **Answer:** Do **not** roll back blindly. First, look back **1–2 more commits** within the Step 2 search window to find the actual policy-changing commit. If the rollback preview still does not show a meaningful reversal of the export policy or prefix-set, stop the rollback path and **escalate**.

**D3.** Step 3 Caution: the guide warns that if the commit contains other changes
that must be preserved, the engineer should "manually edit the policy to its previous
state" rather than using `rollback configuration`. Should the guide provide the
specific IOS XR commands to do a manual policy edit and commit, or is this case
intentionally out of scope (i.e., hand off to a routing engineer)?

> **Answer:** To keep the guide simple, treat manual policy surgery as **out of scope** for this RG. If the commit is mixed and a full rollback would undo unrelated changes that must be preserved, hand off to a qualified routing engineer or escalate. The guide should mention this option, but it does **not** need to include detailed manual edit commands.

**D4.** Step 4 Decision Point: the guide handles two outcomes — session reaches
Established (success) or drops again with the same CEASE (rollback insufficient).
What should the engineer do if the session moves to Active but never reaches
Established — implying something other than max-prefix is now preventing the session
(e.g., TCP connectivity issue, BGP OPEN rejection, capability mismatch)?

> **Answer:** Treat this as **outside the max-prefix rollback path**. If the session reaches **Active** but does not become **Established** within the 120-second threshold, assume a different adjacency problem now exists (for example transport reachability, OPEN negotiation, auth, or capability mismatch). Collect the listed evidence and escalate or hand off to standard BGP adjacency troubleshooting.

### Service Impact Assumptions

**S1.** Step 3 applies `rollback configuration last 1` which reverses an entire
commit. If that commit also included changes unrelated to the route-policy (e.g.,
interface description, another neighbor's config), those changes will also be rolled
back. Does the rollback step require a maintenance window or change-control approval
in the target environment, or is it considered safe to apply during an active incident
without a window?

> **Answer:** Use a simple rule: `rollback configuration last 1` is acceptable during an active incident **only if** the commit is clearly the cause and the preview shows it mainly affects the relevant BGP export policy / prefix-set. If the commit is mixed or the blast radius is unclear, get change approval if required by local process, or avoid full rollback and escalate to a routing engineer.

### Escalation Procedures

**E1.** The Escalation section tells the engineer to "engage Cisco TAC" but does not
specify SR severity or contact method. What severity level should the TAC SR be
opened at (S1/S2/S3/S4)? Is there a specific team or queue (e.g., SP Routing, BGP
escalation group) that should be targeted?

> **Answer:** Use **Severity 2** as the default when a production BGP peering session is down and traffic is impacted.

---

## Original Source Reference

### Overview

This guide diagnoses and resolves BGP session failures on IOS XR routers where a BGP
neighbor sends a CEASE notification to the local router because the local router is
advertising more prefixes than the neighbor's configured inbound maximum-prefix limit
allows. The keyword "BGP Notification received" is the defining indicator: the neighbor
initiated the teardown, not the local router. This guide specifically addresses the
most common root cause: a recent route-policy or prefix-set configuration change that
broadened what the local router advertises to the neighbor.

### Applicability

| Field | Value |
|-------|-------|
| Products | Cisco ASR 9000; Cisco 8000 Series; Cisco NCS 5000/5500/5700; Cisco NCS 540/560; all IOS XR platforms |
| Operating Systems | IOS XR (all releases) |
| Component | Route Processor |
| Severity | Warning |
| Related Defects | None |

### Triggering Events

| Field | Value |
|-------|-------|
| Event Type | Syslog |
| Message ID | ROUTING-BGP-5-ADJCHANGE |
| Example Message | `bgp[1090]: %ROUTING-BGP-5-ADJCHANGE : neighbor 172.20.20.17 Down - BGP Notification received, maximum number of prefixes reached (VRF: default) (AS: 65535)` |
| Key Values to Extract | `neighbor_ip` (after `"neighbor "`), `vrf_name` (after `"VRF: "`), `asn` (after `"AS: "`) |
| Correlation Logic | Single event |
| Recovery Indicator | `%ROUTING-BGP-5-ADJCHANGE : neighbor {{ neighbor_ip }} Up (VRF: {{ vrf_name }}) (AS: {{ asn }})` |

### Symptoms

- BGP neighbor `{{ neighbor_ip }}` in Idle or Active state — not Established
- Routes previously learned from `{{ neighbor_ip }}` are withdrawn from the RIB; traffic may black-hole or reroute
- `show bgp neighbors {{ neighbor_ip }}` shows Last reset reason referencing "maximum number of prefixes reached"
- Session does not auto-recover — requires manual `clear bgp` after fix
- Fault coincides with a recent route-policy or prefix-set commit

### Troubleshooting / Repair Actions (Original)

**Step 1: Confirm the Session Is Down and Identify the CEASE Reason**
- `show bgp neighbors {{ neighbor_ip }} | include State|reset`
- Healthy: `BGP state = Established, up for 2d14h33m`
- Fault: `BGP state = Idle` + `Last reset 00:08:42 ago, due to BGP Notification received (Maximum Number of Prefixes Reached)`
- Decision: if Idle + max-prefix CEASE, proceed to Step 2; else investigate other reason

**Step 2: Check Recent Configuration Changes for Route-Policy Modifications**
- `show configuration commit list` — review commit timestamps vs. session drop time
- `show configuration commit changes last 1` — inspect what changed
- Decision: if route-policy/prefix-set change found → Step 3; if no change found → escalate

**Step 3: Preview and Apply the Configuration Rollback**
- `show configuration rollback changes last 1` — preview
- `rollback configuration last 1` — apply
- `show rpl route-policy {{ policy_name }}` — verify policy restored
- Decision: confirm policy restored → Step 4
- Caution: rollback reverses entire commit; if mixed commit, manually edit policy instead

**Step 4: Restore the BGP Session**
- `clear bgp ipv4 unicast {{ neighbor_ip }}` (default VRF)
- `clear bgp vrf {{ vrf_name }} ipv4 unicast {{ neighbor_ip }}` (non-default VRF)
- Decision: session reaches Established → Post-Repair Verification; drops again with same CEASE → escalate

### Escalation (Original)

- No recent route-policy change found in commit history
- Rollback applied but session drops again with same CEASE reason
- Session remains Idle after `clear bgp` and no new CEASE logged
- Fault recurs repeatedly after rollback

Evidence: `show bgp neighbors {{ neighbor_ip }}`, `show bgp neighbors {{ neighbor_ip }} | include policy`,
`show configuration commit list`, `show configuration commit changes last 5`,
`show rpl route-policy {{ policy_name }}`, `show bgp ipv4 unicast summary`,
`show logging last 500 | include {{ neighbor_ip }}`, `show version`

### Post-Repair Verification (Original)

- `show bgp neighbors {{ neighbor_ip }} | include State|reset|Prefix`
- `show bgp ipv4 unicast summary | include {{ neighbor_ip }}`
- `show logging last 100 | include {{ neighbor_ip }}`
- Expected: BGP state = Established, prefix count at pre-change level, no new ADJCHANGE Down in syslog
- Follow-up: `show bgp neighbors {{ neighbor_ip }} routes` + `show route ipv4 unicast` to confirm RIB repopulation

---

## Instructions for SME Review

1. Review the **Clarifying Questions** section above and adjust the draft answers as
   needed for your environment.
2. Any answer can still be refined or replaced before generating the optimized guide.
3. When you are ready, run `ia-optimize` again and provide this file as input.
   The skill will generate the full optimized `.md` (RG) using your answers.

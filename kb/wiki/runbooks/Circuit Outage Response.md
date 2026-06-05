---
type: runbook
title: "Circuit Outage Response"
created: 2026-05-06
updated: 2026-05-06
status: active
severity_scope: ["SEV-1", "SEV-2", "SEV-3"]
tags:
  - runbook
  - circuit
  - wan
  - outage
  - isp
related:
  - "[[Global Network Operations Center]]"
  - "[[BGP Adjacency Troubleshooting]]"
  - "[[SD-WAN]]"
  - "[[Fortinet]]"
  - "[[Incident Severity SLAs]]"
  - "[[ServiceNow]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Circuit Outage Response

## Purpose

This runbook covers the response procedure for a suspected or confirmed WAN circuit outage affecting a branch, data center, or core routing link. Applies to MPLS circuits, broadband connections, dark fiber, and metro ethernet.

---

## Step 1 — Confirm Circuit Down (T1)

1. **Check [[ThousandEyes]]** for the affected site — confirm network path test shows 100% packet loss or path failure to the affected location
2. **Check [[Splunk]]** for interface down syslogs: `host=<edge-router> "line protocol is down"`
3. **Check the router interface status:**
   ```
   show interfaces <interface-id>
   ```
   - Physical layer down (no light / no signal) = likely carrier issue
   - Protocol down only (physical up) = L3 or authentication issue → use [[BGP Adjacency Troubleshooting]]

4. **Confirm severity** using [[Incident Severity SLAs]]:
   - Single branch with SD-WAN failover active → SEV-3 (service degraded, not down)
   - Core/backbone circuit down = SEV-1 or SEV-2

---

## Step 2 — Check for Automatic Failover

**Branch SD-WAN (Fortinet):**
- SD-WAN should have failed over to the secondary WAN link automatically
- Verify on FortiGate: `diagnose sys sdwan health-check` — confirm primary link is listed as down and traffic is routing via secondary
- If failover did NOT occur, escalate to T2 immediately

**Core / DCI links:**
- Verify [[IS-IS]] has reconverged around the failed link
- Verify [[BGP]] has re-advertised routes via alternate path
- Check for asymmetric routing: `traceroute <destination>` from multiple points

---

## Step 3 — Collect Circuit Information

Before calling the carrier, gather:
- [ ] Circuit ID (from [[NetBox]] or circuit label on the router)
- [ ] Affected interface: `show interfaces <int> | include "circuit|desc"`
- [ ] Time of failure (from [[Splunk]] syslogs — exact timestamp)
- [ ] Physical layer status (light levels if optical): `show controllers <int>`
- [ ] Carrier name and NOC contact number (from [[NetBox]] circuit record)

---

## Step 4 — Open Carrier Trouble Ticket

1. Call the carrier NOC (number in [[NetBox]] circuit record for this circuit)
2. Provide: circuit ID, failure time, physical layer status, and description of symptoms
3. Request an estimated time to restore (ETR) and a carrier ticket number
4. Log the carrier ticket number in the [[ServiceNow]] incident

---

## Step 5 — Ongoing Communication

- Update [[ServiceNow]] ticket every 30 minutes with carrier status
- If ETR > 2 hours for a SEV-1/SEV-2 circuit, notify stakeholders per [[Incident Severity SLAs]]
- If ETR > 4 hours for a core circuit, engage [[Network Architecture and Engineering]] to evaluate temporary rerouting options

---

## Step 6 — Circuit Restoration

When the carrier reports the circuit is restored:
1. Verify physical layer recovery: `show interfaces <int>` — confirm "line protocol is up"
2. Verify routing reconvergence: confirm [[IS-IS]] adjacency and [[BGP]] session re-established
3. Run [[ThousandEyes]] end-to-end test to confirm full user experience recovery
4. Close the carrier ticket and the [[ServiceNow]] incident
5. Conduct a 24-hour monitoring watch; set a [[Splunk]] watch alert for the interface

---

## Related Runbooks
- [[BGP Adjacency Troubleshooting]] — if circuit is up but routing is not
- [[NOC Alert Triage Procedure]] — initial triage process

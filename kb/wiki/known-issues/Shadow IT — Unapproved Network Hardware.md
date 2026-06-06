---
type: known-issue
title: "Shadow IT — Unapproved Network Hardware"
created: 2026-05-06
updated: 2026-05-06
status: active
recurrence: ongoing
affected_systems: ["NAC", "802.1X", "Branch access switches"]
tags:
  - known-issue
  - shadow-it
  - security
  - nac
  - access-control
related:
  - "[[Network Security Operations]]"
  - "[[Cisco]]"
  - "[[Security Zero Trust Mandates]]"
  - "[[Change Management Policy]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Known Issue: Shadow IT — Unapproved Network Hardware

## Summary

End users and local IT staff periodically introduce unapproved network devices (personal routers, unmanaged switches, rogue access points, IoT devices) onto the [[ACME Corp]] corporate network. This is a **recurring and ongoing operational and security concern**.

---

## Symptoms

- New MAC addresses appear on switch ports that are not in [[NetBox]] inventory
- Unauthorized SSIDs detected by wireless infrastructure RF scanning
- NAC authentication failures for devices with no certificates or RADIUS credentials
- [[Splunk]] alert: "Unknown device connected to port GigX/X/X on switch SW-BRANCH-XX"
- [[Oxidized]] alert: configuration drift on access switches where a local admin manually opened a port for an unapproved device

---

## Root Cause

Business users connect personal equipment (home routers, Raspberry Pis, gaming consoles, smart TVs) to desk ports or conference room Ethernet drops. Local facilities or site IT staff occasionally connect unmanaged switches to provide additional ports, bypassing the 802.1X enforcement.

---

## ACME Corp Policy

> **Shadow IT devices are strictly prohibited.** Any unapproved hardware detected on the network will be immediately isolated and the connecting port shut down.

Reference: [[Security Zero Trust Mandates]] — Mandate 4 (Device Hardening Baseline), and the ACME Corp Acceptable Use Policy.

---

## Mitigation in Place

[[Cisco]] Catalyst 9300 series switches have **802.1X / MAB (MAC Authentication Bypass)** enabled on all access ports. Devices that fail 802.1X authentication are dropped into a **quarantine VLAN** with restricted internet-only access and no access to internal resources.

| Auth Result | VLAN Assignment |
|-------------|----------------|
| 802.1X success (corporate device) | Corporate VLAN (as assigned in RADIUS) |
| MAB success (registered MAC, e.g., printer) | Device VLAN |
| Auth failure (unknown device) | **Quarantine VLAN** — internet only, no internal access |

---

## Response Procedure

When a shadow IT device is detected:

1. **Identify the port:** Find the switch and port from the [[Splunk]] alert or NAC quarantine report
2. **Identify the user:** Check the MAC address in [[NetBox]]; if not found, use DHCP logs to find the last IP issued to that MAC and correlate to a user via Active Directory
3. **Notify the user:** Send the user a warning email citing the Acceptable Use Policy
4. **Shut the port:** If the device poses a security risk (e.g., rogue AP broadcasting), shut the port immediately: `interface <int> / shutdown`
5. **Open a [[ServiceNow]] ticket:** SEV-4 for isolated incidents; SEV-3 if a rogue AP is actively broadcasting or if the device is connected to a server VLAN
6. **Escalate if needed:** If the user is repeat-offender or the device appears malicious (C2 traffic, port scanning), escalate to [[Network Security Operations]] and the Security SOC

---

## Workaround

No workaround — the correct resolution is removal and port shutdown. If a legitimate business need exists for the device, the user must submit a request through the IT hardware approval process to get it added to [[NetBox]] and provisioned with proper credentials.

---

## Prevention

- Quarterly NAC audit: NetSecOps runs a sweep of all quarantine VLAN endpoints to identify persistent violators
- Automated port shutdown: Under evaluation — would auto-shutdown ports where rogue APs are detected

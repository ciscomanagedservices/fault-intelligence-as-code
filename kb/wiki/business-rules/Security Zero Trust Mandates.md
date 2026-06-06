---
type: business-rule
title: "Security Zero Trust Mandates"
created: 2026-05-06
updated: 2026-05-06
status: active
tags:
  - business-rule
  - security
  - zero-trust
  - security-baseline
  - compliance
related:
  - "[[Zero Trust]]"
  - "[[Network Security Operations]]"
  - "[[MACsec]]"
  - "[[RPKI]]"
  - "[[BGP]]"
  - "[[Palo Alto Networks]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Security Zero Trust Mandates

## Purpose

This document defines the non-negotiable security mandates that apply to all network infrastructure at [[ACME Corp]]. These mandates are enforced by [[Network Security Operations]] and are subject to periodic compliance audits.

---

## Mandate 1 — MACsec on All DCI Links

**Requirement:** All Data Center Interconnect (DCI) links traversing dark fiber or carrier metro ethernet **must** be encrypted using MACsec (IEEE 802.1AE).

**Rationale:** Carrier-provided circuits may be physically accessible to third parties. Encryption ensures that even a physical fiber tap yields only ciphertext.

**Enforcement:**
- NetSecOps performs quarterly verification of all DCI links
- Any DCI link found without MACsec must be remediated within **72 hours** or the link must be decommissioned
- See [[MACsec]] for technical configuration guidance

---

## Mandate 2 — Strict BGP Peering Security

**Requirements for all external BGP sessions:**
- MD5 or TCP-AO authentication configured on every session
- Maximum-prefix limits configured to prevent route leak flooding
- Inbound prefix-lists configured to reject unexpected prefixes
- RPKI Route Origin Validation (ROV) enabled; Invalid routes **must be dropped** (not just flagged)

**Rationale:** BGP hijacking and route leaks are among the highest-impact attack vectors for internet-facing infrastructure.

**Enforcement:** T3 engineers verify BGP security posture during all new peering provisioning and quarterly audits.

See [[RPKI]] and [[BGP]] for detailed configuration requirements.

---

## Mandate 3 — Out-of-Band Management Isolation

**Requirement:** All network device management interfaces (MGMT0, etc.) must be connected to a **physically separate OOB network**. Access to OOB is only permitted via designated jump hosts requiring MFA.

**Requirements in detail:**
- Management interfaces must NOT be reachable from the production network
- SSH is the only permitted management protocol (Telnet is prohibited)
- Jump hosts require MFA (hardware token or authenticator app)
- Failed SSH authentication attempts must be logged to [[Splunk]]
- OOB network must have its own redundant path to the NOC

**Rationale:** If the production network is compromised, attackers should not be able to pivot to management access. OOB ensures the network remains manageable even during a network-layer attack.

---

## Mandate 4 — Device Hardening Baseline

All network devices must meet the following hardening baseline before being placed into production:

| Category | Requirement |
|----------|------------|
| Unused services | HTTP server, Telnet, and CDP on untrusted interfaces must be **disabled** |
| Password hashing | Minimum SHA-256 (Type 8 on IOS-XR, Type 9 on IOS/NX-OS, equivalent on other platforms) |
| Control plane protection | CoPP (Control Plane Policing) enabled on all routing platforms |
| SNMP | SNMPv3 only; SNMPv1/v2c prohibited |
| SSH | SSHv2 only; SSHv1 prohibited; maximum auth failures set to 3 |
| Banner | Legal warning banners on all management access points |
| AAA | TACACS+ centralized authentication for all admin access; local accounts as break-glass only |

**Compliance:** [[Network Architecture and Engineering]] validates hardening on all new deployments via automated checks in the CI/CD pipeline. [[Oxidized]] detects post-deployment drift.

---

## Mandate 5 — Default Deny Firewall Posture

All [[Palo Alto Networks]] NGFWs must operate with a **default deny** base policy. Every permitted traffic flow requires an explicit policy rule including:
- Source zone and IP
- Destination zone and IP
- Application (App-ID based, not port-based where possible)
- Justification comment in the rule description

No "any/any" or "any/permit" rules are permitted in production.

---
type: entity
entity_type: team
title: "Network Security Operations"
aliases: ["NetSecOps"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - team
  - security
  - acme-corp
related:
  - "[[ACME Corp]]"
  - "[[Global Network Operations Center]]"
  - "[[Network Architecture and Engineering]]"
  - "[[Palo Alto Networks]]"
  - "[[Zero Trust]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Network Security Operations (NetSecOps)

## Overview

NetSecOps works in tandem with the central SOC but focuses specifically on **network transit security**. They own the perimeter and access control layers.

## Sub-Teams

### Perimeter Security
- Manages all Next-Gen Firewalls ([[Palo Alto Networks]] PA-5200 and PA-800 series)
- Manages Web Application Firewalls (WAF)
- Manages DDoS mitigation platforms
- Enforces [[Zero Trust]] "Default Deny" posture
- Responsible for TLS decryption on DMZ inbound flows

### Access Control
- Maintains Network Access Control (NAC) systems using **802.1X / RADIUS**
- Enforces access policies for all branch and campus wired/wireless endpoints
- Actively isolates unapproved "Shadow IT" hardware via NAC policy
- Manages [[MACsec]] encryption on all Data Center Interconnect (DCI) links

## Key Security Mandates Owned

| Mandate | Details |
|---------|---------|
| MACsec on DCI | All dark fiber / metro ethernet DCI links must be MACsec (802.1AE) encrypted |
| BGP hardening | All external BGP sessions require MD5/TCP-AO auth + maximum prefix limits |
| OOB management | All device management on isolated OOB network; access only via MFA jump hosts |
| Device hardening | Telnet/HTTP/CDP disabled; passwords SHA-256 (Type 8/9) minimum |

See [[Security Zero Trust Mandates]] for the full policy document.

## Key Tools

- [[Palo Alto Networks]] Panorama (NGFW central management)
- [[Splunk]] (syslog correlation and security analytics)
- RADIUS / 802.1X NAC infrastructure

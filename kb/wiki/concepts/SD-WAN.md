---
type: concept
title: "SD-WAN"
aliases: ["Software-Defined WAN", "SD WAN"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - technology
  - wan
  - branch
related:
  - "[[Fortinet]]"
  - "[[BGP]]"
  - "[[MPLS]]"
  - "[[Zero Trust]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# SD-WAN — Software-Defined WAN

## Overview

SD-WAN (Software-Defined Wide Area Network) is the branch connectivity technology at [[ACME Corp]]. It abstracts the WAN transport layer so that traffic is steered intelligently across multiple WAN links based on application requirements, link quality, and cost policy.

## ACME Corp Implementation

**Platform:** [[Fortinet]] FortiGate (acting as SD-WAN edge at each branch)

### WAN Transport Options

| Transport | Characteristics | Priority Use |
|-----------|----------------|-------------|
| MPLS | High reliability, QoS guaranteed, expensive | Real-time apps (VoIP, ERP transactions) |
| Broadband (DSL/Cable/Fiber) | Lower cost, higher latency/jitter variance | General internet, bulk file transfer |
| 5G / LTE | Mobile, fast failover, usage-based cost | Backup / failover circuit |

### Active/Active Dual WAN

Both WAN links carry traffic simultaneously (active/active, not active/standby). Application-aware routing policies define which link each application class prefers.

## Application-Aware Routing

SD-WAN continuously measures per-link metrics (latency, jitter, packet loss) and routes each application to its preferred transport:

- **VoIP:** MPLS preferred (low jitter); failover to broadband only if MPLS SLA degraded
- **Video conferencing:** MPLS preferred; broadband acceptable
- **SaaS (Office 365, Salesforce):** Broadband preferred (local internet breakout); MPLS if broadband degraded
- **Bulk backups:** Broadband (cheapest path)

## Tunnels and Security

FortiGate SD-WAN tunnels back to ACME Corp hub sites over IPSec. [[Palo Alto Networks]] PA-800 at larger branches provides dedicated NGFW inspection on top of FortiGate.

## Related

- [[Fortinet]] — the hardware platform
- [[BGP]] — used at hub sites to redistribute SD-WAN branch prefixes
- [[Zero Trust]] — SD-WAN access is subject to zero-trust posture checks before granting access to internal resources

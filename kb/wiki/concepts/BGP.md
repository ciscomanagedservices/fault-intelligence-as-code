---
type: concept
title: "BGP"
aliases: ["Border Gateway Protocol", "MP-BGP", "eBGP", "iBGP"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - protocol
  - routing
  - wan
related:
  - "[[IS-IS]]"
  - "[[RPKI]]"
  - "[[BFD]]"
  - "[[EVPN-VXLAN]]"
  - "[[Cisco]]"
  - "[[Juniper Networks]]"
  - "[[Arista Networks]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# BGP — Border Gateway Protocol

## Overview

BGP (Border Gateway Protocol) is the routing protocol of the internet and ACME Corp's primary **inter-domain and overlay routing protocol**. It is used at multiple layers of the ACME Corp network.

## Usage at ACME Corp

| Layer | BGP Role | Peers |
|-------|---------|-------|
| WAN / Internet edge | External BGP (eBGP) peering with ISPs | [[Cisco]] ASR 9000, [[Juniper Networks]] MX Series |
| WAN overlay | MP-BGP for VPN/MPLS route distribution | Core routers |
| DC underlay | eBGP between spine and leaf | [[Arista Networks]] 7300X3 / 7050X3 |
| DC overlay | EVPN address-family over eBGP | [[Arista Networks]] — see [[EVPN-VXLAN]] |

## ACME Corp Configuration Standards

### External Peering Hardening
- **MD5 / TCP-AO authentication** required on all external BGP sessions
- **Maximum Prefix limits** configured on all sessions to prevent route leak flooding
- **Prefix-List filtering** applied to restrict accepted and advertised prefixes
- **RPKI validation** enforced — see [[RPKI]]

### Fast Convergence
- **[[BFD]]** enabled on all core BGP sessions for sub-second failure detection (50ms target)
- Graceful Restart configured for planned maintenance events

## Troubleshooting Reference
For BGP adjacency issues, follow [[BGP Adjacency Troubleshooting]] runbook.

## Common Failure Modes
- BGP session down due to TCP MD5 mismatch after device replacement
- Session flap caused by BFD misconfiguration or hardware timer mismatch
- Route leak from missing or misconfigured prefix-list
- Max-prefix limit exceeded (triggers shutdown of session)

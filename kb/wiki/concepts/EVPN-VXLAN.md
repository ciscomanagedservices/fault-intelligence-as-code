---
type: concept
title: "EVPN-VXLAN"
aliases: ["EVPN", "VXLAN", "Ethernet VPN", "Virtual Extensible LAN"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - protocol
  - data-center
  - overlay
  - fabric
related:
  - "[[Spine-Leaf Architecture]]"
  - "[[BGP]]"
  - "[[Arista Networks]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# EVPN-VXLAN

## Overview

EVPN-VXLAN is the **data center fabric overlay technology** used in all ACME Corp Tier-3 data centers. It combines:
- **VXLAN** (Virtual Extensible LAN): Layer 2 encapsulation tunneled over Layer 3 UDP, providing network virtualization and extending L2 domains over L3 underlay
- **EVPN** (Ethernet VPN): BGP address family used as the control plane for VXLAN, distributing MAC/IP binding information between leaf switches

## Architecture at ACME Corp

```
[Spine 7300X3]  ←—eBGP underlay + EVPN control plane—→  [Spine 7300X3]
       ↑                                                          ↑
  [Leaf 7050X3]                                            [Leaf 7050X3]
  10G/25G host ports                                       10G/25G host ports
```

- **Underlay:** eBGP between spine and leaf ([[Arista Networks]] EOS)
- **Overlay control plane:** EVPN (BGP L2VPN EVPN address family)
- **Data plane:** VXLAN encapsulation (UDP/4789)

## Anycast Gateways

Each leaf switch acts as an anycast default gateway using the same MAC/IP address. This allows VMs or servers to move between leaf switches without needing to update their default gateway — critical for live VM migration and workload mobility.

## Key Benefits

| Benefit | Details |
|---------|---------|
| East-West optimization | Traffic between servers on same or different leaves stays within the fabric |
| L2 extension | VLANs can span across leaf switches without spanning tree issues |
| VM mobility | Workloads can move without IP changes (anycast gateway) |
| Multi-tenancy | Each VNI (VXLAN Network Identifier) provides tenant isolation |

## Troubleshooting

- Verify EVPN BGP session is established: `show bgp evpn summary`
- Check VXLAN tunnel endpoints (VTEPs) are learned: `show vxlan address-table`
- Confirm anycast gateway MAC/IP is consistent across all leaves
- Check underlay eBGP is up — EVPN control plane depends on it

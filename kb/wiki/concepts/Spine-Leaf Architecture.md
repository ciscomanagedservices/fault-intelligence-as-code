---
type: concept
title: "Spine-Leaf Architecture"
aliases: ["Spine-Leaf", "Clos fabric", "Leaf-Spine"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - architecture
  - data-center
  - fabric
related:
  - "[[EVPN-VXLAN]]"
  - "[[BGP]]"
  - "[[Arista Networks]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Spine-Leaf Architecture

## Overview

Spine-Leaf (also called a Clos fabric) is the **data center switching architecture** used in all ACME Corp Tier-3 data centers. It provides a non-blocking, predictable-latency fabric optimized for east-west traffic (server-to-server) rather than the legacy north-south (server-to-gateway) flows of traditional three-tier architectures.

## How It Works

Every **leaf** switch connects to **every spine** switch. No direct leaf-to-leaf connections exist. Every server-to-server flow traverses exactly one or two hops: leaf → spine → leaf.

```
        [Spine 1]       [Spine 2]
         /    \           /    \
      [L1]   [L2]      [L3]   [L4]
      / \    / \        / \    / \
    S1  S2  S3  S4    S5  S6  S7  S8
```

## ACME Corp Implementation

| Layer | Device | Port Speed | Function |
|-------|--------|-----------|---------|
| Spine | [[Arista Networks]] 7300X3 | 100G / 400G | Non-blocking aggregation; eBGP + EVPN control plane |
| Leaf | Arista 7050X3 | 10G/25G (host), 100G (uplinks) | Host connectivity, VXLAN VTEP, anycast gateway |

## Benefits vs. Traditional 3-Tier

| Metric | Traditional (Core/Dist/Access) | Spine-Leaf |
|--------|-------------------------------|-----------|
| East-west latency | Variable (many hops) | Predictable (always 2 hops) |
| Scalability | Limited (STP blocks ports) | Linear (add leaf or spine) |
| Redundancy | STP blocking | All paths active (ECMP) |
| Oversubscription | High at aggregation | Controlled per design |

## ECMP

All paths between any source and destination leaf are equally loaded via **Equal-Cost Multi-Path (ECMP)** routing. This is achieved through eBGP at the underlay layer and maximizes bandwidth utilization.

## Related

- [[EVPN-VXLAN]] — the overlay fabric running on top of the spine-leaf underlay
- [[Arista Networks]] — the hardware platform implementing this architecture at ACME Corp

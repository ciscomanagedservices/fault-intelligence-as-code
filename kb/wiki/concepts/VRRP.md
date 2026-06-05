---
type: concept
title: "VRRP"
aliases: ["Virtual Router Redundancy Protocol"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - protocol
  - high-availability
  - fhrp
related:
  - "[[BFD]]"
  - "[[Spine-Leaf Architecture]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# VRRP — Virtual Router Redundancy Protocol

## Overview

VRRP (Virtual Router Redundancy Protocol) is the **exclusive First Hop Redundancy Protocol (FHRP)** at [[ACME Corp]]. It provides a virtual gateway IP shared between two routers/switches — if the active device fails, the standby takes over the virtual IP transparently to end hosts.

> [!note] ACME Corp Standard
> VRRP is the **only** approved FHRP at ACME Corp. **HSRP** (Cisco-proprietary) and **GLBP** are both **deprecated** and must not be used in any new deployments. Existing HSRP/GLBP deployments should be migrated during next hardware refresh.

## How It Works

1. Two devices share a virtual IP (VIP) and a virtual MAC address
2. The **Master** device owns the VIP and responds to ARP requests
3. The **Backup** device monitors the master via multicast hello messages
4. If the master becomes unreachable, the backup promotes itself to master within the VRRP dead interval

## ACME Corp Configuration Baseline

- **Preemption:** Enabled — if a higher-priority device recovers, it reclaims the master role
- **Authentication:** MD5 authentication between VRRP peers
- **[[BFD]]:** BFD sessions recommended on VRRP uplinks for fast detection of L3 path failures (not just device failure)
- **Tracking:** VRRP tracking of upstream interfaces — if the uplink fails, VRRP priority decrements to force failover

## Placement

VRRP is used at:
- Distribution/aggregation layer gateways at campus and data center access
- Branch office core switches for LAN default gateway redundancy

Note: In the [[Spine-Leaf Architecture]] data center fabric, **anycast gateways** (not VRRP) are used for first-hop redundancy at the leaf layer.

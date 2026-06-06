---
type: concept
title: "BFD"
aliases: ["Bidirectional Forwarding Detection"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - protocol
  - high-availability
  - fast-failover
related:
  - "[[BGP]]"
  - "[[IS-IS]]"
  - "[[VRRP]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# BFD — Bidirectional Forwarding Detection

## Overview

BFD (Bidirectional Forwarding Detection) is a lightweight hello protocol that provides **sub-second failure detection** for routing protocol adjacencies. It detects forwarding path failures faster than any routing protocol's own keepalive mechanisms.

## Usage at ACME Corp

> [!note] ACME Corp Mandate
> BFD is **mandatory** on all core routing links at ACME Corp. Target failure detection time: **50ms**.

BFD is configured on all of the following:
- [[BGP]] sessions on core routers ([[Cisco]] ASR 9000, [[Juniper Networks]] MX Series)
- [[IS-IS]] adjacencies in the core routing layer
- [[VRRP]] uplink tracking at gateway devices

## How It Works

BFD runs between two endpoints and exchanges hello packets at configurable intervals (e.g., every 10ms). If the far end stops responding within the detection multiplier window (e.g., 3 missed hellos = 30ms), BFD declares the path down and immediately notifies the registered routing protocol to take action.

## ACME Corp Timer Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| Min TX Interval | 10ms | Time between sent BFD hellos |
| Min RX Interval | 10ms | Minimum acceptable receive interval |
| Detection Multiplier | 5 | 5 missed hellos = failure (50ms total) |
| **Effective detection time** | **50ms** | Target per ACME Corp standard |

## Impact of BFD Misconfiguration

If BFD timers are mismatched between peers, the session will flap continuously. This can cause:
- Rapid BGP session drops and re-establishments
- IS-IS adjacency instability and route churn
- Unnecessary failover events on healthy links

**Troubleshooting:** Always verify BFD timer symmetry when investigating flapping routing protocol sessions.

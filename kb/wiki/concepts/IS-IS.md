---
type: concept
title: "IS-IS"
aliases: ["Intermediate System to Intermediate System", "ISIS"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - protocol
  - routing
  - igp
related:
  - "[[BGP]]"
  - "[[BFD]]"
  - "[[Cisco]]"
  - "[[Juniper Networks]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# IS-IS — Intermediate System to Intermediate System

## Overview

IS-IS is a link-state Interior Gateway Protocol (IGP) used within ACME Corp's **core routing and WAN transit** layer. It provides the underlay routing fabric over which MP-BGP overlays run.

## Usage at ACME Corp

IS-IS runs on all [[Cisco]] ASR 9000 and [[Juniper Networks]] MX Series routers in the core/WAN tier. It is used in preference to OSPF due to its:
- Better scalability in large, multi-vendor environments
- Protocol independence (runs directly over Layer 2 rather than inside IP)
- Faster convergence with topology change notifications

## Configuration Baseline

- **[[BFD]]** enabled on all IS-IS adjacencies for sub-second failure detection
- Single IS-IS Level 2 (L2) process used for core backbone (no Level 1 areas)
- IS-IS metric style: **wide metrics** only (supports large metric values required for traffic engineering)
- Passive interfaces configured on all non-transit links (loopbacks, management)

## Relationship to BGP

IS-IS provides the reachability for BGP next-hops. IS-IS must converge correctly before BGP sessions can establish after a link failure. The combination of IS-IS (IGP) + MP-BGP (overlay) is standard at ACME Corp core sites.

## Troubleshooting

- Check IS-IS adjacency state: `show isis neighbors`
- Verify interface is not accidentally marked passive
- Check MTU mismatch (IS-IS will not form adjacency if MTUs differ)
- Verify [[BFD]] session is up if adjacency is flapping rapidly

---
type: folder-index
title: "Concepts Index"
created: 2026-05-06
updated: 2026-05-06
tags:
  - index
  - concepts
status: seed
page_count: 11
related: []
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Concepts

## What Belongs Here

**Purpose:** One page per networking concept, protocol, technology, or pattern relevant to network operations.

**Types of content that belong here:**
- Networking protocols (BGP, OSPF, VLAN, STP, MPLS, VXLAN, etc.)
- Technologies and paradigms (SD-WAN, Zero Trust, SASE, NetDevOps, etc.)
- Operational patterns (change freezes, rolling restarts, canary deployments)
- Terminology and definitions (MTU, TTL, ECMP, BFD, etc.)
- Diagnostic concepts (packet loss, jitter, latency, convergence)

**Boundary:** Concepts are *ideas and definitions*, not *instructions* (that's `runbooks/`) and not *specific instances* (that's `entities/`). A concept page for "BGP" explains what BGP is; it does not list every BGP router in the environment.

## Pages

<!-- Updated by wiki-ingest and wiki-lint -->

### Routing Protocols
- [[BGP]] — Border Gateway Protocol; used for WAN edge, MP-BGP overlay, and DC eBGP underlay
- [[IS-IS]] — IGP for core routing layer; runs on Cisco ASR 9000 and Juniper MX
- [[VRRP]] — First Hop Redundancy Protocol (HSRP/GLBP deprecated)

### Data Center Fabric
- [[Spine-Leaf Architecture]] — Non-blocking Clos fabric for east-west DC traffic
- [[EVPN-VXLAN]] — Overlay fabric control + data plane for DC fabric

### WAN & Branch
- [[SD-WAN]] — Branch connectivity via Fortinet FortiGate; dual-WAN active/active

### Security
- [[Zero Trust]] — Default-deny posture; App-ID, User-ID, 802.1X enforcement
- [[MACsec]] — L2 encryption mandate on all DCI links (802.1AE)
- [[RPKI]] — BGP route origin validation; invalid routes dropped

### Reliability
- [[BFD]] — Sub-second failure detection (50ms target) on all core links

### Operations
- [[Infrastructure as Code]] — NetBox → Ansible → GitLab CI/CD; no manual CLI in production

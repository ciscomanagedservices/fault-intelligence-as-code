---
type: entity
entity_type: vendor
title: "Arista Networks"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - vendor
  - arista
  - data-center
related:
  - "[[Cisco]]"
  - "[[Spine-Leaf Architecture]]"
  - "[[EVPN-VXLAN]]"
  - "[[BGP]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Arista Networks

## Role at ACME Corp

Arista is the **exclusive vendor for the data center fabric** at all of ACME Corp's primary Tier-3 data centers. Arista platforms also support streaming gRPC/OpenConfig telemetry to the [[Prometheus]]/[[Grafana]] monitoring stack.

## Deployed Hardware

### Spine Layer (100G/400G)
| Model | Role |
|-------|------|
| 7300X3 Series | Spine switches — 100G/400G density, non-blocking |

### Leaf Layer (10G/25G host-facing)
| Model | Role |
|-------|------|
| 7050X3 Series | Leaf switches — 10G/25G host ports, 100G uplinks to spine |

## Architecture

All Arista switches run the **EVPN-VXLAN** overlay fabric with an eBGP underlay. See [[Spine-Leaf Architecture]] and [[EVPN-VXLAN]] for full details.

- Anycast gateways deployed for seamless VM mobility
- Non-blocking, low-latency east-west traffic optimization

## Telemetry

Arista platforms stream **gRPC/OpenConfig** telemetry to the Prometheus/Grafana observability stack, providing sub-second visibility into interface counters, BGP state, and fabric health.

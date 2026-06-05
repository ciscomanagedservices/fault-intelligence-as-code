---
type: entity
entity_type: vendor
title: "F5 Networks"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - vendor
  - f5
  - load-balancer
  - adc
related:
  - "[[Arista Networks]]"
  - "[[EVPN-VXLAN]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# F5 Networks

## Role at ACME Corp

F5 provides **Application Delivery Controllers (ADC)** and load balancing for ACME Corp's data center and cloud-hosted applications.

## Deployed Hardware

| Model | Role |
|-------|------|
| BIG-IP i5800 | Application delivery / SSL offload (mid-range) |
| BIG-IP i7800 | Application delivery / SSL offload (high performance) |

## Key Functions

| Function | Details |
|----------|---------|
| SSL Offloading | Terminates TLS at the ADC, reducing CPU load on backend servers |
| Global Server Load Balancing (GSLB) | DNS-based traffic distribution across multiple data centers / regions |
| Application Health Monitoring | Continuously polls backend services; removes unhealthy nodes from rotation |
| L7 Traffic Management | HTTP/HTTPS routing, content switching, persistence profiles |

## Related Platforms

- **NGINX Plus** — used in containerized and cloud-native environments as a software ADC/proxy, complementing F5 BIG-IP in on-prem data centers

## Placement

F5 BIG-IPs are deployed within the [[Arista Networks]] data center fabric (connected to leaf switches) and sit in front of server pools in the Internal and DMZ security zones.

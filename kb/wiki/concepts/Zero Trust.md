---
type: concept
title: "Zero Trust"
aliases: ["Zero Trust Architecture", "ZTA", "Default Deny"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - security
  - architecture
  - zero-trust
related:
  - "[[Palo Alto Networks]]"
  - "[[Network Security Operations]]"
  - "[[MACsec]]"
  - "[[RPKI]]"
  - "[[SD-WAN]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Zero Trust

## Overview

Zero Trust is the **security architecture model** mandated across [[ACME Corp]]'s network. The core principle: **no traffic is trusted by default**, regardless of whether it originates inside or outside the corporate network perimeter.

## Core Principles at ACME Corp

| Principle | Implementation |
|-----------|---------------|
| Default Deny | All [[Palo Alto Networks]] firewalls operate with a default-deny rule; explicit permit rules required for every allowed flow |
| App-ID | Traffic is classified by application identity, not port/protocol — prevents app tunneling over allowed ports |
| User-ID | Every allowed flow is tied to an authenticated user identity via User-ID integration with Active Directory |
| Least Privilege | Users and devices receive only the access required for their role |
| Continuous Verification | NAC (802.1X/RADIUS) verifies device posture at every network attachment point |

## Enforcement Points

| Layer | Mechanism |
|-------|-----------|
| Internet edge | [[Palo Alto Networks]] PA-5200 NGFW (DC) / PA-800 (branch) |
| WAN / SD-WAN | [[Fortinet]] FortiGate with IPSec tunnels; no split tunneling on untrusted links |
| Wired access | 802.1X on all [[Cisco]] Catalyst 9300 switch ports |
| Wireless access | 802.1X on all [[Cisco]] Catalyst 9100 Wi-Fi 6 APs |
| Management plane | OOB network; MFA required on all jump hosts |
| Data center interconnect | [[MACsec]] encryption on all DCI links |

## TLS Decryption

TLS decryption is enabled on **designated DMZ inbound flows** to allow deep packet inspection of encrypted traffic entering the DMZ. Internal-to-internal encrypted traffic is selectively decrypted per policy.

## Related Security Policies

- [[Security Zero Trust Mandates]] — formal policy document
- [[MACsec]] — encryption mandate for DCI links
- [[RPKI]] — BGP route origin validation

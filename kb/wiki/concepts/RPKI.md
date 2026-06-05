---
type: concept
title: "RPKI"
aliases: ["Resource Public Key Infrastructure", "Route Origin Validation", "ROV"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - security
  - protocol
  - bgp
  - routing
related:
  - "[[BGP]]"
  - "[[Zero Trust]]"
  - "[[Cisco]]"
  - "[[Juniper Networks]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# RPKI — Resource Public Key Infrastructure

## Overview

RPKI (Resource Public Key Infrastructure) is a cryptographic framework used to validate that a **BGP route announcement originates from an authorized Autonomous System (AS)**. It prevents route hijacking and prefix-origin spoofing on the internet.

## Usage at ACME Corp

> [!note] ACME Corp Mandate
> RPKI Route Origin Validation (ROV) is **mandatory on all external BGP peerings** at ACME Corp. Invalid routes must be **dropped** (not just flagged).

Enforced on all [[Cisco]] ASR 9000 and [[Juniper Networks]] MX Series routers at the internet/WAN edge.

## How It Works

1. IP address holders (ASNs) sign **Route Origin Authorizations (ROAs)** with their private key and publish them to RPKI repositories
2. ACME Corp's routers connect to a local **RPKI cache/validator** (e.g., Routinator or similar)
3. For each received BGP prefix, the router queries the validator: "Is this origin AS authorized to announce this prefix?"
4. Result: **Valid**, **Invalid**, or **Not Found (Unknown)**

## ACME Corp Route Policy

| RPKI State | Action |
|-----------|--------|
| Valid | Accept and prefer |
| Unknown | Accept (many legitimate prefixes are not yet ROA-signed) |
| Invalid | **Drop** — route is rejected; not installed in routing table |

## Benefit

Without RPKI, a malicious or misconfigured network could announce ACME Corp's IP prefixes or hijack traffic to third-party services by announcing more-specific routes. RPKI with drop-invalid policy prevents this.

## Related

- [[BGP]] — the protocol where RPKI validation occurs
- [[Zero Trust]] — RPKI is part of the broader zero-trust security posture for routing infrastructure

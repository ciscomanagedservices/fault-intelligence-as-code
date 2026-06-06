---
type: concept
title: "MACsec"
aliases: ["MAC Security", "802.1AE", "MACsec encryption"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - security
  - encryption
  - layer-2
related:
  - "[[Zero Trust]]"
  - "[[Network Security Operations]]"
  - "[[Arista Networks]]"
  - "[[Cisco]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# MACsec — 802.1AE MAC Security

## Overview

MACsec (IEEE 802.1AE) is a **Layer 2 link-layer encryption standard** that encrypts all traffic on a point-to-point Ethernet link. At [[ACME Corp]], MACsec is mandated on all Data Center Interconnect (DCI) links.

## ACME Corp Mandate

> [!note] Security Mandate
> **All** Data Center Interconnects (DCI) over dark fiber or metro ethernet **MUST** be encrypted using MACsec (802.1AE). No exceptions. This is enforced by [[Network Security Operations]].

This means any link connecting two ACME Corp data centers — whether across a campus dark fiber run or a carrier-provided metro ethernet circuit — must have MACsec enabled at both ends.

## Why MACsec for DCI

| Risk Without MACsec | Mitigation |
|---------------------|-----------|
| Physical fiber tap on leased circuits | MACsec encrypts all frames; tap yields only ciphertext |
| Carrier/provider access to customer traffic | Traffic is opaque to the carrier |
| Rogue device insertion into fiber path | MACsec mutual authentication prevents unauthorized devices |

## How It Works

1. Two MACsec-capable interfaces negotiate a **Security Association** using the MACsec Key Agreement (MKA) protocol
2. Each side derives encryption keys from a shared pre-shared key (PSK) or certificate
3. All Ethernet frames are encrypted with AES-GCM-128 or AES-GCM-256 before transmission
4. The receiving side decrypts and verifies integrity before forwarding

## Configuration Note

MACsec is transparent to higher-layer protocols (IS-IS, BGP, etc.) — it operates entirely at Layer 2. There is a small (typically sub-microsecond) latency penalty for encryption/decryption.

## Platforms

Both [[Arista Networks]] 7300X3/7050X3 and [[Cisco]] ASR 9000 platforms support hardware MACsec. All DCI ports must use hardware offload (not software MACsec) to avoid performance impact.

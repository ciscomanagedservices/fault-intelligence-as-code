---
type: folder-index
title: "Known Issues Index"
created: 2026-05-06
updated: 2026-05-29
tags:
  - index
  - known-issues
status: active
page_count: 3
related: []
sources:
  - "[[ACME Corp Network Operations Handbook]]"
  - "[[INC-20260314 — BGP Session Flap xr-43 (source)]]"
  - "[[INC-20260421 — Process Memory Exhaustion xr-43 (source)]]"
  - "[[INC-20260509 — Persistent CRC Errors xr-43 (source)]]"
---

# Known Issues

## What Belongs Here

**Purpose:** Documented recurring problems, vendor bugs, environmental quirks, and workarounds that a troubleshooting agent needs to know before taking action.

**Types of content that belong here:**
- Vendor bugs with known workarounds
- Recurring environmental issues (e.g., "Switch X reboots under load")
- Known false positives in monitoring systems
- Configuration drift patterns
- Interoperability issues between specific vendors or versions
- Platform-specific limitations that affect operations
- Temporary workarounds pending permanent fixes

**Boundary:** This folder contains *known patterns and their workarounds*, not one-off incident records (those go in `incidents/`). If something happened once and hasn't recurred, it stays in `incidents/`. If a pattern repeats or a vendor acknowledges a bug, it belongs here. Links back to originating incidents are expected.

**Agent usage:** A troubleshooting agent should check this folder early in any diagnostic workflow — a known issue with a workaround should short-circuit the full diagnostic process.

## Pages

<!-- Updated by wiki-ingest and wiki-lint -->

- [[Shadow IT — Unapproved Network Hardware]] — Recurring issue: users connecting unapproved devices; mitigation via 802.1X quarantine VLAN
- [[SFP+ Silent Degradation — CRC Below BFD Threshold]] — SFP+ modules can fail with power in-spec but CRC errors below BFD threshold; workaround: CRC threshold alerts + proactive SFP lifecycle
- [[ASR-9904 BGP Process OOM — Large Prefix-Sets]] — IaC prefix-set > 8,000 entries OOM-kills BGP process on 16GB ASR-9904; workaround: split prefix-sets + platform-aware Ansible memory checks

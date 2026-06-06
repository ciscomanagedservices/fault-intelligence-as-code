---
type: folder-index
title: "Sources Index"
created: 2026-05-06
updated: 2026-05-29
tags:
  - index
  - sources
status: active
page_count: 4
related: []
sources: []
---

# Sources

## What Belongs Here

**Purpose:** One summary page per raw source document ingested into the vault.

**Types of content that belong here:**
- Vendor documentation summaries (Cisco config guides, Juniper release notes)
- Architecture reference documents
- Internal design docs and network diagrams descriptions
- External standards and RFCs (summary pages, not the full text)
- Post-mortem reports and incident summaries from external sources
- Audit reports and compliance documents

**Boundary:** This folder contains *summaries of source documents*, not the raw documents themselves (those live in `.raw/`). Each page here maps 1:1 to a file in `.raw/`. Extracted knowledge from sources gets filed into `concepts/`, `entities/`, `incidents/`, etc. — not stored here in full.

## Pages

<!-- Updated by wiki-ingest and wiki-lint -->

- [[ACME Corp Network Operations Handbook]] — v3.4.1, internal handbook covering teams, hardware, SOPs, and security mandates
- [[INC-20260314 — BGP Session Flap xr-43 (source)]] — SEV-2 incident; BGP flap from far-end SFP degradation
- [[INC-20260421 — Process Memory Exhaustion xr-43 (source)]] — SEV-1 incident; BGP process OOM from IaC prefix-set push
- [[INC-20260509 — Persistent CRC Errors xr-43 (source)]] — SEV-3 incident; silent SFP failure, CRC below BFD threshold

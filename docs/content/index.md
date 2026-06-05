# Fault Intelligence as Code

**AI Agents, RAG, and MCP for Network Ops** - DEVNET-3171, Cisco Live US 2026

This project demonstrates how network fault knowledge can be captured as version-controlled artifacts and executed by an agentic troubleshooting system. Splunk detects a known fault, the webhook relay opens an OpenCode session, the `network-troubleshooter` agent retrieves the right intelligence artifacts and KB context, and RADKit MCP provides controlled access to live network devices.

This is a Cisco Live demo/reference implementation. Run the local quickstart first, then adapt the endpoints, credentials, and device values for your own lab before connecting the workflow to live infrastructure.

The demo is intentionally small enough to understand on stage, but the architecture mirrors the larger operating model: detection logic, repair workflows, human approval, and operational context are all explicit and reviewable.

## What This Demonstrates

This repository shows a path from **fault intelligence as code** to **fault response as an auditable agentic workflow**. The important operating model is simple:

- Fault Signatures, Repair Action Workflows, and Remediation Guides provide reviewed technical ground truth.
- The Markdown KB adds business rules, maintenance windows, known issues, and escalation policy.
- OpenCode agents and skills execute repeatable procedures against scoped context.
- MCP connects the harness to live systems such as RADKit.
- Human approval gates service-impacting actions.

The point is not to give the agent every document and every possible tool. The point is to give it the right context, in the right structure, at the right time.

## Documentation Approach

These docs are OpenCode-first. Install OpenCode, fork and clone the repository, open OpenCode in the repository folder, and use agent prompts as the primary workflow. Manual commands are included as backup or reference for people who want to see exactly what the agent is doing.

Use **Builder** agent from OpenCode for general setup and customization, `network-troubleshooter` for fault runs and RAW test bundles, `ia-curator` for fault-intelligence artifacts, and `kb-curator` for knowledge-base maintenance.

## Start by Job

| Job | Start here |
|-----|------------|
| Run the local demo | [Local Agent Test](quickstart/local-agent-test.md) |
| Connect a lab | [Lab Environment](quickstart/lab-environment.md) |
| Create new fault intelligence | [Artifact Authoring](quickstart/artifact-authoring.md) |
| Maintain operational context | [KB Curator](quickstart/kb-curator.md) |
| Understand the system | [Architecture Overview](architecture/overview.md) |
| Troubleshoot a failed run | [Troubleshooting](operations/troubleshooting.md) |

## Current Demo Path

The current simulator default is `AD000002`: BGP Neighbor Administrative Shutdown on IOS XR.

| Item | Value |
|------|-------|
| Default device | `xr-43` |
| Default neighbor | `172.20.20.18` |
| Default VRF | `default` |
| Default neighbor AS | `3334` |
| Artifact group | `intelligence-artifacts/AD000002-bgp-neighbor-admin-shutdown-xr/` |

The RAW confirms `BGP state = Idle (Admin)`, verifies `shutdown` exists in the neighbor configuration, requests approval, applies `no shutdown`, and verifies that the BGP session returns to `Established`.

## Key Runtime Boundaries

`network-troubleshooter` can diagnose live faults, call RADKit MCP tools, and invoke read-only sub-agents. It cannot edit repository files and cannot call curator agents. `ia-curator` and `kb-curator` are separate author-time agents for maintaining artifacts and the KB vault.

Next: start with the [Quickstart](quickstart/index.md), or read the [Architecture Overview](architecture/overview.md) for the system map.
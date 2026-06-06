# Fault Intelligence as Code

Welcome. This repository supports Cisco Live DEVNET-3171: **Fault Intelligence as Code: AI Agents, RAG, and MCP for Network Ops**.

The project shows how network fault knowledge can be captured as versioned artifacts, connected to an agentic troubleshooting workflow, grounded with a knowledge base, and exercised safely through simulated or lab-based remediation runs.

Shortcut to this page: [cs.co/fault-intel](https://cs.co/fault-intel)

Questions? Contact [Jason Shoemaker](mailto:jashoema@cisco.com) or [Steve Holl](mailto:sholl@cisco.com).

## Documentation Approach

These docs are written for network engineers and non-coders first. The primary workflow is to install OpenCode, fork and clone this repository, open OpenCode in the cloned folder, and ask the right agent to do the work. Manual commands are included as fallback or reference when they are useful.

Use Opencode's built-in **Builder** agent for general setup, file changes, and lab customization. Use the named project agents for specialized work: `network-troubleshooter` for fault runs and RAW test bundles, `ia-curator` for fault-intelligence artifacts, and `kb-curator` for knowledge-base maintenance.

## Start Here

| Resource | Use it for |
|----------|------------|
| [Published documentation](https://ciscomanagedservices.github.io/fault-mgmt-as-code/) | The best place to read the project docs. |
| [Session slides](docs/presentations/DEVNET-3171.pdf) | The Cisco Live deck for DEVNET-3171. |
| [Quickstarts](https://ciscomanagedservices.github.io/fault-mgmt-as-code/quickstart/) | The fastest paths for trying the demo, setting up a lab, authoring artifacts, and curating the KB. |
| [Local agent prompt test](https://ciscomanagedservices.github.io/fault-mgmt-as-code/quickstart/local-agent-test/) | Run the troubleshooting flow with simulated device responses, no Splunk/RADKit/Webex required. |
| [Architecture overview](https://ciscomanagedservices.github.io/fault-mgmt-as-code/architecture/overview/) | Understand the agent, data flow, knowledge base, and artifact model. |
| [Artifact authoring](https://ciscomanagedservices.github.io/fault-mgmt-as-code/quickstart/artifact-authoring/) | Create Fault Signatures, Repair Action Workflows, Remediation Guides, and tests. |

## What Is In This Repo

| Path | What's there |
|------|--------------|
| [docs/content](docs/content) | Source for the published documentation site. |
| [docs/presentations](docs/presentations) | Cisco Live presentation materials. |
| [intelligence-artifacts](intelligence-artifacts) | Published Fault Signature, Repair Action Workflow, and Remediation Guide examples. |
| [.opencode/agents](.opencode/agents) | OpenCode agents for troubleshooting, KB reading, and KB curation. |
| [.opencode/skills](.opencode/skills) | Skills used by the agents for remediation, wiki access, artifact authoring, testing, and notifications. |
| [kb](kb) | The local knowledge base vault used for RAG-style grounding. |
| [app](app) | FastAPI webhook relay for receiving Splunk-style fault alerts and creating OpenCode sessions. |
| [scripts](scripts) | Alert simulation, RAW test execution, and supporting utilities. |
| [ia-drafts](ia-drafts) | Draft workspace for new intelligence artifacts before publication. |

## Try It

The easiest path is the [Local Agent Prompt Test](https://ciscomanagedservices.github.io/fault-mgmt-as-code/quickstart/local-agent-test/). It uses OpenCode and checked-in test bundles to run the `network-troubleshooter` agent without touching real network devices.

When you are ready to adapt the project, fork this repository first, then clone your fork. That gives you a place to commit your own lab configuration, artifact experiments, and documentation changes without changing the upstream reference copy.

## Session Information

**Cisco Live DEVNET-3171**<br>
Fault Intelligence as Code: AI Agents, RAG, and MCP for Network Ops<br>
Tuesday, Jun 2, 12:30 PM - 1:15 PM PDT<br>
WoS - DevNet Theater<br>

[Cisco Live session catalog](https://www.ciscolive.com/global/learn/session-catalog.html?search=DEVNET-3171#/)

## Abstract

As networks scale, the knowledge required to detect, diagnose, and repair incidents becomes scattered across support cases, vendor advisories, telemetry analysis, and tribal expertise. This session shows how agentic AI can transform that fragmented knowledge into actionable fault intelligence that your tools can consume via simple data models and APIs.

- You'll learn how AI agents, custom knowledge bases, and context-engineering techniques translate historical incidents and vendor recommendations into precise detection logic and automated repair action workflows.
- We'll walk through an architecture and schema for representing "fault intelligence as code," and how to keep agents grounded using RAG and Model Context Protocol (MCP).
- Through practical examples and sample code, you'll learn how to build a lightweight AI agent that constructs its own fault-intelligence knowledge base and emits machine-ready rules and repair workflows.
- You'll also see how these patterns plug into existing observability, ticketing, or automation tooling, and how Cisco CX is using the same ideas to continuously deliver fault intelligence that reduces MTTR and support escalations.

## Authors

**Jason Shoemaker**, CCIE #24255<br>
AI & Automation Architect<br>
Customer Experience Delivery<br>
Cisco Systems, Inc.<br>
[jashoema@cisco.com](mailto:jashoema@cisco.com)<br>

**Steve Holl**, CCIE #22739<br>
Principal Architect<br>
Customer Experience Product Management<br>
Cisco Systems, Inc.<br>
[sholl@cisco.com](mailto:sholl@cisco.com)

Questions are welcome. Reach out to Jason or Steve at the email addresses above.
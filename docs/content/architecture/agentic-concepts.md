# Agentic Concepts

This project uses agentic AI terms in a practical network-operations sense. The goal is not to introduce a new vocabulary for its own sake; it is to explain how the prototype keeps an LLM grounded, useful, and governed while responding to network faults.

## Agent

An agent is more than a raw language model. In this repository, an agent means the model plus the harness around it: instructions, tools, memory, safety controls, allowed skills, sub-agent permissions, and an execution loop.

The `network-troubleshooter` agent is the runtime orchestrator. The `ia-curator` and `kb-curator` agents are author-time tools for maintaining the knowledge sources that runtime agents later consume.

## Agent Harness

An agent harness is the runtime environment around the model. It gives the model controlled access to files, tools, APIs, skills, memory, and multi-step execution.

There are two common harness patterns:

| Pattern | Examples | Useful for |
|---------|----------|------------|
| Interactive coding harness | OpenCode, GitHub Copilot, Claude Code | Rapid prototyping, repository-native workflows, prompt/skill iteration, local demos. |
| Programmatic agent framework | LangGraph, LangChain, similar coded frameworks | Production services, custom orchestration, high-throughput execution, deeper application integration. |

This prototype uses OpenCode because the behavior is file-driven and fast to iterate. Agent definitions, skills, permissions, and MCP configuration live in the repository, so changes can be reviewed through normal Git workflows. The same harness can be exercised interactively during development and invoked programmatically by the relay when an alert fires.

That does not mean every production system should run forever inside a coding harness. The value of this prototype is that it lets the team validate the operating model, prompts, skills, policies, and artifact schemas quickly. If scale or throughput requires another runtime later, the validated behavior can be ported into a coded framework with far less uncertainty.

## Skills

Skills are reusable procedures that an agent loads when it needs specialized behavior. They provide progressive knowledge disclosure: the agent loads the specific procedure for the task instead of carrying every possible instruction in its base prompt.

Examples in this repository:

| Skill | Role |
|-------|------|
| `fault-remediation` | Interprets and executes Repair Action Workflows. |
| `webex-notify` | Renders and sends Webex notifications and approval cards. |
| `ia-research` | Collects support and documentation evidence for new artifacts. |
| `ia-create` | Creates Remediation Guides, Fault Signatures, and Repair Action Workflows. |
| `wiki-query` | Retrieves relevant operational context from the Markdown KB. |
| `wiki-ingest` | Curates source material into the KB wiki. |

Skills are the bridge between a general-purpose model and repeatable domain-specific work.

## MCP Servers

MCP, the Model Context Protocol, exposes tools and APIs to agents through a consistent interface. In practical terms, an MCP server is a wrapper around a system the agent may need to use, such as a network device access layer, documentation source, ticketing system, or support API.

This repository uses MCP in two different phases:

| Phase | MCP use |
|-------|---------|
| Author-time | Cisco support and documentation sources can provide evidence for artifact research. |
| Runtime | RADKit MCP provides controlled CLI access to network devices. |

The important design point is decoupling. The agent workflow can stay stable while the tool implementation changes behind an MCP interface.

## Context Engineering

Context engineering is the practice of deciding what information an agent receives, in what shape, and at what time.

For network operations, this matters more than simply increasing context size. A troubleshooting agent does not need every document, every log, and every possible procedure. It needs a precise bundle of fault metadata, approved artifacts, operational policy, live device state, and approval status.

That is why this repository separates knowledge sources:

| Source | Purpose |
|--------|---------|
| Fault Signature | Detect the known fault and extract variables. |
| Repair Action Workflow | Provide deterministic diagnosis, action selection, repair, verification, and escalation logic. |
| Remediation Guide | Give humans the readable source and review artifact. |
| KB wiki | Provide business policy, known issues, maintenance windows, incident history, and escalation context. |
| RADKit MCP | Collect what is true on the device during the active incident. |

## RAG in This Project

RAG is often used to mean vector search over chunked documents. This project uses the broader agentic meaning: any retrieval of external information that improves the agent's context.

That includes:

- Loading approved FS/RAW/RG artifacts from the repository.
- Querying the Markdown KB through `kb-reader` and `wiki-query`.
- Collecting live device state through RADKit MCP.
- Using author-time MCP tools to gather support or documentation evidence.

The retrieval mechanism matters less than whether the agent receives the right information in a form it can use reliably.
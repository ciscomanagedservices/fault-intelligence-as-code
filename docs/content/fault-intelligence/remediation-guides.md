# Remediation Guides

A Remediation Guide (RG) is the human-readable Markdown source document for a fault. It is written for network engineers and SMEs, not for direct machine execution.

## Core Rules

| Rule | Meaning |
|------|---------|
| Markdown only | RGs are `.md` files. No YAML RG is generated. |
| Human-readable | Write in plain English as a knowledge-base style procedure. |
| No regex or YAML syntax | Triggering events and sample outputs are described in prose and examples; tooling derives regex and workflow logic later. |
| Source for FS and RAW | AI derives FS detection logic and RAW repair flow from the reviewed RG. |
| ID format | `RG######`, aligned with the parent `AD######`, `FS######`, and `RAW######`. |

## Required Structure

The authoritative format is `.opencode/skills/ia-create/references/remediation-guide-template.md`. A guide should include:

| Section | Purpose | Derived artifact content |
|---------|---------|--------------------------|
| Title and Overview | Name the fault and remediation approach. | FS and RAW names/descriptions. |
| Applicability | Products, OS versions, component, severity, related defects. | FS metadata. |
| Triggering Events | Syslog/alarm/telemetry examples and values to extract. | FS events, regex, extraction parameters, clear events. |
| Symptoms | Observable operational indicators. | Human context. |
| Diagnosis and Repair Steps | Commands, sample outputs, decisions, cautions. | RAW validation and action selection. |
| Escalation | When to hand off and what evidence to collect. | RAW `escalate` actions and evidence. |
| Post-Repair Verification | Commands and expected healthy output. | Final RAW validation and `resolve`. |
| References | Docs, bugs, advisories. | Tags and informational context. |

## Example

`AD000002` uses `RG000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_GUIDE.md` to describe the IOS XR procedure for restoring a BGP neighbor that is in administrative shutdown. The linked RAW automates the same logic by confirming `Idle (Admin)`, verifying `shutdown` in config, applying `no shutdown` after approval, and checking for `Established`.

## Authoring Guidance

Use placeholders such as `{{ neighbor_ip }}` for values extracted by the FS. Keep commands complete enough for a human operator; unlike RAW `config_cli.commands[]`, the RG may show full CLI sessions including `configure terminal`, `commit`, and `end` for readability.
---
type: entity
entity_type: team
title: "Network Architecture and Engineering"
aliases: ["NAE"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - team
  - architecture
  - acme-corp
related:
  - "[[ACME Corp]]"
  - "[[Global Network Operations Center]]"
  - "[[Network Security Operations]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Network Architecture and Engineering (NAE)

## Overview

Responsible for the design, scaling, and technology lifecycle of [[ACME Corp]]'s network. NAE is the engineering counterpart to the operational [[Global Network Operations Center]].

## Sub-Teams

### Design Architects
- Evaluate new technologies (SD-WAN, 400G ethernet, IPv6 migration)
- Publish validated design blueprints for deployment use
- Set hardware and vendor standards for the organization

### Deployment Engineers
- Execute planned changes during approved maintenance windows
- Handle hardware refreshes, greenfield site stand-ups, major topology shifts
- Must follow [[Change Management Policy]] for all production work

### Automation Engineers
- Develop and maintain NetDevOps CI/CD pipelines
- Own [[Ansible]] playbooks for configuration push to all devices
- Maintain Python automation scripts and [[Terraform]] modules
- Enforce [[Infrastructure as Code]] principles — no manual CLI changes in production

## Key Responsibilities

- Maintain [[NetBox]] as the Single Source of Truth (SSoT) for all network intent
- Define VLAN assignments, IPAM, and device inventory in [[NetBox]]
- Own the [[GitLab]] CI/CD pipeline for all configuration deployments
- Technology roadmap: currently evaluating SD-WAN expansion, 400G DC fabric, full IPv6 rollout

## Maintenance Windows

- **Global:** Saturdays 22:00 UTC — Sundays 04:00 UTC
- **Regional:** Localized per region (contact NAE for schedule)

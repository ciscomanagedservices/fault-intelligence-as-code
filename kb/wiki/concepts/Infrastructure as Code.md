---
type: concept
title: "Infrastructure as Code"
aliases: ["IaC", "NetDevOps", "Network Automation"]
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - concept
  - automation
  - devops
  - netdevops
  - best-practice
related:
  - "[[NetBox]]"
  - "[[Oxidized]]"
  - "[[Network Architecture and Engineering]]"
  - "[[Change Management Policy]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Infrastructure as Code (IaC)

## Overview

Infrastructure as Code (IaC) is the **operational philosophy and technical practice** at [[ACME Corp]] where all network configuration is defined, versioned, and deployed through code and automated pipelines — never through manual CLI commands.

## The ACME Corp IaC Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Intent / SSOT | [[NetBox]] | Defines desired state (IPs, VLANs, device roles) |
| Config templates | Ansible (Jinja2) | Renders device configurations from NetBox data |
| CI/CD pipeline | GitLab CI/CD | Tests and deploys configurations on merge |
| Infrastructure provisioning | Terraform | Cloud and virtual infrastructure (not physical devices) |
| Drift detection | [[Oxidized]] | Detects unauthorized out-of-band changes |
| Config scripting | Python | Custom automation and one-off operational scripts |

## Policy: No Manual CLI Changes

> [!note] ACME Corp Mandate
> Direct SSH access to production devices is restricted to **Break-Glass emergencies only**. All routine configuration changes must be deployed via the GitLab CI/CD pipeline. Manual changes will be detected by [[Oxidized]] within 4 hours and trigger a NOC alert.

A "Break-Glass" event requires:
1. Approval from a T3 engineer or NOC manager
2. Immediate [[ServiceNow]] ticket documenting the change
3. The manual change must be replicated into the code repository within 24 hours so Oxidized no longer alerts

## CI/CD Workflow

```
Developer/Engineer → GitLab MR → Pipeline: lint → syntax check → 
  diff preview → approval gate → deploy to staging → deploy to production
```

## Benefits

- **Auditability:** Every change is a Git commit with an author, timestamp, and reason
- **Repeatability:** Same template deploys identically to 150 branch switches
- **Rollback:** Git revert + redeploy restores previous state in minutes
- **Drift detection:** [[Oxidized]] ensures the running config matches the Git state

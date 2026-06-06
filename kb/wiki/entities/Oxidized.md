---
type: entity
entity_type: tool
title: "Oxidized"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - tool
  - config-backup
  - configuration-management
related:
  - "[[NetBox]]"
  - "[[Splunk]]"
  - "[[Network Architecture and Engineering]]"
  - "[[Infrastructure as Code]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# Oxidized

## Role at ACME Corp

Oxidized is the **automated network configuration backup** system. It polls every managed network device every **4 hours**, saves the running configuration, and generates diff alerts for any unauthorized changes.

## How It Works

1. Oxidized connects to each device via SSH (or TELNET for very legacy devices — though Telnet is deprecated at ACME Corp)
2. Executes `show running-config` (or platform equivalent)
3. Saves the result to a Git-backed repository
4. Computes a diff against the last saved version
5. If a diff is detected, sends an alert to the **NOC Slack channel**

## Change Detection

Oxidized diffs are critical for detecting unauthorized or accidental manual CLI changes to production devices — a direct violation of [[Infrastructure as Code]] policy (all config changes must go through the [[Ansible]] CI/CD pipeline).

| Scenario | Oxidized Response |
|----------|-----------------|
| Authorized change via CI/CD pipeline | No alert (diff expected, pipeline records the change) |
| Unauthorized manual CLI change | **Diff alert sent to NOC Slack immediately** |
| Device unreachable at poll time | Alert to NOC that backup failed |

## Integration

- Backup repo stored in [[GitLab]] (same platform as CI/CD pipelines)
- Alert integration with [[Splunk]] for archival and correlation
- Device list sourced from [[NetBox]] inventory (dynamic — Oxidized auto-discovers new devices added to NetBox)

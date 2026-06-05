---
type: entity
entity_type: tool
title: "ServiceNow"
created: 2026-05-06
updated: 2026-05-06
status: evergreen
tags:
  - entity
  - tool
  - itsm
  - change-management
  - ticketing
related:
  - "[[Global Network Operations Center]]"
  - "[[Network Architecture and Engineering]]"
  - "[[Change Management Policy]]"
sources:
  - "[[ACME Corp Network Operations Handbook]]"
---

# ServiceNow

## Role at ACME Corp

ServiceNow is the **ITSM platform** used for all incident ticketing and change management at [[ACME Corp]]. It is the system of record for every operational event and change.

## Key Functions

### Incident Management
- All incidents opened by [[Global Network Operations Center]] T1 analysts are logged in ServiceNow
- Severity levels (SEV-1 through SEV-4) are tracked with SLA timestamps
- Escalation path documented per ticket; T1 → T2 → T3 escalations recorded

### Change Management
- **All** network changes must have a ServiceNow change ticket before work begins (ITIL compliance)
- Change tickets must include: scope, risk assessment, testing plan, and **rollback procedure**
- Changes affecting Tier-1 services or core routing require **CAB approval** (meets Tuesdays 14:00 UTC)
- Maintenance window compliance tracked via ServiceNow scheduled CIs

## ITIL Alignment

ACME Corp's change management process follows the **ITIL** framework:

| Change Type | Approval Required | Example |
|------------|-------------------|---------|
| Standard | Pre-approved template | Add a VLAN at a branch |
| Normal (Minor) | Manager approval | Firmware upgrade on branch switch |
| Normal (Major / Tier-1) | Full CAB review | Core routing change, firewall policy change |
| Emergency | ECAB (expedited CAB) | Sev-1 mitigation requiring a change |

See [[Change Management Policy]] for the full policy.

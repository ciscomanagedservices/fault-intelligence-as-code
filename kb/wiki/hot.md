---
type: meta
title: "Hot Cache"
updated: 2026-05-29T00:00:00
tags:
  - meta
  - cache
status: evergreen
---

# Recent Context

## Last Updated
2026-05-29. Batch ingest completed: 3 incident records for xr-43 (Cisco ASR-9904).

## Key Recent Facts

- **Batch ingest:** 3 INC raw files (BGP flap, memory exhaustion, interface CRC errors) — all involving xr-43
- **11 new wiki pages created** across incidents, sources, entities, known-issues, and runbooks
- **xr-43 profile:** Cisco ASR-9904, IOS-XR 7.9.2, 16GB RAM — 3 SEV-1/2/3 incidents in ~2 months
- **New known issues:** SFP+ silent degradation pattern + ASR-9904 OOM memory limit
- **New runbook:** Interface CRC Error Troubleshooting

## ACME Corp Key Facts (Quick Lookup)

| Topic | Key Fact |
|-------|---------|
| Core routing vendors | Cisco ASR 9904/9910, Juniper MX480/MX960 |
| DC fabric vendor | Arista 7300X3 (spine), 7050X3 (leaf) |
| DC fabric protocol | EVPN-VXLAN over eBGP |
| Firewall vendor | Palo Alto Networks PA-5200 (DC), PA-800 (branch) |
| SD-WAN vendor | Fortinet FortiGate |
| Load balancer | F5 BIG-IP iSeries + NGINX Plus |
| FHRP | VRRP only — HSRP/GLBP deprecated |
| Failure detection | BFD at 50ms on all core links |
| DCI encryption | MACsec (802.1AE) mandatory |
| BGP security | MD5/TCP-AO auth + max-prefix + RPKI drop-invalid |
| Config management | NetBox → Ansible → GitLab CI/CD; no manual CLI |
| Config backup | Oxidized every 4h; diff alerts to NOC Slack |
| ITSM | ServiceNow (all incidents + changes) |
| Monitoring stack | Splunk (SNMP/syslog), ThousandEyes (synthetic), Kentik (flow), Prometheus/Grafana (telemetry) |

## Incident SLA Quick Reference

| SEV | Response | Notes |
|-----|---------|-------|
| SEV-1 | 5 min + bridge call | T1+T2+T3+Mgmt |
| SEV-2 | 15 min | T2+T3 on-call |
| SEV-3 | 2 hours | T2 notified |
| SEV-4 | 24 hours | — |

## Change Management Quick Reference
- CAB: **Tuesdays 14:00 UTC** (submit by Friday 17:00 UTC)
- Global maintenance window: **Sat 22:00 — Sun 04:00 UTC**
- Every change MUST have a verified rollback procedure

## xr-43 Key Facts (Active Device — 3 Incidents)

| Field | Value |
|-------|-------|
| Platform | Cisco ASR-9904 |
| OS | IOS-XR 7.9.2 |
| RAM | **16 GB** (vs xr-44 at 32GB) |
| IaC management | Ansible (`netauto` user) |
| BGP peers | 14 total (iBGP + eBGP) |
| Uplink | GigabitEthernet0/0/0/1 → ISP-A (AS 65001, 198.51.100.1) |
| Inter-DC link | TenGigE0/0/0/3 → DC-West |

## Known Issues Quick Reference (Agent Short-Circuits)

| Pattern | Known Issue | Action |
|---------|------------|--------|
| CRC errors on interface (link UP, BFD silent) | [[SFP+ Silent Degradation — CRC Below BFD Threshold]] | Go to [[Interface CRC Error Troubleshooting]] |
| All 14 BGP sessions drop simultaneously after `netauto` commit | [[ASR-9904 BGP Process OOM — Large Prefix-Sets]] | Monitor auto-restart; rollback IaC commit |
| BGP Hold Timer Expired + CRC errors on same interface | [[SFP+ Silent Degradation — CRC Below BFD Threshold]] | Check CRC before escalating BGP config |

## Recent Incident Summary (xr-43)

| ID | Date | SEV | Summary |
|----|------|-----|---------|
| [[INC-20260314 — BGP Session Flap xr-43]] | 2026-03-14 | SEV-2 | Far-end ISP-A SFP → CRC → BGP flap; resolved by ISP-A |
| [[INC-20260421 — Process Memory Exhaustion xr-43]] | 2026-04-21 | SEV-1 | IaC prefix-set OOM; 23 branches, 4m12s outage |
| [[INC-20260509 — Persistent CRC Errors xr-43]] | 2026-05-09 | SEV-3 | Local SFP failure; silent CRC degradation; VoIP impact |

## Recent Changes (2026-05-29)
- Ingested 3 incident records for xr-43
- Created entity pages: xr-43, ISP-A
- Created known-issue pages: SFP+ Silent Degradation, ASR-9904 OOM
- Created runbook: Interface CRC Error Troubleshooting
- Updated all indexes

## Active Threads
- No incidents open
- No open questions
- xr-43 warrants: (1) proactive SFP lifecycle review, (2) CRC threshold Splunk alert, (3) Oxidized CRC diff alert, (4) Ansible platform memory check for ASR-9904

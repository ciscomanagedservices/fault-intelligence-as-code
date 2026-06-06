---
type: runbook
title: "Interface CRC Error Troubleshooting"
created: 2026-05-29
updated: 2026-05-29
status: active
tags:
  - runbook
  - crc-errors
  - hardware
  - optics
  - sfp
  - interface
related:
  - "[[SFP+ Silent Degradation — CRC Below BFD Threshold]]"
  - "[[BGP Adjacency Troubleshooting]]"
  - "[[BFD]]"
  - "[[xr-43]]"
  - "[[INC-20260509 — Persistent CRC Errors xr-43]]"
  - "[[INC-20260314 — BGP Session Flap xr-43]]"
  - "[[Incident Severity SLAs]]"
sources:
  - "[[INC-20260509 — Persistent CRC Errors xr-43 (source)]]"
  - "[[INC-20260314 — BGP Session Flap xr-43 (source)]]"
---

# Interface CRC Error Troubleshooting

## When to Use This Runbook

Use this runbook when:
- Splunk alerts on CRC error threshold (> 500 in 15 min, or > 100 per 4-hour Oxidized snapshot)
- `show interfaces <int>` shows incrementing CRC input errors
- VoIP quality complaints or latency-sensitive traffic degradation without a link-down event
- BGP session flaps with Hold Timer Expired AND CRC errors visible on the upstream interface

> [!warning] Check known issues first
> Before starting diagnostics, verify whether the affected device/interface has an open known issue:
> - [[SFP+ Silent Degradation — CRC Below BFD Threshold]] — may short-circuit to SFP replacement
> - [[BGP Adjacency Troubleshooting]] — if BGP sessions are also flapping

---

## Step 1: Confirm and Isolate the Interface

```
show interfaces summary
show interfaces <int>
```

- Verify CRC counter is incrementing (not a stale count)
- Note rate: errors per minute (check at T=0 and T+5 min)
- Confirm interface is UP/UP (if it's down, this is a different issue — see [[BGP Adjacency Troubleshooting]])

**Expected:** Input CRC errors incrementing; line protocol UP.

---

## Step 2: Check Local Optics

```
show controllers optics <slot/port>
```

- Record Rx power (dBm) and Tx power (dBm)
- Compare to module spec (typical 10G SR: Rx threshold -11.1 dBm min)

> [!warning] Power in-spec does NOT rule out SFP failure
> See [[SFP+ Silent Degradation — CRC Below BFD Threshold]]. A failing module may read -2.1 dBm Rx (within spec) while producing hundreds of CRC errors per minute.

---

## Step 3: Check Far-End Optics

Log into the far-end device (peer router or DC switch) and run the equivalent optics check:

```
# IOS-XR peer
show controllers optics <slot/port>

# Arista/NX-OS peer
show interfaces <int> transceiver
```

- If far-end Tx power is **low or out-of-spec** → far-end SFP is likely the culprit
- If far-end looks normal → likely a local SFP issue or a cable/connector problem

---

## Step 4: Clean Fiber Connectors

At the MMR/patch panel:

1. Remove and inspect fiber patch cord connectors under inspection microscope if available
2. Use appropriate fiber-optic cleaning tool (swab or reel cleaner) for both SC/LC connectors
3. Re-seat patch cord

**Recheck:** Monitor CRC rate for 5 minutes.

- If CRC rate drops to zero → dirty connector was the cause (resolved)
- If CRC rate unchanged → proceed to SFP replacement

---

## Step 5: Replace SFP Transceiver

> [!warning] Maintenance window requirement
> Replacing an SFP on a live interface may cause a brief link interruption. Verify traffic impact:
> - If interface has a redundant path (BFD failover available) → notify NOC and proceed
> - If interface is sole path for critical traffic → schedule during maintenance window per [[Change Management Policy]]

**Procedure:**
1. Obtain spare SFP+ from on-site stock (verify spec match: wavelength, reach, form factor)
2. Note the serial number of the module being removed for RMA
3. Remove and replace SFP+ transceiver
4. Monitor for 15 minutes: `show interfaces <int>` — verify CRC errors stop

**If CRC errors stop:** Incident resolved. Open RMA for failed module.
**If CRC errors continue:** Escalate — suspect cable, patch panel, or far-end issue.

---

## Step 6: Open RMA for Failed SFP

If SFP replacement resolved the issue:

1. Record failed module serial number (from `show controllers optics` or label on module)
2. Open TAC case for RMA via ServiceNow
3. Return defective module within RMA window

---

## Step 7: Post-Incident Verification

After resolution, run a 15-minute clean window check:

```
show interfaces <int>
```

Confirm: Input CRC errors count NOT incrementing during the observation window.

Update the incident record in ServiceNow and flag for post-incident review if > SEV-3.

---

## Escalation Path

| Condition | Action |
|-----------|--------|
| BGP sessions also dropping | Engage T3 routing team; cross-reference [[BGP Adjacency Troubleshooting]] |
| No spare SFP available | Escalate to T3 + procurement; consider temporary traffic re-route |
| CRC errors persist after SFP swap and connector cleaning | Engage TAC for cable/link-layer analysis |
| Far-end device is ISP/carrier equipment | Engage ISP NOC with CRC evidence from local interface |

---

## Related Incidents

| Incident | Summary |
|----------|---------|
| [[INC-20260509 — Persistent CRC Errors xr-43]] | Local SFP failure on TenGigE0/0/0/3; resolved with SFP swap |
| [[INC-20260314 — BGP Session Flap xr-43]] | Far-end ISP-A optic caused CRC → BFD → BGP flap; resolved by ISP-A |

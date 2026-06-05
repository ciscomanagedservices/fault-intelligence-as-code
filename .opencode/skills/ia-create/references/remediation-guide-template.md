# Remediation Guide — Format Specification and Templates

This document defines the format for Remediation Guides (RGs). A Remediation Guide is a human-readable troubleshooting document written by a network engineer or SME. It contains no regex, no YAML syntax, and no machine-specific expressions — it reads like a knowledge base article. From a single RG, AI tooling derives both a **Fault Signature** (FS) and a **Repair Action Workflow** (RAW).

---

## Part 1: Format Specification

Each section of the RG maps to specific FS and RAW fields. The table below each section heading shows what AI derives from that section.

### 1. Title & Overview

A short title naming the fault condition, followed by a 2–4 sentence overview of what this guide covers: the fault, the affected technology area, and the general remediation approach.

| Human writes | AI → FS | AI → RAW |
|---|---|---|
| Title | `metadata.name` (converted to UPPER_SNAKE_CASE) | `workflow.metadata.name` (appended with `_REPAIR`) |
| Overview paragraph | `metadata.description` | `workflow.metadata.description` |

### 2. Applicability

Describes where this guide applies: hardware platforms, operating system versions, the affected component or subsystem, and the severity of the fault condition.

**Subsections:**

- **Products:** List of hardware platforms or product families (e.g., "Cisco 8000 Series", "Catalyst 9300, 9400, 9500").
- **Operating Systems:** OS and version ranges (e.g., "IOS XE 17.x", "IOS XR 7.x and later").
- **Component:** The primary subsystem affected (e.g., "Fan", "Power Supply", "Route Processor", "Optics").
- **Severity:** One of: Critical, Major, Warning, Minor.
- **Related Defects** *(optional)*: Known Cisco bug IDs relevant to this fault (e.g., "CSCxx12345").

| Human writes | AI → FS | AI → RAW |
|---|---|---|
| Products list | `metadata.product_ids` (converted to regex patterns) | — |
| OS versions | `metadata.os_versions` | — |
| Component | `metadata.component` (mapped to enum) | — |
| Severity | `metadata.severity` (mapped to enum) | — |
| Related defects | `metadata.tags`, `references` | `workflow.metadata.description` context |

### 3. Triggering Events

Describes the syslog messages, alarms, or telemetry conditions that indicate this fault has occurred. This is the most important section for FS generation.

**Per-event subsections** (repeat for each triggering event):

- **Event label:** A short name (e.g., "Event 1: BGP Neighbor Down Notification").
- **Type:** One of: Syslog, Alarm, State Counter, Metric.
- **Message ID** *(for syslog)*: The syslog mnemonic (e.g., `BGP-5-ADJCHANGE`, `PKT_INFRA-FM-2-FAULT_CRITICAL`). **Each unique message ID must be defined as a separate event.** If a fault can be triggered by `PKT_INFRA-FM-2-FAULT_CRITICAL` or `PKT_INFRA-FM-3-FAULT_MAJOR`, those are two events with OR correlation — not one event listing two message IDs.
- **Example message:** A complete, realistic sample of the raw syslog or alarm text. This is the primary input for AI to derive the regex match pattern.
- **Key values to extract:** Which parts of the message are operationally significant and should be captured as variables (e.g., "the neighbor IP address", "the fan tray number"). Describe what to extract and where it appears in the message.

**Correlation and time window** *(for multi-event)*:

- **Correlation logic:** Whether **all** events must occur (AND) or **any** event triggers the fault (OR).
- **Time window:** How long to wait for correlated events (e.g., "Both events within 5 minutes"). Omit for single-event signatures.

**Recovery indicator** *(optional)*:

- **Recovery event:** A syslog message or condition that indicates the fault has cleared on its own (e.g., "BGP neighbor goes back to Up state"). Include an example message.
- **Recovery window:** How long after the fault event to watch for the recovery event (e.g., "within 5 minutes").

| Human writes | AI → FS | AI → RAW |
|---|---|---|
| Example syslog message | `evaluation.value` (regex derived from example) | — |
| Key values to extract | `extraction_parameter` (variable name, pattern, group) | `workflow.inputs` |
| "Both events" / "Either event" | `conditions.logic` (`AND` / `OR`) | — |
| "Within 5 minutes" | `logic_lookback_time: 300` | — |
| Recovery event example | `clear_event.pattern` + `clear_event.lookback_period` | — |

### 4. Symptoms

A bullet list of observable behaviors a network engineer would notice when this fault is active. These are the human-visible indicators that something is wrong — not the machine-parseable syslog events.

| Human writes | AI → FS | AI → RAW |
|---|---|---|
| Symptom bullets | — (informational context) | — (informational context) |

### 5. Diagnosis & Repair Steps

The core of the guide. Each step follows a consistent structure that allows AI to derive both FS evaluation patterns (from the sample outputs) and RAW validation/action steps (from the commands and decision points).

**Per step:**

- **Step number and purpose:** What this step determines (e.g., "Step 1: Confirm BGP session is down and identify failure reason").
- **Commands:** The exact CLI commands to run. Use `{{ variable_name }}` placeholders for extracted values.
- **What to look for:** Plain-English description of what the output means.
- **Sample output — healthy (pass):** A realistic CLI output showing what a healthy/non-faulted state looks like. Label it clearly.
- **Sample output — fault confirmed (fail):** A realistic CLI output showing the faulted state. Label it clearly.
- **Decision point:** What to do based on the output. Written as prose: "If X, proceed to Step N. If Y, this guide does not apply." or "If X, proceed to RMA. Otherwise, continue."
- **Caution** *(optional)*: Safety warnings about the command (e.g., "Do not leave debug running on a production router").

| Human writes | AI → FS | AI → RAW |
|---|---|---|
| CLI commands with placeholders | — | `eval_cli.commands` |
| Sample output (pass) | — | `eval_cli.pattern` (derived — pass pattern) |
| Sample output (fail) | `evaluation.value` refinement | `eval_cli.pattern` (derived — fault pattern) |
| Decision point prose | — | `action_select` branches with conditions |
| "Proceed to Step 5" | — | `goto: step_id` |
| "Open an RMA" | — | `escalate: type: rma` |
| "Wait 15 minutes" | — | `wait: duration: 900` |
| Caution text | — | — (informational) |

### 6. Escalation

When to give up on self-service repair and engage vendor support. Includes what data to collect before escalating.

| Human writes | AI → FS | AI → RAW |
|---|---|---|
| Escalation conditions | — | `escalate` action trigger conditions |
| Evidence to collect | — | `escalate.data` (list of show commands) |

### 7. Post-Repair Verification

Steps to confirm the fault is resolved after repair actions are applied.

| Human writes | AI → FS | AI → RAW |
|---|---|---|
| Verification commands | — | Final step `eval_cli` + `resolve` action |
| Expected healthy output | `clear_event` pattern refinement | `eval_cli.pattern` for success |

### 8. References *(optional)*

Links to Cisco bug IDs, release notes, configuration guides, or other documentation relevant to this fault.

| Human writes | AI → FS | AI → RAW |
|---|---|---|
| Bug IDs, doc links | `metadata.tags`, informational | `references` section |

---

## Part 2: Blank Template

Copy the template below and fill in each section. Write in plain English as if authoring a knowledge base article for a network engineer. No regex, no YAML, no code expressions.

---

````markdown
# Remediation Guide: [Fault Condition Title]

> **Alert Definition:** AD###### *(6-digit ID; matches parent folder `AD######-<slug>/` and the suffix on the linked FS, RAW, and this RG)*
> **Guide ID:** RG######
> **Linked Fault Signature:** FS######
> **Linked Repair Action Workflow:** RAW######

## Overview

[2–4 sentences: What fault does this guide address? What technology area is affected?
What is the general approach to diagnosis and repair?]

## Applicability

- **Products:** [List of hardware platforms or product families]
- **Operating Systems:** [OS name and version ranges]
- **Component:** [Primary subsystem: Fan, PSU, Optics, Route Processor, etc.]
- **Severity:** [Critical / Major / Warning / Minor]
- **Related Defects:** [Bug IDs, if any — e.g., CSCxx12345]

## Triggering Events

### Event 1: [Short event name]

- **Type:** [Syslog / Alarm / State Counter / Metric]
- **Message ID:** [Syslog mnemonic, e.g., BGP-5-ADJCHANGE]
- **Example Message:**
  ```
  [Paste a complete, realistic sample message exactly as it appears in the log]
  ```
- **Key Values to Extract:** [Describe what to capture — e.g., "The neighbor IP address
  appearing after 'neighbor' in the message", "The fan tray number in the FT<n> field"]

### Event 2: [Short event name] *(if applicable)*

[Same structure as Event 1]

### Correlation *(if multiple events)*

- **Logic:** [Both events must occur (AND) / Either event triggers the fault (OR)]
- **Time Window:** [e.g., "Both events within 5 minutes" or omit for single-event]

### Recovery Indicator *(optional)*

- **Recovery Event:** [Description + example message that indicates the fault cleared]
- **Recovery Window:** [e.g., "Within 5 minutes of the triggering event"]

## Symptoms

- [Observable behavior 1 — what the engineer notices]
- [Observable behavior 2]
- [Observable behavior 3]

## Diagnosis & Repair Steps

### Step 1: [Purpose — what this step determines]

**Commands:**
```
[exact CLI commands — use {{ variable_name }} for extracted values]
```

**What to Look For:** [Plain-English description of what the output means]

**Sample Output — Healthy:**
```
[Realistic CLI output showing the non-faulted state]
```

**Sample Output — Fault Confirmed:**
```
[Realistic CLI output showing the faulted state]
```

**Decision Point:** [What to do based on the output — e.g., "If hold time expired (4/0)
is confirmed, proceed to Step 2. If a different error code is present, this guide does
not apply."]

### Step 2: [Purpose]

[Same structure as Step 1. Repeat for each diagnosis and repair step.]

## Escalation

**When to Escalate:**
- [Condition 1 — e.g., "All repair steps applied but fault persists"]
- [Condition 2]

**Evidence to Collect Before Escalating:**
```
[List of show commands and data to gather]
```

## Post-Repair Verification

**Commands:**
```
[CLI commands to confirm the fault is resolved]
```

**Expected Healthy Output:**
```
[What the output should look like after successful repair]
```

## References *(optional)*

- [Bug ID or doc title — URL if available]
````

---

## Part 3: Filled Examples

### Example A: Fan Tray Hardware Failure (Cisco 8000 Series)

This example demonstrates: three events with OR logic (one per syslog message ID across severity levels), key value extraction (fan tray number), a multi-step RAW with branching to RMA escalation, and post-replacement verification.

---

# Remediation Guide: Fan Tray Voltage/Current/Thermal Failure

## Overview

This guide provides step-by-step instructions to diagnose and resolve fan tray hardware failures on Cisco 8000 Series routers running IOS XR. When a voltage, current, or thermal alarm is raised for a fan tray, the engineer validates the failure through CLI inspection of environmental sensors, determines whether the fan tray requires replacement (RMA), and verifies the replacement after installation.

## Applicability

- **Products:** Cisco 8000 Series (8808, 8812, 8818)
- **Operating Systems:** IOS XR 7.x and later
- **Component:** Fan
- **Severity:** Major
- **Related Defects:** CSCxx12345 (Fan controller firmware issue in specific releases)

## Triggering Events

### Event 1: Fan Tray Critical Alarm

- **Type:** Syslog
- **Message ID:** PKT_INFRA-FM-2-FAULT_CRITICAL
- **Example Message:**
  ```
  envmon[156]: %PKT_INFRA-FM-2-FAULT_CRITICAL : ALARM_CRITICAL :low voltage alarm :DECLARE :0/FT0: Input_Vol
  ```
- **Key Values to Extract:** The fan tray number — the digit after "FT" in the location field (e.g., `0/FT0` means fan tray 0, `0/FT1` means fan tray 1).

### Event 2: Fan Tray Major Alarm

- **Type:** Syslog
- **Message ID:** PKT_INFRA-FM-3-FAULT_MAJOR
- **Example Message:**
  ```
  envmon[156]: %PKT_INFRA-FM-3-FAULT_MAJOR : ALARM_MAJOR :low voltage alarm :DECLARE :0/FT0: Input_Vol
  ```
- **Key Values to Extract:** The fan tray number — same as Event 1.

### Event 3: Fan Tray Minor Alarm

- **Type:** Syslog
- **Message ID:** PKT_INFRA-FM-4-FAULT_MINOR
- **Example Message:**
  ```
  envmon[156]: %PKT_INFRA-FM-4-FAULT_MINOR : ALARM_MINOR :low voltage alarm :DECLARE :0/FT0: Input_Vol
  ```
- **Key Values to Extract:** The fan tray number — same as Event 1.

### Correlation

- **Logic:** Any one of the three events triggers this guide (OR). Each syslog message ID is a distinct event and generates a separate Fault Signature. PKT_INFRA-FM-2-FAULT_CRITICAL, PKT_INFRA-FM-3-FAULT_MAJOR, and PKT_INFRA-FM-4-FAULT_MINOR are not aliases — they must not be combined into a single event definition.

### Recovery Indicator

- **Recovery Event:** Not applicable — fan tray hardware faults do not self-recover. The alarm clears only after the fan tray is physically replaced and environmental sensors return to normal.

## Symptoms

- Environmental alarm LED illuminated on the chassis
- Syslog messages indicating voltage, current, or thermal alarm for a fan tray slot
- Possible elevated chassis temperature if multiple fan trays are affected
- `show environment` output shows dash (`-`) values for the affected fan tray sensors

## Diagnosis & Repair Steps

### Step 1: Identify Faulted Fan Tray Location

Confirm which fan tray triggered the alarm by reviewing the syslog event.

**Commands:**
```
show logging | include FT
```

**What to Look For:** The syslog message contains the fan tray location in the format `0/FT<number>`. Record the fan tray number for use in subsequent commands.

**Sample Output — Fault Confirmed:**
```
envmon[156]: %PKT_INFRA-FM-2-FAULT_CRITICAL : ALARM_CRITICAL :low voltage alarm :DECLARE :0/FT0: Input_Vol
```

**Decision Point:** Record the fan tray number (e.g., `0` from `0/FT0`) and proceed to Step 2.

### Step 2: Check Fan Tray Environment Status

Inspect the voltage, current, and power readings for the affected fan tray. Dash (`-`) values indicate a sensor read failure, which confirms a hardware fault.

**Commands:**
```
show environment all location 0/FT{{ module_number }}
```

**What to Look For:** Check the `Input_Vol`, `Input_Cur`, and `Power Used` fields. A dash (`-`) in any of these fields means the sensor cannot communicate with the fan tray — the hardware has failed.

**Sample Output — Healthy:**
```
RP/0/RP0/CPU0:router#show environment all location 0/FT1
Location  VOLTAGE                Value    Crit   Minor   Minor   Crit
          Sensor                 (mV)     (Lo)   (Lo)    (Hi)    (Hi)
-------------------------------------------------------------------------
0/FT1     Input_Vol              54200    47000  50500   56000   57500

Location  CURRENT                Value
          Sensor                 (mA)
-------------------------------------------------------------------------
0/FT1     Input_Cur              2800
```

**Sample Output — Fault Confirmed:**
```
RP/0/RP0/CPU0:router#show environment all location 0/FT1
Location  VOLTAGE                Value    Crit   Minor   Minor   Crit
          Sensor                 (mV)     (Lo)   (Lo)    (Hi)    (Hi)
-------------------------------------------------------------------------
0/FT1     Input_Vol              -        47000  50500   56000   57500

Location  CURRENT                Value
          Sensor                 (mA)
-------------------------------------------------------------------------
0/FT1     Input_Cur              -
```

**Decision Point:** If any field shows a dash (`-`), the fan tray has a confirmed hardware failure — proceed to Step 5 (Process RMA). If all values are numeric, continue to Step 3.

### Step 3: Validate Input Voltage

Check whether the fan tray input voltage is within the acceptable operating range.

**Commands:**
```
show environment voltage | begin 0/FT{{ module_number }}
```

**What to Look For:** The input voltage value. Normal range is approximately 48,000–56,000 mV. A value of 0 or greater than 60,000 mV indicates a voltage regulator failure.

**Sample Output — Healthy:**
```
0/FT1     Input Voltage          54200
```

**Sample Output — Fault Confirmed:**
```
0/FT1     Input Voltage          0
```

**Decision Point:** If input voltage is 0 or exceeds 60,000 mV, the fan tray has a confirmed voltage failure — proceed to Step 5 (Process RMA). Otherwise, continue to Step 4.

### Step 4: Validate Input Current

Check whether the fan tray is drawing current.

**Commands:**
```
show environment current | begin 0/FT{{ module_number }}
```

**What to Look For:** The input current value. A value of 0 means the fan tray is not drawing power — either the power connection has failed or the fan controller is dead.

**Sample Output — Healthy:**
```
0/FT1     Input Current          2800
```

**Sample Output — Fault Confirmed:**
```
0/FT1     Input Current          0
```

**Decision Point:** If input current is 0, the fan tray has a confirmed power failure — proceed to Step 5 (Process RMA). If the current is nonzero and all previous checks passed, the alarm may be transient — proceed to Step 6 (Monitor).

### Step 5: Process RMA

The fan tray has a confirmed hardware failure and must be replaced.

**Actions:**
1. Open an RMA case with Cisco TAC
2. Provide the syslog messages and CLI output from Steps 1–4 as evidence
3. Include the fan tray location (`0/FT{{ module_number }}`), serial number, and contract information

**Decision Point:** After the replacement fan tray is installed, proceed to Step 7 (Post-Repair Verification).

### Step 6: Monitor for Recurrence

No explicit failure was found in voltage, current, or power readings, but the alarm was triggered. The condition may be transient.

**Actions:**
1. Clear the alarm if supported by the platform
2. Monitor for recurrence over the next 24–48 hours
3. If alarms persist, open a support case with Cisco TAC for further investigation

**Decision Point:** If alarms do not recur, the issue was transient — no further action. If alarms recur, escalate per the Escalation section.

## Escalation

**When to Escalate:**
- All diagnostic steps completed but no explicit failure condition found and alarms persist
- Multiple fan trays show simultaneous failures (may indicate a power shelf or backplane issue rather than individual fan tray failure)
- Suspected firmware defect (CSCxx12345) on affected software versions

**Evidence to Collect Before Escalating:**
```
show environment all
show environment voltage
show environment current
show logging | include FT
show platform
show version
admin show inventory
```

## Post-Repair Verification

After the replacement fan tray is installed, confirm it is operating normally.

**Commands:**
```
show environment all location 0/FT{{ module_number }}
show environment voltage | begin 0/FT{{ module_number }}
show environment current | begin 0/FT{{ module_number }}
```

**Expected Healthy Output:**
```
0/FT1     Input_Vol              54200    47000  50500   56000   57500
0/FT1     Input_Cur              2800
```

All values are numeric (no dashes), voltage is in the 48,000–56,000 mV range, and current is nonzero. All fan tray alarms should have cleared from the syslog.

## References

- CSCxx12345 — Fan controller firmware issue in specific IOS XR releases

---

### Example B: BGP Session Failure Due to MTU/PMTUD Black Hole (IOS XE)

This example demonstrates: two correlated events with AND logic, key value extraction (neighbor IP address), version-specific applicability with known defects, multiple repair options (immediate workaround vs. permanent fix), and a recovery indicator.

---

# Remediation Guide: BGP Session Failure — Path MTU Mismatch / PMTUD Black Hole

## Overview

This guide diagnoses and resolves BGP session failures caused by path MTU mismatch or Path MTU Discovery (PMTUD) black holes on IOS XE routers. When the actual path MTU is less than 1500 bytes (due to GRE tunnels, IPsec, or MPLS label stacks) and ICMP "Fragmentation Needed" messages are filtered, large BGP UPDATE messages are silently dropped. The TCP connection stalls and the BGP hold timer expires. This guide walks through confirming the MTU root cause, applying an immediate TCP MSS workaround, and scheduling a permanent fix.

## Applicability

- **Products:** Catalyst 9200, 9300, 9400, 9500, 9600; ISR 1000, 4000; ASR 1000; Cisco 8000 Series
- **Operating Systems:** IOS XE 16.x, IOS XE 17.x
- **Component:** Route Processor
- **Severity:** Major
- **Related Defects:** CSCwp39234 (large BGP packets exceeding IPsec tunnel MTU not forwarded), CSCwm17981 (per-neighbor PMTUD disable does not correctly set MSS to 536 on IOS XE 17.12.2)

## Triggering Events

### Event 1: BGP Neighbor Down Notification

- **Type:** Syslog
- **Message ID:** BGP-5-ADJCHANGE
- **Example Message:**
  ```
  %BGP-5-ADJCHANGE: neighbor 10.1.1.2 Down BGP Notification sent
  ```
- **Key Values to Extract:** The neighbor IP address — the IPv4 address appearing immediately after "neighbor" in the message (e.g., `10.1.1.2`).

### Event 2: BGP Hold Timer Expired Notification

- **Type:** Syslog
- **Message ID:** BGP-3-NOTIFICATION
- **Example Message:**
  ```
  %BGP-3-NOTIFICATION: sent to neighbor 10.1.1.2 4/0 (hold time expired) 0 bytes
  ```
- **Key Values to Extract:** The neighbor IP address — same as Event 1. The error code `4/0` (hold time expired) is the distinguishing indicator but does not need to be extracted as a variable.

### Correlation

- **Logic:** Both events must occur (AND). Event 1 alone (BGP neighbor down) has many causes; Event 2 alone (hold time expired notification) narrows the failure mode. Together they confirm the specific BGP-down-due-to-hold-timer-expired pattern that is characteristic of MTU/PMTUD issues.
- **Time Window:** Both events within 5 minutes.

### Recovery Indicator

- **Recovery Event:** BGP neighbor returns to Up state.
  ```
  %BGP-5-ADJCHANGE: neighbor 10.1.1.2 Up
  ```
- **Recovery Window:** Within 5 minutes of the triggering event.

## Symptoms

- BGP neighbor repeatedly drops to Idle or Active state
- Basic ICMP ping to the BGP neighbor succeeds but large pings with DF-bit set fail
- Session establishes briefly (a few routes learned) then drops again
- BGP UPDATE message count is asymmetric: many sent, few or none received from the peer
- TCP retransmission count is climbing for the BGP TCP session
- Partial route table — some prefixes installed, then session resets

## Diagnosis & Repair Steps

### Step 1: Confirm BGP Session Down with Hold Timer Expired

Verify the BGP session is down and confirm the specific failure reason is hold-timer-expired (error code 4/0). This error code distinguishes MTU-related failures from other BGP drop causes.

**Commands:**
```
show ip bgp summary
show ip bgp neighbors {{ neighbor_ip }} | include state|Hold|Notification|Last reset
show logging | include BGP
```

**What to Look For:** BGP state should be Idle, Active, or Connect (not Established). The "Last reset" reason should say "BGP Notification sent" and the notification error code should be "hold time expired (4/0)".

**Sample Output — Healthy:**
```
BGP state = Established, up for 3d14h
```

**Sample Output — Fault Confirmed:**
```
BGP state = Idle
Last reset 00:02:15, due to BGP Notification sent
Notification errorcode is hold time expired(4/0)
```

**Decision Point:** If "hold time expired (4/0)" is confirmed, proceed to Step 2. If a different notification error code is present (e.g., 2/2 Unsupported Capability, 6/7 Connection Collision), this guide does not apply — investigate the specific notification code.

### Step 2: Verify Basic Connectivity

Confirm that basic IP connectivity to the BGP neighbor exists. Small packets will succeed even when the path MTU is reduced, so a successful ping here does *not* rule out MTU issues.

**Commands:**
```
ping {{ neighbor_ip }} repeat 5
```

**What to Look For:** All 5 pings should succeed (100% success rate). Total failure indicates a link-layer or routing problem unrelated to MTU.

**Sample Output — Healthy (expected for MTU scenario):**
```
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms
```

**Sample Output — Total Failure (different problem):**
```
Success rate is 0 percent (0/5)
```

**Decision Point:** If all pings fail, this is a basic connectivity problem — troubleshoot the physical link and IP routing before revisiting BGP. If pings succeed, proceed to Step 3.

### Step 3: Test Path MTU with DF-Bit Pings

Send large pings with the Don't Fragment (DF) bit set to test the actual path MTU. This is the pivotal diagnostic step.

**Commands:**
```
ping {{ neighbor_ip }} size 1500 df-bit repeat 3
ping {{ neighbor_ip }} size 1400 df-bit repeat 3
ping {{ neighbor_ip }} size 1450 df-bit repeat 3
```

**What to Look For:** If the 1500-byte DF-bit ping fails (timeout or unreachable) but smaller sizes succeed, the path MTU is less than 1500 bytes. Find the largest size that succeeds to determine the actual path MTU.

**Sample Output — MTU Issue Confirmed:**
```
ping 10.1.1.2 size 1500 df-bit repeat 3
Success rate is 0 percent (0/3)

ping 10.1.1.2 size 1400 df-bit repeat 3
Success rate is 100 percent (3/3)
```

**Sample Output — No MTU Issue:**
```
ping 10.1.1.2 size 1500 df-bit repeat 3
Success rate is 100 percent (3/3)
```

**Decision Point:** If the 1500-byte DF-bit ping fails, path MTU is confirmed as the root cause — proceed to Step 4. If all sizes including 1500 succeed, MTU is not the root cause — consider BGP timer misconfiguration, CPU overload, or TCP RST injection by a firewall.

**Caution:** In some environments, ICMP is blocked so pings show timeout (`.`) rather than unreachable (`U`). Both indicate failure. The absence of an ICMP response to 1500-byte pings combined with BGP hold-timer expiry confirms the PMTUD black hole.

### Step 4: Check Interface MTU and TCP MSS

Examine the local interface MTU settings and the TCP MSS negotiated for the BGP session. The interface may report 1500 bytes, but the actual path MTU is lower due to tunnel or MPLS overhead on intermediate links.

**Commands:**
```
show interfaces <bgp_interface> | include MTU
show ip bgp neighbors {{ neighbor_ip }} | include segment
```

**What to Look For:** The interface MTU will typically show 1500 bytes (standard Ethernet). The TCP MSS will show "max data segment is 1460 bytes" (1500 − 40 for IP + TCP headers). This 1460-byte MSS is too large for any path with an effective MTU below 1500 bytes.

**Sample Output — Fault Confirmed (MSS too high for path):**
```
MTU 1500 bytes
Datagrams (max data segment is 1460 bytes)
```

**Decision Point:** Proceed to Step 5 to confirm PMTUD is broken, or proceed directly to Step 6 to apply the workaround if you are confident MTU is the cause.

### Step 5: Confirm PMTUD Black Hole

Verify that ICMP "Fragmentation Needed" (Type 3 Code 4) messages are not reaching the router. If PMTUD were working, TCP would have already reduced the MSS automatically.

**Commands:**
```
debug ip icmp
ping {{ neighbor_ip }} size 1500 df-bit repeat 3
undebug all
```

**What to Look For:** With debug enabled, watch for ICMP fragmentation-needed messages after the large ping.

**Sample Output — PMTUD Working (not expected in this fault):**
```
ICMP: dst (10.1.1.2) frag. needed and DF set rcvd from 10.2.2.1
```

**Sample Output — PMTUD Broken (black hole confirmed):**
```
[No ICMP fragmentation-needed debug messages appear despite the ping failing]
```

**Decision Point:** If no ICMP fragmentation-needed messages appear, PMTUD is broken — a firewall, ACL, or "no ip unreachables" on an intermediate device is filtering ICMP. Proceed to Step 6 (Apply Workaround).

**Caution:** Do not leave `debug ip icmp` running on a production router under load. Disable immediately after the test with `undebug all`.

### Step 6: Apply TCP MSS Workaround (Immediate Fix)

Apply a global TCP MSS clamp to prevent BGP TCP segments from exceeding the path MTU. This is an operational workaround that takes effect for new TCP connections.

**Option A — Global TCP MSS (recommended):**
```
configure terminal
ip tcp mss 1360
end
```
Calculate MSS = path_MTU (from Step 3) − 40 bytes. Example: path MTU of 1400 → MSS of 1360.

**Option B — Per-neighbor PMTUD disable (more conservative, forces MSS to 536):**
```
configure terminal
router bgp <local_as>
 neighbor {{ neighbor_ip }} transport path-mtu-discovery disable
end
```

**What to Look For:** After applying, verify the MSS has been updated.

**Sample Output — Fix Applied:**
```
router#show ip bgp neighbors 10.1.1.2 | include segment
  Datagrams (max data segment is 1360 bytes)
```

**Decision Point:** Option A (global MSS) is preferred because a 536-byte MSS from Option B is unnecessarily conservative and degrades throughput. After applying, proceed to Step 7 to verify recovery. Schedule a permanent fix (Step 8) for the next maintenance window.

**Caution:** The global `ip tcp mss` command affects all TCP connections on the router, not just BGP. On IOS XE 17.12.2, defect CSCwm17981 causes Option B to not correctly set MSS to 536 — use Option A on affected versions.

### Step 7: Verify BGP Session Recovery

Wait for the BGP hold timer to expire and the session to re-establish with the corrected MSS. This typically takes one hold-timer cycle (60–180 seconds).

**Commands:**
```
show ip bgp summary
show ip bgp neighbors {{ neighbor_ip }} | include state|Hold|Prefixes|segment
show ip bgp neighbors {{ neighbor_ip }} | include retransmit
```

**What to Look For:** BGP state should return to Established. Prefixes received should match the expected route count from the peer. TCP retransmissions should be stable (not accumulating).

**Sample Output — Healthy (recovered):**
```
BGP state = Established, up for 00:01:30
Prefixes Current:  12500  (Coverage: full table from peer)
Datagrams (max data segment is 1360 bytes)
0 retransmissions in last 60 seconds
```

**Sample Output — Still Faulted:**
```
BGP state = Idle
```

**Decision Point:** If the session is Established with correct MSS and stable retransmissions, the workaround is successful — schedule Step 8 for permanent fix. If the session remains down after applying the MSS workaround, escalate per the Escalation section.

### Step 8: Permanent Fix (Scheduled Maintenance)

Correct the underlying MTU problem to eliminate the need for MSS clamping workarounds. Choose the appropriate option:

**Option A — Allow ICMP unreachables (restore PMTUD):**
Identify and modify the firewall or ACL blocking ICMP Type 3 Code 4. On intermediate IOS XE routers:
```
interface <intermediate_interface>
 ip unreachables
```

**Option B — Fix intermediate link MTU:**
If a tunnel is adding overhead, increase the tunnel MTU:
```
interface Tunnel0
 ip mtu 1400
 ip tcp adjust-mss 1360
```

**Option C — Align CE interface MTU to path:**
```
interface <bgp_interface>
 ip mtu 1400
```

**Decision Point:** After applying the permanent fix, remove the MSS workaround from Step 6 if it is no longer needed, and verify via Step 7 that the session remains stable.

**Caution:** Changing interface MTU causes a brief traffic interruption. If modifying a firewall to allow ICMP, specifically permit ICMP Type 3 Code 4 only — do not open all ICMP types without a security review. Schedule these changes during a maintenance window.

## Escalation

**When to Escalate:**
- BGP session remains down after applying all workaround and permanent fix steps
- Path MTU test (Step 3) succeeds at 1500 bytes but BGP still drops with hold-time-expired — MTU is not the root cause
- Platform/version matches CSCwp39234 (Cat 9x00, IOS XE 17.12.x–17.15.x) or CSCwm17981 (IOS XE 17.12.2) and workarounds are not effective
- The intermediate device reducing MTU is not under the customer's control

**Evidence to Collect Before Escalating:**
```
show ip bgp neighbors {{ neighbor_ip }}
show ip bgp summary
show interfaces <bgp_interface>
show ip traffic
show version
show logging (last 500 lines)
ping {{ neighbor_ip }} size 1500 df-bit
ping {{ neighbor_ip }} size 1400 df-bit
show ip bgp neighbors {{ neighbor_ip }} | section Message statistics
```

## Post-Repair Verification

After applying the permanent fix (Step 8) and removing any temporary workarounds:

**Commands:**
```
show ip bgp neighbors {{ neighbor_ip }} | include state|Hold|Prefixes|segment
show ip bgp neighbors {{ neighbor_ip }} | include retransmit
ping {{ neighbor_ip }} size 1500 df-bit repeat 5
```

**Expected Healthy Output:**
```
BGP state = Established, up for 1d02h
Prefixes Current:  12500
Datagrams (max data segment is 1460 bytes)
0 retransmissions in last 60 seconds
Success rate is 100 percent (5/5)
```

BGP state is Established, the MSS has returned to the default 1460 (because the path MTU is now 1500 or PMTUD is functioning), no TCP retransmissions are accumulating, and the 1500-byte DF-bit ping now succeeds.

## References

- CSCwp39234 — Large BGP packets exceeding IPsec tunnel MTU not forwarded (Cat 9x00, IOS XE 17.12.x–17.15.x)
- CSCwm17981 — C9500 not honoring TCP MSS of 536 bytes when PMTUD disabled (IOS XE 17.12.2)
